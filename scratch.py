import pandas as pd
import numpy as np


data = pd.read_excel('vwap_backtests/fixed_volume_streaming_data_VWAP_8_20_2018.xlsx',sheetname='ML_INPUT',index_col='time')

rd = np.full((1, data.shape[0]),10)
#rd = np.random.random((1,data.shape[0]))
print(rd[0], 'rd np')
rd = [0] * data.shape[0]
print('rd list', rd)

rd_series = pd.Series(rd, index=data.index.values)
print(rd_series)

x = [[1,3,4],[5,6,7],[8,9,10]]

slice = x[0][:]
print('slice', slice)


