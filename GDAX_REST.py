from websocket import create_connection, _exceptions
import thread
import json, time, ast
import pandas as pd
import sys
import datetime
sys.path.append('../')
from ML_Trading import ML_functions as mlfcn
from ML_Trading import Signals_Testing as st
import cPickle


def on_message(ws, message):
    print(message)

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    def run(*args):
        for i in range(3):
            time.sleep(1)
            ws.send("Hello %d" % i)
        time.sleep(1)
        ws.close()
        print("thread terminating...")
    thread.start_new_thread(run, ())

'''
# Create permanant connection
enableTrace(True)
ws = WebSocketApp("wss://ws-feed.pro.coinbase.com",
                  on_message = on_message,
                  on_error = on_error,
                  on_close = on_close)
ws.on_open = on_open
ws.run_forever()
'''


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
LEDGE_LIMIT = 61
block_counter = 1
curBlock = {'sizeLeft': SIZE, 'prices': [], 'sizes': [], 'id': 0}
transactions = []

start_time =  datetime.datetime.now()
run_time_sec = 60 * 60 * 9
end_time = start_time + datetime.timedelta(seconds=run_time_sec)

while datetime.datetime.now() < end_time:
    try:
        result = ws.recv()
    except _exceptions.WebSocketConnectionClosedException:
        # Create connection
        print('Connection Lost')
        ws = create_connection("wss://ws-feed.pro.coinbase.com")
        ws.send(json.dumps(message))
        continue

    try:
        #Converts json to dict
        result = json.loads(result)
        print('trade id', result['trade_id'])
        print('sequence', result['sequence'])

        px =  float(result['price'])
        size = float(result['last_size'])
        side = str(result['side'])
        time = result['time']
        time = datetime.datetime.strptime(time, '%Y-%m-%dT%H:%M:%S.%f000Z')

        transactions.append([time, px, size, side])

        if size < curBlock['sizeLeft']:
            curBlock['prices'].append(px)
            curBlock['sizes'].append(size)
            curBlock['sizeLeft'] -= size
            continue

        if size >= curBlock['sizeLeft']:
            size_leftover = size
            while size_leftover - curBlock['sizeLeft'] > 0:
                size_leftover = size_leftover - curBlock['sizeLeft']
                curBlock['sizes'].append(curBlock['sizeLeft'])
                curBlock['prices'].append(px)

                #Calc completed block
                vwap_lst = [size * px for px,size in zip(curBlock['prices'], curBlock['sizes'])]
                vwap = float(sum(vwap_lst))/sum(curBlock['sizes'])
                num_trades = len(curBlock['sizes'])
                bar = [time, vwap, num_trades, curBlock['id']]
                if len(bars) >= LEDGE_LIMIT:
                    del bars[0]
                    bars.append(bar)
                else:
                    bars.append(bar)

                pickle_bar = open('tick_block_history.pickle', 'wb')
                cPickle.dump(bars, pickle_bar)
                pickle_bar.close()

                #Create new block
                curBlock = {'sizeLeft': SIZE, 'prices': [], 'sizes': [], 'id': block_counter}
                block_counter += 1

            #We know size_leftover is not bigger than SIZE from above loop.
            if size_leftover > 0:
                curBlock['sizes'].append(size_leftover)
                curBlock['sizeLeft'] -= size_leftover
                curBlock['prices'].append(px)
        print('curblock', curBlock)
    except:
        continue

#transactions = pd.DataFrame(transactions, columns=['time','px','size','side'])
#st.write(transactions, 'transactions.xlsx', 'sheet1')
#bars = pd.DataFrame(bars)
#st.write(bars, 'bars.xlsx','sheet1')



'''
with open('../btc_usd.json', 'w') as fp:
    json.dump(result, fp)

ws.close()

with open('../btc_usd.json') as jdb:
    data = json.load(jdb)
    print('data',data)

'''
