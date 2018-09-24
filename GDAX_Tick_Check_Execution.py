import gdax
import inspect
import numpy as np
import pandas as pd
import datetime
import time
from Execution_Algorithms import *
from Signal_Algorithms_Tick_Data import getMA,getThreeAgreeSignal
from pytz import timezone
import sys
import pickle

sys.path.append('../')
from ML_Trading import ML_functions as mlfcn
from ML_Trading import Signals_Testing as st


logfile = open("logfile.txt", "a+")
logfile.truncate()
public_client = gdax.PublicClient(api_url='https://api.pro.coinbase.com')

MODE = 'REAL'

if MODE == 'REAL':
    API_FILE = '../gdax_real.txt'
    PUBLIC_CLIENT = gdax.PublicClient(api_url='https://api.pro.coinbase.com')
    AUTH_CLIENT = 'https://api.gdax.com'
elif MODE == 'FAKE':
    API_FILE = '../gdax_fake.txt'
    PUBLIC_CLIENT = gdax.PublicClient(api_url='https://api-public.sandbox.gdax.com')
    AUTH_CLIENT = 'https://api-public.sandbox.gdax.com'
with open(API_FILE) as f:
    lines = [line.rstrip('\n') for line in open(API_FILE)]


auth_client = gdax.AuthenticatedClient(lines[1],lines[2],lines[0],api_url=AUTH_CLIENT)
public_client = PUBLIC_CLIENT


eth_acc_id_file  = open('../eth_acct_id.txt','r')
ETH_ACCT_ID = eth_acc_id_file.readline()
btc_acc_id_file  = open('../btc_acct_id.txt','r')
BTC_ACCT_ID = btc_acc_id_file.readline()

hist_data_cols = {'time': 0, 'low': 1, 'high': 2, 'open': 3, 'close': 4, 'volume': 5}
tick_data_cols = {'time': 0, 'vwap': 1, 'num_trades': 2, 'id': 3}

PRODUCT = 'ETH-USD'

pos_man = PositionManager(public_client=public_client, auth_client=auth_client, product=PRODUCT, product_acct_id=ETH_ACCT_ID)
all_orders = auth_client.get_orders()[0]

#Get time of last order
timestamps = []
for order in all_orders:
    timestamp = datetime.datetime.strptime(str(order['created_at']),'%Y-%m-%dT%H:%M:%S.%fZ')
    order['created_at'] = timestamp
    timestamps.append(timestamp)
latest_time = max(timestamps)
print(latest_time)

#Cancel all orders except the latest one
for order in all_orders:
    if order['created_at'] < latest_time:
        order_id = str(order['id'])
        auth_client.cancel_order(order_id=order_id)


