
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
        self.conn.commit()
        self.conn.close()

    def add_miner(self, nm: str, tp: str, ip: str):
        self.conn = sqlite3.connect(self.dbfile)
        self.conn.execute("""INSERT INTO minerlist (name, type, ip)
                        VALUES('{}', '{}', '{}');""".format(nm, tp, ip))
        self.conn.commit()
        self.conn.close()

    def get_miners(self):
        self.conn = sqlite3.connect(self.dbfile)
        ret = []
        res = self.conn.execute("SELECT * FROM minerlist")
        self.conn.commit()
        for row in res:
            ret += [[row[0], row[1], row[2], row[3]]]

        self.conn.close()
        return ret
