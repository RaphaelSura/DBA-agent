""" File containing main database class. Includes *postings* table."""
import psycopg2


class BikeDBAData:

    def __init__(self):
        self.conn = psycopg2.connect(
            "dbname='dba' user='postgres' password='postgres' host='127.0.0.1' port='5432'"
        )
        self.cur = self.conn.cursor()
        self.create()

    def create(self):
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS postings
        (url TEXT NOT NULL UNIQUE,
        price INTEGER,
        brand VARCHAR(200),
        frame_size INT,
        gears INT,
        frame_number VARCHAR(50),
        location VARCHAR(100),
        description TEXT,
        created TIMESTAMP,
        active BOOL,
        sent_to_user BOOL)
        """)

        self.conn.commit()

    def insert(self, args):

        self.cur.execute("INSERT INTO postings VALUES %s", (args, ))
        self.conn.commit()

    def update_active_status(self, active_urls):
        """ updates active status to FALSE for non existing postings.
            args: active_urls [tuple]: currently active postings """
        active_urls = tuple(active_urls)
        self.cur.execute(f"""
            UPDATE postings
            SET active = FALSE
            WHERE url NOT IN {active_urls}""")
        self.conn.commit()

    def update_sent_status(self, url):
        """ updates sent_to_user to TRUE after it is sent.
            args: url [string]: primary key in DB to find row."""

        self.cur.execute(f"""
            UPDATE postings
            SET sent_to_user = TRUE
            WHERE url = '{url}'""")
        self.conn.commit()

    # method to destroy the object: is run when the script is exited
    def __del__(self):
        self.conn.close()