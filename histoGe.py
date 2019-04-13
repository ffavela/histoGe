#!/usr/bin/python
###!/home/mauricio/anaconda3/bin/python3

from matplotlib import pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from scipy import asarray as ar,exp
from math import sqrt, pi

import sys
import os.path
from os.path import basename

def is_float(n):
    try:
        float_n = float(n)
    except ValueError:
        return False
    else:
        return True

def parseCalData(calStringData):
    myStrArray=calStringData.split(" ")
    myValueArray=[float(val) for val in myStrArray]
    return myValueArray

# def gaus(x,a,x0,sigma):
#     return a*exp(-(x-x0)**2/(2*sigma**2))


def gaus(x,a,x0,sigma,c=0):
    return a*np.exp(-(x-x0)**2/(2*sigma**2)) + c

# def lineGaus(x,a,x0,sigma,c,lineCoef):


def fwhm(sigma):
    return 2*np.sqrt(2*np.log(2))*sigma

def getDictFromInfoFile(infoFileName):
    infoDict={}
    for line in open(infoFileName):
        print(line)
        if line[0] == "#":
            print("skipping comment")
            continue
        newList=line.split()
        infoDict[newList[2]]=[float(val)\
                              for val in newList[0:2]]
        print("newList = ")
        print(newList)
    return infoDict

def getSPEDataList(speFile):
    myCounter=0
    aCoef,bCoef,cCoef=[0.0,0.0,0.0]
    myXvals=[]
    myYvals=[]
    calBool=False

    for line in open(speFile):
        if is_float(line):
            myCounter+=1
            myYvals.append(float(line))
            myXvals.append(myCounter)
        if line.find("$ENER_FIT") != -1:
            calBool=True
            continue
        if calBool:
            #The next line should have calibration data
            calStringData=line
            myValueArray=parseCalData(calStringData)
            print("myValueArray = ", myValueArray)
            aCoef,bCoef,cCoef=myValueArray
            #Assuming E=bCoef*bin+aCoef, as I understood aCoef is
            #always zero (I'm reading it anyway) and I don't know
            #what's cCoef for.
            calBool=False

    #Creating calibrated in Energy bins
    if bCoef != 0:
        eBins=np.array([bCoef*xVal+bCoef for xVal in myXvals])
        return [eBins,myYvals]
    else:
        print("No calibration info, weird. Using normal bins.")
        return [myXvals,myYvals]

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

def getListFromMCA(mcaFilename):
    mcaList=[]
    str2init = "<<DATA>>"
    str2end = "<<END>>"
    strCal = "<<CALIBRATION>>"
    strIgn = "LABEL"
    strCalEnd = "<<"
    appendBool = False

    calBool = False

    x4cal=[]
    y4cal=[]

    for line in open(mcaFilename):
        if line.find(strCal) != -1:
            calBool = True
            continue

        if line.find(str2init) != -1:
            appendBool = True
            calBool = False
            continue

        if calBool:
            if line.find(strIgn) != -1:
                continue

            if line.find(strCalEnd) != -1:
                calBool = False
            x4cal.append(float(line.split()[0]))
            y4cal.append(float(line.split()[1]))

        if line.find(str2end) != -1:
            appendBool = False
            continue

        if appendBool :
            mcaList.append(float(line))

    if len(x4cal) > 1:
        print("Entered the calibration part")
        print(x4cal,y4cal)
        a,b=getTentParams(x4cal,y4cal)
        print(a,b)
        popt,pcov = curve_fit(myLine,x4cal, y4cal, p0=[a,b])
        a,b=popt
        print(a,b)
        #Do the calibration etc
        xCalibrated = [a*ch+b for ch in range(len(mcaList))]
        totalList = [xCalibrated, mcaList]
    else:
        totalList=[range(len(mcaList)),mcaList]

    return totalList

def getListFromGammaVision(gvFilename):
    gvList=[]
    str2init = "SPECTRUM"
    appendBool = False
    for line in open(gvFilename):
        if line.find(str2init) != -1:
            appendBool = True
        if appendBool:
            lineList=line.split()
            if len(lineList) == 5:
                gvList +=[float(e) for e in lineList[1:]]
    totalList=[range(len(gvList)),gvList]
    return totalList

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
        lowXVal,uppXVal=infoDict[e]

        print(getIdxRangeVals(myDataList,lowXVal,uppXVal))
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

        # return gilmoreDict
    return gilmoreDict

def doFittingStuff(infoDict,myDataList):
    fittingDict={}
    if infoDict == {}: #minor optimization
        return fittingDict
    for e in infoDict:
        xMin,xMax=infoDict[e]
        mean=(xMin+xMax)*0.5
        print("calculated mean = ",mean)

        # mean=1460.68
        print("xMin,xMax = ",xMin,xMax)
        minIdx,maxIdx=getIdxRangeVals(myDataList,\
                                      xMin,xMax)
        xVals=myDataList[0]
        print("minIdx,maxIdx = ",minIdx,maxIdx)
        print("xVals[minIdx],xVals[maxIdx] = ",\
              xVals[minIdx],xVals[maxIdx])
        sigma=1.0 #need to automate this!!
        # a=150
        yVals=myDataList[1]
        a=max(yVals[minIdx:maxIdx])
        print("a = ",a)
        c=(yVals[minIdx]+yVals[maxIdx])/2
        print("c= ",c)
        #need to handle cases where fit fails
        try:
            popt,pcov = curve_fit(gaus,myDataList[0],\
                                  myDataList[1],\
                                  p0=[a,mean,sigma,c])
        except:
            print("Fit failed for %s" %(e))
            fittingDict[e]=[None,None,None,None,None,None]
            continue

        print("popt,pcov = ",popt,pcov)
        a,mean,sigma,c=popt
        print("a,mean,sigma,c = ",a,mean,sigma,c)
        myIntegral=a*sigma*sqrt(2*pi)
        fittingDict[e]=[a,mean,sigma,c,minIdx,maxIdx]
        print("myIntegral = ", myIntegral)
        # return fittingDict
    return fittingDict

def main(args):
    functionDict = {
            "SPE": getSPEDataList,
            "mca": getListFromMCA,
            "Txt": getListFromGammaVision
            }
    infoDict={}
    #Here put the command line argument
    print("The number of arguments is ", len(args))
    if len(args) == 1:
        print("usage: %s file.extension [-c data4fits.info]"\
              %(basename(args[0])))
        print("Valid extensions are:")
        for ext in functionDict:
            print("\t\t%s" %(ext))
        return 1

    myFilename = args[1]
    print("myFilename=",myFilename)
    myExtension = myFilename.split(".")[-1]

    print(myExtension)

    if len(args) == 4:
        print("There are 4 arguments")
        print(args)
        if args[2] != '-c':
            print("error: second argument should be -c")
            return False
        if not os.path.isfile(args[3]):
            print("error: %s does not exist" %(args[3]))
            return False
        infoDict=getDictFromInfoFile(args[3])
        print("infoDict = ")
        print(infoDict)

    # myDataList=getSPEDataList(args[1])
    # myDataList=getListFromMCA(args[1])
    #myDataList=getListFromGammaVision(args[1])
    print("myExtension = ",myExtension)
    myDataList = functionDict[myExtension](args[1])
    plt.plot(myDataList[0],myDataList[1])

    print("")
    print("Entering fittingDict part")
    fittingDict=doFittingStuff(infoDict,myDataList)
    for e in fittingDict:
        a,mean,sigma,c,minIdx,maxIdx=fittingDict[e]
        if a == None:
            continue
        myFWHM=fwhm(sigma)
        print("FWHM= ",myFWHM)
        xVals=myDataList[0][minIdx:maxIdx]
        plt.plot(xVals,gaus(xVals,a,mean,sigma,c),\
                 'r:',label=e)
        plt.annotate(e, xy=[mean,a])

    gilmoreDict=doGilmoreStuff(infoDict,myDataList)

    #erase this part?
    # plt.hist(myArr, bins=16384)
    # plt.bar(np.arange(len(li)),li)
    # plt.yscale('log', nonposy='clip')

    plt.show()

if __name__ == "__main__":
    main(sys.argv)
