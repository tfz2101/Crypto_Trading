import numpy as np
import pandas as pd
import datetime
import time
from Execution_Algorithms import *
import sys
sys.path.append('../../')
from ML_Trading import ML_functions as mlfcn
from ML_Trading import Signals_Testing as st
from pytz import timezone
from bitfinex.client import Client
import requests

'''
client = Client()
symbols = client.symbols()
print(symbols)

symbol = 'btcusd'


print(client.ticker(symbol))
print(client.today(symbol))
print(client.stats(symbol))

parameters = {'limit_asks': 2, 'limit_bids': 2}

print(client.lendbook('btc', parameters))
print(client.order_book(symbol, parameters))
'''




start_date = datetime.datetime(2018, 4, 26, 0, 0, 0)
start_date = time.mktime(start_date.timetuple())
print('start date',start_date)
url = "https://api.bitfinex.com/v1/lends/btc/?limit_lends=5000?timestamp=" + str(start_date)

response = requests.request("GET", url)

data = response.json()
transactions = []
for trade in data:

    rate = trade['rate']
    amount_lent = trade['amount_lent']
    amount_used = trade['amount_used']
    ts = int(trade['timestamp'])
    time = datetime.datetime.fromtimestamp(ts)
    print('time', time)
    transactions.append([time, rate, amount_lent, amount_used])

transactions_pd = pd.DataFrame(transactions, columns=['time', 'rate', 'amount_lent', 'amount_used'])

print(transactions_pd)
#st.write_new(transactions_pd, 'btc_lending_rates2.xlsx','sheet1')