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
import cPickle

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
MAX_POSITION = 0.1

PROP_POSITION = 171.06504777   #@TODO: THIS WILL CHANGE!!!

GDAX_ZONE = 'Atlantic/Azores'
SIZE = 0.1


start_time =  datetime.datetime.now()
run_time_sec = 60 * 60 * 9
end_time = start_time + datetime.timedelta(seconds=run_time_sec)
hist_read_time = start_time
HIST_READ_INTERVAL = datetime.timedelta(seconds=5)

#Empty order manager
pos_man = PositionManager(public_client=public_client, auth_client=auth_client, product=PRODUCT, product_acct_id=ETH_ACCT_ID)

#Empty order manager, is string initially
order_man = 'EMPTY'
last_used_block_id = -1000
MIN_TICK_BARS = 60

#@TODO: CHECK FOR OUTDATED FEEDS FOR BOTH TICK AND HISTORICAL DATA
#@TODO: CANCEL LAST ORDER BEFORE EXECUTING LATEST ONE
#starting capital = 184.01


'''
cur_order = auth_client.buy(price=211,
                             size=0.1,
                             product_id=PRODUCT,
                             post_only=True)

order_id = cur_order['id']

cancel_order_id = auth_client.cancel_order(order_id=order_id)
print('cancel order id', cancel_order_id)
'''


#MAIN LOOP
while datetime.datetime.now() < end_time:
    isExecute = False

    #READ HISTORICAL DATA
    if datetime.datetime.now() >= hist_read_time:
        print('READING HISTORICAL DATA')
        pickle_1min = open('zscore_1min.pickle', 'rb')
        try:
            min_1_z = cPickle.load(pickle_1min)
            pickle_1min.close()
        except EOFError:
            min_1_z = cPickle.load(pickle_1min)
            pickle_1min.close()
        print('zscores 1min', min_1_z)
        pickle_5min = open('zscore_5min.pickle', 'rb')
        try:
            min_5_z = cPickle.load(pickle_5min)
            pickle_5min.close()
        except EOFError:
            min_5_z = cPickle.load(pickle_5min)
            pickle_5min.close()
        print('zscores 5min', min_5_z)
        pickle_15min = open('zscore_15min.pickle', 'rb')
        try:
            min_15_z = cPickle.load(pickle_15min)
            pickle_15min.close()
        except EOFError:
            min_15_z = cPickle.load(pickle_15min)
            pickle_15min.close()
        print('zscores 15min', min_15_z)

        hist_read_time =  hist_read_time + HIST_READ_INTERVAL

    #READ TICK BLOCKS DATA

    try:
        pickle_in = open('tick_block_history.pickle', 'rb')
        tick_bars = cPickle.load(pickle_in)
        pickle_in.close()
    except EOFError:
        pickle_in = open('tick_block_history.pickle', 'rb')
        tick_bars = cPickle.load(pickle_in)
        pickle_in.close()

        #tick bar format: list[[time, vwap, num_trades]]
    tick_bars = np.array(tick_bars)


        #Check to see if there are at least 60 blocks in the tick data
    if tick_bars.shape[0] < MIN_TICK_BARS:
        print('NOT ENOUGH TICK BARS')
        continue

        #Check if there has been an updated block
    if tick_bars[tick_bars.shape[0]-1,tick_data_cols['id']] <= last_used_block_id:
        print('NO NEW BLOCKS')
        continue

        #Record last used block
    last_used_block_id = tick_bars[tick_bars.shape[0]-1,tick_data_cols['id']]
    pickle_last_block = open('last_used_block_id.pickle', 'wb')
    cPickle.dump(last_used_block_id, pickle_last_block)
    pickle_last_block.close()

    

    #Recalcs Signals with updated Tick Block Data - Only do it if new blocks are present
    LOOKBACK = 60

    price_bars_lookback = tick_bars[(tick_bars.shape[0] - LOOKBACK):tick_bars.shape[0], tick_data_cols['vwap']].astype('float')
    #print('price bars for ticks', price_bars_lookback)
    num_trades_lookback = tick_bars[(tick_bars.shape[0] - LOOKBACK):tick_bars.shape[0], tick_data_cols['num_trades']].astype('float')
    #print('num trades', num_trades_lookback)
    vwap = np.dot(price_bars_lookback, num_trades_lookback) / np.sum(num_trades_lookback)
    print('vwap', vwap)
    price_bars_std = np.std(price_bars_lookback)
    last_tick_px = tick_bars[tick_bars.shape[0] - 1, tick_data_cols['vwap']]
    tick_zscore = (last_tick_px - vwap) / price_bars_std
    print('tick zsscore', tick_zscore)
    trade_rec = getThreeAgreeSignal(min_1_z, min_5_z, min_15_z, tick_zscore)
    print('trade rec', trade_rec)
    if abs(trade_rec) > 0:
        isExecute = True

    side = 'BUY'
    #Execute or Not Execute
    if isExecute:
        print('EXECUTE NOW!!')

        #First, cancel the old order
        try:
            cancel_order_id = order_man.cancelOrder()
        except:
            print('Cant cancel order')
        # Are we over MAX_POSITION?
        current_position = pos_man.getCurrentPositionFromAcct() - PROP_POSITION
        print('current position', current_position)

        if trade_rec > 0.0 and current_position >= MAX_POSITION:
                print('WE ARE ALREADY MAXED OUT')
                continue
        if trade_rec < 0.0 and current_position <= 0.0:
                print('WE DONT HAVE ANY TO SELL')
                continue

        size = SIZE

        if trade_rec > 0:
            side = 'BUY'
        if trade_rec < 0:
            side = 'SELL'

        mkt_man = MarketManager(public_client=public_client, auth_client=auth_client, product=PRODUCT, side=side, order_size=size)
    
        cur_order = mkt_man.makeLimitOrder(limit_px=round(vwap, ndigits=2))
        print('signal trade initiated!',cur_order)

            #Record the order id of the current order
        order_id =  cur_order['id']
        order_man = OrderManager(public_client=public_client, auth_client=auth_client, product=PRODUCT, side=side, order_size=size,order_id=order_id)
    
        #logfile.write('current position: ' + str(cur_pos) + '\n')
        #When isExecute:
                #log
                    #time




