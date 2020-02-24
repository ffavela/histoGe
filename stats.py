#import sys
import os.path
#from os.path import basename
#import re
import pandas as pd #para imprimir en forma de tabla
from matplotlib import pyplot as plt
#import numpy as np
#from scipy.optimize import curve_fit
#from scipy import asarray as ar,exp
#from math import sqrt, pi
#import time
#import signal
#import keyboard

# mainPath=sys.path[0] # sources dir
#from myLibs.parsers import getDictFromInfoFile,getDictFromMCA,getDictFromSPE,getDictFromGammaVision,functionDict,isValidSpecFile
#from myLibs.fitting import doFittingStuff,gaus
#from myLibs.gilmoreStats import doGilmoreStuff,doOutputFile
#from myLibs.miscellaneus import complexPlot
#from myLibs.autoPeakFunk import *
#from myLibs.QueryDB import *
#from myLibs.plotting import *

from myLibs.parsers import getDictFromInfoFile,getDictFromMCA,getDictFromSPE,getDictFromGammaVision,functionDict,isValidSpecFile
from myLibs.fitting import doFittingStuff,gaus
from myLibs.gilmoreStats import doGilmoreStuff,doOutputFile
from myLibs.plotting import complexPlot

def statsFun(ListOpt):
    List = ListOpt.copy()
    List.pop(0)
    if '--noCal' in List:
        noCalFlag = True
        List.remove('--noCal')
    else:
        noCalFlag = False

    if '--noPlot' in List:
        noPlotFlag = True
        List.remove('--noPlot')
    else:
        noPlotFlag = False
    
    if '--wof' in List:
        wofFlag = True
        List.remove('--wof')
    else:
        wofFlag = False
    
    if '--log' in List:
        logFlag = True
        List.remove('--log')
    else:
        logFlag = False

    #infoFile=List[0]
    
    for arg in List:
        if isValidSpecFile(arg):
            if arg.endswith('.info'):
                infoFile = arg
            else:
                FileName = arg
    
    try:
        if isValidSpecFile(FileName):
            FileExt = FileName.split('.')[-1]
    except:
        print('ERROR: Unexpected error. Not a valid file used.')
        return 110

    if not os.path.isfile(infoFile):
        print("ERROR: %s does not exist, are you in the right path?" %(infoFile))
        return 111
    if not infoFile.endswith('.info'):
        print("ERROR: %s needs a .info extension" % (infoFile))
        return 112   
    
    infoDict=getDictFromInfoFile(infoFile)

    if noCalFlag:
        FileDict = functionDict[FileExt](FileName,False)
    else:
        FileDict = functionDict[FileExt](FileName)
        
    myDataList = FileDict['theList']

    print("")
    print("Gilmore statistics\n[variables in counts]")
    fittingDict=doFittingStuff(infoDict,myDataList)
    gaussData4Print=[]
    #fig, ax = plt.subplots()
    for e in fittingDict:
        #a,mean,sigma,c,minIdx,maxIdx,myFWHM=fittingDict[e]
        a,mean,sigma,c=fittingDict[e][:-3]
        if a == None:
            print("Skipping failed fit")
            continue
        gaussData4Print.append([e,a,mean,sigma,c])
        
        #plt.annotate(e, xy=[mean,a])
    myGaussRows=['#tags','a','mean','sigma','c']
    pd.set_option('display.max_rows', None)
    dfG = pd.DataFrame(gaussData4Print, columns = myGaussRows)

    gilmoreDict=doGilmoreStuff(infoDict,myDataList)
    data4print=[]
    for e in gilmoreDict:
        gL=gilmoreDict[e]
        data4print.append(gL[0:6])
    realXVals=myDataList[0]

    myHStr4=['Tags','NetArea','Area+ExtBkgd','GrossInt','Background','Sigma_A']
    pd.set_option('display.max_rows', len(data4print))#imprime todas las filas
    df = pd.DataFrame([data for data in data4print], columns = myHStr4)
    print(df)
    print('\nGauss Parameters')
    print(dfG)
    #keyboard.press_and_release('\n')
    if wofFlag:
        doOutputFile(FileName,df,dfG)

    count = 0
    AnnotateArg = []
    idxPairL = []
    for e in gilmoreDict:
        #tag,netArea,G,B,sigma_A,EBA,extSigma_A,myFWHMSigma_A,myFWHMExtSigma_A,max_index,max_value=gilmoreDict[e]
        a,mean,sigma,c,_,_=[str(val) for val in fittingDict[e][:-1]]
        #a,mean,sigma,c,minIdx,maxIdx=[str(val) for val in fittingDict[e][:-1]]
        max_index = gilmoreDict[e][-2]
        max_value = gilmoreDict[e][-1]
        floatMean=fittingDict[e][1]
        idxPairL.append([infoDict[e]['start'],infoDict[e]['end']])
        AnnotateArg.append(["%s,%2.1f"%(e,floatMean),[realXVals[max_index],max_value]])
        count += 1
        #if None != floatMean:
        #    plt.annotate("%s,%2.1f" %(e,floatMean),xy=[realXVals[max_index],max_value])
        #else:
        #    plt.annotate(e, xy=[realXVals[max_index],max_value])
    #erase this part?
    # plt.hist(myArr, bins=16384)
    # plt.bar(np.arange(len(li)),li)
    # plt.yscale('log', nonposy='clip')
    #print("exposure time = ", FileDict["expoTime"])
    
    complexPlot(FileDict,idxPairL,fittingDict,AnnotateArg,logFlag=logFlag,noCalFlag=noCalFlag,Show=not(noPlotFlag),FitCurve=True)

    return 0