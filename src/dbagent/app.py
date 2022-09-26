""" Main file to instantiate the bot and database and monitor for new postings
"""
import time
import pathlib
import numpy as np
from dbagent.bot import WebpageMonitor, TelegramBot
from dbagent.database import BikeDBAData


def main():
    """
    the app is run indefinitely in a Docker container
    and communicates to a Postgres database running in another container.
    """
    delta_t = 1800
    project_dir = pathlib.Path(__file__).parent.parent.parent.resolve()
    # telegram bot credentials
    cred_file = project_dir.joinpath("etc", "telegram_creds.txt")
    tlg_token, tlg_chat_id = np.loadtxt(cred_file, dtype=str)
    # web browser driver for selenium
    driver = pathlib.Path("/usr/lib/geckodriver")

    # url and filters already
    website = "https://www.dba.dk"
    frame_size_min = 58
    price_min = 1000
    price_max = 10000
    dba_database = BikeDBAData()
    telegram_bot = TelegramBot(tlg_token, tlg_chat_id, dba_database)
    url = f"/cykler/cykler-og-cykelanhaengere/racercykler/type-herreracer/?stelstoerrelse=({frame_size_min}-)&pris=({price_min}-{price_max})&soegfra=2600&radius=40"

    # simple time spacing between url request call
    send_warning = True
    while True:
        try:
            bot = WebpageMonitor(website, dba_database, driver)
            bot.fetch_url_data(url)
            bot.parse_items()
            bot.detect_new_postings()
            time.sleep(1)
            telegram_bot.notify_user()

            time.sleep(delta_t)
            send_warning = True
        except RuntimeError:
            print(f"Error running, retrying in {delta_t} seconds.")
            # this is so that the warning is sent only at the first fail.
            if send_warning:
                telegram_bot.send_warning()
                send_warning = False

    ##########


if __name__ == '__main__':
    main()
