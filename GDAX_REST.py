from websocket import create_connection
import json, time, ast
import pandas as pd
import sys
import datetime
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

bars = []
SIZE = 5
curBlock = {'sizeLeft': SIZE, 'prices': [], 'sizes': []}
transactions = []
for i in range(0,20):
    result = ws.recv()

    #Converts json to dict
    result = json.loads(result)
    print('result', result)

    try:
        px =  float(result['price'])
        size = float(result['last_size'])
        side = str(result['side'])
        time = result['time']
        time = datetime.datetime.strptime(time, '%Y-%m-%dT%H:%M:%S.%f000Z')

        print('px', px)
        print('side', side)
        print('time', time)
        print('size', size)
        transactions.append([time, px, size, side])
        if size >= curBlock['sizeLeft']:
            size_leftover = 1000
            while size_leftover > 0:
                size_leftover = size - curBlock['sizeLeft']
                curBlock['sizes'].append(curBlock['sizeLeft'])
                curBlock['prices'].append(px)

                #Calc completed block
                print('current blockness', curBlock)
                vwap_lst = [size * px for px,size in zip(curBlock['prices'], curBlock['sizes'])]
                vwap = float(sum(vwap_lst))/sum(curBlock['sizes'])
                print('vwap', vwap)
                num_trades = len(curBlock['sizes'])
                bar = [time, vwap, num_trades]
                bars.append(bar)

                #Create new block
                curBlock = {'sizeLeft': SIZE, 'prices': [], 'sizes': []}
            #We know size_leftover is not bigger than SIZE from above loop.
            if size_leftover > 0:
                curBlock['sizes'].append(size_leftover)
                curBlock['prices'].append(px)
        if size < curBlock['sizeLeft']:
            curBlock['prices'].append(px)
            curBlock['sizes'].append(size)
            curBlock['sizeLeft'] -= size

        print('curblock', curBlock)
    except:
        continue

transactions = pd.DataFrame(transactions, columns=['time','px','size','side'])
st.write(transactions, 'transactions.xlsx', 'sheet1')
bars = pd.DataFrame(bars)
st.write(bars, 'bars.xlsx','sheet1')

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
