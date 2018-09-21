import gdax
import inspect
import numpy as np
import pandas as pd
import datetime
import time
from Execution_Algorithms import *
from Signal_Algorithms import *
from pytz import timezone
import sys
import pickle

sys.path.append('../')
from ML_Trading import ML_functions as mlfcn
from ML_Trading import Signals_Testing as st


logfile = open("logfile.txt", "a+")
logfile.truncate()
public_client = gdax.PublicClient()

MODE = 'REAL'

if MODE == 'REAL':
    API_FILE = '../gdax_real.txt'
    PUBLIC_CLIENT = gdax.PublicClient()
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


BUY_SIZE = 0.001
PRODUCT = 'ETH-USD'
MAX_POSITION = 0.003
EXIT_NOW = False
GDAX_ZONE = 'Atlantic/Azores'



start_time =  datetime.datetime.now()
run_time_sec = 60 * 60 * 9
end_time = start_time + datetime.timedelta(seconds=run_time_sec)


#Read Updated Tick Block Data
pickle_in = open('test.tick_block_history.pickle', 'rb')
data = pickle.load(pickle_in)
print('data', data)

#Recalcs Signals with updated Tick Block Data


#Execute or Not Execute



#Every 10 seconds, pull in refreshed Historical Data





#Empty order manager
pos_man = PositionManager(public_client=public_client, auth_client=auth_client, product=PRODUCT, product_acct_id=ETH_ACCT_ID)


while datetime.datetime.now() < end_time:
    if pos_man.getCurrentPositionFromAcct() <= 0.0:
        #GENERATE SIGNAL--------------------------------------------------------------------------------------------------------------------------
        time.sleep(60)

        END = datetime.datetime.now(timezone(GDAX_ZONE))
        delta  = 300 * 60
        lookback = datetime.timedelta(seconds=delta)
        START = END -lookback

        print('END',END)

        try:
            dataDF = getHistoricalData(public_client,symbol=PRODUCT,start=START,end=END,granularity=60)
        except:
            print('getHistoricalData Retreival Faulty')
            continue

        orig_hist_data = dataDF

        dataDF = makeSignalDF(dataDF)
        signalList = getLiveSignal2(dataDF)

        print('signal output',signalList)
        target_price = signalList[1]
        signal = signalList[2]

    side = ''
    size = 0
    isTriggered = False
    SELL_TRIGGER_THRESHOLD = np.nan
    BUY_TRIGGER_THRESHOLD = 1
    if pos_man.getCurrentPositionFromAcct() <= 0:
        if signal >= BUY_TRIGGER_THRESHOLD:
            isTriggered = True
            side = 'BUY'
            signal_run = 60*10
            size = BUY_SIZE
            signal_man = SignalManager(public_client=public_client,auth_client=auth_client,product=PRODUCT,entry_time=datetime.datetime.now(),signal_run_sec=signal_run)
            print('TRIGGERED!!!!!!',signalList)
            logfile.write('TRIGGERED!!!!!! ' + str(signal) + ' '+  str(target_price) + '\n')
            logfile.write('date of trigger: ' + str(datetime.datetime.now(timezone(GDAX_ZONE))) + '\n')




    #---------------------------------------------------------------------------------------------------------
    #EXECUTION

    if isTriggered:
        TARGET_PRICE = target_price
        SIZE = size
        SIZE_MAX = 0.003
        SIDE = side
        TIME_LIMIT_SEC = 60*1
        START_TIME = datetime.datetime.now()
        END_TIME = START_TIME + datetime.timedelta(seconds=TIME_LIMIT_SEC)

        mkt_man = MarketManager(public_client=public_client, auth_client=auth_client, product=PRODUCT, side=SIDE, order_size=SIZE)

        cur_order = mkt_man.makePassiveOrder(post_only=True)
        print('signal trade initiated!',cur_order)

        order_id =  cur_order['id']
        order_man= OrderManager(public_client=public_client, auth_client=auth_client, product=PRODUCT, side=SIDE, order_size=SIZE,order_id=order_id)

        while datetime.datetime.now()<END_TIME:
            # FAILSAFE
            if order_man.order_size > SIZE_MAX:
                order_man.cancelOrder()
                sys.exit()

            cur_pos = pos_man.getCurrentPositionFromAcct()
            print('current position', cur_pos)
            #logfile.write('current position: ' + str(cur_pos) + '\n')
            if pos_man.isTargetPositionReached(size=SIZE, side=SIDE):
                print('POSITION ALREADY MET, BREAK OUT OF THE LOOP')
                #logfile.write('POSITION ALREADY MET, BREAK OUT OF THE LOOP, PRICE WAS' +  '\n')
                break

            if order_man.getOrderStatus()=='done':
                print('ORDER WAS DONE!')
                #logfile.write('ORDER WAS DONE!' + '\n')

                cur_pos = pos_man.getCurrentPositionFromAcct()
                print('order done, get current position', cur_pos)
                #logfile.write('order done, get current position: '+ str(cur_pos) + '\n')
                break



'''
#If execution time runs out, cancel lingering orders
old_order = order_man.cancelOrder()
print('execution timed out, order cancelled', old_order)
if old_order == 'DONE':
    logfile.write('This was the executed price: ' + str(order_man.getExecutedPrice()) + '/n')
    logfile.write('EXECUTION TIME: ' + str(datetime.datetime.now(timezone(GDAX_ZONE))) + '/n')
#logfile.write('execution timed out, order cancelled ' + str(old_order) + '\n')

#Reset Signal as to not Trigger Execution
signal = 0
'''







