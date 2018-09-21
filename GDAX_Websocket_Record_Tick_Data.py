from websocket import create_connection
import json, time, ast
import pandas as pd
import sys
sys.path.append('../')
from ML_Trading import ML_functions as mlfcn
from ML_Trading import Signals_Testing as st
import pickle


# Create connection
ws = create_connection("wss://ws-feed.gdax.com")

# Create subscription message
message = {
    "type": "subscribe",
    "channels": [{"name": "ticker", "product_ids": ["ETH-USD"]}]
}

#Level 2 Message
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

resultList = []
for i in range(0,4000):
    result = ws.recv()
    print('result', result)
    try:
        result = json.loads(result)
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

data = getTickerChannelData(resultList)
pickle_in = open('streaming_data_09_21_18_3.pickle','wb')
pickle.dump(data, pickle_in)
pickle_in.close()
st.write(data,'streaming_tick_data_9_21_2018_3.xlsx','sheet1')

'''
with open('../btc_usd.json', 'w') as fp:
    json.dump(result, fp)

ws.close()

with open('../btc_usd.json') as jdb:
    data = json.load(jdb)
    print('data',data)

'''
