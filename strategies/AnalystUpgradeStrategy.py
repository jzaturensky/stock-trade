import logging
import sys

import schedule

from datasource.MarketbeatAnalystUpgradeSource import MarketbeatAnalystUpgradeSource
from strategies.Strategy import Strategy


class AnalystUpgradeStrategy(Strategy):
    PRICE_PERCENT_DIFF_THRESHOLD = 10  # target price has to be PRICE_PERCENT_DIFFERENCE_THRESHOLD % gt current price
    MAX_BUY_AMOUNT_PER_UPGRADE = 1000

    def on_market_open(self):
        upgrades = self.get_analyst_upgrades()
        viable_upgrade_buys = []
        for upgrade in upgrades:
            if upgrade.get_target_price_percentage_increase() > AnalystUpgradeStrategy.PRICE_PERCENT_DIFF_THRESHOLD:
                if upgrade.ticker.upper() not in self.blacklist:
                    viable_upgrade_buys.append(upgrade)

        allocations = self.allocate_positions(viable_upgrade_buys)
        for ticker, num_shares in allocations.items():
            self.brokerage.buy(ticker, num_shares)

    def on_market_close(self):
        self.brokerage.sell_all_positions()

    def get_analyst_upgrades(self, date=None):
        upgrades = []
        for upgrade in MarketbeatAnalystUpgradeSource.get_analyst_upgrades(date):
            if self.brokerage.is_tradable_stock(upgrade.ticker):
                upgrades.append(upgrade)
                logging.info(f"Parsed upgrade object: {upgrade.__dict__}")
            else:
                logging.debug(f"Not adding {upgrade.ticker} as it is not tradable on this brokerage")

        for upgrade in upgrades:
            logging.info(f"ANALYST UPGRADE - {upgrade.ticker} @ {upgrade.current_price}: "
                         f"{upgrade.old_rating} -> {upgrade.new_rating} w/ target {upgrade.new_target_price}")
        return upgrades

    def allocate_positions(self, upgrades, max_per_stock=sys.maxsize):
        """
        Allocates how many shares of each upgrade to buy. Splits evenly amongst all upgrades.
        TODO: Also base the amount bought based on the impact

        :param upgrades: List of upgrades
        :param max_per_stock: Maximum dollar amount to invest in each stock (defaults to unlimited)
        :return: Dictionary with mapping from stock name to number of shares to buy
        """
        allocations = {}
        if upgrades:
            available_power = self.brokerage.buying_power * 0.9  # to account for market fluctuations and safety
            max_per_stock = min(max_per_stock, round(available_power / len(upgrades), 2))
            logging.info(f"Allocating ${max_per_stock} towards each upgrade")
            allocations = {upgrade.ticker: int(max_per_stock / upgrade.current_price) for upgrade in upgrades}
            for upgrade in upgrades:
                num_shares = int(max_per_stock / upgrade.current_price)
                if num_shares:
                    allocations[upgrade.ticker] = num_shares
                else:
                    logging.warning(f"{upgrade.ticker} was in viable buys, but computed 0 shares to buy")
        return allocations

    def register_events(self):
        schedule.every().day.at("07:15").do(self.on_market_open)
        schedule.every().day.at("12:45").do(self.on_market_close)
