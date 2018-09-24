import pickle
import time
import pandas as pd

'''
for i in range(0, 100):
    pickle_in = open('tick_block_history.pickle', 'rb')
    data = pickle.load(pickle_in)
    print('data', data)
    time.sleep(0.1)
'''

pickle_in = open('tick_block_history.pickle', 'rb')
data = pickle.load(pickle_in)
print('data', pd.DataFrame(data))
