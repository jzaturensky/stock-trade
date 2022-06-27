import sys
import time
import os
import csv
import threading
import yfinance as yf
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

log_dir = '../logs'
log_filename = 'analyst_upgrades_log.csv'

total_gains = 0
total_stocks = 0

start_date = ''
end_date = ''

def get_percent_change(start_price, end_price):
    return 100 * (end_price - start_price) / (start_price)

def calculate_gains(row):
    global total_gains, total_stocks
    buy_price = round(float(row['current_price']), 2)
    buy_date = row['date']
    ticker = row['ticker']
    #print(ticker, buy_date)
    try:
        stock = yf.Ticker(ticker)
        sell_price = round(float(stock.history(start=buy_date, end=buy_date).Close.item()), 2)
        gains = get_percent_change(buy_price, sell_price)
        total_gains += gains
        total_stocks += 1
    except:
        pass

start_time = time.time()

with open(os.path.join(log_dir, log_filename), 'r') as csv_file:
    reader = csv.DictReader(csv_file)
    threads = []
    start_date = next(reader)['date']

    for row in reader:
        t = threading.Thread(target=calculate_gains,args=(row,))
        threads.append(t)
        t.start()

    end_date = row['date']

    for t in threads:
        t.join()

# Calculate SPY gains
stock = yf.Ticker('SPY')
spy_price = stock.history(start=start_date, end=end_date)
spy_gain = round(float(get_percent_change(spy_price.Open[0].item(), spy_price.Close[-1].item())), 2)

print()
print('='*20)
print('Start : '+start_date+'\n End  : '+end_date)
print('='*20)
print('Total = %.2f' % (total_gains/total_stocks) + ' %')
print(' SPY  = %.2f' % (spy_gain) + ' %')
print('='*20)
print()

print("--- %s seconds ---" % round(time.time() - start_time, 2))