#!/usr/bin/env python3

from os import path
import configparser

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

    dbfile = cfg["DEFAULT"]["db"]


if __name__ == '__main__':
    main()
