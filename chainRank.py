#import sys
import os.path
#from os.path import basename
#import re
import pandas as pd #para imprimir en forma de tabla
#from matplotlib import pyplot as plt
#import numpy as np
#from scipy.optimize import curve_fit
#from scipy import asarray as ar,exp
#from math import sqrt, pi
#import time
#import signal
#import keyboard

# mainPath=sys.path[0] # sources dir
from myLibs.parsers import getDictFromInfoFile
#from myLibs.miscellaneus import getIdxRangeVals, WriteOutputFileRR
#from myLibs.gilmoreStats import *
#from myLibs.fitting import *
#from myLibs.autoPeakFunk import *
from myLibs.QueryDB import OpenDatabase, CloseDatabase, GetChainAndChild, GetMainChain, EnergyRange, halfLifeUnit, GetIntensities, chaintoList
#from myLibs.plotting import *

def ChainRankFun(ListOpt):
    List = ListOpt.copy()
    List.pop(0)  
    
    if '--wof' in List:
        wofFlag = True
        List.remove('--wof')
    else:
        wofFlag = False

    if '--all' in List:
        allFlag = True
        List.remove('--all')
    else:
        allFlag = False

    if len(List) == 0:
        print("error: --chainRank option needs an argument")
        return 3500
    
    infoFile=List[0]
    if not os.path.isfile(infoFile):
        print("error: %s does not exist, are you in the right path?" %(infoFile))
        return 3501
    if not infoFile.endswith('.info'):
        print("error: %s needs a .info extension" % (infoFile))
        return 3502

    infoDict=getDictFromInfoFile(infoFile)
    minRange = infoDict['Range']['start']
    maxRange = infoDict['Range']['end']
    #del infoDict['Range']

    pathfile = os.path.realpath(__file__)
    pathfile = pathfile.strip('chainRank.py')
    conexion = OpenDatabase(pathfile)

    ChainDict = {}

    memoLenDict={}
    isoPeakLL = []
    isoCountD = {}
    DBInfoL = []
    DBInfoDL = []
    #tMinE,tMaxE = infoDict['theList'][0],infoDict['theList'][-1]
    tMinEL = []
    tMaxEL = []
    idxPairL = []

    for DictEle in infoDict.values():
        idxPairL.append([DictEle['start'],DictEle['end']])

    if True:
        for infoPair in infoDict.values():
            tMinEL.append(infoPair['start'])
            tMaxEL.append(infoPair['end'])
        tMinE = min(tMinEL)
        tMaxE = max(tMaxEL)
    else:
        tMinE = minRange
        tMaxE = maxRange

    for idxR in idxPairL:
        iEner = idxR[0]
        fEner = idxR[1]
        #DBInfoL.append(EnergyRange(conexion,iEner,fEner))
        DBInfoL.append(GetIntensities(conexion,iEner,fEner))
        DBInfo = DBInfoL[-1]
        DBInfoD = {}
        for e in DBInfo: 
            #Filling dict with isotope name each isotope has only one tupple
            DBInfoD[e[-1]] = e      
        DBInfoDL.append(DBInfoD)   
        isoPeakL = []
        for Ele in DBInfo:
            MainChainIso, _ = GetChainAndChild(conexion,Ele[-1])
            if MainChainIso not in ChainDict and MainChainIso is not None:
                ChainDict[MainChainIso] = chaintoList(GetMainChain(conexion,MainChainIso)[0])

            pass

        print('Hola Mundo')

        
        #     iso = Ele[-1]
        #     if [iso,1,0,0] not in isoPeakL:
        #         isoPeakL.append([iso,1,0,Ele[10]]) #So that there is only one count of each isotope per peak
        #         if iso not in isoCountD: #Considering the number of entries in the energy range of the histogram
        #             if iso not in memoLenDict:
        #                 #memoLenDict[iso]=len(EnergyRange(conexion,tMinE,tMaxE,iso))
        #                 memoLenDict[iso]=len(GetIntensities(conexion,tMinE,tMaxE,iso))
        #             nInRange=memoLenDict[iso]
        #             isoCountD[iso] = [0,nInRange,0]
        #         isoCountD[iso][0] += 1
        # isoPeakLL.append(isoPeakL)










    # for Isotope in List:
    #     MainChainIso,Child = GetChainAndChild(conexion,Isotope)
    #     if MainChainIso == None or Child == None:
        
    #         print('Isotope: ' + Isotope + ' -- Parent: ' + 'None' + ' --Child: ' + 'None' +  '\n')
    #         print('There is not enough information in the database or the isotope ' + Isotope + ' do not have Child or parents isotopes. \n')
        
    #     else:
        
    #         MainChain = GetMainChain(conexion,MainChainIso)
    #         if '+' in MainChain:
    #             AuxStr = MainChain.split('+')[1]
    #             Parentiso = AuxStr.split('#')[0]
    #         else:
    #             Parentiso = MainChain[0].split('#')[0]

    #         print('Isotope: ' + Isotope + ' -- Parent: ' + Parentiso + ' --Child: ' + Child + '\n')
        
    CloseDatabase(conexion)
    return 0