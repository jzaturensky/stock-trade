#!/usr/bin/env python3
import sys
sys.path.append('..')

import requests
from datetime import timedelta
from datetime import datetime
import matplotlib.pyplot as plt
import yfinance as yf
from brokerages.DryRunBrokerage import DryRunBrokerage
from datasource.MarketbeatAnalystUpgradeSource import MarketbeatAnalystUpgradeSource
import time
import os


brokerage = DryRunBrokerage()

DAYS_TO_BACKTEST = int(sys.argv[1])

spy_total = 0
data_total = 0

start_date = datetime.today() - timedelta(days=DAYS_TO_BACKTEST)
date_arr = []
spy_open_arr = []
spy_close_arr = []
spy_daily_growth_arr = []
analyst_daily_growth_arr = []
spy_overall_growth_arr = []
analyst_overall_growth_arr = []


def get_open_and_close(ticker, date):
    r = requests.get("https://api.polygon.io/v1/open-close/"
                     + ticker + "/" + date + "?apiKey=" + os.environ['POLYGON']).json()

    return r["open"], r["close"]


# get_open_and_close("SPY", "2019-05-13")

def get_percent_change(start_price, end_price):
    return 100 * (end_price - start_price) / (start_price)


start_time = time.time()
for date in (start_date + timedelta(days=n) for n in range(DAYS_TO_BACKTEST)):
    if date.weekday() < 5:
        temp_date = date
        date = temp_date.strftime("%Y-%m-%d")
        date_robinhood = temp_date.strftime("%Y-%m-%d")
        print(date)
        r = requests.get(
            'https://api.robinhood.com/markets/XNYS/hours/' + date_robinhood)
        if r.json()['is_open']:
            upgrades = []
            try:
                for upgrade in MarketbeatAnalystUpgradeSource.get_analyst_upgrades(date):
                    if brokerage.is_tradable_stock(upgrade.ticker):
                        upgrades.append(upgrade)
                # spy_open, spy_close = get_open_and_close("SPY", date)
                spy = yf.download("SPY", start=date, end=date, progress=False)
                spy_open = spy.Open.item()
                spy_close = spy.Close.item()
                spy_change = get_percent_change(spy_open,
                                                spy_close)
                spy_total += spy_change

                print(
                    f"Open SPY price was {spy_open}, close price was {spy_close}")

                date_arr.append(date)
                spy_open_arr.append(spy_open)
                spy_close_arr.append(spy_close)
                spy_daily_growth_arr.append(spy_change)
                spy_overall_growth_arr.append(spy_total)

            except Exception as e:
                print(e)
                pass
            analyst_daily_growth_arr.append(0)
            for upgrade in upgrades:
                try:
                    data = yf.download(
                        upgrade.ticker, start=date, end=date, progress=False)
                    data_open = data.Open.item()
                    data_close = data.Close.item()
                    # data_open, data_close = get_open_and_close(
                    #     upgrade.ticker, date)
                    data_change = get_percent_change(
                        data_open, data_close) / len(upgrades)
                    data_total += data_change
                    analyst_daily_growth_arr[-1] += data_change
                except:
                    print("Error " + upgrade.ticker)
            analyst_overall_growth_arr.append(data_total)


print("\n=='=========================================================================")
print(f"Day trade SPY\t -->\t {str(round(spy_total, 4))}".expandtabs(30))
print(f"Analyst upgrades\t -->\t {str(round(data_total, 4))}".expandtabs(30))
data = yf.download("SPY", start=start_date,
                   end=datetime.today(), progress=False)
print(
    f"Hold SPY\t -->\t {str(round(get_percent_change(data.Open.values[0], data.Open.values[-1]), 4))}".expandtabs(30))

plt.figure(1)
plt.xlabel("Days")
plt.ylabel("Stock Price")
plt.title(f"SPY Prices over the past {DAYS_TO_BACKTEST} days")
plt.plot(date_arr, spy_open_arr, label="SPY_OPEN")
plt.plot(date_arr, spy_close_arr, label="SPY_CLOSE")
plt.legend()
plt.show(block=False)

plt.figure(2)
plt.xlabel("Days")
plt.ylabel("Daily Percent Growth")
plt.title(f"Daily SPY VS Analyst Growth over the past {DAYS_TO_BACKTEST} days")
plt.plot(date_arr, spy_daily_growth_arr, label="SPY_GROWTH")
plt.plot(date_arr, analyst_daily_growth_arr, label="ANALYST_GROWTH")
plt.legend()
plt.show(block=False)

plt.figure(3)
plt.xlabel("Days")
plt.ylabel("Overall Percent Growth")
plt.title(
    f"Overall SPY VS Analyst Growth over the past {DAYS_TO_BACKTEST} days")
plt.plot(date_arr, spy_overall_growth_arr, label="SPY_GROWTH")
plt.plot(date_arr, analyst_overall_growth_arr, label="ANALYST_GROWTH")
plt.legend()
plt.show(block=False)

plt.pause(0.001)
end_time = time.time()
print(
    f"The total elapsed time for {DAYS_TO_BACKTEST} days was {end_time-start_time}")
plt.show()
