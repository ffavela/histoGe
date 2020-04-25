#import sys
import os.path
#from os.path import basename
#import re
import pandas as pd #para imprimir en forma de tabla
from myLibs.miscellaneus import WriteOutputFileRR
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
from myLibs.miscellaneus import getIdxRangeVals
#from myLibs.gilmoreStats import *
#from myLibs.fitting import *
#from myLibs.autoPeakFunk import *
from myLibs.QueryDB import OpenDatabase, CloseDatabase, EnergyRange, halfLifeUnit, GetIntensities
#from myLibs.plotting import *

def rankFun(ListOpt):
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
#####    
    if '--op1' in List:
        op1Flag = True
        List.remove('--op1')
    else:
        op1Flag = False
#####
    if len(List) == 0:
        print("error: --energyRanges option needs an argument")
        return 0

    infoFile=List[0]
    if not os.path.isfile(infoFile):
        print("error: %s does not exist, are you in the right path?" %(infoFile))
        return 100
    if not infoFile.endswith('.info'):
        print("error: %s needs a .info extension" % (infoFile))
        return 101
    infoDict=getDictFromInfoFile(infoFile)
    minRange = infoDict['Range']['start']
    maxRange = infoDict['Range']['end']
    del infoDict['Range']

    idxPairL = []
    for DictEle in infoDict.values():
        ####
        if op1Flag:
            deltaEle = (DictEle['end']-DictEle['start'])*.1 #peak +/- % of the infoFile range
            meanEle = (DictEle['start']+DictEle['end'])/2
            DictEle['start'] = meanEle - deltaEle
            DictEle['end'] = meanEle + deltaEle
            idxPairL.append([DictEle['start'],DictEle['end']])
        else:
            idxPairL.append([DictEle['start'],DictEle['end']])
        ####
    #Energy range of the histogram
    
    DBInfoL = []
    pathfile = os.path.realpath(__file__)
    pathfile = pathfile.rstrip('rank.py')
    conexion = OpenDatabase(pathfile)

    memoLenDict={}
    isoPeakLL = []
    isoCountD = {}
    DBInfoL = []
    DBInfoDL = []
    #tMinE,tMaxE = infoDict['theList'][0],infoDict['theList'][-1]
    tMinEL = []
    tMaxEL = []
    
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
            iso = Ele[-1]
            if [iso,1,0,0] not in isoPeakL:
                isoPeakL.append([iso,1,0,Ele[10]]) #So that there is only one count of each isotope per peak
                if iso not in isoCountD: #Considering the number of entries in the energy range of the histogram
                    if iso not in memoLenDict:
                        #memoLenDict[iso]=len(EnergyRange(conexion,tMinE,tMaxE,iso))
                        memoLenDict[iso]=len(GetIntensities(conexion,tMinE,tMaxE,iso))
                    nInRange=memoLenDict[iso]
                    isoCountD[iso] = [0,nInRange,0]
                isoCountD[iso][0] += 1
        isoPeakLL.append(isoPeakL)

    for isoLL in isoPeakLL:
        for isoL in isoLL:
            iso = isoL[0]
            isoC = isoCountD[iso][0]
            isoL[1] = isoC
            isoL[2] = isoC/isoCountD[iso][1]
            isoCountD[iso][2] += isoL[-1]

        isoLL.sort(key = lambda x: x[3],reverse = True)
    
    Ranges = []
    for idxR, isoPeakL, DBInfoD in zip(idxPairL,isoPeakLL,DBInfoDL):
        iEner = idxR[0]
        fEner = idxR[1]
        Ranges.append([iEner,fEner])

        print('\nThe energy range consulted is between %.2f keV and %.2f keV.\n' % (iEner,fEner))
        Eg , Ig , Decay, Half , Parent, rank, rank2,rank3 = [],[],[],[],[],[],[],[]
        for pInfo in isoPeakL:
            iso = pInfo[0]
            Ele = DBInfoD[iso]
            Eg.append(str(Ele[1])+' ('+str(Ele[2])+')')
            Ig.append(round(Ele[3],2))#+' ('+str(Ele[4])+')') #Normalized Intensity
            Decay.append(Ele[5])
            #Half.append(str(Ele[6])+' '+Ele[7]+' ('+str(Ele[8])+')')
            x=halfLifeUnit(Ele)
            if x == 0:
                y = str(x)
            else:
                y = str('{0:.2e}'.format(x))
            Half.append(y+ ' [s] ')# + str(Ele[6]) +' ' +str(Ele[7]) + ' ('+str(Ele[8])+')')
            Parent.append(Ele[-1])
            rank.append(pInfo[1])
            rank2.append(round(pInfo[2],3))
            rank3.append(round(pInfo[-1],3))

        if allFlag:
            pd.set_option('display.max_rows', None) #imprime todas las filas
            df = pd.DataFrame(list(zip(Eg,Ig,Decay,Half,Parent,rank,rank2,rank3)),columns=['Eg [keV]','Ig (%)','Decay m','Half Life','Parent','Rank','Rank2','Rank3'])#crea  la tabla
            print(df)#.sort_values(by=['Rank2'], ascending=False))
        else:
            pd.set_option('display.max_rows', len(Ele))
            df = pd.DataFrame(list(zip(Eg,Ig,Decay,Half,Parent,rank,rank2,rank3)),columns=['Eg [keV]','Ig (%)','Decay mode','Half Life','Parent','Rank','Rank2','Rank3'])#crea  la tabla
            print(df.head(10))#.sort_values(by=['Rank2'], ascending=False)) #print('\nOnly the first 10')
            
            

        if wofFlag:
            try:
                myfilename = infoFile.strip('.info') + '_energyRanges.txt'
                WriteOutputFileRR(myfilename,df,iEner,fEner)
                print('-----------------------------------------')
                print('The file was saved as:')
                print(myfilename)
                print('-----------------------------------------')
            except IOError:
                print('ERROR: An unexpected error ocurrs. Data could not be saved.')
    
    return 0
    
