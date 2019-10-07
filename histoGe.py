#!/usr/bin/python3

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
from myLibs.autoPeakFunk import *

accOpts=['-h', '--help','-c',\
         '-r','--ROI','-n','--dump',\
         '--noPlot','--netArea',\
         '--grossInt','--bkgd',\
         '--extBkInt','--gSigma',\
         '--extSigma','--noCal',\
         '--autoPeak','--log',\
         '--noBkgd']

def isValidSpecFile(strVal):
    if strVal.endswith('.Txt') or\
       strVal.endswith('.SPE') or\
       strVal.endswith('.mca'):
        return True
    return False

def isDataFile(strVal):
    if isValidSpecFile(strVal) or\
       strVal.endswith('.info'):
        return True
    return False

def getMyOptDict(myArgs):
    myOptDict={}
    myOptDict['specFiles']=[]
    myOptDict['infoFiles']=[]

    tmpOpt=''
    for i in range(len(myArgs)):
        e=myArgs[i]
        if e[0] == '-' and not isFloat(e): #only changes if new option
                                           #is found negative numbers
                                           #are not options
            myOptDict[e]=[]
            tmpOpt=e
            continue #Just skipping the option

        if tmpOpt == '-r':
            #There should be only one argument in -r. If there are
            #more (hence the '-r' not in myOptDict) then they are
            #taken as specFiles.

            myOptDict[tmpOpt].append(i) #only 1 should be appended, we
                                        #avoid them getting this into
                                        #the specFiles entry
            continue

        # if e.endswith('.Txt') or e.endswith('.SPE') or e.endswith('.mca'):
        if isValidSpecFile(e):
            myOptDict['specFiles'].append(i)

        if e.endswith('.info'):
            myOptDict['infoFiles'].append(i)
            #leaving the tmpOpt conditional after this one for now

        if tmpOpt != '':
            if tmpOpt != '--dump':
                myOptDict[tmpOpt].append(i)
            else:
                if not isDataFile(e):
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

def printHelp(argv, functionDict, extBool=False):
    # print("%s [-h|--help]\n" %(basename(argv[0])))
    # print("%s file0.fits [file1.fits ...] #displays fits file info\n" %(basename(argv[0])))

    print("usage:\t%s -h #for extended help"\
          %(basename(argv[0])))
    print("\t%s [options] file.extension"\
          %(basename(argv[0])))
    print("\t%s --dump [number] file.extension"\
          %(basename(argv[0])))
    print("\t%s file1.extension [file2.extension ...] #multifile plot"\
          %(basename(argv[0])))
    print("\t%s file.extension --autoPeak" %(basename(argv[0])))
    if extBool:
        print("")
        print("If no options are provided then it simply plots the file.")
        print("\noptions:")
        print("\t-c:\tNeeds an .info file as argument.")
        print("\t\tit uses the defined ranges for getting")
        print("\t\trelevant statistics.\n")
        print("\t-r:\tNeeds a spectrum file as argument.\n")
        print("Extra options:\n")
        print("\t--noCal:\tWill not use any calibration info.")
        print("\t\t\tMight mess with your ranges (used with -c).\n")
        print("Extra options 2 (-c is required), Gilmore Stats:\n")
        print("\t--netArea:\tCalculates net area.\n")
        print("\t--grossInt:\tCalculates gross integral.\n")
        print("\t\t\taccount surrounding bins (5 by default)")
        print("\t\t\tbefore and after the region of interest.\n")
        print("\t--extBkIn:\tCalculates integral taking into\n")
        print("\t--gSigma:\tCalculates Sigma using Gilmore's")
        print("\t\t\tmethod.\n")
        print("\t--extSigma:\tSame as gSigma but using 5 bins")
        print("\t\t\tbefore and after region.\n")
        print("\t--log:\t\tprint Y axis with Log scale ")
        print("Valid extensions are:")
        for ext in functionDict:
            print("\t\t%s" %(ext))
        print("\nExamples:\n")
        print("\tThe files for the following examples can be downloaded from:\n")
        print("\tPut url here!\n")
        print("\tPut more readable names for the files!\n")
        print("\tFor simply plotting the file:\n")
        print("\t\t$ histoGe am241_blindaje_calibracion_645.mca\n")
        print("\tFor doing peak statistics on the ranges defined\n\
        inside an info file:\n")
        print("\t\t$ histoGe am241_blindaje_calibracion_645.mca\
 -c am241_blindaje_calibracion_645.info\n")
        print("\tFor substracting the background:\n")
        print("\t\t$ histoGe am241_blindaje_calibracion_645.mca\
 -r bkgd_0_70_no_scope_3380.mca\n")
    return

def parseCalData(calStringData):
    myStrArray=calStringData.split(" ")
    myValueArray=[float(val) for val in myStrArray]
    return myValueArray

def getDictFromInfoFile(infoFileName):
    infoDict={}
    for line in open(infoFileName):
        if len(re.split('\n\s*\n',line)[0])<=1:
            continue
        if line[0] == "#":
            continue
        newList=line.split()
        infoDict[newList[2]]=[float(val)\
                              for val in newList[0:2]]
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

        # mean=1460.68
        minIdx,maxIdx=getIdxRangeVals(myDataList,\
                                      xMin,xMax)
        xVals=myDataList[0]
        sigma=1.0 #need to automate this!!
        # a=150
        yVals=myDataList[1]
        a=max(yVals[minIdx:maxIdx])
        c=(yVals[minIdx]+yVals[maxIdx])/2
        #need to handle cases where fit fails
        try:
            popt,pcov = curve_fit(gaus,myDataList[0],\
                                  myDataList[1],\
                                  p0=[a,mean,sigma,c])
        except:
            print("Fit failed for %s" %(e))
            fittingDict[e]=[None,None,None,None,None,None,None]
            continue

        a,mean,sigma,c=popt
        myIntegral=a*sigma*sqrt(2*pi)
        myFWHM=fwhm(sigma)
        fittingDict[e]=[a,mean,sigma,c,minIdx,maxIdx,myFWHM]
        # return fittingDict
    return fittingDict

def isFloat(myStr):
    try:
        float(myStr)
    except ValueError:
        return False
    return True

def checkIfFloatVals(myList):
    for v in myList:
        if not isFloat(v):
            return False
    return True

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
        extBool=True
        if len(argv) == 1:
            extBool=False
        printHelp(argv, functionDict, extBool)
        return 1

    if not checkIfValidOpts(myOptDict, accOpts):
        return 4

    myFList=[argv[myOptDict['specFiles'][i]]\
             for i in range(len(myOptDict['specFiles']))]
    # myFilename = argv[myOptDict['specFiles'][0]]
    myFilename = myFList[0]
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
            print("error: background substraction needs the same extension as the main file. (for now)")
            return False

        if '--noCal' in myOptDict:
            print("Entered --noCal part")
            mySubsDict = functionDict[myExtension](myNewFilename,\
                                                   False)
        else:
            mySubsDict = functionDict[myExtension](myNewFilename)
        mySubsList = mySubsDict["theList"]

    if '--ROI' in myOptDict:
        #This part should use somehow the infoDict
        myROIIdxList=myOptDict['--ROI']
        if len(myROIIdxList) == 0:
            print("error: --ROI option needs arguments")
            return False
        if len(myROIIdxList) < 2:#should be == 2 but need to handle other
                              #stuff first
            print("error: --ROI needs 2 arguments")
            return False
        myROIIdxList=myROIIdxList[:2] #Just stripping any extra stuff
        floatBool=checkIfFloatVals([argv[e] for e in myROIIdxList])
        if not floatBool:
            print("error: --ROI needs all arguments to be floats")
            return False
        myROIList=[float(argv[e]) for e in myROIIdxList]
        if myROIList[0] >= myROIList[1]:
            print("error: %.1f %.1f is an invalid range" %\
                  (myROIList[0],myROIList[1]))
            return False
        print(myROIList)

        if '--netArea' in myOptDict:
            if myOptDict == {}:
                print("error: --netArea needs the -c option used")
                return 679

    if len(myFList) > 1:
        print("Doing multiplot stuff")
        specialX=None
        for e in myFList:
            print(e)
            if '--noCal' in myOptDict:
                mySpecialDict = functionDict[myExtension](e,\
                                                          False)
            else:
                mySpecialDict = functionDict[myExtension](e)

            myDataList = mySpecialDict["theList"]
            if specialX == None:
                #Will only use the x values of the first file
                #even if calibration is different.
                specialX=myDataList[0]
            plt.plot(specialX,myDataList[1],label=e)
            plt.legend(loc='best')
            #print(e)
        if '-n' not in myOptDict:
            if '--log' in myOptDict:
               plt.yscale('log')
            if '--noCal' not in myOptDict and mySpecialDict['calBoolean'] == True:
                plt.xlabel('Energies [KeV]')
            else:
                plt.xlabel('Channels')
        plt.ylabel('Counts')
        plt.title(myFilename)

        plt.show()
        return 3905
    if '--noCal' in myOptDict:
        mySpecialDict = functionDict[myExtension](myFilename,False)
    else:
        mySpecialDict = functionDict[myExtension](myFilename)
    myDataList = mySpecialDict["theList"]

    if '--dump' in myOptDict:
        dumpSize=None
        if myOptDict['--dump'] != []:
            dumpSize=int(argv[myOptDict['--dump'][0]])

        print("#chanOrE\tcounts")
        mDX,mDY = myDataList
        if dumpSize != None:
            if dumpSize >= 0:
                mDX,mDY=mDX[:dumpSize],mDY[:dumpSize]
            else:
                mDX,mDY=mDX[dumpSize:],mDY[dumpSize:]

        for xDVal,yDVal in zip(mDX,mDY):
            print("%0.4f\t%0.4f" %(xDVal,yDVal))
        return 0

    # there is an "Qt::AA_EnableHighDpiScaling" error here.
    if "--autoPeak" not in myOptDict:
        plt.plot(myDataList[0],myDataList[1],label=myFilename)

    if mySubsList: # != None
        myLen1=len(myDataList[1])
        myLen2=len(mySubsList[1])
        print("myLens = ",myLen1, myLen2)
        if myLen1 != myLen2:
            print("error: histograms do not have the same length (can't continue (for now))")
            return 667
        time1=mySpecialDict["expoTime"]
        time2=mySubsDict["expoTime"]
        tRatio=time1/time2
        rescaledList=getRescaledList(mySubsList,tRatio)
        subsTractedL=getSubstractedList(myDataList,rescaledList)
        if "--noBkgd" not in myOptDict:
            plt.plot(rescaledList[0],rescaledList[1],label="rescaledB")
        plt.plot(subsTractedL[0],subsTractedL[1],label="substracted")

    myHStr="#tags" #Header String
    myStatsD={e: [] for e in infoDict}
    if '--netArea' in myOptDict:
        myHStr+="\tnetArea"
        for e in infoDict:
            lowXVal,uppXVal=infoDict[e]
            myNetArea=gilmoreNetArea(myDataList,lowXVal,uppXVal)
            myStatsD[e].append(myNetArea)

    if '--grossInt' in myOptDict:
        myHStr+="\tgrInt"
        for e in infoDict:
            lowXVal,uppXVal=infoDict[e]
            myGrossInt=gilmoreGrossIntegral(myDataList,lowXVal,uppXVal)
            myStatsD[e].append(myGrossInt)

    if '--bkgd' in myOptDict:
        myHStr+="\tbkgd"
        for e in infoDict:
            lowXVal,uppXVal=infoDict[e]
            myBkgd=gilmoreBackground(myDataList,lowXVal,uppXVal)
            myStatsD[e].append(myBkgd)

    if  '--extBkInt' in myOptDict:
        myHStr+="\textBkInt"
        for e in infoDict:
            lowXVal,uppXVal=infoDict[e]
            myExtBk=gilmoreExtendedBkgExtensionsInt(myDataList,lowXVal,uppXVal)
            myStatsD[e].append(myExtBk)

    if  '--gSigma' in myOptDict:
        myHStr+="\tgSigma"
        for e in infoDict:
            lowXVal,uppXVal=infoDict[e]
            mygSigma=gilmoreSigma(myDataList,lowXVal,uppXVal)
            myStatsD[e].append(mygSigma)

    if  '--extSigma' in myOptDict:
        myHStr+="\textSigma"
        for e in infoDict:
            lowXVal,uppXVal=infoDict[e]
            myExtSigma=gilmoreExtendedSigma(myDataList,lowXVal,uppXVal)
            myStatsD[e].append(myExtSigma)

    if '--netArea' in myOptDict or\
       '--grossInt' in myOptDict or\
       '--bkgd' in myOptDict or\
       '--extBkInt' in myOptDict or\
       '--gSigma' in myOptDict or\
       '--extSigma' in myOptDict:
        print(myHStr)
        myFStr="%s"
        for e in myStatsD:
            myLen=len(myStatsD[e])
            break
        for i in range(myLen):
            myFStr+="\t%0.2f"
        for e in myStatsD:
            print(myFStr %tuple([e]+myStatsD[e]))
        return 0

    if '--autoPeak' in myOptDict:
        print('autoPeak option found')
        printTest()
        x = np.random.randn(100)
        x[60:81] = np.nan
        ind = detect_peaks(myDataList[1],mph=10, mpd=80, show=True)
        print(ind)
        return 0

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

    if '--noPlot' in myOptDict:
        #this option and -n are equivalent.
        myOptDict['-n']=[]

    if '-n' not in myOptDict:
        if '--log' in myOptDict:
            plt.yscale('log')
        if '--noCal' not in myOptDict and mySpecialDict['calBoolean'] == True:
            plt.xlabel('Energies [KeV]')
        else:
            plt.xlabel('Channels')


        plt.ylabel('Counts')
        plt.title(myFilename + ', exposition time = ' + str(mySpecialDict["expoTime"]))
        plt.show()

if __name__ == "__main__":
    main(sys.argv)
