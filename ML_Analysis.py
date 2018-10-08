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
from sklearn.ensemble import RandomForestClassifier as RFC
import pydotplus

from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import LeaveOneOut
from sklearn.model_selection import KFold


#KFOLD CROSS VALIDATION ON RANDOM FOREST CLASSIFIER
'''
ml_data = pd.read_excel('ETC_Diff_Freq_Momentum_May_To_June.xlsx','ml_input',index_col='Dates')
ml_data = ml_data.dropna()
ml_data = ml_data.drop(['Volume','LAST_PRICE','NUMBER_TICKS','Exec_Buy_Or_Sale'],axis=1)
print('ml data', ml_data)

Y_ = ml_data['Y']
X_ = ml_data.drop('Y', axis=1)

#COLUMNS =[Y,..., index=datetime]
kf = KFold(n_splits=5)
for train, test in kf.split(ml_data):
    Y_train = Y_[train]
    X_train = X_.ix[train,:]
    print('train', Y_train)
    print('test', X_train)
    Y_test = Y_[test]
    X_test = X_.ix[test,:]
    clf = RFC().fit(X_train, Y_train)
    score = clf.score(X_test, Y_test)
    print('score', score)

'''

#TRAIN ON DATASET TO PREDICT A SECOND DATASET
#training dataset
ml_data = pd.read_excel('ETC_Diff_Freq_Momentum_May_To_June.xlsx','ml_input',index_col='Dates')
ml_data = ml_data.dropna()
ml_data = ml_data.drop(['Volume','LAST_PRICE','NUMBER_TICKS','Exec_Buy_Or_Sale'],axis=1)
print('ml data', ml_data)

Y_ = ml_data['Y']
X_ = ml_data.drop('Y', axis=1)

clf = RFC().fit(X_, Y_)

#testing dataset
ml_data = pd.read_excel('ETC_Diff_Freq_Momentum_July_To_August.xlsx','ml_input',index_col='Dates')
ml_data = ml_data.dropna()
ml_data = ml_data.drop(['Volume','LAST_PRICE','NUMBER_TICKS','Exec_Buy_Or_Sale'],axis=1)
print('ml data', ml_data)
Y_test = ml_data['Y']
X_test = ml_data.drop('Y', axis=1)


score = clf.score(X_test, Y_test)
print('score', score)

predicts = clf.predict(X_test).tolist()
print('predicts', predicts)
predicts_log_proba = clf.predict_log_proba(X_test)
print('preidcts proba', predicts_log_proba)
predicts_proba = clf.predict_proba(X_test)

output = pd.DataFrame(predicts, index=X_test.index.values, columns=['predictions'])

st.write_new(output, 'ml_test.xlsx', 'sheet1')