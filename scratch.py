import numpy as np
import pandas as pd
import sys
sys.path.append('../')
from ML_Trading import ML_functions as mlfcn

import scipy as sp
import matplotlib.pyplot as plt
import pandas as pd
pd.set_option('display.width', 500)
pd.set_option('display.max_columns', 100)
import seaborn as sns
import statsmodels.api as sm
import statsmodels.graphics.tsaplots as tsaplots
from IPython.display import Image


N=1000
#sigma=1
ts=np.random.randn(1000)
tsaplots.plot_acf(ts, lags=10);




def getFixedVolumeData(orig_data, size):
    #@FORMAT: orig_data = df(price, volume, index=dates)
    out = []
    data =  orig_data.copy()
    curBlock ={'time': [], 'sizeLeft': size, 'prices': [], 'sizes': []}

    for i in range(0,data.shape[0]):

        while data.iloc[i,1] > 0:
            if curBlock['sizeLeft'] < data.iloc[i,1]:
                data.iloc[i,1] = data.iloc[i,1] - curBlock['sizeLeft']
                curBlock['sizes'].append(curBlock['sizeLeft'])
                curBlock['prices'].append(data.iloc[i,0])
                curBlock['time'].append(data.index.values[i])

                end_time = curBlock['time'][-1]
                vwap = sum([i * j for i, j in zip(curBlock['prices'], curBlock['sizes'])])
                num_trades = len(curBlock['prices'])
                out.append([end_time, vwap, num_trades])
                curBlock = {'time': [], 'sizeLeft': size, 'prices': [], 'sizes': []}

            elif curBlock['sizeLeft'] >= data.iloc[i,1]:
                curBlock['sizes'].append(data.iloc[i,1])
                curBlock['prices'].append(data.iloc[i,0])
                curBlock['time'].append(data.index.values[i])
                data.iloc[i,1] = 0

    #RETURN: [end_time, VWAP, num_trades]
    return out

