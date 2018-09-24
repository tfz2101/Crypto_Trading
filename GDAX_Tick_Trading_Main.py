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

BUY_SIZE = 0.001
PRODUCT = 'ETH-USD'
MAX_POSITION = 0.003
EXIT_NOW = False
GDAX_ZONE = 'Atlantic/Azores'



start_time =  datetime.datetime.now()
run_time_sec = 60 * 60 * 9
end_time = start_time + datetime.timedelta(seconds=run_time_sec)
hist_read_time = start_time
HIST_READ_INTERVAL = datetime.timedelta(seconds=5)

#Empty order manager
pos_man = PositionManager(public_client=public_client, auth_client=auth_client, product=PRODUCT, product_acct_id=ETH_ACCT_ID)
SIZE = 0.1
SIZE_MAX = 0.003

last_used_block_id = -1000

#Main Loop
#while datetime.datetime.now() < end_time:
isExecute = False
isNewBar = False


#Read Updated Historical Data
if datetime.datetime.now() >= hist_read_time:
    #read historical data pickle
    pickle_1min = open('zscore_1min.pickle')
    min_1_z = pickle.load(pickle_1min)
    pickle_5min = open('zscore_5min.pickle')
    min_5_z = pickle.load(pickle_5min)
    pickle_15min = open('zscore_15min.pickle')
    min_15_z = pickle.load(pickle_15min)
    hist_read_time =  hist_read_time + HIST_READ_INTERVAL

#Read Updated Tick Block Data
pickle_in = open('tick_block_history.pickle', 'rb')
tick_bars = pickle.load(pickle_in)
    #tick bar format: list[[time, vwap, num_trades]]
tick_bars = np.array(tick_bars)

    #Check if there has been an updated block
if tick_bars[tick_bars.shape[0]-1,tick_data_cols['id']] > last_used_block_id:
    isNewBar = True

    #Record last used block
last_used_block_id = tick_bars[tick_bars.shape[0]-1,tick_data_cols['id']]
pickle_last_block = open('last_used_block_id.pickle')
pickle.dump(pickle_last_block, last_used_block_id)
pickle_last_block.close()


print('data', tick_bars)



#Recalcs Signals with updated Tick Block Data
LOOKBACK = 60

price_bars_lookback = tick_bars[(tick_bars.shape[0] - LOOKBACK):tick_bars.shape[0], tick_data_cols['vwap']].astype('float')
num_trades_lookback = tick_bars[(tick_bars.shape[0] - LOOKBACK):tick_bars.shape[0], tick_data_cols['num_trades']].astype('float')
vwap = np.dot(price_bars_lookback, num_trades_lookback) / np.sum(num_trades_lookback)
price_bars_std = np.std(price_bars_lookback)
tick_zscore = (tick_data_cols[tick_bars.shape[0] - 1, tick_data_cols['vwap']] - vwap) / price_bars_std

trade_rec = getThreeAgreeSignal(min_1_z, min_5_z, min_15_z, tick_zscore)
if abs(trade_rec) > 0:
    isExecute = True

#Execute or Not Execute
if isExecute and isNewBar:
    size = SIZE
    if trade_rec > 0:
        side = 'BUY'
    if trade_rec < 0:
        side = 'SELL'

    mkt_man = MarketManager(public_client=public_client, auth_client=auth_client, product=PRODUCT, side=side, order_size=size)

    cur_order = mkt_man.makePassiveOrder(post_only=True)
    print('signal trade initiated!',cur_order)

    order_id =  cur_order['id']
    order_man= OrderManager(public_client=public_client, auth_client=auth_client, product=PRODUCT, side=side, order_size=size,order_id=order_id)

    #logfile.write('current position: ' + str(cur_pos) + '\n')





