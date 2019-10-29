from matplotlib import pyplot as plt
import numpy as np

def plotCos():
    t2 = np.arange(0.0, 5.0, 0.02)
    plt.plot(t2, np.cos(2*np.pi*t2), 'r--')
    plt.show()


def myPlotF(myDataList):
    plt.plot(myDataList[0],myDataList[1])
    #plt.show()
    
