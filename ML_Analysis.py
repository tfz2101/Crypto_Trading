import numpy as np
import pandas as pd
import sys
import datetime as datetime
sys.path.append('../')
from ML_Trading import ML_functions as mlfcn
from ML_Trading import Signals_Testing as st
from ML_Trading import Stat_Fcns as sf

from sklearn.tree import export_graphviz
from sklearn.ensemble import RandomForestRegressor as RF
from sklearn.ensemble import RandomForestClassifier as RFC

from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import LeaveOneOut
from sklearn.model_selection import KFold
from sklearn.metrics import confusion_matrix

#KFOLD CROSS VALIDATION ON RANDOM FOREST CLASSIFIER
'''
ml_data = pd.read_excel('ETC_Diff_Freq_Momentum_BITMEX_BTC.xlsx','ml_input',index_col='Dates')
ml_data = ml_data.dropna()
print('ml data', ml_data)

Y_ = ml_data['Y']
X_ = ml_data.drop('Y', axis=1)

#COLUMNS =[Y,..., index=datetime]
kf = KFold(n_splits=5)
for train, test in kf.split(ml_data):
    Y_train = Y_[train]
    X_train = X_.ix[train,:]
    #print('train', Y_train)
    #print('test', X_train)
    Y_test = Y_[test]
    X_test = X_.ix[test,:]
    clf = RFC().fit(X_train, Y_train)
    score = clf.score(X_test, Y_test)
    print('score', score)
'''


#TRAIN SPLIT TEST WITH RFC
'''
N_ESTIMATORS = 200
MAX_DEPTH = 8

ml_data = pd.read_excel('ETC_Diff_Freq_Momentum_BITMEX_BTC3.xlsx','ml_input',index_col='Dates')
ml_data = ml_data.dropna()

#buy and sell
Y_long = ml_data['Y_exec_60_buy']
X = ml_data.drop(['Y_exec_60_buy','Y_exec_60_sell'], axis=1)
X_train, X_test, Y_train, Y_test = train_test_split(X, Y_long, train_size= 0.70, random_state=0, shuffle=False)

#columns =[Y,..., index=datetime]
clf = RFC().fit(X_train, Y_train)
pred_long = pd.DataFrame(clf.predict(X_test), index = X_test.index.values)
pred_long_probs = pd.DataFrame(clf.predict_proba(X_test), index = X_test.index.values)
score = clf.score(X_test, Y_test)
print('score', score)

#sell and buy back
Y_short = ml_data['Y_exec_60_sell']
X = ml_data.drop(['Y_exec_60_buy','Y_exec_60_sell'], axis=1)
X_train, X_test, Y_train, Y_test = train_test_split(X, Y_short, train_size= 0.70, random_state=0, shuffle=False)

clf = RFC().fit(X_train, Y_train)
pred_short = pd.DataFrame(clf.predict(X_test), index = X_test.index.values)
pred_short_probs = pd.DataFrame(clf.predict_proba(X_test), index = X_test.index.values)
score = clf.score(X_test, Y_test)
print('score', score)

#predictions = pd.concat([pred_long, pred_short])

st.write_new(pred_long, 'predictions1.xlsx', 'pred_long')
st.write(pred_long_probs, 'predictions1.xlsx', 'pred_long_probs')
st.write(pred_short, 'predictions1.xlsx', 'pred_short')
st.write(pred_short_probs, 'predictions1.xlsx', 'pred_short_probs')
'''


#TRAIN SPLIT TEST WITH RF Regression
N_ESTIMATORS = 200
MAX_DEPTH = 8
TRAIN_SIZE = 0.7

ml_data = pd.read_excel('ETC_Diff_Freq_Momentum_BITMEX_BTC_3.xlsx','ml_input',index_col='Dates')
ml_data = ml_data.dropna()

#buy and sell
Y_long = ml_data['Y_exec_60_buy']
X = ml_data.drop(['Y_exec_60_buy','Y_exec_60_sell'], axis=1)
X_train, X_test, Y_train, Y_test = mlfcn.trainTestSplit(X, Y_long, trainsplit= TRAIN_SIZE)

    #columns =[Y,..., index=datetime]
clf = RF().fit(X_train, Y_train)
pred_long = pd.DataFrame(clf.predict(X_test), index = X_test.index.values)

#sell and buy back
Y_short = ml_data['Y_exec_60_sell']
X = ml_data.drop(['Y_exec_60_buy','Y_exec_60_sell'], axis=1)
X_train, X_test, Y_train, Y_test = mlfcn.trainTestSplit(X, Y_short, trainsplit= TRAIN_SIZE)

clf = RF().fit(X_train, Y_train)
pred_short = pd.DataFrame(clf.predict(X_test), index = X_test.index.values)

st.write_overwritesheet(pred_long, 'ml_test.xlsx', 'long_predictions')
st.write_overwritesheet(pred_short, 'ml_test.xlsx', 'short_predictions')



#TRAIN ON DATASET TO PREDICT A SECOND DATASET USING RFC
'''
#training dataset
ml_data = pd.read_excel('ETC_Diff_Freq_Momentum_BITMEX_BTC.xlsx','ml_input',index_col='Dates')
ml_data = ml_data.dropna()
print('ml data', ml_data)
Y = 'Y_long'
Y_ = ml_data[Y]
X_ = ml_data.drop(['Y_long', 'Y_short'], axis=1)

clf = RFC().fit(X_, Y_)

#testing dataset
ml_data = pd.read_excel('ETC_Diff_Freq_Momentum_BITMEX_BTC_2.xlsx','ml_input',index_col='Dates')
ml_data = ml_data.dropna()
print('ml data', ml_data)
Y_test = ml_data[Y]
X_test = ml_data.drop(['Y_long', 'Y_short'], axis=1)


score = clf.score(X_test, Y_test)
print('score', score)

predicts = clf.predict(X_test).tolist()
print('predicts', predicts)
predicts_log_proba = clf.predict_log_proba(X_test)
print('preidcts proba', predicts_log_proba)
predicts_proba = clf.predict_proba(X_test)

predicts = pd.DataFrame(predicts, index=X_test.index.values, columns=['predictions'])
predicts_proba = pd.DataFrame(predicts_proba, index=X_test.index.values)

confusion = confusion_matrix(Y_test.values, predicts.values)
print('confusion matrix', confusion)
#st.write_new(predicts, 'ml_test_long.xlsx', 'predictions')
#st.write(predicts_proba, 'ml_test_long.xlsx', 'prediction_probs')
'''



#TRAIN ON DATASET TO PREDICT A SECOND DATASET USING RF_REGRESSION
'''
N_ESTIMATORS = 200
MAX_DEPTH = 8

#LONG SIDE
#training dataset
ml_data_tr = pd.read_excel('ETC_Diff_Freq_Momentum_BITMEX_BTC.xlsx','ml_input',index_col='Dates')
ml_data_tr = ml_data_tr.dropna()
ml_data = ml_data_tr
Y = 'Y_exec_60_buy'
Y_ = ml_data[Y]
X_ = ml_data.drop(['Y_exec_60_buy', 'Y_exec_60_sell'], axis=1)

clf = RF(n_estimators=N_ESTIMATORS, max_depth=MAX_DEPTH).fit(X_, Y_)
print('features column', X_.columns.values)
print('feature important', clf.feature_importances_)

#testing dataset
ml_data_te = pd.read_excel('ETC_Diff_Freq_Momentum_BITMEX_BTC_2.xlsx','ml_input',index_col='Dates')
ml_data_te = ml_data_te.dropna()
ml_data = ml_data_te
Y_test = ml_data[Y]
X_test = ml_data.drop(['Y_exec_60_buy', 'Y_exec_60_sell'], axis=1)

predicts = clf.predict(X_test).tolist()

predicts = pd.DataFrame(predicts, index=X_test.index.values, columns=['predictions'])
st.write_overwritesheet(predicts, 'ml_test.xlsx', 'long_predictions')  #ml_test.xlsx already exists, has formula sheets embedded in it


#SHORT SIDE
#training dataset
ml_data = ml_data_tr
Y = 'Y_exec_60_sell'
Y_ = ml_data[Y]
X_ = ml_data.drop(['Y_exec_60_buy', 'Y_exec_60_sell'], axis=1)

clf = RF(n_estimators=N_ESTIMATORS, max_depth=MAX_DEPTH).fit(X_, Y_)

#testing dataset
ml_data = ml_data_te
Y_test = ml_data[Y]
X_test = ml_data.drop(['Y_exec_60_buy', 'Y_exec_60_sell'], axis=1)

predicts = clf.predict(X_test).tolist()

predicts = pd.DataFrame(predicts, index=X_test.index.values, columns=['predictions'])
st.write_overwritesheet(predicts, 'ml_test.xlsx', 'short_predictions')
'''


#ROLLING ML FIT AND PREDICTION ON COMBINED DATASETS
'''
#combine two datasets
ml_data1 = pd.read_excel('ETC_Diff_Freq_Momentum_BITMEX_BTC.xlsx','ml_input',index_col='Dates')
ml_data1 = ml_data1.dropna()
ml_data2 = pd.read_excel('ETC_Diff_Freq_Momentum_BITMEX_BTC_2.xlsx','ml_input',index_col='Dates')
ml_data2 = ml_data2.dropna()
data = pd.concat([ml_data1, ml_data2])
Y = 'Y_exec_60_buy'
Y_drop = 'Y_exec_60_sell'

data = data.drop(Y_drop, axis = 1)

Y_ind = len(data.columns.tolist())-1

kwaargs = {'n_estimators': 100}
preds = mlfcn.getBlendedSignal(data=data, ml_model = RF, gap = 20000, Y_index = Y_ind, **kwaargs)
preds = pd.DataFrame(preds)
st.write_new(preds, 'ml_preds','sheet1')
'''


#CALC EXECUTION LEVELS FOR GIVEN SET OF PRICES
'''
px_data = pd.read_excel('Execution_Levels_Template.xlsx','Price_Data',index_col='Dates')
px_data = px_data.dropna()
print('px data', px_data)
out_data = st.getNextExecutionLevels(px_data)
print('out_data', out_data)

st.write(out_data, 'Execution_Levels_Template.xlsx', 'execution_pxes')
'''


#RETURNS STATISTICAL TRAITS OF TIME SERIES
'''
stat_data = pd.read_excel('ETC_Diff_Freq_Momentum_BITMEX_BTC_3.xlsx',sheetname='traits_input',index_col='Dates')

rolling_stat_fcns = sf.RollingTraitStatFcns()

stat_fcns = [rolling_stat_fcns.acf_fcn_ith_cor, rolling_stat_fcns.dickeyfuller_fcn, rolling_stat_fcns.hurstExp]
traits_data = st.getRollingTraits(stat_data, stat_fcns, gap=30)
print(traits_data)

st.write_new(traits_data, 'traits_data_bit_mex3.xlsx','sheet1')
'''
