#!/usr/bin/env python3

import sqlite3
from os import path
import configparser
import json

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
    print(miner)


def query_miner_data_dbg(miner):
    m_type = miner[2]
    m_ip = miner[3]
    print("[DEBUG]: Querying {} ({})...".format(m_ip, m_type))

    mf = open("docs/{}.json".format(m_type), "r")
    ret = json.load(mf)["data"]
    mf.close()

    print("[DEBUG]: Size: {}".format(len(ret)))

    return ret


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
            if dbg:
                k = query_miner_data_dbg(miner)
                print(k)
            else:
                query_miner_data(miner)
    else:
        print("The miners list is empty. Exiting...")


if __name__ == '__main__':
    main()
