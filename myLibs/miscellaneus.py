"""Just a set of useful functions"""
import numpy as np

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
