
import sqlite3


class MinerData:
    def __init__(self, dbfile: str):
        self.dbfile = dbfile
        self.conn = None

        self.connect_db()

    def connect_db(self):
        self.conn = sqlite3.connect(self.dbfile)

        self.conn.execute("""CREATE TABLE IF NOT EXISTS minerlist (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     name TEXT,
                     type TEXT,
                     ip TEXT);""")

    def add_miner(self, nm: str, tp: str, ip: str):
        self.conn.execute("""INSERT INTO minerlist (name, type, ip)
                        VALUES('{}', '{}', '{}');""".format(nm, tp, ip))
        self.conn.commit()

    def get_miners(self):
        ret = []
        res = self.conn.execute("SELECT * FROM minerlist")
        for row in res:
            ret += [[row[0], row[1], row[2], row[3]]]

        return ret
