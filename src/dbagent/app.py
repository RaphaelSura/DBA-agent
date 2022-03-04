""" Main file to instantiate the bot and database and monitor for new postings
    Only runs once. Can be setup in crontab to run on regular basis.
"""
import time
import random
import pathlib
from dbagent.bot import WebpageMonitor
from dbagent.database import DBAData


def main():
    """
    # the app is run through crontab and is started every 10 minutes
    $ crontab -e
    */10 6-23 * * * /usr/bin/python3 /path-to-folder/pet-finder/app_with_crontab.py
    """
    # database file
    project_dir = pathlib.Path(__file__).parent.parent.parent.resolve()
    db_path = project_dir.joinpath("data", "dba.db")
    # telegram bot credentials
    cred_file = project_dir.joinpath("etc", "telegram_creds.txt")
    driver = pathlib.Path("/usr/lib/geckodriver")

    # url and filters already
    website = "https://dba.dk"
    item_urls = {
        #     'bike':
        #     "/cykler/cykler-og-cykelanhaengere/herrecykler/reg-koebenhavn-og-omegn/?soeg=cykel&stelstoerrelse=(60-)&pris=(-1999)&iswildcard",
        'ceramic oven': [
            "/soeg/reg-sjaelland/?soeg=keramikovn&pris=(2000-30000)",
            "/soeg/reg-sjaelland/?soeg=keramik+ovn&pris=(2000-30000)",
            "/soeg/reg-sjaelland/?soeg=ler+ovn&pris=(2000-30000)",
            "/soeg/reg-sjaelland/?soeg=scandia+ovn&pris=(2000-30000)",
            "/soeg/reg-sjaelland/?soeg=cerama&pris=(2000-30000)"
        ]
    }

    dba_database = DBAData(db_path)
    for item_type, urls in item_urls.items():
        for url in urls:
            print('Checking DBA on:', url)
            bot = WebpageMonitor(website, item_type, dba_database, cred_file,
                                 driver)
            bot.fetch_url_data(url)
            bot.parse_items()
            bot.detect_new_postings()
            # to help not making it look like a bot
            time.sleep(random.randrange(1, 5) + random.random())
    print('Shutting down virtual browser')


if __name__ == '__main__':
    main()
