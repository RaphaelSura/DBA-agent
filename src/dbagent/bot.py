""" File where the main bot is defined: class WebpageMonitor"""
from datetime import datetime
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from dbagent.database import BikeDBAData


class WebpageMonitor:
    """ Main class fetching data on website, communicating with database and sending telegram """

    def __init__(self, website: str, database: BikeDBAData, driver: Path):
        self.website = website
        self.active_postings = []
        self.page_items = []
        self.database = database
        self.driver = driver

    def fetch_url_data(self, specific_url):
        # define browser options
        url = self.website + specific_url

        options = Options()
        options.headless = True

        # start headless browser - all this needed to run on Raspberry PI
        profile = webdriver.FirefoxProfile()
        profile.native_events_enabled = False
        browser = webdriver.Firefox(firefox_profile=profile,
                                    executable_path=self.driver,
                                    options=options)
        browser.get(url)
        browser.implicitly_wait(5)
        # fetch html code
        source_code = browser.page_source
        # close the browser
        browser.close()

        # parse data
        soup = BeautifulSoup(source_code, 'html.parser')

        # dba has different classes depending on bold attributes etc...
        items1 = soup.find_all('tr',
                               {'class': "dbaListing listing hasInsertionFee"})
        items2 = soup.find_all(
            'tr', {'class': "dbaListing listing boldListing hasInsertionFee"})
        items3 = soup.find_all(
            'tr', {'class': "dbaListing listing lastListing hasInsertionFee"})
        items4 = soup.find_all('tr', {
            'class':
            "dbaListing listing boldListing lastListing hasInsertionFee"
        })
        self.page_items = [*items1, *items2, *items3, *items4]

    def parse_items(self):
        # loop thru each item and store in a dict(url: data)
        for item in self.page_items:
            link_url = item.find('a', {'class': 'listingLink'}).get('href')
            price = item.find('td', {'title': 'Pris'}).text.strip()
            price = int(price.split(" kr")[0].replace(".", ""))
            description = item.find_all(
                'a',
                {'class': 'listingLink'})[1].text.strip().replace('\n', ' ')
            location = item.find('ul', {
                'class': "details"
            }).find_all('span')[1].text.strip()
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            #             status_id = 1
            # parse description for brand, frame_size, gears, frame_number
            first_part_desc = description.split("cm stel, ")[0]

            _, brand, frame_size = first_part_desc.split(", ")
            frame_size = int(frame_size)
            second_part_desc = description.replace(
                first_part_desc + "cm stel, ", "")[:50].split(", ")
            #             print(second_part_desc)
            gears = None
            frame_number = None
            for desc in second_part_desc[:2]:
                if "gear" in desc:
                    try:
                        gears = int(desc.split(" gear")[0])
                    except ValueError:
                        gears = 1

                if "stelnr." in desc:
                    frame_number = desc.split("stelnr. ")[1]

            # aggregate data
            data = (link_url, price, brand, frame_size, gears, frame_number,
                    location, description, date, True, False)

            #             print(data)
            # add to the list of active posts
            self.active_postings.append(data)

        self.active_urls = [d[0] for d in self.active_postings]
        self.database.update_active_status(self.active_urls)

    def detect_new_postings(self):
        for data in self.active_postings:

            self.database.cur.execute(
                f"SELECT * FROM postings WHERE url = '{data[0]}'")

            # if empty -> new data -> add to database
            if not self.database.cur.fetchone():
                self.database.insert(data)


class TelegramBot:
    """Handles sending messages to user via Telegram
    """

    def __init__(self, token, chat_id, database):
        self.token = token
        self.chat_id = chat_id
        self.database = database

    def notify_user(self):
        # check database for sent=False
        self.database.cur.execute(
            "SELECT url, price, location FROM postings WHERE sent_to_user = False"
        )
        unsent_postings = self.database.cur.fetchall()

        # format the message:
        for url, price, location in unsent_postings:
            msg = f"💥 New bike on DBA 💥\nlocation: {location}\nPrice: {price}\n\n{url}"
            # send the telegram
            send_text = f"https://api.telegram.org/bot{self.token}/sendMessage?chat_id={self.chat_id}&parse_mode=Markdown&text={msg}"
            requests.get(send_text)
            # update sent status in database
            self.database.update_sent_status(url)

    def send_warning(self):
        date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"⚠️ Program failed to run on {date_now}. Check log file ⚠️"
        # send the telegram
        send_text = f"https://api.telegram.org/bot{self.token}/sendMessage?chat_id={self.chat_id}&parse_mode=Markdown&text={msg}"
        requests.get(send_text)
