import datetime
import logging

import requests
from bs4 import BeautifulSoup

from datasource.DataSource import DataSource
from models.Upgrade import Upgrade

import yfinance as yf


class MarketbeatAnalystUpgradeSource(DataSource):

    @staticmethod
    def get_analyst_upgrades(date=None):
        logging.info("Fetching analyst upgrades")
        upgrades = []
        url = f"https://www.marketbeat.com/ratings/Upgrades/{date if date is not None else 'latest'}/"
        html = requests.get(url).text
        soup = BeautifulSoup(html, 'html.parser')
        ratings_table = soup.find('table', {'id': 'ratingstable'})
        ratings = ratings_table.find('tbody')
        for rating in ratings:

            if not len(rating.contents) or "No ratings meeting this criteria" in rating.contents[0].text:
                logging.warning(f"No ratings found. Skipping further parsing")
                break

            # There is an extra irrelevant table element with class 'dontexpand' that we want to ignore
            if not rating.get('class'):
                # Only trade USD securities
                ticker = rating.contents[2].get('data-order')
                if rating.contents[3].text.startswith('$'):
                    upgrade = Upgrade()
                    upgrade.analyst_name = rating.contents[0].get('data-order')
                    upgrade.ticker = ticker
                    upgrade.current_price = yf.Ticker(
                        ticker).info["regularMarketPrice"]

                    upgrade.impact = int(rating.contents[6].get('data-order'))

                    old_and_new_target_price = rating.contents[4].text.strip()
                    if old_and_new_target_price:
                        old_and_new_target_price = old_and_new_target_price.split(
                            '➝')
                        if len(old_and_new_target_price) == 1:
                            upgrade.new_target_price = float(
                                old_and_new_target_price[0].strip()[1:].replace(',', ''))
                        elif len(old_and_new_target_price) == 2:
                            upgrade.old_target_price = float(
                                old_and_new_target_price[0].strip()[1:].replace(',', ''))
                            upgrade.new_target_price = float(
                                old_and_new_target_price[1].strip()[1:].replace(',', ''))

                    # If the target price < current price, we do not want to act on this upgrade
                    if upgrade.new_target_price is not None and upgrade.new_target_price < upgrade.current_price:
                        logging.warning(
                            f"{ticker}'s target price is lower than current price. Skipping...")
                        continue

                    old_and_new_rating = rating.contents[5].text.strip()
                    old_and_new_rating = old_and_new_rating.split('➝')
                    if len(old_and_new_rating) == 1:
                        upgrade.new_rating = old_and_new_rating[0].strip()
                    elif len(old_and_new_rating) == 2:
                        upgrade.old_rating = old_and_new_rating[0].strip()
                        upgrade.new_rating = old_and_new_rating[1].strip()

                    upgrades.append(upgrade)

                else:
                    logging.warning(
                        f"{ticker} is a non-USD security. Skipping...")

        return upgrades
