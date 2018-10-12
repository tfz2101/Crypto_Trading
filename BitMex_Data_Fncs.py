import numpy as np
import pandas as pd
import datetime
import time
import sys
sys.path.append('../')
from ML_Trading import ML_functions as mlfcn
from ML_Trading import Signals_Testing as st
from pytz import timezone
import requests
import bitmex
import json

#Convert unicode time index to datetime index and gets rid of the 000Z suffix from API data
def getTimeIndex(data):
    timeindex =  data.index.values
    for i in range(0, timeindex.shape[0]):
        #timeindex[i] = datetime.datetime.strptime(str(timeindex[i]), '%Y-%m-%dT%H:%M:%S.000000000')
        #timeindex[i] = pd.to_datetime(timeindex[i]).replace(tzinfo=None)
        timeindex[i] = str(timeindex[i])
        #print('time index', timeindex[i])
    data = data.set_index(timeindex)
    return data


'''
API_FILE = '../bitmex.txt'
with open(API_FILE) as f:
    lines = [line.rstrip('\n') for line in open(API_FILE)]
print(lines)
client = bitmex.bitmex(test=False, api_key=lines[0], api_secret=lines[1])
'''

client = bitmex.bitmex()

start_date = datetime.datetime(2018, 1, 1, 7, 59, 0)
bars = 500
bar_unit = 8
delta = datetime.timedelta(hours=bars*bar_unit)
end_date = start_date + delta
print('end date', end_date)

#out = client.Trade.Trade_getBucketed(binSize='5m', symbol='ETHUSD', count=bars, reverse=False, startTime = start_date, endTime = end_date).result()[0]
out = client.Funding.Funding_get(symbol='XBTUSD',  count=bars, reverse=False, startTime = start_date, endTime = end_date).result()[0]
out = pd.DataFrame(out)
out = out.set_index(keys=['timestamp'])
print('out', out)

out = getTimeIndex(out)
st.write_new(out, 'bitmex_ethusd_funding_rates.xlsx','sheet1')






