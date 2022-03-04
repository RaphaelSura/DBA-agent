![build](https://github.com/RaphaelSura/DBA-agent/actions/workflows/build.yml/badge.svg)

# DBA-agent
App that monitors the Danish equivalent of Craigslist (Den Blå Avis - DBA) for new specific items. A telegram is sent whenever a new item is added given a specific category and filters. DBA has an 'agent' feature that does the same job, but ususally notifications come delayed, which is a problem for items that need very fast reaction. 

Technologies used here:
- Web monitoring/scraping
- SQLite database
- Telegram bot
- Crontab

## Installation
The repo is setup so as to install ```dbagent``` as a package. Once cloned and done creating a virtual environment, pip install the repo in editable mode (-e), which will take care of all the dependencies.
```
$ git clone https://github.com/RaphaelSura/DBA-agent.git
$ cd DBA-agent
$ python -m virtualenv .env
$ source .env/bin/activate
$ pip install -e .
```
Now ``` dbagent ``` is like any other python package.
```
from dbagent.database import DBAData
```
## Telegram bot setup
Install Telegram app on your phone or computer and create an account. Search for Botfather and type the following two commands in the chat:

- ```/start``` to get the BotFather bot setup.

- ```/newbot``` to create a new bot.

Choose a **bot name** e.g. FindMyPetBot. Then choose a **bot usernmae** e.g. mypetfinder_bot (must end with the word 'bot'). After creating the bot, it will display an **HTTP API token** ,you'll need this shortly. 

Now start a conversation with the bot, in the telegram app search for @bot_name and press *START*.

In a browser, type https://api.telegram.org/bot{my_bot_http_api_token}/getUpdates, where you use the correct value for your bot API token. In the response, note down the **Chat ID**. 

Put the **HTTP API token** and **chat ID** into etc/telegram_creds.txt. Note: the *etc* folder is in *.gitignore* as the content shouldn't be public.

## Run the app - CRONTAB on Ubuntu server
```
# python script for Pet App bot, runs every 10 minutes from 6am til midnight
*/10 6-23 * * * ~/dba-agent/.env/bin/python3 ~/dba-agent/app.py
```