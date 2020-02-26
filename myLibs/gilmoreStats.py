"""A simple implementation of the statistical equations that are
presented in Gilmore's book. myDataList is a python list containing
the histogram information lowXVal and uppXVal are values in that can
be floats they are converted to integer indeces so they can be
addressed easely by the closest value on myDataList.

"""

from math import sqrt, pi
import numpy as np
from myLibs.miscellaneus import *

def gilmoreGrossIntegral(myDataList,lowXVal,uppXVal):  #checked
    xVals,yVals=myDataList
    L,U=getIdxRangeVals(myDataList,lowXVal,uppXVal)
    G=sum(yVals[L:U+1])  #incluye en la suma el bin L y U
    return G             #para el caso del DppMCA, no incluye la suma de los bins L y U
                         #asi lo calcula el DppMCA     G=sum(yVals[L+1:U])

def gilmoreBackground(myDataList,lowXVal,uppXVal):     #checked
    xVals,yVals=myDataList
    L,U=getIdxRangeVals(myDataList,lowXVal,uppXVal)
    n=(U-L)+1                   #n is the number of channels within the peak region
    C=yVals
    B=n*(C[L-1]+C[U+1])/2       #
                                #B=(n-1)*(C[L]+C[U])/2 asi lo hace DppMCA
    return B

def gilmoreNetArea(myDataList,lowXVal,uppXVal):        #checked
    xVals,yVals=myDataList
    G=gilmoreGrossIntegral(myDataList,lowXVal,uppXVal)
    B=gilmoreBackground(myDataList,lowXVal,uppXVal)
    A=G-B
    return A

def doOutputFile(myFilename,df,dfG):
    myOutputfile=open(myFilename+'_out.put','w')
    myOutputfile.write("Gilmore statistics\n[variables in counts]\n")
    myOutputfile.write(df.to_string())
    myOutputfile.close()
    myOutputfile=open(myFilename+'_out.put','a')
    myOutputfile.write("\nGauss Parameters\n")
    myOutputfile.write(dfG.to_string())
    myOutputfile.close()
    return 0

def gilmoreExtendedBkgExtensionsInt(myDataList,lowXVal,uppXVal,m=1): #checked
    """Takes into account the bins (1 by default) before and after the
region of interest. Default m=1 NetArea=Area+ExtendedBKGD""" 
    xVals,yVals=myDataList
    L,U=getIdxRangeVals(myDataList,lowXVal,uppXVal)
    n=(U-L)+1                   #n is the number of channels within the peak region
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

def gilmoreExtendedSigma(myDataList,lowXVal,uppXVal,m=5):
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
        # lowXVal,uppXVal=infoDict[e]
        for i in infoDict[e]:               
            if i == 'start':
                lowXVal=infoDict[e][i]
            elif i == 'end':
                uppXVal=infoDict[e][i]
        #print(lowXVal, uppXVal)
        #print(e)
        
        

        #print(getIdxRangeVals(myDataList,lowXVal,uppXVal))
        minX,maxX=getIdxRangeVals(myDataList,lowXVal,uppXVal)
        max_value = max(yVals[minX:maxX])
        max_index = minX+yVals[minX:maxX].index(max_value)
        #print("max_index,max_value = ",max_index,max_value)
        #print("testing maxYval with the index ", yVals[max_index])
        #print("testing maxXval with the index ", xVals[max_index])
        G=gilmoreGrossIntegral(myDataList,lowXVal,uppXVal)
        B=gilmoreBackground(myDataList,lowXVal,uppXVal)
        netArea=gilmoreNetArea(myDataList,lowXVal,uppXVal)
        sigma_A=gilmoreSigma(myDataList,lowXVal,uppXVal)

        m=2 #extended region
        EBA=gilmoreExtendedBkgExtensionsInt(myDataList,\
                                           lowXVal,uppXVal,m)
        extSigma_A=gilmoreExtendedSigma(myDataList,\
                                        lowXVal,uppXVal,m)
        #print("G,B,netArea,sigma_A = ",G,B,netArea,sigma_A)
        #print("EBA, extSigma_A = ",EBA,extSigma_A)
        myFWHMSigma_A=fwhm(sigma_A)
        myFWHMExtSigma_A=fwhm(extSigma_A)
        #print("myFWHMSigma,myFWHMExtSigma_A = ",\
              #myFWHMSigma_A,myFWHMExtSigma_A)

        gilmoreDict[e]=[e,netArea,EBA,G,B,\
                        sigma_A,\
                        extSigma_A,\
                        myFWHMSigma_A,\
                        myFWHMExtSigma_A,\
                        max_index,\
                        max_value]

        # return gilmoreDict
    return gilmoreDict
