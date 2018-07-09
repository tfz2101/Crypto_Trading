import numpy as np
import pandas as pd
import sys
sys.path.append('../')
from ML_Trading import ML_functions as mlfcn
from ML_Trading import Signals_Testing as st



#Takes fixed internal price and volume time series and transforms it into a fixed volume time series
def getFixedVolumeData(orig_data, size):
    #@FORMAT: orig_data = df(price, volume, index=dates)
    out = []
    data =  orig_data.copy()
    curBlock ={'time': [], 'sizeLeft': size, 'prices': [], 'sizes': []}

    def sumproduct(list1, list2):
        sum = 0
        for i in range(0, len(list1)):
            sum += list1[i] * list2[i]

        return sum

    for i in range(0,data.shape[0]):

        print('raw size', data.iloc[i,1])
        while data.iloc[i,1] > 0.0:
            print('size',data.iloc[i,1])
            if curBlock['sizeLeft'] < data.iloc[i,1]:
                data.iloc[i,1] = data.iloc[i,1] - curBlock['sizeLeft']
                print('size left', data.iloc[i, 1])
                curBlock['sizes'].append(curBlock['sizeLeft'])
                curBlock['prices'].append(data.iloc[i,0])
                curBlock['time'].append(data.index.values[i])
                print('size after record', data.iloc[i, 1])
                end_time = curBlock['time'][-1]
                try:
                   vwap = sumproduct(curBlock['prices'], curBlock['sizes'])
                   print('vwap', vwap)
                except:
                    print('curblock prices',curBlock['prices'])
                    print('curblock sizes',curBlock['sizes'])
                    vwap = 0
                num_trades = len(curBlock['prices'])
                out.append([end_time, vwap, num_trades])
                curBlock = {'time': [], 'sizeLeft': size, 'prices': [], 'sizes': []}

            elif curBlock['sizeLeft'] >= data.iloc[i,1]:
                curBlock['sizes'].append(data.iloc[i,1])
                curBlock['prices'].append(data.iloc[i,0])
                curBlock['time'].append(data.index.values[i])
                curBlock['sizeLeft'] = curBlock['sizeLeft'] - data.iloc[i,1]
                print('remaining size left',curBlock['sizeLeft'])
                data.iloc[i,1] = 0
                print('size depleted',data.iloc[i, 1])


    #RETURN: [end_time, VWAP, num_trades]
    return out



data = pd.read_excel('streaming_tick_data.xlsx', sheetname='test_data', index_col='time')

#new_data = pd.DataFrame(getFixedVolumeData(data, 1))
#print(new_data)

#st.write(new_data,'fixed_volume_streaming_data.xlsx','Sheet1')
