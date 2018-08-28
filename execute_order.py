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
from coinmarketcap import Market

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
GDAX_ZONE = 'Atlantic/Azores'

eth_acc_id_file  = open('../eth_acct_id.txt','r')
ETH_ACCT_ID = eth_acc_id_file.readline()
btc_acc_id_file  = open('../btc_acct_id.txt','r')
BTC_ACCT_ID = btc_acc_id_file.readline()


PRODUCT = "ETH-USD"
TARGET_PRICE = ""
SIZE = 2
SIDE = "BUY"
TIME_LIMIT_SEC = 60*1
START_TIME = datetime.datetime.now()
END_TIME = START_TIME + datetime.timedelta(seconds=TIME_LIMIT_SEC)

mkt_man = MarketManager(public_client=public_client, auth_client=auth_client, product=PRODUCT, side=SIDE, order_size=SIZE)
cur_order = mkt_man.makePassiveOrder(post_only=True)