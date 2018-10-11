import numpy as np
import pandas as pd
import datetime
import time
import sys
sys.path.append('../')
from ML_Trading import ML_functions as mlfcn
#from ML_Trading import Signals_Testing as st
from pytz import timezone
import requests
import bitmex
import json

API_FILE = '../bitmex.txt'
with open(API_FILE) as f:
    lines = [line.rstrip('\n') for line in open(API_FILE)]
print(lines)
client = bitmex.bitmex(test=False, api_key=lines[0], api_secret=lines[1])

out = client.Trade.Trade_getBucketed(binSize='5m', symbol='XBTUSD', count=100, reverse=True).result()[0]

print(out)





'''
start_date = datetime.datetime(2018, 7, 26, 0, 0, 0)
start_date = time.mktime(start_date.timetuple())
print('start date',start_date)
url = "https://api.bitfinex.com/v1/lends/eth/?limit_lends=4000?timestamp=" + str(start_date)

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
st.write(transactions_pd, 'eth_lending_rates.xlsx','sheet1')
'''