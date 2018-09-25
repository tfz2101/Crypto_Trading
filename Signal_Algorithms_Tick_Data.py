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




