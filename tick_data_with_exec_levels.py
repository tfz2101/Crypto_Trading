import numpy as np
import pandas as pd
import sys
import datetime as datetime
sys.path.append('../')
from ML_Trading import ML_functions as mlfcn
from ML_Trading import Signals_Testing as st


def sumproduct(list1, list2):
    sum = 0
    for i in range(0, len(list1)):
        sum += list1[i] * list2[i]

    return sum


#Takes fixed internal price and volume time series and transforms it into a fixed volume time series
def getFixedVolumeData(orig_data, size):
    #@FORMAT: orig_data = df(price, volume, side, index=dates)
    out = []
    fullout = []
    data =  orig_data.copy()
    curBlock ={'time': [], 'sizeLeft': size, 'prices': [], 'sizes': []}

    for i in range(0,data.shape[0]):

        while data.iloc[i,1] > 0.0:
            if curBlock['sizeLeft'] < data.iloc[i,1]:
                data.iloc[i,1] = data.iloc[i,1] - curBlock['sizeLeft']
                curBlock['sizes'].append(curBlock['sizeLeft'])
                curBlock['prices'].append(data.iloc[i,0])
                curBlock['time'].append(data.index.values[i])
                end_time = curBlock['time'][-1]
                try:
                   vwap = sumproduct(curBlock['prices'], curBlock['sizes'])/sum(curBlock['sizes'])
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
                data.iloc[i,1] = 0

        #attach original data to a block point that coincides or precedes it
        if len(out) <= 0:
            fullout.append([orig_data.index.values[i], orig_data.iloc[i, 0], orig_data.iloc[i, 1]])
        elif orig_data.index.values[i] <= out[len(out)-1][0]:
            row = [orig_data.index.values[i], orig_data.iloc[i,0], orig_data.iloc[i,1], orig_data.iloc[i,2]] + out[len(out)-1]
            print('row', type(orig_data.index.values[i]))
            fullout.append(row)
        elif orig_data.index.values[i] < out[len(out)-1][0]:
            row = [orig_data.index.values[i], orig_data.iloc[i,0], orig_data.iloc[i,1]] + [''] * len(out)
            print('row', type(orig_data.index.values[i]))
            fullout.append(row)

    #RETURN: [end_time, VWAP, num_trades], [time, price, size, side, end_time, VWAP, num_trades]
    return out, fullout

#For each line, look ahead in the fills and returns the fill level for both a passive buy and sell
def getNextExecutionLevel(orig_data, size, side, colName):
    #@FORMAT: orig_data = df(price, volume, side, etc, etc, index=dates)
    data  = orig_data.copy()
    sizeLeft = size
    prices = []
    volume = []
    for i in range(0, data.shape[0]):
        for j in range(i+1, data.shape[0]):
            if sizeLeft <= 0:
                continue
            else:
                if data.iloc[j,2] == side:
                    prices.append(data.iloc[j, 0])
                    sizeToDo = min(sizeLeft, data.iloc[j, 1])
                    volume.append(sizeToDo)
                    sizeLeft -= sizeToDo
        print('volumes',volume)
        print('prices', prices)
        print('sizeLeft', sizeLeft)
        if sizeLeft <= 0:
            exec_price = sumproduct(prices, volume)/ sum(volume)
            print('exec price', exec_price)
            data.ix[i,colName] = exec_price
            sizeLeft = size
            prices = []
            volume = []
        else:
            continue

    # RETURN: df([ORIGINAL FEATURES], exec_price, index=dates)
    return data

data = pd.read_excel('streaming_tick_data3.xlsx', sheetname='refined_data', index_col='time')
SIZE = 1

#Convert unicode time index to datetime index
timeindex =  data.index.values
for i in range(0, timeindex.shape[0]):
    timeindex[i] = datetime.datetime.strptime(timeindex[i], '%Y-%m-%dT%H:%M:%S.%f')
    #print('time index', timeindex[i])

data = data.set_index(timeindex)
block_data, full_block_data = getFixedVolumeData(data, SIZE)
col_name = ['time', 'price', 'size', 'side', 'end_time', 'VWAP', 'num_trades']
full_block_data = pd.DataFrame(full_block_data, columns=col_name)
full_block_data = full_block_data.set_index('end_time')
#st.write(full_block_data, 'fixed_volume_streaming_data3.xlsx','Sheet1')
print('full block data', full_block_data)

print('data', data)
data_next_level = getNextExecutionLevel(data, SIZE, 'sell', 'next_buy_level')
#data_next_level2 = getNextExecutionLevel(data_next_level, SIZE, 'buy', 'next_sell_level')
print('data next level', data_next_level)

#st.write(data_next_level2,'fixed_volume_streaming_data_execpxes3.xlsx','Sheet1')
