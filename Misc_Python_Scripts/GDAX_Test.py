import gdax
import inspect
import numpy as np
import pandas as pd
import datetime
import time
from Execution_Algorithms import *
from Signal_Algorithms import *

import sys
sys.path.append('../')
from ML_Trading import ML_functions as mlfcn
from ML_Trading import Signals_Testing as st


public_client = gdax.PublicClient()

#WRITE A LONG HISTORY FOR BACKTESTING
'''
END = datetime.datetime.now()

#@REMINDER - GDAX can only return up to 300 requests

delta = 300 * 200
lookback = datetime.timedelta(seconds=delta)

START_dt =  END - lookback

START = convertDateToISO8601(START_dt)
END = convertDateToISO8601(END)

data = getHistoricalData(public_client,start=START,end=END,granularity=300)

START_DT = datetime.datetime(2017,7,1,0,0,0,0)

dfs = []
for i in range(0,20):
    END_DT = START_DT + lookback
    START = convertDateToISO8601(START_DT)
    END = convertDateToISO8601(END_DT)
    print(START, END)
    data = getHistoricalData(public_client, start=START, end=END, granularity=300)
    reverse_data = data.iloc[::-1]
    print(reverse_data)
    dfs.append(reverse_data)
    START_DT = END_DT
    time.sleep(2)

total_history = pd.concat(dfs, ignore_index=True)
print(total_history)
st.write(total_history,'gdax_history.xlsx','sheet1')
'''


MODE = 'REAL'

if MODE == 'REAL':
    #API_FILE = 'C:/Users/Frank Zhi/PycharmProjects/gdax_real.txt'
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
PRODUCT = 'BTC-USD'

print('accts',auth_client.get_accounts())
start_time =  datetime.datetime.now()
run_time = datetime.timedelta(seconds=360)
end_time = start_time + run_time

acct = auth_client.get_accounts()
btc_acct = auth_client.get_account(account_id='44036a36-a524-4a22-9258-28a88cd17b02')['balance']
print(btc_acct)


#Empty order manager
eth_pos_man = PositionManager(public_client=public_client, auth_client=auth_client, product=PRODUCT)
SIZE = 0.01
SIDE = 'BUY'
cur_order = auth_client.buy(type='market',
               size=SIZE, #BTC
               product_id='BTC-USD')
order_id = cur_order['id']
#print('cancel order',auth_client.cancel_order(order_id))
print('get info on filled order',auth_client.get_order(order_id))


'''
order_id = cur_order['id']
order_man = OrderManager(public_client=public_client, auth_client=auth_client, product=PRODUCT, side=SIDE, order_size=SIZE,order_id=order_id)
end_time = datetime.datetime.now()+datetime.timedelta(seconds=30)

while datetime.datetime.now() < end_time:
    order_status = auth_client.get_order(order_id)
    print('order status',order_status)
    print('old order manager fill amt',order_man.filled_amt)
    lastFillAmt = order_man.getLastFillAmt(update_filled_amt=True)
    print('lastFillAmt',lastFillAmt)
    print('new order manager fill amt',order_man.filled_amt)
    print('old position',eth_pos_man.getCurrentPosition())
    eth_pos_man.updateCurrentPosition(lastFillAmt, side=SIDE)
    print('new position',eth_pos_man.getCurrentPosition())
'''