""" File where the main bot is defined: class WebpageMonitor"""
from datetime import datetime
from pathlib import Path
import numpy as np
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from dbagent.database import DBAData


class WebpageMonitor:
    """ Main class fetching data on website, communicating with database and sending telegram """

    def __init__(self, website: str, item_type: str, database: DBAData,
                 telegram_info: Path, driver: Path):
        self.website = website
        self.item_type = item_type
        self.active_postings = []
        self.page_items = []
        self.database = database

        # credentials for sending telegram
        self.token, self.chat_id = np.loadtxt(telegram_info, dtype=str)
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
            description = item.find_all(
                'a',
                {'class': 'listingLink'})[1].text.strip().replace('\n', ' ')
            location = item.find('ul', {
                'class': "details"
            }).find_all('span')[1].text.strip()
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            status_id = 1

            # aggregate data
            data = (link_url, self.item_type, price, location, description,
                    date, status_id)

            # add to the list of active posts
            self.active_postings.append(data)

    def detect_new_postings(self):
        for data in self.active_postings:
            url = data[0]
            # returns id if exists else None
            curr_post_id = self.database.cur.execute(
                f"SELECT id FROM item WHERE url = '{url}'").fetchone()
            # if empty -> new data -> add to database
            if not curr_post_id:
                self.database.insert_pet(data)
                useful_data = (self.item_type, data[2], data[3], data[0])
                self.notify_user(useful_data)

        # update status in database - need to work on this
        # status is 2 (inactive) for all, then set 1 (active) for all postings
        # self.database.update_status(self.active_posts)

    def notify_user(self, info):
        # format the message:
        item_type, price, location, url = info
        msg = f"💥 New {item_type} on DBA 💥\nlocation: {location}\nPrice: {price}\n\n{url}"
        # send the telegram
        send_text = f"https://api.telegram.org/bot{self.token}/sendMessage?chat_id={self.chat_id}&parse_mode=Markdown&text={msg}"
        requests.get(send_text)