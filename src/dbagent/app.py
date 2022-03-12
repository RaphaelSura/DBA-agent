""" Main file to instantiate the bot and database and monitor for new postings
    Only runs once. Can be setup in crontab to run on regular basis.
"""
import time
import random
import pathlib
from dbagent.bot import WebpageMonitor
from dbagent.database import DBAData

# add *user* to database. A new posting will then have a column *user_id* for which user should get a notification
# add status update to *item* table


def main():
    """
    # the app is run through crontab and is started every 10 minutes
    $ crontab -e
    */10 6-23 * * * /usr/bin/python3 /path-to-folder/dbagent/app.py
    """
    # database file
    project_dir = pathlib.Path(__file__).parent.parent.parent.resolve()
    db_path = project_dir.joinpath("data", "dba.db")
    # telegram bot credentials
    cred_file = project_dir.joinpath("etc", "telegram_creds.txt")
    driver = pathlib.Path("/usr/lib/geckodriver")

    # url and filters already
    website = "https://dba.dk"

    # search for 1 item through several search key words
    items = {
        'ceramic oven':
        ['keramikovn', 'keramik+ovn', 'ler+ovn', 'scandia+ovn', 'cerama']
    }
    region = 'sjaelland'
    price_min = 500
    price_max = 30000
    dba_database = DBAData(db_path)

    for item_type, keywords in items.items():
        for k_w in keywords:
            url = f"/soeg/reg-{region}/?soeg={k_w}&pris=({price_min}-{price_max})"
            print('Checking DBA on:', url)
            bot = WebpageMonitor(website, item_type, dba_database, cred_file,
                                 driver)
            bot.fetch_url_data(url)
            bot.parse_items()
            bot.detect_new_postings()
            # to help not making it look like a bot
            time.sleep(random.randrange(1, 3) + random.random())


if __name__ == '__main__':
    main()
