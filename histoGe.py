#!/usr/bin/python3

import sys
import os.path
from os.path import basename
import re
import pandas as pd #para imprimir en forma de tabla
from matplotlib import pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from scipy import asarray as ar,exp
from math import sqrt, pi
import time



# mainPath=sys.path[0] # sources dir
from myLibs.parsers import *
from myLibs.gilmoreStats import *
from myLibs.fitting import *
from myLibs.autoPeakFunk import *
from myLibs.QueryDB import *
from myLibs.plotting import *

accOpts=['-h', '--help','-c',\
         '-r','--ROI','-n','--dump',\
         '--noPlot','--netArea',\
         '--grossInt','--bkgd',\
         '--extBkInt','--gSigma',\
         '--extSigma','--noCal',\
         '--autoPeak','--log',\
         '--noBkgd','--rebin',\
         '-q','--query',\
         '-i','--isotope',\
         '--testing',\
         '--noRank',\
         '--noQuery', '--all']

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

    if '--query' in myOptDict:
        myOptDict['-q']=myOptDict['--query']

    if '--isotope' in myOptDict:
        myOptDict['-i'] = myOptDict['--isotope']

    return myOptDict

def checkIfValidOpts(myOptDict, accOpts):
    if '-q' in myOptDict:
        return True

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
    print("\t%s (-q|--query) iEner fEner #DB handling"\
          %(basename(argv[0])))
    print("\t%s (-i|--isotope) IsotopeName #DB handling"\
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
        print("\t--rebin:\tNeeds a positive integer for")
        print("\t\tgrouping the contents of consecutive bins")
        print("\t\ttogether.\n")
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
        print("\t--query:\tQuery the database RadioactiveIsoptopes.db using a range of energies.")
        print("\t--isotope:\tLook for that isotope in the database.")
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

def checkQOption(myOptDict,argv):
    if '-q' not in myOptDict:
        print("this is a programming error, -q should be defined!")
        return False
    myList=[argv[i] for i in myOptDict["-q"]]
    if not checkIfFloatVals(myList):
        print("error: query values should be floats")
        return False

    if len(myList) != 2:
        print("error: query option needs exactly 2 values")
        return False

    iEner=float(myList[0])
    fEner=float(myList[1])

    if iEner > fEner:
        print("error: initial value has to be lower than final")
        return False

    return True

def checkIOption(myOptDict,argv):
    if '-i' not in myOptDict:
        print("this is a programming error, -q should be defined!")
        return False
    myList=[argv[i] for i in myOptDict["-i"]]

    if len(myList) != 1:
        print("error: isotope option needs exactly 1 value")
        return False

    return True

def checkRebinOpt(myOptDict,argv):
    if '--rebin' not in myOptDict:
        print("error: this function should not have been called, this is a\
programming error.")
        return False

    if len(myOptDict['--rebin']) != 1:
        print('error: --rebin option needs exactly one argument')
        return False

    rebinStr=argv[myOptDict['--rebin'][0]]
    if not rebinStr.isdigit():
        print("error: --rebin argument has to be a non-negative integer.")
        return False

    if int(rebinStr) == 0:
        print("error: rebin value can't be zero!")
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
    if '--testing' in myOptDict:
        print('inside Testing')
        plotCos()
        return 666

    if len(argv) == 1 or '-h' in myOptDict:
        extBool=True
        if len(argv) == 1:
            extBool=False
        printHelp(argv, functionDict, extBool)
        return 1

    if '-i' in myOptDict:
        if not checkIOption(myOptDict,argv):
            print("there were errors in the query")
            return False

        pathfile = os.path.realpath(__file__)
        pathfile = pathfile.strip('histoGe.py')

        try:
            conexion = OpenDatabase(pathfile)
            element = argv[myOptDict['-i'][0]]
            Isotope = LookForElement(conexion,element,order = 'ASC')
        except:
            print('ERROR: Database cannot be read. Please, be sure that database is in the folder myDatabase.')

        if len(Isotope) == 0:
            print('\nThe isotope consulted is ' + element)
            print('The query did not give any result.')
        else:
            Eg , Ig , Decay, Half , Parent = [],[],[],[],[]
            for Ele in Isotope:
                Eg.append(str(Ele[1])+' ('+str(Ele[2])+')')
                #DEg.append(str(Ele[2]))
                Ig.append(str(Ele[3])+' ('+str(Ele[4])+')')
                #DIg.append(str(Ele[4]))
                Decay.append(Ele[5])
                Half.append(str(Ele[6]) +' ' +str(Ele[7]) + ' ('+str(Ele[8])+')')
                #Half.append(str(Ele[6])+' '+Ele[7]+' ('+str(Ele[8])+')')
                #DHalf.append(str(Ele[8]))
                Parent.append(Ele[10])
            pd.set_option('display.max_rows', None)#imprime todas las filas
            df = pd.DataFrame(list(zip(Eg,Ig,Decay,Half,Parent)),columns=['Eg [keV]','Ig (%)','Decay mode','Half Life','Parent'])#crea  la tabla
            print(df) #imprime la tabla


        CloseDatabase(conexion)

        return True

    if not checkIfValidOpts(myOptDict, accOpts):
        return 4

    if '-q' in myOptDict:
        if not checkQOption(myOptDict,argv):
            print("there were errors in the query")
            return False

        pathfile = os.path.realpath(__file__)
        pathfile = pathfile.strip('histoGe.py')
        conexion = OpenDatabase(pathfile)
        try:
            iEner=float(argv[myOptDict['-q'][0]])
            fEner=float(argv[myOptDict['-q'][1]])
        except ValueError:
            print('ERROR: Argument cannot be converted to float')
            return 10
        if iEner > fEner:
            iEnerAux = iEner
            iEner = fEner
            fEner = iEnerAux
            del iEnerAux

        DBInfo = EnergyRange(conexion,iEner,fEner)
        if len(DBInfo) == 0:
            print('\nThe energy range consulted is %.2f keV to %.2f keV.\n' % (iEner,fEner))
            print('No results were found.')
        else:
            print('\nThe energy range consulted is %.2f keV to %.2f keV.\n' % (iEner,fEner))
            Eg , Ig , Decay, Half , Parent = [],[],[],[],[]
            for Ele in DBInfo:
                Eg.append(str(Ele[1])+' ('+str(Ele[2])+')')
                #DEg.append(str(Ele[2]))
                Ig.append(str(Ele[3])+' ('+str(Ele[4])+')')
                #DIg.append(str(Ele[4]))
                Decay.append(Ele[5])
                Half.append(str(Ele[6]) +' ' +str(Ele[7]) + ' ('+str(Ele[8])+')')
                #Half.append(str(Ele[6])+' '+Ele[7]+' ('+str(Ele[8])+')')
                #DHalf.append(str(Ele[8]))
                Parent.append(Ele[10])
            pd.set_option('display.max_rows', 30)#imprime todas las filas
            df = pd.DataFrame(list(zip(Eg,Ig,Decay,Half,Parent)),columns=['Eg [keV]','Ig (%)','Decay mode','Half Life','Parent'])#crea  la tabla
            print(df) #imprime la tabla

        CloseDatabase(conexion)
        return True

    myFList=[argv[myOptDict['specFiles'][i]]\
             for i in range(len(myOptDict['specFiles']))]
    # myFilename = argv[myOptDict['specFiles'][0]]
    myFilename = myFList[0]
    myExtension = myFilename.split(".")[-1]

    if '--rebin' in myOptDict:
        if not checkRebinOpt(myOptDict,argv):
            print("error: correct the error and retry running")
            return False
        # else:
        #     print("passed all the --rebin tests. Stopping here for now")
        #     return True

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
        if '--rebin' in myOptDict:
            rebInt=int(argv[myOptDict['--rebin'][0]])
            if "theRebinedList" not in mySubsList:
                mySubsDict["theRebinedList"]=getRebinedList(mySubsDict["theList"],rebInt)
                mySubsList = mySubsList["theRebinedList"]

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
            if '--rebin' in myOptDict:
                rebInt=int(argv[myOptDict['--rebin'][0]])
                if "theRebinedList" not in mySpecialDict:
                    mySpecialDict["theRebinedList"]=getRebinedList(mySpecialDict["theList"],rebInt)
                    myDataList = mySpecialDict["theRebinedList"]

            if specialX is None:
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
        # pid = os.fork()
        # if pid == 0:
        #     time.sleep(0.1)
        #     plt.show()
        plt.show()
        return 3905

    if '--noCal' in myOptDict:
        mySpecialDict = functionDict[myExtension](myFilename,False)
    else:
        mySpecialDict = functionDict[myExtension](myFilename)
    myDataList = mySpecialDict["theList"]
    if '--rebin' in myOptDict:
        rebInt=int(argv[myOptDict['--rebin'][0]])
        if "theRebinedList" not in mySpecialDict:
            mySpecialDict["theRebinedList"]=getRebinedList(mySpecialDict["theList"],rebInt)
            myDataList = mySpecialDict["theRebinedList"]

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
        #myPlotF(myDataList)

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
            #myPlotF(rescaledList[0],rescaledList[1],label="rescaledB")
        plt.plot(subsTractedL[0],subsTractedL[1],label="substracted")
        #myPlotF(subsTractedL[0],subsTractedL[1],label="substracted")

    myHStr="#tags" #Header String
    myHStrL=['#tags']
    myStatsD={e: [e] for e in infoDict}

    if '--netArea' in myOptDict:
        myHStr+="\tnetArea"
        myHStrL.append('netArea')
        for e in infoDict:
            lowXVal,uppXVal=infoDict[e]
            myNetArea=gilmoreNetArea(myDataList,lowXVal,uppXVal)
            myStatsD[e].append(myNetArea)

    if '--grossInt' in myOptDict:
        myHStr+="\tgrInt"
        myHStrL.append('grInt')
        for e in infoDict:
            lowXVal,uppXVal=infoDict[e]
            myGrossInt=gilmoreGrossIntegral(myDataList,lowXVal,uppXVal)
            myStatsD[e].append(myGrossInt)

    if '--bkgd' in myOptDict:
        myHStr+="\tbkgd"
        myHStrL.append('bkgd')
        for e in infoDict:
            lowXVal,uppXVal=infoDict[e]
            myBkgd=gilmoreBackground(myDataList,lowXVal,uppXVal)
            myStatsD[e].append(myBkgd)

    if  '--extBkInt' in myOptDict:
        myHStr+="\textBkInt"
        myHStrL.append('extBkInt')
        for e in infoDict:
            lowXVal,uppXVal=infoDict[e]
            myExtBk=gilmoreExtendedBkgExtensionsInt(myDataList,lowXVal,uppXVal)
            myStatsD[e].append(myExtBk)

    if  '--gSigma' in myOptDict:
        myHStr+="\tgSigma"
        myHStrL.append('gSigma')
        for e in infoDict:
            lowXVal,uppXVal=infoDict[e]
            mygSigma=gilmoreSigma(myDataList,lowXVal,uppXVal)
            myStatsD[e].append(mygSigma)

    if  '--extSigma' in myOptDict:
        myHStr+="\textSigma"
        myHStrL.append('extSigma')
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
        pd.set_option('display.max_rows', len(myStatsD))#imprime todas las filas
        df = pd.DataFrame([myStatsD[v] for v in myStatsD] , columns = myHStrL)
        print(df)
        return 0

    if '--autoPeak' in myOptDict:
        #Energy range of the histogram
        tMinE,tMaxE=myDataList[0][0],myDataList[0][-1]

        #For memoizing the database queries for the histogram energy
        #range
        memoLenDict={}
        idxPairL = peakRangeFinder(myDataList)
        ind = getSimpleIdxAve(idxPairL,myDataList)
        peakXVals=[myDataList[0][i] for i in ind]
        peakYVals=[myDataList[1][i] for i in ind]

        if '--noQuery' not in myOptDict:
            if '--noRank' not in myOptDict:
                print("#This might take a while, be patient")
            pathfile = os.path.realpath(__file__)
            pathfile = pathfile.strip('histoGe.py')
            conexion = OpenDatabase(pathfile)
            energyArr = myDataList[0]
            if '--noRank' not in myOptDict:
                isoPeakLL = []
                isoCountD = {}
                DBInfoL = []
                DBInfoDL = []
                for idxR in idxPairL:
                    start,end = idxR
                    iEner = energyArr[start]
                    fEner = energyArr[end]
                    DBInfoL.append(EnergyRange(conexion,iEner,fEner))
                    DBInfo = DBInfoL[-1]
                    DBInfoD = {}
                    for e in DBInfo:
                        DBInfoD[e[-1]] = e
                    DBInfoDL.append(DBInfoD)
                    isoPeakL = []

                    for Ele in DBInfo:
                        iso = Ele[-1]
                        if [iso,1,0] not in isoPeakL:
                            isoPeakL.append([iso,1,0])
                            #So that there is only one count of each isotope
                            #per peak
                            #if '--noRank' not in myOptDict:
                            if iso not in isoCountD:
                                #Considering the number of entries in the
                                #energy range of the histogram
                                if iso not in memoLenDict:
                                    memoLenDict[iso]=\
                                        len(EnergyRange(conexion,tMinE,tMaxE,iso))
                                nInRange=memoLenDict[iso]
                                isoCountD[iso] = [0,nInRange]
                            isoCountD[iso][0] += 1
                    isoPeakLL.append(isoPeakL)

                #if '--noRank' not in myOptDict:
                for isoLL in isoPeakLL:
                    for isoL in isoLL:
                        iso = isoL[0]
                        isoC = isoCountD[iso][0]
                        isoL[1] = isoC
                        isoL[2] = isoC/isoCountD[iso][1]

                    isoLL.sort(key = lambda x: x[2],reverse = True)

                for idxR, isoPeakL, DBInfoD in zip(idxPairL,isoPeakLL,DBInfoDL):
                    start,end = idxR
                    iEner = energyArr[start]
                    fEner = energyArr[end]
                    print('\nThe energy range consulted is between %.2f keV and %.2f keV.\n' % (iEner,fEner))
                    Eg , Ig , Decay, Half , Parent, rank, rank2 = [],[],[],[],[],[],[]
                    for pInfo in isoPeakL:
                        iso = pInfo[0]
                        Ele = DBInfoD[iso]
                        Eg.append(str(Ele[1])+' ('+str(Ele[2])+')')
                        Ig.append(str(Ele[3])+' ('+str(Ele[4])+')')
                        Decay.append(Ele[5])
                        #Half.append(str(Ele[6])+' '+Ele[7]+' ('+str(Ele[8])+')')
                        x=halfLifeUnit(Ele)
                        if x == 0:
                            y = str(x)
                        else:
                            y = str('{0:.2e}'.format(x))
                        Half.append(y+ ' [s] ')# + str(Ele[6]) +' ' +str(Ele[7]) + ' ('+str(Ele[8])+')')
                #
                        Parent.append(Ele[10])
                        rank.append(pInfo[1])
                        rank2.append(pInfo[2])

                    if '--all' not in myOptDict:
                        pd.set_option('display.max_rows', len(Ele))
                    else:
                        pd.set_option('display.max_rows', None)#imprime todas las filas

                    df = pd.DataFrame(list(zip(Eg,Ig,Decay,Half,Parent,rank,rank2)),columns=['Eg [keV]','Ig (%)','Decay mode','Half Life','Parent','Rank','Rank2'])#crea  la tabla

                    if '--all' not in myOptDict:
                        print(df.head(10)) #imprime la tabla
                    else:
                        print(df)

            else:
                DBInfoL = []
                for idxR in idxPairL:
                    start,end = idxR
                    iEner = energyArr[start]
                    fEner = energyArr[end]
                    DBInfoL.append(EnergyRange(conexion,iEner,fEner))
                    DBInfo = DBInfoL[-1]
                #for idxR, isoPeakL, DBInfoD in zip(idxPairL,isoPeakLL,DBInfoDL):
                    start,end = idxR
                    iEner = energyArr[start]
                    fEner = energyArr[end]
                    print('\nThe energy range consulted is between %.2f keV and %.2f keV.\n' % (iEner,fEner))
                    Eg , Ig , Decay, Half , Parent = [],[],[],[],[]
                    for Ele in DBInfo:
                        Eg.append(str(Ele[1])+' ('+str(Ele[2])+')')
                        Ig.append(str(Ele[3])+' ('+str(Ele[4])+')')
                        Decay.append(Ele[5])
                        Half.append(halfLifeUnit(Ele))
                        Parent.append(Ele[10])

                    if '--all' not in myOptDict:
                        pd.set_option('display.max_rows', len(Ele))
                    else:
                        pd.set_option('display.max_rows', None)#imprime todas las filas

                    df = pd.DataFrame(list(zip(Eg,Ig,Decay,Half,Parent)),columns=['Eg [keV]','Ig (%)','Decay mode','Half Life','Parent'])

                    if '--all' not in myOptDict:
                        print(df.head(10)) #imprime la tabla
                    else:
                        print(df)

            CloseDatabase(conexion)
        # print("Histogram energy range is = ",tMinE,tMaxE)
        if '--noPlot' not in myOptDict:
            if '--log' in myOptDict:
                plt.yscale('log')
            if '--noCal' not in myOptDict and mySpecialDict['calBoolean'] == True:
                plt.xlabel('Energies [KeV]')
            else:
                plt.xlabel('Channels')

            plt.plot(myDataList[0],myDataList[1],label="testing")
            plt.plot(peakXVals, peakYVals, 'ro', markersize=8)
            # pid = os.fork()
            # if pid == 0:
            #     time.sleep(0.1)
            #     plt.show()
            plt.show()
        return 0

    print("")
    print("Gilmore statistics")
    fittingDict=doFittingStuff(infoDict,myDataList)
    gaussData4Print=[]
    for e in fittingDict:
        #print("###################################################################################################################################################################################################")
        a,mean,sigma,c,minIdx,maxIdx,myFWHM=fittingDict[e]
        if a == None:
            print("Skipping failed fit")
            continue
        gaussData4Print.append([e,a,mean,sigma,c])
        #print("FWHM= ",myFWHM)
        xVals=myDataList[0][minIdx:maxIdx]
        plt.plot(xVals,gaus(xVals,a,mean,sigma,c),\
                 'r:')
        # plt.annotate(e, xy=[mean,a])
    myGaussRows=['#tags','a','mean','sigma','c']
    pd.set_option('display.max_rows', None)
    dfG = pd.DataFrame(gaussData4Print, columns = myGaussRows)

    gilmoreDict=doGilmoreStuff(infoDict,myDataList)
    data4print=[]
    for e in gilmoreDict:
        gL=gilmoreDict[e]
        data4print.append(gL[0:6])
    realXVals=myDataList[0]

    myHStr4=['#tags','NetArea[counts]','NetArea ExtBkgd','GrossInt','Background','Sigma_A']
    pd.set_option('display.max_rows', len(data4print))#imprime todas las filas
    df = pd.DataFrame([data for data in data4print], columns = myHStr4)
    print(df)
    print('\nGauss Parameters')
    print(dfG)

    for e in gilmoreDict:
        tag,netArea,G,B,sigma_A,EBA,extSigma_A,myFWHMSigma_A,myFWHMExtSigma_A,max_index,max_value=gilmoreDict[e]
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

     #   print("%s\t%f\t%f\t%f\t%f\t%f\t%f\t%f\t%f\t%s\t%s\t%s\t%s\t%s" %(e,netArea,G,B,sigma_A,EBA,extSigma_A,myFWHMSigma_A,myFWHMExtSigma_A,a,mean,sigma,c,myFWHM))

        # print("%s\t%s\t%s\t%s\t%s" %(a,mean,sigma,c,myFWHM))
    #erase this part?
    # plt.hist(myArr, bins=16384)
    # plt.bar(np.arange(len(li)),li)
    # plt.yscale('log', nonposy='clip')
    print("exposure time = ", mySpecialDict["expoTime"])
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
        plt.title(myFilename + ', exposure time = ' + str(mySpecialDict["expoTime"]))
        plt.show()
        # pid = os.fork()
        # if pid == 0:
        #     time.sleep(0.1)
        #     plt.show()

if __name__ == "__main__":
    main(sys.argv)
