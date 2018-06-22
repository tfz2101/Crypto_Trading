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

import sys
sys.path.append('C:\Users\Frank Zhi\PycharmProjects\ML_Trading')
#from Signals_Testing import rolling_data_fcn2


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


def getArgs(func):
    return inspect.getargspec(func).args

def convertDateToISO8601(date):
  return '{year}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}'.format(
      year=date.year,
      month=date.month,
      day=date.day,
      hour=date.hour,
      minute=date.minute,
      second=date.second)


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


public_client = gdax.PublicClient()

END = datetime.datetime.now()
delta  = 300 * 300
lookback = datetime.timedelta(seconds=delta)
START = END - lookback

#@TODO: FIX DATE TIME CONVERSION - IT'S NOT FEEDING BACK TO THE HISTORICAL DATA CORRECTLY!!!!!

dataDF = getHistoricalData(public_client,symbol='BTC-USD',start=START,end='NOTHING',granularity=60)
orig_hist_data = dataDF

#Make signals from GDAX dataset of 300 points
def makeSignalDF(dataDF):
    columns =  dataDF.columns.values.tolist()
    data  = dataDF.values

    colDict ={}
    count = 0
    for column in columns:
        colDict[column] = count
        count += 1


    def getRangePctOfPx(block_data, colDict):
        HIGH = block_data[0,colDict['high']]
        LOW = block_data[0,colDict['low']]
        out = (HIGH-LOW)/((HIGH+LOW)/2)
        return out

    rangekwargs = {'colDict':colDict}
    rangepct = rolling_data_fcn_lookfwd(data,getRangePctOfPx,gap=1,**rangekwargs)
    dataDF['interval_range_pct_px'] = np.array(rangepct)

    def getKurtosis(block_data, colDict):
        closes = block_data[:,colDict['close']]

        kurt = kurtosis(closes,fisher=True)
        return kurt

    kurt = rolling_data_fcn_lookback(data,getKurtosis,gap= 59,**rangekwargs)
    kurt = pd.Series(kurt,name='KURTOSIS_30')
    dataDF = pd.concat([dataDF,kurt],axis=1)

    def getSkew(block_data, colDict):
        closes = block_data[:,colDict['close']]
        sq = skew(closes)
        return sq

    sq = rolling_data_fcn_lookback(data,getSkew,gap=59,**rangekwargs)

    sq = pd.Series(sq,name='SKEW')
    dataDF = pd.concat([dataDF,sq],axis=1)



    def getY_10(block_data, colDict):
        closes = block_data[:,colDict['close']]
        ret = (closes[10]- closes[0])/closes[0]
        return ret

    ret =  rolling_data_fcn_lookfwd(data,getY_10,gap=11,**rangekwargs)
    dataDF['Y_10']=ret

    def getRegressionSignal(block_data, colName, colDict):
        closes = block_data[:,colDict[colName]]

        Y = closes[0:(closes.shape[0]-1)]
        X = np.array(range(0,closes.shape[0]-1))
        m,a,r,p,std = linregress(X,Y)

        past_preds = []
        for i in range(0,Y.shape[0]):
            past_pred = X[i] * 1.0 * m + a
            past_preds.append(past_pred)
        RMSE = np.sqrt(((past_preds - Y) ** 2).sum()/1.0/(len(past_preds)-2))

        x = closes.shape[0]-1
        y = closes[closes.shape[0]-1]
        pred = x * 1.0 * m + a

        z = (y - pred)/RMSE
        return z


    maregkwargs = {'colDict':colDict,'colName':'close'}
    ma_reg_signal = rolling_data_fcn_lookback(data,getRegressionSignal,gap= 32,**maregkwargs)
    dataDF['signal'] = ma_reg_signal


    volumeregkwargs = {'colDict':colDict,'colName':'volume'}
    volume_reg_signal = rolling_data_fcn_lookback(data,getRegressionSignal,gap= 28,**volumeregkwargs)
    dataDF['volume_zscore'] = volume_reg_signal


    def getVWAP_Diff(block_data, colDict):
        closes = block_data[:,colDict['close']]
        volumes = block_data[:,colDict['volume']]
        closes_1 = closes[0:(closes.shape[0]-1)]
        volumes_1 = volumes[0:(volumes.shape[0]-1)]
        VWAP = (closes_1 * volumes_1).sum()/volumes_1.sum()
        diff = closes[closes.shape[0]-1] - VWAP
        return diff

    #vwap = getVWAP_Diff(data,colDict)
    vwap_diff = rolling_data_fcn_lookback(data,getVWAP_Diff,gap= 28,**rangekwargs)
    dataDF['vwap_diff'] =  vwap_diff

    vwap_diff_zscore_kwargs = {'vwap_diff_ind':12}
    def getVWAP_Diff_Zscore(block_data, vwap_diff_ind):
        vwap_diffs = block_data[:, vwap_diff_ind]
        lookback =  vwap_diffs[0:vwap_diffs.shape[0]-1]
        x =  vwap_diffs[vwap_diffs.shape[0]-1]
        try:
            out = x/lookback.std()
        except:
            out = np.nan
        return out

    vwap_diff_zscore = rolling_data_fcn_lookback(dataDF.values,getVWAP_Diff_Zscore,gap= 32,**vwap_diff_zscore_kwargs)
    dataDF['VWAP_Diff_Zscore'] = vwap_diff_zscore

    def getVolumeMASignal(block_data,colDict):
        volumes = block_data[:, colDict['volume']]
        lookback  = volumes[0:volumes.shape[0]-1]
        x =  volumes[volumes.shape[0]-1]
        return (x-lookback.mean())/lookback.std()

    volume_ma_signal = rolling_data_fcn_lookback(data,getVolumeMASignal,gap= 28,**rangekwargs)
    dataDF['volume_signal']=volume_ma_signal

    return dataDF

dataDF = makeSignalDF(dataDF)

#TRADE TESTING -------------------------------------------------------------------------------------------------------------------------
data = dataDF

cur_data = data.loc[:,['Y_10','close', 'KURTOSIS_30', 'SKEW', 'volume_zscore', 'volume_signal', 'signal', 'interval_range_pct_px','VWAP_Diff_Zscore']]
orig_data = cur_data
cur_data = cur_data.dropna()

X = cur_data.drop(['Y_10','close'], axis=1)
Y = cur_data['Y_10']
px_col = cur_data['close']

X_norm = mlfcn.normalizeDF(X)
cur_data = pd.concat([Y, X_norm, px_col], axis=1)

ml_out = mlfcn.getBlendedSignalKeepColumns(cur_data,'close', RandomForestRegressor, gap=35)
ml_out = pd.DataFrame(ml_out)

#st.write(dataDF,'signals_algorithms2.xlsx','sheet1')
#st.write(ml_out,'signals_algorithms2_ml_data.xlsx','sheet1')


#LIVE TRADING SIGNAL------------------------------------------------------------------------------------------------------------------------
#Generate a live trading signal from the results of makeSignalDF()
def getLiveSignal(dataDF):
    raw_cur_data = dataDF.loc[:,['time','Y_7','close','KURTOSIS_30', 'SKEW', 'volume_zscore', 'volume_signal', 'signal', 'interval_range_pct_px','VWAP_Diff_Zscore']]
    X_test = raw_cur_data.drop(['time','Y_7','close'],axis=1).values
    X_test = X_test[X_test.shape[0]-1]
    X_test = X_test.reshape(1, -1)

    cur_data = raw_cur_data.dropna()
    X = cur_data.drop(['Y_7','time','close'],axis=1)
    Y = cur_data['Y_7']

    #NOTE THE NORMALIZATION MIGHT BE THROWN OFF BY THE FACT THAT YOU'RE USING A SHORTER DATASET!!!!!!
    X_norm = mlfcn.normalizeDF(X)
    cur_data = pd.concat([Y,X_norm],axis=1)

    #GET UPDATED SIGNAL
    gap = 230
    ml_model = RandomForestRegressor

    data = cur_data
    Y = data.iloc[:, 0].values
    X = data.drop(data.columns[[0]], axis=1).values
    endInd = X.shape[0]

    X_ = X[(endInd - gap):endInd]
    Y_ = Y[(endInd - gap):endInd]

    model = ml_model(n_estimators=20,random_state=0)
    model.fit(X_, Y_)

    pred = model.predict(X_test)
    return [raw_cur_data.ix[raw_cur_data.shape[0]-1,'time'],raw_cur_data.ix[raw_cur_data.shape[0]-1,'close'],pred[0]]



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

