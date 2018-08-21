import requests
import pandas as pd
import numpy as np
import tablib
import sys
sys.path.append('../')
from ML_Trading import ML_functions as mlfcn
from ML_Trading import Signals_Testing as st

url = 'https://rest.coinapi.io/v1/orderbooks/BITSTAMP_SPOT_BTC_USD/history?time_start=2018-08-17T00:00:00'
headers = {'X-CoinAPI-Key' : '7C973F6B-9E95-49DA-8E9E-55F35FC3092F', 'Accept' : 'application/json'}
response = requests.get(url, headers=headers)

data = response.json()
print(data)

def getTickerChannelData(listData):
    #EXPECTS A LIST OF DICTIONARIES
    def toUnicode(string):
        return  unicode(string, "utf-8")

    data = []
    for d in listData:
            try:
                #print('time', d[toUnicode('time')])
                #print('price',d[toUnicode('price')])
                #print('side',d[toUnicode('side')])
                #print('size',d[toUnicode('last_size')])
                #print('bid',d[toUnicode('best_bid')])
                #print('ask',d[toUnicode('best_ask')])
                data.append([d[toUnicode('time_exchange')],d[toUnicode('price')],d[toUnicode('side')],d[toUnicode('last_size')],d[toUnicode('best_bid')],d[toUnicode('best_ask')],d[toUnicode('trade_id')]])
            except:
                pass

    return pd.DataFrame(data,columns=['time','price','side','last_size','best_bid','best_ask','trade_id'])



#new_data = tablib.Dataset(data)
#open('coinapi.xls', 'wb').write(new_data.xls)