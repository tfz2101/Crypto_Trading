import requests
import pandas as pd
import numpy as np
import tablib
import sys
sys.path.append('../')
from ML_Trading import ML_functions as mlfcn
from ML_Trading import Signals_Testing as st

url = 'https://rest.coinapi.io/v1/exchangerate/BTC/USD'
headers = {'X-CoinAPI-Key' : '7C973F6B-9E95-49DA-8E9E-55F35FC3092F', 'Accept' : 'application/json'}
response = requests.get(url, headers=headers)

data = response.json()
tablib.Dataset(data)
pd.read_json(data).to_excel("coinapi.xlsx")

