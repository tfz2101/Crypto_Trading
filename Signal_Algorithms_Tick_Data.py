import gdax
import inspect
import numpy as np
import pandas as pd
import datetime
import time
from scipy.stats import kurtosis, skew, linregress
from Execution_Algorithms import *
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import sys
sys.path.append('../')
from ML_Trading import ML_functions as mlfcn
from ML_Trading import Signals_Testing as st
from GDAX_Data_Fncs import getHistoricalDataFast,getHistoricalData
from pytz import timezone


def rolling_data_fcn_lookfwd(data,fcn,gap=5,*args,**kwargs):
    #@FORMAT: data = np.array
    out = np.empty([data.shape[0],])
    out[:] = np.nan
    out = out.tolist()
    for i in range(0,data.shape[0]-(gap-1),1):

        block_values = data[i:i+gap]
        stat = fcn(block_values,**kwargs)
        out[i]=stat
    return out

def rolling_data_fcn_lookback(data,fcn,gap=5,*args,**kwargs):
    #@FORMAT: data = np.array
    out = np.empty((data.shape[0],))
    out[:] = np.nan
    out = out.tolist()
    for i in range(gap,data.shape[0],1):

        block_values = data[(i-gap):(i+1)]
        stat = fcn(block_values,**kwargs)
        out[i]=stat

    return out



#Make signals from GDAX dataset of 300 points
def makeSignalDF(data):
    #@FORMAT: data = list()
    pass

def getMA(data, index, rowIndex, lookback):
    #@FORMAT: data = np(), assumes earliest to latest order
    slice = data[(rowIndex-lookback):rowIndex, index]
    return np.average(slice)

def getThreeAgreeSignal(min_1_z, min_5_z, min_15_z, block_zscore):
    print('signs', np.sign([block_zscore, min_1_z, min_5_z]))
    if abs(np.sum(np.sign([block_zscore, min_1_z, min_5_z]))) == 3:
        return np.sign(min_15_z)
    else:
        return 0






#LIVE TRADING SIGNAL------------------------------------------------------------------------------------------------------------------------

public_client = gdax.PublicClient()

gdax_zone = 'Atlantic/Azores'
END = datetime.datetime.now(timezone(gdax_zone))

delta  = 300 * 300
lookback = datetime.timedelta(seconds=delta)

secs = END.second
print('secs', secs)
microsecs = END.microsecond
print('micro', microsecs)

cutoff_delta = datetime.timedelta(seconds=secs, microseconds=microsecs)
CURTAILED_END = END - cutoff_delta
print('curtailed start', CURTAILED_END)

cols = {'time': 0, 'low': 1, 'high': 2, 'open': 3, 'close': 4, 'volume': 5}

#1 min intervals
freq = 60 #in seconds
delta  = freq * 35
lookback = datetime.timedelta(seconds=delta)
START = CURTAILED_END - lookback

print('START',START)

data = getHistoricalDataFast(public_client,start=START,end=CURTAILED_END,granularity=freq)
data = np.array(data)

ma_1m = getMA(data, cols['close'], data.shape[0], 30)
print('ma', ma_1m)


#5 min intervals
freq = 300 #in seconds
delta  = freq * 35
lookback = datetime.timedelta(seconds=delta)
START = CURTAILED_END - lookback

print('START',START)

data = getHistoricalDataFast(public_client,start=START,end=CURTAILED_END,granularity=freq)
data = np.array(data)

ma_5m = getMA(data, cols['close'], data.shape[0], 30)
print('ma', ma_5m)



#15 min intervals
freq = 900 #in seconds
delta  = freq * 35
lookback = datetime.timedelta(seconds=delta)
START = CURTAILED_END - lookback

print('START',START)

data = getHistoricalDataFast(public_client,start=START,end=CURTAILED_END,granularity=freq)
data = np.array(data)

ma_15m = getMA(data, cols['close'], data.shape[0], 30)
print('ma', ma_15m)





def getLiveSignal2(dataDF):
    raw_cur_data = dataDF.loc[:,['time', 'Y_10', 'close', 'KURTOSIS_30', 'SKEW', 'volume_zscore', 'volume_signal', 'signal','interval_range_pct_px', 'VWAP_Diff_Zscore']]
    endInd = raw_cur_data.shape[0] - 1

    skew = raw_cur_data.ix[endInd, 'SKEW']
    kurt = raw_cur_data.ix[endInd, 'KURTOSIS_30']
    volume_z = raw_cur_data.ix[endInd, 'volume_zscore']
    vwap_z = raw_cur_data.ix[endInd, 'VWAP_Diff_Zscore']

    factor_lst = [skew, kurt, volume_z, vwap_z]
    thresholds = [1, 1.25, 1, 1.25]
    print('factor_lst', factor_lst)
    sum = 0
    for i in range(0, len(factor_lst)):
        if abs(factor_lst[i]) > thresholds[i]:
            sum = sum + float(np.sign(factor_lst[i]))

    pred = min(sum, 2)
    return [raw_cur_data.ix[endInd, 'time'], raw_cur_data.ix[endInd, 'close'], pred]

#signal =  getLiveSignal2(dataDF)






