"""Just a set of useful functions"""
import numpy as np
from matplotlib import pyplot as plt

###### MATPLOTLIB CONF #########################
SMALL_SIZE = 15
MEDIUM_SIZE = 22
BIGGER_SIZE = 30

plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

#################################################

def is_float(n):
    try:
        float_n = float(n)
    except ValueError:
        return False
    else:
        return True

def getIdxRangeVals(myDataList,xMin,xMax):
    xVals=myDataList[0]
    xMinIdx=xVals[0]
    xMaxIdx=xVals[-1]
    for i,x in enumerate(xVals):
        if xMin <= x:
            xMinIdx=i
            break
    #This needs to be optimized!
    for i,x in enumerate(xVals):
        if xMax <= x:
            xMaxIdx=i
            break

    return [xMinIdx,xMaxIdx]

def fwhm(sigma):
    return 2*np.sqrt(2*np.log(2))*sigma

def getRescaledList(myDataList,tRatio):
    newYVals=[yVal*tRatio for yVal in myDataList[1]]
    newDataList=[myDataList[0],newYVals]
    return newDataList

def getSubstractedList(myDataList,myRescaledList):
    dataYVals=myDataList[1]
    rescaledYVals=myRescaledList[1]
    subsYVals=[datY-rescY for \
               datY,rescY in zip(dataYVals,rescaledYVals)]
    return [myDataList[0],subsYVals]

def getRebinedList(myDataList,rebInt):
    xVals,yVals=myDataList
    assert (len(xVals) == len(yVals)), "Can't continue if arrays are not the same size!!"
    newYVals = np.add.reduceat(yVals, np.arange(0, len(yVals), rebInt))
    newXVals = xVals[rebInt//2::rebInt] #numpy slice.
    if len(newYVals) != len(newXVals):
        #If here then only 1 xValue was truncated.
        res=len(xVals)%rebInt
        theIdx=(len(xVals)//rebInt)*rebInt+res//2
        newXVals=np.append(newXVals,[xVals[theIdx]])
    return [newXVals,newYVals]
