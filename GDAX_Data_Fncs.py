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
from pytz import timezone




def getHistoricalData(public_client,symbol='ETH-USD',start='2018-01-23T16:25:00.00000Z',end='NOTHING',granularity=60):
    if end == 'NOTHING':
        hist_data = public_client.get_product_historic_rates(symbol,start=start,granularity=granularity)
    else:
        hist_data = public_client.get_product_historic_rates(symbol, start=start, end=end,granularity=granularity)
    hist_data = pd.DataFrame(hist_data, columns=['time','low','high','open','close','volume'])

    hist_data = hist_data.sort_values(['time'], ascending=True)
    hist_data = hist_data.reset_index(drop=True)

    #RETURNS historical data dataframe, sorted where the latest datapoint is in the last row
    return hist_data

#Faster version of original function that uses no dataframes
def getHistoricalDataFast(public_client,symbol='ETH-USD',start='2018-01-23T16:25:00.00000Z',end='NOTHING',granularity=60):
    if end == 'NOTHING':
        hist_data = public_client.get_product_historic_rates(symbol,start=start,granularity=granularity)
    else:
        hist_data = public_client.get_product_historic_rates(symbol, start=start, end=end,granularity=granularity)

    #cols = {'time': 0, 'low': 1, 'high': 2, 'open': 3, 'close': 4, 'volume': 5}
    hist_data = sorted(hist_data, key=lambda row: row[0])  # sort by age

    #RETURNS historical data dataframe, sorted where the latest datapoint is in the last row
    return hist_data




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


