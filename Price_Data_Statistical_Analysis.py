import numpy as np
import pandas as pd
import sys
import datetime as datetime
sys.path.append('../')
from ML_Trading import ML_functions as mlfcn
from ML_Trading import Signals_Testing as st
from ML_Trading import Stat_Fcns as sf
import cPickle

from matplotlib import pyplot
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf


#PLOT CORRELLEGRAM OF 1MIN, 5MIN, 15MIN DATA
#1min data

#PICKLE IN
'''
data = pd.read_excel('BTC_Diff_Freq_Momentum_BITMEX_3.xlsx','traits_input',index_col='Dates')
data = data.dropna()

data_pickle = open('data.pickle', 'wb')
cPickle.dump(data, data_pickle)
data_pickle.close()
'''

pickle_in = open('data.pickle', 'rb')
data = cPickle.load(pickle_in)

bps_chg_data = data['PRICE_BPS_CHG']
plot_acf(x=bps_chg_data, lags=np.arange(1, 30), alpha=.05)
plot_pacf(x=bps_chg_data, lags=np.arange(1, 30), alpha=.05)

pyplot.show()


