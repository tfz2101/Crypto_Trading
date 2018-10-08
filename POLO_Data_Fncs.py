import gdax
import inspect
import numpy as np
import pandas as pd
import datetime
import time
from scipy.stats import kurtosis, skew, linregress
from Execution_Algorithms import *
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import sys
sys.path.append('../')
from ML_Trading import ML_functions as mlfcn
from ML_Trading import Signals_Testing as st
from pytz import timezone
from poloniex import Poloniex


polo = Poloniex()
#help(polo)
ticker = polo.returnLoanOrders('ETH')
print(ticker)