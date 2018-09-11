import numpy as np
import pandas as pd
import sys
import datetime as datetime
sys.path.append('../')
from ML_Trading import ML_functions as mlfcn
from ML_Trading import Signals_Testing as st
from ML_Trading import Stat_Fcns as sf

from sklearn.tree import DecisionTreeRegressor as DTC
from sklearn.tree import export_graphviz
from sklearn.ensemble import RandomForestRegressor as RF
import graphviz
import pydotplus


#Class for Decision Tree Regressors analysis on datasets
class DTCAnalyzer():
    def __init__(self, data, **kwarg):
        #@FORMAT: data = df('Y', signal1, signal2, etc, index=dates)
        self.data = data
        self.DTC = DTC()
        self.Y = self.data['Y'].values
        self.X = self.data.drop(['Y','num_trades_zscore','skew','time_elapsed_zscore'], axis=1).values
        print('Y', self.Y)
        print('X', self.X)

    def fitDTC(self):
        self.DTC.fit(self.X, self.Y)


    def getR_2(self):
        return self.DTC.score(self.X, self.Y)

    def showTreeGraph(self):
        dot_data = export_graphviz(self.DTC, out_file='tree_chart.bmp')
        graph = pydotplus.graph_from_dot_data(dot_data)
        graph.write_png('tree.png')

        #graph = graphviz.Source(dot_data)
        #graph.render("tree_chart")

    def getDecisionPath(self):
        return self.DTC.decision_path(self.X)

#Class for Decision Tree Regressors analysis on datasets
class RFAnalyzer():
    def __init__(self, data, **kwarg):
        #@FORMAT: data = df('Y', signal1, signal2, etc, index=dates)
        self.data = data
        self.RF = RF()
        self.Y = self.data['Y'].values
        self.X = self.data.drop(['Y','acf_value','acf_pval','df_pval'], axis=1).values
        print('Y', self.Y)
        print('X', self.X)

    def fitModel(self):
        self.RF.fit(self.X, self.Y)

    def getR_2(self):
        return self.RF.score(self.X, self.Y)

    def getFeatureImportance(self):
        return self.RF.feature_importances_

    #Returns how many features were actually used in the model fit
    def getNumFeatures(self):
        return self.RF.n_features_

def getBuySellFlux(orig_data, sample_size, start_index):
    #@FORMAT: orig_data = df(price, size, side, index=dates)
    PRICE_UNIT = .01
    data = orig_data.copy()
    for i in range(start_index, data.shape[0]):
        buys = {'deltas': [], 'prices': [], 'sizes': [], 'money': []}
        sells = {'deltas': [], 'prices': [], 'sizes': [], 'money': []}
        for j in range(i, 0, -1):
            if len(buys['prices']) >= sample_size and len(sells['prices']) >= sample_size:
                break
            #@TODO: look for upper case 'buys' and 'sell'
            #Only look at consecutive buys and sells so we can ascertain the price impact for current time t
            #Note we take t-1 values to calculate price impact since it's determined by looking at how much money was required to move price from t-1 to t
            if data.iloc[j,2] == "buy" and data.iloc[j-1,2] == "buy":
                buys['deltas'].append(data.iloc[j,0] - data.iloc[j-1,0])
                #print('delta add', buys['deltas'])
                buys['prices'].append(data.iloc[j-1, 0])
                buys['sizes'].append(data.iloc[j-1, 1])
                buys['money'].append(data.iloc[j-1, 0] * data.iloc[j-1, 1])
                #print('money', buys['money'])
            if data.iloc[j,2] == "sell" and data.iloc[j-1,2] == "sell":
                sells['deltas'].append(-1*(data.iloc[j, 0] - data.iloc[j - 1, 0]))
                #print('last price', data.iloc[j-1, 0])
                #print('deltas', float(data.iloc[j, 0]) - float(data.iloc[j - 1, 0]))
                sells['prices'].append(data.iloc[j-1,0])
                sells['sizes'].append(data.iloc[j-1, 1])
                sells['money'].append(data.iloc[j-1, 0] * data.iloc[j-1, 1])
                #print('money', sells['money'])

        #Check that the deltas are nonzero since divide by zero is not allowed
        try:
            buy_flux = sum(buys['money'])/(sum(buys['deltas'])/PRICE_UNIT)
        except ZeroDivisionError:
            buy_flux = 'unch'
        try:
            sell_flux = sum(sells['money']) / (sum(sells['deltas']) / PRICE_UNIT)
        except ZeroDivisionError:
            sell_flux = 'unch'
        print('buys grid', buys)
        data.ix[i, 'buys_flux'] = buy_flux
        data.ix[i, 'sells_flux'] = sell_flux
        print('sells grid', sells)
    #RETURN: df(price, size, side, buy_flux, sell_flux, index=dates)
    return data

def sumproduct(list1, list2):
    sum = 0
    for i in range(0, len(list1)):
        sum += list1[i] * list2[i]

    return sum

#Takes fixed internal price and volume time series and transforms it into a fixed volume time series
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

#For each line, look ahead in the fills and returns the fill level for both a passive buy and sell
def getNextExecutionLevel(orig_data, size, side, colName):
    #@FORMAT: orig_data = df(price, volume, side, etc, etc, index=dates)
    data  = orig_data.copy()
    sizeLeft = size
    prices = []
    volume = []
    for i in range(0, data.shape[0]):
        #Changed the starting index from i+1 to i - should look at current trade to determine next fill level
        for j in range(i, data.shape[0]):
            if sizeLeft <= 0:
                continue
            else:
                if data.iloc[j,2] == side:
                    prices.append(data.iloc[j, 0])
                    sizeToDo = min(sizeLeft, data.iloc[j, 1])
                    volume.append(sizeToDo)
                    sizeLeft -= sizeToDo
        print('volumes',volume)
        print('prices', prices)
        print('sizeLeft', sizeLeft)
        if sizeLeft <= 0:
            exec_price = sumproduct(prices, volume)/ sum(volume)
            print('exec price', exec_price)
            data.ix[i,colName] = exec_price
            sizeLeft = size
            prices = []
            volume = []
        else:
            continue

    # RETURN: df([ORIGINAL FEATURES], exec_price, index=dates)
    return data

'''
data = pd.read_excel('streaming_tick_data4.xlsx', sheetname='refined_data', index_col='time')
BLOCK_SIZE = 5

#Convert unicode time index to datetime index
timeindex =  data.index.values
for i in range(0, timeindex.shape[0]):
    timeindex[i] = datetime.datetime.strptime(timeindex[i], '%Y-%m-%dT%H:%M:%S.%f')
    #print('time index', timeindex[i])

data = data.set_index(timeindex)
'''

'''
block_data, full_block_data = getFixedVolumeData(data, BLOCK_SIZE)
#col_name = ['time', 'price', 'size', 'side', 'end_time', 'VWAP', 'num_trades']
col_name = ['end_time','vwap', 'num_trades']
block_data = pd.DataFrame(block_data, columns=col_name)
block_data = block_data.set_index('end_time')
st.write(block_data, 'fixed_volume_streaming_data_VWAP_4.xlsx','Sheet1')
print('block data', block_data)

EXEC_SIZE = 1
data_next_level = getNextExecutionLevel(data, EXEC_SIZE, 'sell', 'next_buy_level')
data_next_level2 = getNextExecutionLevel(data_next_level, EXEC_SIZE, 'buy', 'next_sell_level')
print('data next level', data_next_level)

st.write(data_next_level2,'fixed_volume_streaming_data_execpxes_4.xlsx','Sheet1')
'''


#ml_data = pd.read_excel('vwap_backtests/fixed_volume_streaming_data_VWAP_8_20_2018.xlsx',sheetname='ML_INPUT',index_col='time')
ml_data = pd.read_excel('r_input.xlsx','sheet2',index_col='Date')
ml_data = ml_data.dropna()
print('ml data', ml_data)

rf_analyzer = RFAnalyzer(data=ml_data)
rf_analyzer.fitModel()
feat_imp = rf_analyzer.getFeatureImportance()
print('feat imp', feat_imp)

feat_num = rf_analyzer.getNumFeatures()
print('feat num', feat_num)

r_2 = rf_analyzer.getR_2()
print('r_2', r_2)




'''
tick_data = pd.read_excel('eth_dataset_07_15_2018_Bull_Market.xlsx', sheetname='refined_data_clean', index_col='time')

flux_data  = getBuySellFlux(tick_data, 30, 200)
print('flux data', flux_data)
st.write(flux_data, 'eth_dataset_07_15_2018_Bull_Market_FLUXDATA.xlsx')
'''

'''
stat_data = pd.read_excel('ETC_Diff_Freq_Momentum.xlsx',sheetname='STATS_INPUT',index_col='Date')
print(stat_data)


rolling_stat_fcns = sf.RollingTraitStatFcns()
acf_1 = rolling_stat_fcns.acf_fcn_ith_cor(data=stat_data.values, ith=1, lags=2, alpha=.05)
print('acf', acf_1)

df = rolling_stat_fcns.dickeyfuller_fcn(data= stat_data.values, maxlag=1)
print('df', df)

stat_fcns = [rolling_stat_fcns.acf_fcn_ith_cor, rolling_stat_fcns.acf_fcn_ith_cor_pval, rolling_stat_fcns.dickeyfuller_fcn]
traits_data = st.getRollingTraits(stat_data, stat_fcns, gap=30)
print(traits_data)

st.write(traits_data, 'traits_data.xlsx','sheet1')
'''


r_data = pd.read_excel('ETC_Diff_Freq_Momentum.xlsx','R_INPUT',index_col='Date')
r_data = r_data.dropna()
print('r_data', r_data)
st.write(r_data, 'R_Scripts/signals.xlsx','sheet1')

