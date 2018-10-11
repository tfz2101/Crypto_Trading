import numpy as np
import pandas as pd
import datetime
import time
import sys
sys.path.append('../')
from ML_Trading import ML_functions as mlfcn
#from ML_Trading import Signals_Testing as st
from pytz import timezone
import requests
import bitmex
import json

API_FILE = '../bitmex.txt'
with open(API_FILE) as f:
    lines = [line.rstrip('\n') for line in open(API_FILE)]
print(lines)
client = bitmex.bitmex(test=False, api_key=lines[0], api_secret=lines[1])


start_date = datetime.datetime(2018, 8, 4, 0, 0, 0)
bars = 750
bar_unit = 5
delta = datetime.timedelta(minutes=bars*bar_unit)
end_date = start_date + delta


out = client.Trade.Trade_getBucketed(binSize='5m', symbol='ETHUSD', count=bars, reverse=False, startTime = start_date, endTime = end_date).result()[0]
print(out)






