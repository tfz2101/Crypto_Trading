import numpy as np
import pandas as pd
import sys
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
                data.iloc[i,1] = 0

        #attach original data to a block point that coincides or precedes it
        if len(out) <= 0:
            fullout.append([orig_data.index.values[i], orig_data.iloc[i, 0], orig_data.iloc[i, 1]])
        elif orig_data.index.values[i] >= out[len(out)-1][0]:
            print('out len',([orig_data.index.values[i], orig_data.iloc[i,0], orig_data.iloc[i,1], orig_data.iloc[i,2]] + out[len(out)-1]))
            fullout.append(([orig_data.index.values[i], orig_data.iloc[i,0], orig_data.iloc[i,1], orig_data.iloc[i,2]] + out[len(out)-1]))
        elif orig_data.index.values[i] < out[len(out)-1][0]:
            print('out len', ([orig_data.index.values[i], orig_data.iloc[i,0], orig_data.iloc[i,1]] + out[len(out)-2]))
            fullout.append(([orig_data.index.values[i], orig_data.iloc[i,0], orig_data.iloc[i,1], orig_data.iloc[i,2]] + out[len(out)-2]))

    #RETURN: [end_time, VWAP, num_trades], [time, price, size, side, end_time, VWAP, num_trades]
    return out, fullout

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

data = pd.read_excel('streaming_tick_data.xlsx', sheetname='test_data', index_col='time')

block_data, full_block_data = getFixedVolumeData(data, 1)

full_block_data = pd.DataFrame(full_block_data, columns=["time", "price", "size", "side", "end_time", "VWAP", "num_trades"])
full_block_data = full_block_data.set_index('time')
full_data_next_level = getNextExecutionLevel(full_block_data, 1, 'sell', 'next_buy_level')
full_data_next_level2 = getNextExecutionLevel(full_data_next_level, 1, 'buy', 'next_sell_level')
print('full data next level', full_data_next_level2)

st.write(full_data_next_level2,'fixed_volume_streaming_data_execpxes.xlsx','Sheet1')
