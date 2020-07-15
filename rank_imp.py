#import sys
import os.path
#from os.path import basename
#import re
import pandas as pd #para imprimir en forma de tabla
from myLibs.miscellaneus import WriteOutputFileRR
from math import sqrt
#from matplotlib import pyplot as plt
#import numpy as np
#from scipy.optimize import curve_fit
#from scipy import asarray as ar,exp
#from math import sqrt, pi
#import time
#import signal
#import keyboard

# mainPath=sys.path[0] # sources dir
from myLibs.parsers import getDictFromInfoFile, getMyFileDictRankAdv, functionDictAdv, findRangeInfoDict
from myLibs.miscellaneus import getIdxRangeVals, removeDuplicates
#from myLibs.gilmoreStats import *
#from myLibs.fitting import *
#from myLibs.autoPeakFunk import *
from myLibs.QueryDB import OpenDatabase, CloseDatabase, EnergyRange, halfLifeUnit, GetIntensities
from myLibs.fitting import doFittingStuff
from myLibs.gilmoreStats import doGilmoreStuff
#from myLibs.plotting import *

def rankImp(ListOpt):
    List = ListOpt.copy()
    List.pop(0)  
    i = 0 #for rank op
    rankOp = []

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
    
    if 'and' in List:
        addFlag = True
        List.remove('and')
    else:
        addFlag = False
 
    for Arg in List:
        try:
            rankOp.append(int(Arg))
            if rankOp[i] > 0 and rankOp[i] < 4:
                
                if type(rankOp[i]) == int:
                    i += 1
            
            #break
        except:
            rankOp.append(3)
            continue
    if len(List) == 0:
        print("error: --energyRanges option needs an argument")
        return 0

    infoFile=List[0]
    if not os.path.isfile(infoFile):
        print("error: %s does not exist, are you in the right path?" %(infoFile))
        return 10000
    if not infoFile.endswith('.info'):
        print("error: %s needs a .info extension" % (infoFile))
        return 10001
    infoDict=getDictFromInfoFile(infoFile)
    try:
        minRange = infoDict['Range']['start']
        maxRange = infoDict['Range']['end']
        del infoDict['Range']
    except:
        minRange, maxRange = findRangeInfoDict(infoDict)
    
    idxPairL = []
    for DictEle in infoDict.values():

        if addFlag :
            if rankOp[2] == 1:
                rankSort = 'Rank'
                
                idxPairL.append([DictEle['start'],DictEle['end']])
            
            elif rankOp[2] == 2:
                rankSort = 'Rank2'
                
                idxPairL.append([DictEle['start'],DictEle['end']])
                
            
            elif rankOp[2] == 3:
                rankSort = 'Rank3'
                
                idxPairL.append([DictEle['start'],DictEle['end']])
            
            else:
                idxPairL.append([DictEle['start'],DictEle['end']])
                print('theres n|o rank op {}, please try an option between 1 and 3'.format(rankOp))
                break
        else:
            rankSort = 'Rank3'
            
            idxPairL.append([DictEle['start'],DictEle['end']])


    DBInfoL = []
    pathfile = os.path.realpath(__file__)
    pathfile = pathfile.rstrip('rank_imp.py')
    conexion = OpenDatabase(pathfile)

    memoLenDict={}

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

    PeakNum = -1
    for idxR in idxPairL:
        PeakNum += 1
        iEner = idxR[0]
        fEner = idxR[1]
        #DBInfoL.append(EnergyRange(conexion,iEner,fEner))
        DBInfoL.append(GetIntensities(conexion,iEner,fEner))
        DBInfo = DBInfoL[-1]
        DBInfoD = {}
        for e in DBInfo: 
            #Filling dict with isotope name each isotope has only one tupple
            if e[-1] not in DBInfoD:
                DBInfoD[e[-1]] = [e]
            else:
                DBInfoD[e[-1]].append(e)
        DBInfoDL.append(DBInfoD)   
    
        for Ele in DBInfo:
            iso = Ele[-1]
            if iso not in memoLenDict:
                memoLenDict[iso]=[len(GetIntensities(conexion,tMinE,tMaxE,iso)),1,Ele[10],[PeakNum]]
                
                isoCountD[iso] = [Ele]
            else:
                memoLenDict[iso][1] += 1 
                memoLenDict[iso][2] += Ele[10]
                memoLenDict[iso][3].append(PeakNum)
                isoCountD[iso].append(Ele)

    memoLenDictKeys = memoLenDict.copy().keys()
    for Ele in memoLenDictKeys:
        if memoLenDict[Ele][0] == 0 or memoLenDict[Ele][2] == 0:
            del memoLenDict[Ele]
            del isoCountD[Ele]
            for DBInfoD in DBInfoDL:
                try:
                    del DBInfoD[Ele]
                except KeyError:
                    continue

    memoLenDictKeys = memoLenDict.keys()
    

    #DBInfoDLshort = DBInfoDL.copy()
    
    Ranges = []
    rankList = []
    for idxR, DBInfoD in zip(idxPairL,DBInfoDL):
        iEner = idxR[0]
        fEner = idxR[1]
        Ranges.append([iEner,fEner])
        Eg , Ig , Decay, Half , Parent, rank, rank2,rank3 = [],[],[],[],[],[],[],[]
        for Key in DBInfoD:
            #Ele = DBInfoD[Key]
            for Ele in DBInfoD[Key]:
                Eg.append(Ele[1])
                Ig.append(round(Ele[3],2))
                Decay.append(Ele[5])
                x=halfLifeUnit(Ele)
                if x == 0:
                    y = str(x)
                else:
                    y = str('{0:.2e}'.format(x))
                Half.append(y+ ' [s] ')# + str(Ele[6]) +' ' +str(Ele[7]) + ' ('+str(Ele[8])+')')
                Parent.append(Ele[-1])
                rank.append(memoLenDict[Ele[-1]][0])
                rank2.append(round(memoLenDict[Ele[-1]][1],3))
                rank3.append(round(memoLenDict[Ele[-1]][2],3))
#list1, list2 = (list(t) for t in zip(*sorted(zip(list1, list2))))
        # if addFlag:
        #     isoLL.sort(key = lambda x: x[rankOp[1]],reverse = True) # Main Sort of RANK HGE
        # else:
        #     if i:
        #         isoLL.sort(key = lambda x: x[rankOp[1]],reverse = True) # Main Sort of RANK HGE
        #     else:
        #         isoLL.sort(key = lambda x: x[rankOp[0]],reverse = True) # Main Sort of RANK HGE
        


        
        if addFlag:
            if rankOp[1] == 1:
                rankList = rank.copy()
                        
            elif rankOp[1] == 2:
                rankList = rank2.copy()
                
            elif rankOp[1] == 3:
                rankList = rank3.copy()
                
        else:
            if i:
                if rankOp[1] == 1:
                    rankList = rank.copy()
                            
                elif rankOp[1] == 2:
                    rankList = rank2.copy()
                    
                elif rankOp[1] == 3:
                    rankList = rank3.copy()
            else:
                if rankOp[1] == 1:
                    rankList = rank.copy()
                            
                elif rankOp[1] == 2:
                    rankList = rank2.copy()
                    
                elif rankOp[1] == 3:
                    rankList = rank3.copy()
        
        rankList,Eg,Ig,Decay,Half,Parent,rank,rank2,rank3 = (list(t) for t in zip(*sorted(zip(rankList,Eg,Ig,Decay,Half,Parent,rank,rank2,rank3),reverse=True)))

        print('\nThe energy range consulted is between %.2f keV and %.2f keV.\n' % (iEner,fEner))
        
        if allFlag:
            pd.set_option('display.max_rows', None) #imprime todas las filas
            pd.options.display.float_format = '{:,.5f}'.format
            df = pd.DataFrame(list(zip(Eg,Ig,Decay,Half,Parent,rank,rank2,rank3)),columns=['Eg [keV]','Ig (%)','Decay m','Half Life','Parent','Rank','Rank2','Rank3'])#crea  la tabla
            if addFlag:
                print(df.sort_values(by=[rankSort], ascending=False))
            else:
                print(df)#.sort_values(by=['Rank2'], ascending=False))
        else:
            pd.set_option('display.max_rows', len(Ele))
            df = pd.DataFrame(list(zip(Eg,Ig,Decay,Half,Parent,rank,rank2,rank3)),columns=['Eg [keV]','Ig (%)','Decay mode','Half Life','Parent','Rank','Rank2','Rank3'])#crea  la tabla
            if addFlag:
                print(df.head(10).sort_values(by=[rankSort], ascending=False)) #print('\nOnly the first 10')
            else:
                print(df.head(10))#.sort_values(by=[rankSort], ascending=False)) #print('\nOnly the first 10')
            

        if wofFlag:
            try:
                if rankOp[1] == 1:
                    myfilename = infoFile.strip('.info') + '_rank_B.txt'
                
                elif rankOp[1] == 2:
                    myfilename = infoFile.strip('.info') + '_rank_C.txt'
                
                elif rankOp[1] == 3:
                    myfilename = infoFile.strip('.info') + '_rank_D.txt'

                else:
                    myfilename = infoFile.strip('.info') + '_rank_D.txt'

                if allFlag:
                    if addFlag:
                        WriteOutputFileRR(myfilename,df.sort_values(by=[rankSort], ascending=False),iEner,fEner)
                    else:
                        WriteOutputFileRR(myfilename,df,iEner,fEner)
                else:
                    if addFlag:
                        WriteOutputFileRR(myfilename,df.head(10).sort_values(by=[rankSort], ascending=False),iEner,fEner)
                    else:
                        WriteOutputFileRR(myfilename,df.head(10),iEner,fEner)
                
                print('-----------------------------------------')
                print('The file was saved as:')
                print(myfilename)
                print('-----------------------------------------')        
            

            except IOError:
                print('ERROR: An unexpected error ocurrs. Data could not be saved.')
                break
    
    return 0
    
