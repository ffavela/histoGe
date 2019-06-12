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

accOpts=['-h', '--help','-c',\
         '-r']

def getMyOptDict(myArgs):
    myOptDict={}
    myOptDict['specFiles']=[]
    myOptDict['infoFiles']=[]

    tmpOpt=''
    for i in range(len(myArgs)):
        e=myArgs[i]
        if e[0] == '-': #only changes if new option is found
            myOptDict[e]=[]
            tmpOpt=e
            continue #Just skipping the option

        if tmpOpt == '-r':
            myOptDict[tmpOpt].append(i)
            # so files with extensions are unambiguosly stored here
            # and we avoid them getting into the specFiles entry
            continue

        if e.endswith('.Txt') or e.endswith('.SPE') or e.endswith('.mca'):
            myOptDict['specFiles'].append(i)

        if e.endswith('.info'):
            myOptDict['infoFiles'].append(i)
            #leaving the tmpOpt conditional after this one for now

        if tmpOpt != '':
            myOptDict[tmpOpt].append(i)

    return myOptDict

def checkIfValidOpts(myOptDict, accOpts):
    if len(myOptDict['specFiles'])==0:
        print("error: a spectrum file needs to be provided")
        return False

    for e in myOptDict:
        if e == 'specFiles' or e == 'infoFiles':
            #just ommiting these ones, they're not really options
            continue
        if e not in accOpts:
            print("error: %s is not a valid option" %(e))
            return False
    return True

def printHelp(argv, functionDict):
    # print("%s [-h|--help]\n" %(basename(argv[0])))
    # print("%s file0.fits [file1.fits ...] #displays fits file info\n" %(basename(argv[0])))
    print("usage: %s file.extension [-c data4fits.info]"\
          %(basename(argv[0])))
    print("Valid extensions are:")
    for ext in functionDict:
        print("\t\t%s" %(ext))
    return 1

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

def main(argv):
    #The following is a dictionary that maps keys (file extensions) to
    #the proper parsing function. See parse
    functionDict = {
            "SPE": getDictFromSPE,
            "mca": getDictFromMCA,
            "Txt": getDictFromGammaVision
            }
    mySubsList = None
    infoDict={} #From the info file
    #Here put the command line argument
    myOptDict=getMyOptDict(argv)
    if len(argv) == 1 or '-h' in myOptDict:
        printHelp(argv, functionDict)
        return 1


    print(myOptDict)
    if not checkIfValidOpts(myOptDict, accOpts):
        return 4

    myFilename = argv[myOptDict['specFiles'][0]]
    print("myFilename=",myFilename)
    myExtension = myFilename.split(".")[-1]

    if '-c' in myOptDict:
        if len(myOptDict['-c']) == 0:
            print("error: -c option needs an argument")
            return False
        infoFile=argv[myOptDict['-c'][0]]
        if not os.path.isfile(infoFile):
            print("error: %s does not exist, are you in the right path?"\
                  %(infoFile))
            return False
        if not infoFile.endswith('.info'):
            print("error: %s needs a .info extension" % (infoFile))
            return False
        infoDict=getDictFromInfoFile(infoFile)
    elif '-r' in myOptDict:
        if len(myOptDict['-r']) == 0:
            print("error: -r option needs an argument")
            return False
        myNewFilename = argv[myOptDict['-r'][0]]
        if not os.path.isfile(myNewFilename):
            print("error: %s does not exist, are you in the right path?"\
                  %(myNewFilename))
            return False

        if not myNewFilename.endswith(myExtension):
            print("Error: background substraction needs the same extension as the main file. (for now)")
            return False

        mySubsDict = functionDict[myExtension](myNewFilename)
        mySubsList = mySubsDict["theList"]

        print("infoDict = ")
        print(infoDict)

    print("myExtension = ",myExtension)
    mySpecialDict = functionDict[myExtension](argv[1])
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
