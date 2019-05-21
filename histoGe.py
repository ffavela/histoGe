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
import re

# mainPath=sys.path[0] # sources dir
from myLibs.parsers import *
from myLibs.gilmoreStats import *
from myLibs.fitting import *

def parseCalData(calStringData):
    myStrArray=calStringData.split(" ")
    myValueArray=[float(val) for val in myStrArray]
    return myValueArray

def getDictFromInfoFile(infoFileName):
    infoDict={}
    for line in open(infoFileName):
        print(line)
        if len(re.split('\n\s*\n',line)[0])<=1:
            print("skipping empty line")
            print(line)
            continue
        if line[0] == "#":
            print("skipping comment")
            print(line)
            continue
        newList=line.split()
        infoDict[newList[2]]=[float(val)\
                              for val in newList[0:2]]
        print("newList = ")
        print(newList)
    return infoDict

def doFittingStuff(infoDict,myDataList):
    """Need 2 put this in fitting.py but for some reason fitting fails
there"""
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
            fittingDict[e]=[None,None,None,None,None,None,None]
            continue

        print("popt,pcov = ",popt,pcov)
        a,mean,sigma,c=popt
        print("a,mean,sigma,c = ",a,mean,sigma,c)
        myIntegral=a*sigma*sqrt(2*pi)
        myFWHM=fwhm(sigma)
        fittingDict[e]=[a,mean,sigma,c,minIdx,maxIdx,myFWHM]
        print("myIntegral = ", myIntegral)
        # return fittingDict
    return fittingDict

def main(args):
    #The following is adictionary that maps keys (file extensions) to
    #the proper parsing function. See parse
    functionDict = {
            "SPE": getDictFromSPE,
            "mca": getDictFromMCA,
            "Txt": getDictFromGammaVision
            }
    mySubsList = None
    infoDict={} #From the info file
    #Here put the command line argument
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
        print(args)
        if args[2] not in ['-c','-r']:
            print("error: second argument should be -c or -r")
            return False
        if not os.path.isfile(args[3]):
            print("error: %s does not exist" %(args[3]))
            return False
        if args[2] == "-c":
            infoDict=getDictFromInfoFile(args[3])
        elif args[2] == "-r":
            print("Calling the new function")
            myNewFilename = args[3]
            print("myNewFilename=",myNewFilename)
            myNewExtension = myNewFilename.split(".")[-1]
            if myExtension != myNewExtension:
                print("Error: background substraction needs the same extension as the main file. (for now)")
                return 666
            mySubsDict = functionDict[myNewExtension](args[3])
            mySubsList = mySubsDict["theList"]


        print("infoDict = ")
        print(infoDict)

    print("myExtension = ",myExtension)
    mySpecialDict = functionDict[myExtension](args[1])
    myDataList = mySpecialDict["theList"]

    myLen1=len(myDataList[1])
    plt.plot(myDataList[0],myDataList[1],label="data")

    if mySubsList: # != None
        myLen2=len(mySubsList[1])
        print("myLens = ",myLen1, myLen2)
        if myLen1 != myLen2:
            print("Error: histograms do not hace the same length (can't continue (for now))")
            return 667
        time1=mySpecialDict["expoTime"]
        time2=mySubsDict["expoTime"]
        print("times are = ", time1,time2)
        tRatio=time1/time2
        print("tRatio = ",tRatio)
        rescaledList=getRescaledList(mySubsList,tRatio)
        subsTractedL=getSubstractedList(myDataList,rescaledList)
        plt.plot(rescaledList[0],rescaledList[1],label="rescaledB")
        plt.plot(subsTractedL[0],subsTractedL[1],label="substracted")

    print("")
    print("Entering fittingDict part")
    fittingDict=doFittingStuff(infoDict,myDataList)
    for e in fittingDict:
        print("###################################################################################################################################################################################################")
        a,mean,sigma,c,minIdx,maxIdx,myFWHM=fittingDict[e]
        if a == None:
            print("Skipping failed fit")
            continue
        print("FWHM= ",myFWHM)
        xVals=myDataList[0][minIdx:maxIdx]
        plt.plot(xVals,gaus(xVals,a,mean,sigma,c),\
                 'r:',label=e)
        # plt.annotate(e, xy=[mean,a])

    print("Entering gilmore dict part")
    gilmoreDict=doGilmoreStuff(infoDict,myDataList)
    realXVals=myDataList[0]
    # yet another "for" for pretty printing
    print("tag\tnetArea\tG\tB\tsigma_A\tEBA\textSigma_A\tmyFWHMSigma_A\tmyFWHMExtSigma_A")
    for e in gilmoreDict:
        G,B,netArea,sigma_A,EBA,extSigma_A,myFWHMSigma_A,myFWHMExtSigma_A,max_index,max_value=gilmoreDict[e]
        a,mean,sigma,c,minIdx,maxIdx,myFWHM=[str(val)\
                                             for val in\
                                             fittingDict[e]]
        floatMean=fittingDict[e][1]
        if None != floatMean:
                    plt.annotate("%s,%2.1f" %(e,floatMean),\
                                 xy=[realXVals[max_index],max_value])
        else:
            plt.annotate(e, xy=[realXVals[max_index],max_value])

        # print(a,mean,sigma,c,minIdx,maxIdx,myFWHM)

        # print("%s\t%f\t%f\t%f\t%f\t%f\t%f\t%f\t%f" %(e,netArea,G,B,sigma_A,EBA,extSigma_A,myFWHMSigma_A,myFWHMExtSigma_A))

        print("%s\t%f\t%f\t%f\t%f\t%f\t%f\t%f\t%f\t%s\t%s\t%s\t%s\t%s" %(e,netArea,G,B,sigma_A,EBA,extSigma_A,myFWHMSigma_A,myFWHMExtSigma_A,a,mean,sigma,c,myFWHM))

        # print("%s\t%s\t%s\t%s\t%s" %(a,mean,sigma,c,myFWHM))
    #erase this part?
    # plt.hist(myArr, bins=16384)
    # plt.bar(np.arange(len(li)),li)
    # plt.yscale('log', nonposy='clip')
    print("exposition time = ", mySpecialDict["expoTime"])
    plt.legend(loc='best')
    plt.show()

if __name__ == "__main__":
    main(sys.argv)
