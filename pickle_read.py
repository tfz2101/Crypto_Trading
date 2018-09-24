import pickle
import time

for i in range(0, 1000):
    pickle_in = open('test.pickle', 'rb')
    data = pickle.load(pickle_in)
    print('data', data)
