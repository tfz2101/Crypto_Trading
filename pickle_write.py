import cPickle
import time
for i in range(0, 1000):

    pickling = open('test.pickle','wb')
    cPickle.dump(i, pickling)
    pickling.close()
    time.sleep(0.2)


