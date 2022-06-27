import os
from datetime import datetime

import yfinance

from brokerages.Brokerage import Brokerage
from datasource.MarketbeatAnalystUpgradeSource import MarketbeatAnalystUpgradeSource
from models.Upgrade import Upgrade
from strategies.Strategy import Strategy
import schedule
import csv


class MarketbeatPeriodicChecker(Strategy):

    def __init__(self, brokerage: Brokerage):
        super().__init__(brokerage)
        self.daily_upgrades = []
        self.is_market_open = False
        self.log_dir = "logs"
        self.log_filename = "analyst_upgrades_log.csv"
        self.csv_columns = list(Upgrade().__dict__.keys())
        self.csv_columns.insert(0, "time")
        self.csv_columns.insert(0, "date")

        # If the daemon is started/restarted during the middle of the day, set market open if necessary
        weekday = datetime.today().weekday()
        if weekday >= 0 and weekday <= 4:
            hour = datetime.today().hour
            minute = datetime.today().minute
            if (hour == 6 and minute >= 30) or (hour > 6 and hour <= 12):
                self.is_market_open = True

    def register_events(self):
        schedule.every().day.at("06:30").do(self.on_market_open)
        schedule.every().day.at("13:00").do(self.on_market_close)
        schedule.every(30).seconds.do(self.get_analyst_upgrades)

    def on_market_open(self):
        self.daily_upgrades = []
        self.is_market_open = True

    def on_market_close(self):
        self.is_market_open = False

    def get_analyst_upgrades(self):
        if not self.is_market_open:
            return

        upgrades = MarketbeatAnalystUpgradeSource.get_analyst_upgrades()
        new_upgrades = [
            upgrade for upgrade in upgrades if not self.daily_db_contains(upgrade.ticker)]
        self.daily_upgrades = upgrades
        self.log_new_upgrades(new_upgrades)

    def daily_db_contains(self, ticker):
        return any(ticker == upgrade.ticker for upgrade in self.daily_upgrades)

    def log_new_upgrades(self, new_upgrades):
        date = datetime.today().strftime('%Y-%m-%d')
        time = datetime.today().strftime('%H:%M:%S')
        dir_exists = os.path.isdir(self.log_dir)
        file_exists = os.path.isfile(
            os.path.join(self.log_dir, self.log_filename))

        if not dir_exists:
            os.mkdir(self.log_dir)

        with open(os.path.join(self.log_dir, self.log_filename), 'a') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.csv_columns)

            if not file_exists:
                writer.writeheader()

            for upgrade in new_upgrades:
                row = upgrade.__dict__
                row["date"] = date
                row["time"] = time
                writer.writerow(row)
