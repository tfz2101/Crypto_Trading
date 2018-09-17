from websocket import create_connection
import json, time, ast
import pandas as pd
import sys
sys.path.append('../')
from ML_Trading import ML_functions as mlfcn
from ML_Trading import Signals_Testing as st



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


# Create connection
ws = create_connection("wss://ws-feed.pro.coinbase.com")

# Create subscription message
message = {
    "type": "subscribe",
    "channels": [{"name": "ticker", "product_ids": ["ETH-USD"]}]
}

'''
message = {
    "type": "subscribe",
    "product_ids": [
        "ETH-USD",
       # "BTC-USD"
    ],
    #Channel Types: heartbeat, ticker, snapshot, l2update
    "channels": [
        "level2",
        #"heartbeat",
        #"ticker",

        {
            "name": "ticker",
            "product_ids": [
                "ETH-USD",
                #"BTC-USD"

            ]
        }
    ]
}
'''


# Send subscribe Message
ws.send(json.dumps(message))


def toUnicode(string):
    return unicode(string, "utf-8")

resultList = []
SIZE = 5
curBlock = {'time': [], 'sizeLeft': SIZE, 'prices': [], 'sizes': []}
for i in range(0,10):
    result = ws.recv()

    try:
        #Converts json to dict
        result = json.loads(result)
        print('result', result)
        px =  float(result['price'])
        size = float(result['last_size'])
        side = str(result['side'])
        time = result['time']
        print('px', px)
        print('side', side)
        resultList.append(result)
    except:
        continue

def getTickerChannelData(listData):
    #EXPECTS A LIST OF DICTIONARIES
    def toUnicode(string):
        return  unicode(string, "utf-8")

    data = []
    for d in listData:
        if d[toUnicode('type')] == 'ticker':

            try:
                #print('time', d[toUnicode('time')])
                #print('price',d[toUnicode('price')])
                #print('side',d[toUnicode('side')])
                #print('size',d[toUnicode('last_size')])
                #print('bid',d[toUnicode('best_bid')])
                #print('ask',d[toUnicode('best_ask')])
                data.append([d[toUnicode('time')],d[toUnicode('price')],d[toUnicode('side')],d[toUnicode('last_size')],d[toUnicode('best_bid')],d[toUnicode('best_ask')],d[toUnicode('trade_id')]])
            except:
                pass

    return pd.DataFrame(data,columns=['time','price','side','last_size','best_bid','best_ask','trade_id'])

#data = getTickerChannelData(resultList)
#st.write(data,'streaming_tick_data7.xlsx','sheet1')

'''
with open('../btc_usd.json', 'w') as fp:
    json.dump(result, fp)

ws.close()

with open('../btc_usd.json') as jdb:
    data = json.load(jdb)
    print('data',data)

'''
