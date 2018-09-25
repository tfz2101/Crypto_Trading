import cPickle
import time
import pandas as pd


for i in range(0, 1000):
    pickle_in = open('test.pickle', 'rb')
    data = cPickle.load(pickle_in)
    print('data', data)
    time.sleep(0.1)


'''
pickle_in = open('zscore_5min.pickle', 'rb')
data = pickle.load(pickle_in)
print('data', data)
'''