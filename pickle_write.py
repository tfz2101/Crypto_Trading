import pickle
import time
for i in range(0, 1000):

    pickling = open('test.pickle','wb')
    pickle.dump(i, pickling)
    pickling.close()
    time.sleep(0.2)


