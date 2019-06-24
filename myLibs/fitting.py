"""Curve fitting functions"""

import numpy as np
from myLibs.miscellaneus import *

def gaus(x,a,x0,sigma,c=0):
    """A gaussian bell. I added temporarly an additive constant."""
    return a*np.exp(-(x-x0)**2/(2*sigma**2)) + c

def lorentzian(x,x0,w,c):
    """I added temporarly an additive constant here too."""
    # w is the width. Still need to test this one
    return 1/np.pi*(w/2)/((x-x0)**2+(w/2)**2)

# def lineGaus(x,a,x0,sigma,c,lineCoef): # for later

def myLine(x,a,b):
    return a*x+b

def getTentParams(x4cal,y4cal):
    C1=x4cal[0]
    C2=x4cal[-1]
    E1=y4cal[0]
    E2=y4cal[-1]
    a=(E2-E1)/(C2-C1)
    b=E1-a*C1
    return a,b

###Fitting fails often here... don't know why... see histoGe.py where
###it is really called ####

# def doFittingStuff(infoDict,myDataList):
#     fittingDict={}
#     if infoDict == {}: #minor optimization
#         return fittingDict
#     for e in infoDict:
#         xMin,xMax=infoDict[e]
#         mean=(xMin+xMax)*0.5
#         print("calculated mean = ",mean)

#         # mean=1460.68
#         print("xMin,xMax = ",xMin,xMax)
#         minIdx,maxIdx=getIdxRangeVals(myDataList,\
#                                       xMin,xMax)
#         xVals=myDataList[0]
#         print("minIdx,maxIdx = ",minIdx,maxIdx)
#         print("xVals[minIdx],xVals[maxIdx] = ",\
#               xVals[minIdx],xVals[maxIdx])
#         sigma=1.0 #need to automate this!!
#         # a=150
#         yVals=myDataList[1]
#         a=max(yVals[minIdx:maxIdx])
#         print("a = ",a)
#         c=(yVals[minIdx]+yVals[maxIdx])/2
#         print("c= ",c)
#         #need to handle cases where fit fails
#         try:
#             popt,pcov = curve_fit(gaus,myDataList[0],\
#                                   myDataList[1],\
#                                   p0=[a,mean,sigma,c])
#         except:
#             print("Fit failed for %s" %(e))
#             fittingDict[e]=[None,None,None,None,None,None,None]
#             continue

#         print("popt,pcov = ",popt,pcov)
#         a,mean,sigma,c=popt
#         print("a,mean,sigma,c = ",a,mean,sigma,c)
#         myIntegral=a*sigma*sqrt(2*pi)
#         myFWHM=fwhm(sigma)
#         fittingDict[e]=[a,mean,sigma,c,minIdx,maxIdx,myFWHM]
#         print("myIntegral = ", myIntegral)
#         # return fittingDict
#     return fittingDict