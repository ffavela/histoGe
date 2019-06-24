"""A simple implementation of the statistical equations that are
presented in Gilmore's book. myDataList is a python list containing
the histogram information lowXVal and uppXVal are values in that can
be floats they are converted to integer indeces so they can be
addressed easely by the closest value on myDataList.

"""

from math import sqrt, pi
import numpy as np
from myLibs.miscellaneus import *

def gilmoreGrossIntegral(myDataList,lowXVal,uppXVal):
    xVals,yVals=myDataList
    L,U=getIdxRangeVals(myDataList,lowXVal,uppXVal)
    G=sum(yVals[L:U+1])
    return G

def gilmoreBackground(myDataList,lowXVal,uppXVal):
    xVals,yVals=myDataList
    L,U=getIdxRangeVals(myDataList,lowXVal,uppXVal)
    n=U-L
    C=yVals
    B=n*(C[L-1]+C[U+1])/2
    return B

def gilmoreNetArea(myDataList,lowXVal,uppXVal):
    xVals,yVals=myDataList
    G=gilmoreGrossIntegral(myDataList,lowXVal,uppXVal)
    B=gilmoreBackground(myDataList,lowXVal,uppXVal)
    A=G-B
    return A

def gilmoreExtendedBkgExtensionsInt(myDataList,lowXVal,uppXVal,m=5):
    """Takes into account the bins (5 by default) before and after the
region of interest"""
    xVals,yVals=myDataList
    L,U=getIdxRangeVals(myDataList,lowXVal,uppXVal)
    n=U-L
    C=yVals
    G=gilmoreGrossIntegral(myDataList,lowXVal,uppXVal)
    A=G-n*(sum(C[L-m:L])+sum(C[U+1:U+m+1]))/(2*m)
    return A

def gilmoreSigma(myDataList,lowXVal,uppXVal):
    xVals,yVals=myDataList
    A=gilmoreNetArea(myDataList,lowXVal,uppXVal)
    B=gilmoreBackground(myDataList,lowXVal,uppXVal)
    sigma_A=np.sqrt(A+2*B)
    return sigma_A

def gilmoreExtendedSigma(myDataList,lowXVal,uppXVal,m):
    xVals,yVals=myDataList
    L,U=getIdxRangeVals(myDataList,lowXVal,uppXVal)
    n=U-L
    A=gilmoreNetArea(myDataList,lowXVal,uppXVal)
    B=gilmoreBackground(myDataList,lowXVal,uppXVal)
    extSigma_A=np.sqrt(A+B*(1+n/(2*m)))
    return extSigma_A

def doGilmoreStuff(infoDict,myDataList):
    gilmoreDict={}
    if infoDict == {}:
        return gilmoreDict
    xVals,yVals=myDataList
    for e in infoDict:
        print(e)
        lowXVal,uppXVal=infoDict[e]

        print(getIdxRangeVals(myDataList,lowXVal,uppXVal))
        minX,maxX=getIdxRangeVals(myDataList,lowXVal,uppXVal)
        max_value = max(yVals[minX:maxX])
        max_index = minX+yVals[minX:maxX].index(max_value)
        print("max_index,max_value = ",max_index,max_value)
        print("testing maxYval with the index ", yVals[max_index])
        print("testing maxXval with the index ", xVals[max_index])
        G=gilmoreGrossIntegral(myDataList,lowXVal,uppXVal)
        B=gilmoreBackground(myDataList,lowXVal,uppXVal)
        netArea=gilmoreNetArea(myDataList,lowXVal,uppXVal)
        sigma_A=gilmoreSigma(myDataList,lowXVal,uppXVal)

        m=5 #extended region
        EBA=gilmoreExtendedBkgExtensionsInt(myDataList,\
                                           lowXVal,uppXVal,m)
        extSigma_A=gilmoreExtendedSigma(myDataList,\
                                        lowXVal,uppXVal,m)
        print("G,B,netArea,sigma_A = ",G,B,netArea,sigma_A)
        print("EBA, extSigma_A = ",EBA,extSigma_A)
        myFWHMSigma_A=fwhm(sigma_A)
        myFWHMExtSigma_A=fwhm(extSigma_A)
        print("myFWHMSigma,myFWHMExtSigma_A = ",\
              myFWHMSigma_A,myFWHMExtSigma_A)

        gilmoreDict[e]=[G,B,netArea,\
                        sigma_A,EBA,\
                        extSigma_A,\
                        myFWHMSigma_A,\
                        myFWHMExtSigma_A,\
                        max_index,\
                        max_value]

        # return gilmoreDict
    return gilmoreDict
