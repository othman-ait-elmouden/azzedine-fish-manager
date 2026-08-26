import sqlite3
from contextlib import contextmanager
from config import DB_PATH

class Database:
    def __init__(self, path=DB_PATH):
        self.path = str(path)

    def connect(self):
        con = sqlite3.connect(self.path, timeout=20)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys=ON")
        con.execute("PRAGMA journal_mode=WAL")
        return con

    @contextmanager
    def transaction(self):
        con = self.connect()
        try:
            yield con
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

    def execute(self, sql, params=()):
        with self.transaction() as con:
            cur = con.execute(sql, params)
            return cur.lastrowid

    def query(self, sql, params=()):
        with self.connect() as con:
            return con.execute(sql, params).fetchall()

    def one(self, sql, params=()):
        with self.connect() as con:
            return con.execute(sql, params).fetchone()

db = Database()

