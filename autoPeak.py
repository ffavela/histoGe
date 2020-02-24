import sys
#import os.path
#from os.path import basename
#import re
import pandas as pd #para imprimir en forma de tabla
from matplotlib import pyplot as plt
#import numpy as np
#from scipy.optimize import curve_fit
#from scipy import asarray as ar,exp
import math
#import time
#import signal
#import keyboard

# mainPath=sys.path[0] # sources dir
from myLibs.parsers import functionDict, getDictFromSPE, getDictFromMCA, getDictFromGammaVision,isValidSpecFile
#from myLibs.gilmoreStats import *
#from myLibs.fitting import *
#from myLibs.autoPeakFunk import *
#from myLibs.QueryDB import *
from myLibs.plotting import simplePlot
from myLibs.miscellaneus import getRebinedList
from scipy.signal import savgol_filter

def isFloat(myStr):
    try:
        float(myStr)
    except ValueError:
        return False
    return True

def getMyFileDict(myArg):  #check if is a valid 
    myFileDict={}
    myFileDict['specFiles']=[]
    
    #tmpOpt=''
    for i in range(len(myArg)):
        e=myArg[i]
        # if e.endswith('.Txt') or e.endswith('.SPE') or e.endswith('.mca'):
        if isValidSpecFile(e):
            myFileDict['specFiles'].append(e)

        if e.endswith('.info'):
            print("\n Error: The argument is an Info File. \n --autoPeak option needs an spectrum file to generates the ranges\n")
       
    return myFileDict

def peakRangeFinder(theList):
    energy,counts=theList
    maxIdx=len(energy)
    sg = savgol_filter(counts, 5, 1)

    indRange=[]

    data = [0]*len(counts)
    filtered = [0]*len(counts)
    std = [0]*len(counts)
    sub = [0]*len(counts)

    # peakheight=[]
    # peakindex=[]

    overT=False

    start=0
    end=0

    i=0

    #Maybe implement some ranges criteria here...
    for i in range(0,len(counts),1):
        data[i]=float(counts[i])
        filtered[i]=float(sg[i])
        sub[i] = data[i] - filtered[i]
        if filtered[i] > 0:
            std[i] = math.sqrt(filtered[i])
        else:
            std[i] = 0
        if sub[i] > 3*std[i]  and not overT:
            # peakheight.append(data[i])
            start=i
            overT = True
        elif sub[i] < 3*std[i] and overT:
            overT = False
            end = i-1
            # ind.append((start+end)//2)

            #making sure the rebining doesn't affect
            #negatively the start the range
            if start != 0:
                start-=1
            if end < maxIdx:
                end+=1
            indRange.append([start,end])

    return indRange

def autoPeakFun(Command):
    
    #print('\n\n'+ str(Command) +'\n\n')

    Commands=Command
    noCalFlag = False
    logFlag = False

    List = Command.copy()
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
    if '--rebin' in List:
        rebinFlag = True
        List.remove('--rebin')
        rebinNum = None
        for Arg in List:
            try:
                rebinNum = int(Arg)
                break
            except:
                continue
        if rebinNum == None:
            return 120

    else:
        rebinFlag = False


    myFileDict=getMyFileDict(Commands)
    
    myFilename=myFileDict['specFiles'][0]
              
    if len(myFileDict['specFiles']) > 1:
       
        print(' Error: to many files to do autopeak\n')

    elif not myFilename.endswith('.info'):       
       
        myExtension = myFilename.split(".")[-1] #verifies the file extention
        mySpecialDict = functionDict[myExtension](myFilename,True) #fill de dictionary
                                                                   #from data file
        
        if '--rebin' in Commands:
            
            if isinstance(rebinNum, int) == False:
                rebinNum=5
                print("There was no rebin integer detected, the default rebin value used was 5")
                

            if "theRebinedList" not in mySpecialDict:
                mySpecialDict["theRebinedList"]=getRebinedList(mySpecialDict["theList"],rebinNum)
                myDataList = mySpecialDict["theRebinedList"]
                
                idxPairL = peakRangeFinder(myDataList)
                energyArr = myDataList[0]
                Ranges=[]
                for idxR in idxPairL:
                    start,end = idxR
                    iEner = energyArr[start]
                    fEner = energyArr[end]
                    Ranges.append([iEner,fEner])
                
        else:
            print("There was no rebin option detected, the rebin option is --rebin")
            myDataList = mySpecialDict["theList"]
                
            idxPairL = peakRangeFinder(myDataList)
            energyArr = myDataList[0]
            Ranges=[]
            for idxR in idxPairL:
                start,end = idxR
                iEner = energyArr[start]
                fEner = energyArr[end]
                Ranges.append([iEner,fEner])
                      
        myInfofile=open( myFilename+'.info','w')
        pd.set_option('display.max_rows', len(Ranges))
        df = pd.DataFrame(list(Ranges),columns=['start','end'])
        myInfofile.write(df.to_string())
        myInfofile.close()

        print('\n'+myFilename+'.info was created\n')

        PlotTitle='Peaks in '+ myFilename.split('/')[-1]

        simplePlot(myDataList,logFlag,noCalFlag,myFilename,True,PlotTitle)
        
        # plt.plot(myDatalist[0],myDatalist[1]) #plot the spectrum
        # plt.show()
        
        return 0