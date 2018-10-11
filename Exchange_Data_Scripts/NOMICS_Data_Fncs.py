import numpy as np
import pandas as pd
import datetime
import time
from Execution_Algorithms import *
import sys
sys.path.append('../')
from ML_Trading import ML_functions as mlfcn
from ML_Trading import Signals_Testing as st
from pytz import timezone
import requests


import urllib.request
url = "https://api.nomics.com/v1/currencies?key=2018-09-demo-dont-deploy-b69315e440beb145"
print(urllib.request.urlopen(url).read())



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