#!/usr/bin/env python3
"""
This script uses Goldshell miner's API to query for miner data:
- /mcb/cgminer?cgminercmd=devs  -- Query most miner data
- /mcb/pools                    -- Query currently connected pools
"""

import sqlite3
from os import path
import configparser
import requests
from datetime import datetime

DEFAULT_CONFIG_FILE = "minermon.cfg"


def create_default_config():
    """
    Create new default config file
    :return: ConfigParser object with the new configuration by default
    """
    cfg = configparser.ConfigParser()
    cfg["DEFAULT"]["db"] = "miners.db"
    with open(DEFAULT_CONFIG_FILE, "w") as cfgfile:
        cfg.write(cfgfile)

    return cfg


def db_create(c):
    """
    Create basic DB structure.
    Tables:
        - minerlist     -- List of current registered miners
            * id            -- Miner ID in the DB
            * name          -- Name of the miner
            * type          -- Type of miner (kdbox, kd5, ckbox, ...)
            * ip            -- Current ip of the miner

        - minerdata     -- Average readings for the specified miner
            * id            -- Reading ID
            * miner_id      -- ID of the miner (from the 'minerlist' table)
            * timestamp     -- Timestamp of the reading. Format: "YYYY-MM-DD HH:MM:SS"
            * status        -- True (1) if miner is online, False (0) if it's offline
            * uptime        -- Number of minutes the miner has been running
            * hr            -- Current hashrate of the miner (in MH/s)
            * tmp_chip      -- Average chip temperature
            * tmp_brd       -- Average board temperature
            * fan0..fan3    -- Speed of fans 0 to 3
            * n_tot         -- Total nonces (across all boards)
            * n_acc         -- Accepted nonces
            * n_rej         -- Rejected nonces
            * n_err         -- Hardware errors

        - boarddata     -- Current readings for each miner boards
            * id            -- Reading ID
            * entry_id      -- ID of the associated reading entry (in 'minerdata' table)
            * board_id      -- ID of the board as part of the miner (0 to n-1, n being the number of boards in a miner)
            * hr            -- Board hashrate
            * tmp_chip      -- Average temperature of the chips in the board
            * tmp_brd       -- Board temperature
            * fan0..fan3    -- Speed of fans 0 to 3 as reported by the board
            * n_tot         -- Total nonces (from this board)
            * n_acc         -- Accepted nonces
            * n_rej         -- Rejected nonces
            * n_err         -- Hardware errors

    :param c: DB connection object
    :return: Nothing
    """
    c.execute("""CREATE TABLE IF NOT EXISTS minerlist (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT,
                 type TEXT,
                 ip TEXT);
            """)

    c.execute("""CREATE TABLE IF NOT EXISTS minerdata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                miner_id INTEGER,
                timestamp TEXT,
                status BOOLEAN,
                uptime INTEGER,
                pool TEXT,
                hr FLOAT,
                tmp_chip FLOAT,
                tmp_brd FLOAT,
                fan0 INTEGER,
                fan1 INTEGER,
                fan2 INTEGER,
                fan3 INTEGER,
                n_tot INTEGER,
                n_acc INTEGER,
                n_rej INTEGER,
                n_err INTEGER);
            """)

    c.execute("""CREATE TABLE IF NOT EXISTS boarddata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_id INTEGER,
                board_id INTEGER,
                hr FLOAT,
                tmp_chip FLOAT,
                tmp_brd FLOAT,
                fan0 INTEGER,
                fan1 INTEGER,
                fan2 INTEGER,
                fan3 INTEGER,
                n_tot INTEGER,
                n_acc INTEGER,
                n_rej INTEGER,
                n_err INTEGER);
            """)
    c.commit()


def db_insert_data(c, miner):
    sql = """INSERT INTO minerdata(miner_id, timestamp, status, uptime, pool, hr, tmp_chip, tmp_brd, fan0, fan1, fan2, fan3,
            n_tot, n_acc, n_rej, n_err) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
    data = (
        miner["id"],
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        miner["status"] == 1,
        miner["uptime"],
        miner["pool"],
        miner["hr"],
        miner["avg_tmps"][0] if len(miner["avg_tmps"]) > 0 else 0,
        miner["avg_tmps"][1] if len(miner["avg_tmps"]) > 1 else 0,
        miner["avg_fans"][0] if len(miner["avg_fans"]) > 0 else 0,
        miner["avg_fans"][1] if len(miner["avg_fans"]) > 1 else 0,
        miner["avg_fans"][2] if len(miner["avg_fans"]) > 2 else 0,
        miner["avg_fans"][3] if len(miner["avg_fans"]) > 3 else 0,
        miner["tot_nonces"][0],
        miner["tot_nonces"][1],
        miner["tot_nonces"][2],
        miner["tot_nonces"][3],
    )

    # Execute SQL and get last row ID
    cur = c.cursor()
    cur.execute(sql, data)
    c.commit()
    row_id = cur.lastrowid

    sql = """INSERT INTO boarddata(entry_id, board_id, hr, tmp_chip, tmp_brd, fan0, fan1, fan2, 
                    fan3, n_tot, n_acc, n_rej, n_err) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)"""

    for brd_num, brd in enumerate(miner["boards"]):
        brd_data = (
            row_id,
            brd_num,
            brd["hr"],
            brd["tmps"][0] if len(brd["tmps"]) > 0 else 0,
            brd["tmps"][1] if len(brd["tmps"]) > 1 else 0,
            brd["fans"][0] if len(brd["fans"]) > 0 else 0,
            brd["fans"][1] if len(brd["fans"]) > 1 else 0,
            brd["fans"][2] if len(brd["fans"]) > 2 else 0,
            brd["fans"][3] if len(brd["fans"]) > 3 else 0,
            brd["nonces"][0],
            brd["nonces"][1],
            brd["nonces"][2],
            brd["nonces"][3]
        )

        c.execute(sql, brd_data)
        c.commit()


def query_miner_data(miner):
    """
    miner_data = {
        status = 1                  # Online = 1 / Offline = 0
        uptime = 234234,
        hr = 14123412.234,          # Total Miner Hashrate (MH/s)
        pool = "us.pool.com"        # Pool where the miner is connected to
        avg_tmps = [                # Avg temperatures
            123.23,                     # Avg Chip temp
            123.23                      # Avg Board temp
        ],
        avg_fans = [                # Avg Fans speed
            4564,                       # Avg Fan #0 RPM
            3453,                       # Avg Fan #1 RPM
            ...     
            4564                        # Avg Fan #n RPM
        ],
        tot_nonces = [              # Total nonce metrics 
            2342,                       # total nonces
            2342,                       # total accepted
            23423,                      # total rejected
            2342                        # total err
        ],
        boards = [                  # Boards absolute data
            {                           # Board #0
                hr = 2342342.234,
                tmps = [
                    123.23,
                    123.23
                ],
                fans = [
                    1234,
                    1234,
                    ...
                    1234
                ],
                nonces = [              # Nonce metrics 
                    2342,                       # Nonces
                    2342,                       # Accepted
                    23423,                      # Rejected
                    2342                        # Err
                ],
            },
            ...
            {                           # Board #n
                ...
            }
        ]
    }
    """
    m_id = miner[0]
    m_name = miner[1]
    m_type = miner[2]
    m_ip = miner[3]
    miner_data = {
        "id": m_id,
        "status": 0,
        "uptime": 0,
        "pool": "(none)",
        "hr": 0,
        "avg_tmps": [0, 0],
        "avg_fans": [0],
        "tot_nonces": [0, 0, 0, 0],
        "boards": []
    }

    base_url = "http://{}".format(m_ip)
    data_url = "{}/mcb/cgminer?cgminercmd=devs".format(base_url)
    pool_url = "{}/mcb/pools".format(base_url)
    print("Getting {} -- {} ({})...".format(data_url, m_name, m_type))

    try:
        r = requests.get(data_url, timeout=10)
    except requests.exceptions.ConnectionError:
        print("[ERROR] Connection error")
        r = None

    if r is not None:
        jdata = r.json()["data"]
        # print(jdata)

        if len(jdata) > 0:
            miner_data["id"] = m_id
            miner_data["status"] = 1
            miner_data["uptime"] = jdata[0]["time"]
            miner_data["boards"] = []
            for jbrd in jdata:
                board_data = {
                    "hr": jbrd["hashrate"],
                    "tmps": [float(e) for e in jbrd["temp"].replace("°C", "").replace(" ", "").split("/")],
                    "fans": [int(e) for e in jbrd["fanspeed"].replace("rpm", "").replace(" ", "").split("/")],
                    "nonces": [
                        jbrd["nonces"],
                        jbrd["accepted"],
                        jbrd["rejected"],
                        jbrd["hwerrors"]
                    ]
                }
                miner_data["boards"] += [board_data]

            miner_data["hr"] = sum([e["hr"] for e in miner_data["boards"]])

            temps = [e["tmps"] for e in miner_data["boards"]]
            temps_transposed = [[row[i] for row in temps] for i in range(len(temps[0]))]
            miner_data["avg_tmps"] = [sum(e)/len(e) for e in temps_transposed]

            fan_speeds = [e["fans"] for e in miner_data["boards"]]
            fan_speeds_transposed = [[row[i] for row in fan_speeds] for i in range(len(fan_speeds[0]))]
            miner_data["avg_fans"] = [sum(e)/len(e) for e in fan_speeds_transposed]

            tot_nonces = [e["nonces"] for e in miner_data["boards"]]
            tot_nonces_transposed = [[row[i] for row in tot_nonces] for i in range(len(tot_nonces[0]))]
            miner_data["tot_nonces"] = [sum(e) for e in tot_nonces_transposed]

            try:
                r = requests.get(pool_url, timeout=10)
            except requests.exceptions.ConnectionError:
                print("[ERROR] Connection error")
                r = None
                pool_str = "(error)"

            if r is not None:
                jdata = r.json()

                pool_str = "(none)"
                for p in jdata:
                    if p["active"] is True:
                        pool_str = p["url"]

                miner_data["pool"] = pool_str

        else:
            pass

    else:
        pass

    return miner_data


def main():
    """
    MAIN FUNCTION
    """

    # Read config file, or create it with default values if it does not exist
    if path.exists(DEFAULT_CONFIG_FILE):
        cfg = configparser.ConfigParser()
        cfg.read(DEFAULT_CONFIG_FILE)
    else:
        cfg = create_default_config()

    dbfile = cfg["DEFAULT"].get("db")
    dbg = (cfg["DEFAULT"].get("debug") == "yes")
    con = sqlite3.connect(dbfile)
    db_create(con)

    res = con.execute("SELECT * FROM minerlist")
    minerlist = res.fetchall()

    if len(minerlist) > 0:
        for miner in minerlist:
            m_data = query_miner_data(miner)
            print(m_data)
            db_insert_data(con, m_data)

    else:
        print("The miners list is empty. Exiting...")


if __name__ == '__main__':
    main()
