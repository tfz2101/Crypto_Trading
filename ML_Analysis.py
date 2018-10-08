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


#RUN A DECISION TREE OR RANDOM FOREST ON DATA

ml_data = pd.read_excel('r_input.xlsx','sheet2',index_col='Date')
ml_data = ml_data.dropna()
print('ml data', ml_data)

#COLUMNS =[Y,..., index=datetime]
kf = KFold(n_splits=5)
for train, test in kf.split(ml_data):
    Y_train = train['Y']
    X_train = train.drop('Y', axis=1)
    Y_test = test['Y']
    X_test = test.drop('Y', axis=1)
    clf = RFC().fit(X_train, Y_train)
    score = clf.score(X_test, Y_test)
    print('score', score)


