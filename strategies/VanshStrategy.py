import logging
import csv
import datetime
import schedule

from brokerages.Brokerage import Brokerage
from brokerages.DryRunBrokerage import DryRunBrokerage
from strategies.AnalystUpgradeStrategy import AnalystUpgradeStrategy


class VanshStrategy(AnalystUpgradeStrategy):
    PROFIT_PERCENT = 2.5
    LOSS_PERCENT = 1.0

    def __init__(self, brokerage: Brokerage):
        super().__init__(brokerage)
        self.blacklist = ["CRM"]

    def register_events(self):
        super().register_events()
        schedule.every(5).minutes.do(self.sell_extreme_positions, self.PROFIT_PERCENT, self.LOSS_PERCENT)
        schedule.every().day.at("06:30").do(self.log_portfolio)

    def sell_extreme_positions(self, profit_percent, loss_percent):
        logging.info(f"Checking for any 'extreme' positions with return > {profit_percent}% or < {loss_percent}...")
        for position in self.brokerage.positions:
            if position.total_percent_return >= profit_percent or position.total_percent_return < loss_percent:
                self.brokerage.sell(position.ticker, position.num_shares)

    def log_portfolio(self):
        try:
            if isinstance(self.brokerage, DryRunBrokerage):
                return

            with open("portfolio_value.csv", "a+") as csv_file:
                writer = csv.writer(csv_file)
                row = str(datetime.datetime.now()).split(" ")
                row.append(self.brokerage.portfolio_value)
                writer.writerow(row)
        except Exception as ex:
            # Don't want to crash the app due to logging issues
            logging.error(f"Error logging portfolio: {ex}")

