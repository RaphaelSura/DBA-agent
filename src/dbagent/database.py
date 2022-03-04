import sqlite3
import pandas as pd


class DBAData:

    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.cur = self.conn.cursor()
        self.create()

    def create(self):
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS item
        (id INTEGER PRIMARY KEY,
        type_id INTEGER REFERENCES type(id),
        price TEXT,
        location TEXT,
        description TEXT,
        url TEXT NOT NULL UNIQUE,
        creation TIMESTAMP,
        status_id INTEGER REFERENCES status(id))
        """)

        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS type
        (id INTEGER PRIMARY KEY,
        name TEXT NOT NULL UNIQUE)
        """)

        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS status
        (id INTEGER PRIMARY KEY,
        value TEXT NOT NULL UNIQUE)
        """)

        # add active (1) and inactive (2) to status table
        if pd.read_sql("SELECT * FROM status", con=self.conn).empty:
            self.cur.execute("INSERT INTO status VALUES (NULL,?)",
                             ('active', ))
            self.cur.execute("INSERT INTO status VALUES (NULL,?)",
                             ('inactive', ))

        self.conn.commit()

    def insert_pet(self, args):
        link_url, item_type, price, location, description, date, status_id = args

        # convert race -> race_id
        type_id = self.cur.execute(
            f"SELECT id FROM type WHERE name = '{item_type}'").fetchone()
        if not type_id:
            self.insert_type(item_type)
            type_id = self.cur.execute(
                f"SELECT id FROM type WHERE name = '{item_type}'").fetchone()

        data = (type_id[0], price, location, description, link_url, date,
                status_id)
        self.cur.execute("INSERT INTO item VALUES (NULL,?,?,?,?,?,?,?)", data)
        self.conn.commit()

    def insert_type(self, type_):
        self.cur.execute("INSERT INTO type VALUES (NULL,?)", (type_, ))
        self.conn.commit()

    def update_status(self, active_ids):
        pass
        # self.cur.execute(
        #     f"""UPDATE INTO pet VALUES (NULL,?)
        # WHERE id NOT IN {active_ids}""", (2, ))
        # self.conn.commit()

    # method to destroy the object: is run when the script is exited
    def __del__(self):
        self.conn.close()
