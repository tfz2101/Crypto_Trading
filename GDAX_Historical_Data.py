import gdax
import numpy as np
import pandas as pd
import datetime
import time
from Execution_Algorithms import *
from GDAX_Data_Fncs import getHistoricalDataFast
import sys
sys.path.append('../')
from ML_Trading import ML_functions as mlfcn
from ML_Trading import Signals_Testing as st
#from Signal_Algorithms_Tick_Data import getMA
from GDAX_Data_Fncs import getHistoricalData, getHistoricalDataFast
from pytz import timezone
import pickle


def getTimeIndex(data, start, timedelta):
    #@FORMAT: data = list
    print('test',start.strftime("%Y-%m-%d %H:%M:%S"))

    data[0][0] = start.strftime("%Y-%m-%d %H:%M:%S")
    time_counter = start
    for i in range(1, len(data)):
        time_counter = time_counter + timedelta
        print('data', data_1min)
        time_string = time_counter.strftime("%Y-%m-%d %H:%M:%S")
        data[i][0] = time_string

    return data



public_client = gdax.PublicClient(api_url='https://api.pro.coinbase.com')

gdax_zone = 'Atlantic/Azores'
END = datetime.datetime.now(timezone(gdax_zone))
FAST_MA_LOOKBACK = 2
SLOW_MA_LOOKBACK = 3
cols = {'time': 0, 'low': 1, 'high': 2, 'open': 3, 'close': 4, 'volume': 5}

#1 min intervals
freq = 60 #in seconds
delta  = freq * 35
lookback = datetime.timedelta(seconds=delta)
START = END - lookback

print('START',START)
print('END', END)

data_1min = getHistoricalDataFast(public_client,start=START,end=END,granularity=freq)
data_1min = getTimeIndex(data_1min, START, datetime.timedelta(seconds=freq))
data_1min = np.array(data_1min)
print('data', data_1min)

slow_data = data_1min[(data_1min.shape[0] - SLOW_MA_LOOKBACK):data_1min.shape[0], cols['close']].astype(float)
print('slowdata', slow_data)

slow_ma = np.mean(slow_data)
ma_std = np.std(slow_data)
print('slow ma', slow_ma)

fast_data = data_1min[(data_1min.shape[0] - FAST_MA_LOOKBACK):data_1min.shape[0], cols['close']].astype(float)
fast_ma = np.mean(fast_data)
min1_zscore = (fast_ma - slow_ma)/ma_std

pickling = open('zscore_1min.pickle','wb')
pickle.dump(min1_zscore, pickling)
pickling.close()



#5 min intervals
freq = 300 #in seconds
delta  = freq * 35
lookback = datetime.timedelta(seconds=delta)
START = END - lookback

print('START',START)
print('END', END)

data_5min = getHistoricalDataFast(public_client,start=START,end=END,granularity=freq)
data_5min = getTimeIndex(data_5min, START, datetime.timedelta(seconds=freq))
data_5min = np.array(data_5min)
print('data', data_5min)

slow_data = data_5min[(data_5min.shape[0] - SLOW_MA_LOOKBACK):data_5min.shape[0], cols['close']].astype(float)
slow_ma = np.average(slow_data)
ma_std = np.std(slow_data)
print('slow ma', slow_ma)

fast_data = data_5min[(data_5min.shape[0] - FAST_MA_LOOKBACK):data_5min.shape[0], cols['close']].astype(float)
fast_ma = np.average(fast_data)
min5_zscore = (fast_ma - slow_ma)/ma_std



pickling = open('zscore_5min.pickle','wb')
pickle.dump(min5_zscore, pickling)
pickling.close()



#15 min intervals
freq = 900 #in seconds
delta  = freq * 35
lookback = datetime.timedelta(seconds=delta)
START = END - lookback

print('START',START)
print('END', END)

data_15min = getHistoricalDataFast(public_client,start=START,end=END,granularity=freq)
data_15min = getTimeIndex(data_15min, START, datetime.timedelta(seconds=freq))
data_15min = np.array(data_15min)
print('data', data_15min)


slow_data = data_15min[(data_15min.shape[0] - SLOW_MA_LOOKBACK):data_15min.shape[0], cols['close']].astype(float)
slow_ma = np.average(slow_data)
ma_std = np.std(slow_data)
print('slow ma', slow_ma)

fast_data = data_15min[(data_15min.shape[0] - FAST_MA_LOOKBACK):data_15min.shape[0], cols['close']].astype(float)
fast_ma = np.average(fast_data)
min5_zscore = (fast_ma - slow_ma)/ma_std


pickling = open('zsore_15min.pickle','wb')
pickle.dump(data_15min, pickling)
pickling.close()
