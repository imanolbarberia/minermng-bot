#!/usr/bin/env python3

import sqlite3
from os import path
import configparser
import json
import requests

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


def create_db(c):
    c.execute("""CREATE TABLE IF NOT EXISTS minerlist (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT,
                 type TEXT,
                 ip TEXT);""")
    c.commit()


def query_miner_data(miner):
    m_type = miner[2]
    m_ip = miner[3]
    """
    miner_data = {
        status = 1                  # Online = 1 / Offline = 0
        uptime = 234234,
        hr = 14123412.234,          # Total Miner Hashrate (MH/s)
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
    miner_data = {
        "status": 0,
        "uptime": 0,
        "hr": 0,
        "avg_tmps": [],
        "avg_fans": [],
        "tot_nonces": [],
        "boards": []
    }
    
    url = "http://www.hallsnet.org/{}.json".format(m_type)
    print("Getting {} ({})...".format(url, m_type))

    try:
        r = requests.get(url, timeout=5)
    except requests.exceptions.ConnectionError:
        print("[ERROR] Connection error")
        r = None

    if r is None:
        jdata = None
    else:
        jdata = r.json()["data"]
        # print(jdata)

        if len(jdata) > 0:
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
            miner_data["avg_tmps"] = [
                sum([e["tmps"][0] for e in miner_data["boards"]]) / len(miner_data["boards"]),
                sum([e["tmps"][1] for e in miner_data["boards"]]) / len(miner_data["boards"])
            ]
            fan_speeds = [e["fans"] for e in miner_data["boards"]]
            fan_speeds_transposed = [[row[i] for row in fan_speeds] for i in range(len(fan_speeds[0]))]
            miner_data["avg_fans"] = [sum(e)/len(e) for e in fan_speeds_transposed]

            tot_nonces = [e["nonces"] for e in miner_data["boards"]]
            tot_nonces_transposed = [[row[i] for row in tot_nonces] for i in range(len(tot_nonces[0]))]
            miner_data["tot_nonces"] = [sum(e) for e in tot_nonces_transposed]

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
    create_db(con)

    res = con.execute("SELECT * FROM minerlist")
    minerlist = res.fetchall()

    if len(minerlist) > 0:
        for miner in minerlist:
            k = query_miner_data(miner)
            print(k)
    else:
        print("The miners list is empty. Exiting...")


if __name__ == '__main__':
    main()
