"""A series of parser functions for different ascii files that contain
spectrum information from germanium detectors. They accept a filename
parses the data accordinly and returns a dictionary with all the
internal values (it tries) including the spectrum and the exposition
time.

"""
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
from myLibs.fitting import myLine,getTentParams


MainOptD = {'help':['-h','--help'],'autoPeak':['-P','--autoPeak'],'query':['-q','--query'],'test':['-t','--test'],\
        'isotope':['-i','--isotope'],'sum':['-s','--sum'],'rank':['-R','--Rank'],'sub':['-r','--sub'],'stats':['-c','--stats'],'energy':['--energyRanges','-e']}
SubOptD = {'help':[],'autoPeak':['--rebin','--wif','--noPlot','--log','--noCal'],'query':['--all'],'test':[],'isotope':[],'sum':['--noCal','--log','--noPlot','--wof'],\
        'rank':['--wof'],'sub':['--noCal','--log','--noPlot','--wof','--rebin'],'stats':['--wof','--noPlot','--noCal','--log'],'energy':['--all','--wof']}
    #NumArgD = {'help':[0],'autoPeak':[1],'query':[1],'test':[0],'isotope':[2],'sum':['--noCal','noPlot','wof'],\
    #    'rank':['--noCal','noPlot','wof'],'sub':['--noCal','noPlot','wof'],'stats':[],'energy':[]}


def isValidSpecFile(strVal):
    if strVal.endswith('.Txt') or\
       strVal.endswith('.SPE') or\
       strVal.endswith('.mca') or\
       strVal.endswith('.info'):
        return True
    return False

def getDictFromSPE(speFile,calFlag=True):
    """Parses the .SPE file format that is used in Boulby"""
    internDict = {}
    myCounter=0
    aCoef,bCoef,cCoef=[0.0,0.0,0.0]
    myXvals=[]
    myYvals=[]
    calBool=False
    internDict['calBoolean']=False
    appendBool=False

    str2init = "DATA"
    for line in open(speFile):
        iFound = line.find("$")
        if iFound != -1: #iFound == 0
            fFound=line.find(":")
            newEntry=line[iFound+1:fFound] #Avoiding the :
            internDict[newEntry]=[]
            continue
        internDict[newEntry].append(line)

    myXvals=list(range(len(internDict["DATA"][1:])))
    myYvals=[float(yVal) for yVal in internDict["DATA"][1:]]

    if "ENER_FIT" in internDict and calFlag:
        aCoef,bCoef,cCoef=[float(e) for e in\
                           internDict['ENER_FIT'][0].split()]
        #Assuming E=bCoef*bin+aCoef, as I understood aCoef is
        #always zero (I'm reading it anyway) and I don't know
        #what's cCoef for.

    #Creating calibrated in Energy bins
    if bCoef != 0:
        eBins=np.array([bCoef*xVal+bCoef for xVal in myXvals])
        internDict["theList"]=[eBins,myYvals]
        internDict['calBoolean']=True
    else:
        print("No calibration info, weird. Using normal bins.")
        internDict["theList"]=[myXvals,myYvals]

    tStr="MEAS_TIM"
    if tStr in internDict:
        internDict["expoTime"]=float(internDict[tStr][0]\
                                     .split()[0])

    return internDict

def getDictFromMCA(mcaFilename,calFlag=True):
    #"""Parses the .mca file format comming from either the micro mca or the px5."""
    internDict={}
    mcaList=[]
    str2init = "<<DATA>>"
    str2end = "<<END>>"
    strCal = "<<CALIBRATION>>"
    strIgn = "LABEL"
    strCalEnd = "<<"
    strExpTime= "REAL_TIME"
    appendBool = False
    internDict['calBoolean']=False
    calBool = False

    x4cal=[]
    y4cal=[]

    #Ignoring errors for now, however bins are not skipped
    for line in open(mcaFilename, errors='ignore'):
        if line.find(strExpTime) != -1:
            tempList = line.split("-")
            internDict["expoTime"]=float(tempList[1])

        if line.find(strCal) != -1:
            calBool = True
            continue

        if line.find(str2init) != -1:
            appendBool = True
            calBool = False
            continue

        if calBool and calFlag:
            if line.find(strIgn) != -1:
                continue

            if line.find(strCalEnd) != -1:
                calBool = False
            x4cal.append(float(line.split()[0]))
            y4cal.append(float(line.split()[1]))

        if line.find(str2end) != -1:
            appendBool = False
            break #stopping here for now


        if appendBool :
            mcaList.append(float(line))

    if len(x4cal) > 1:
        a,b=getTentParams(x4cal,y4cal)
        popt,pcov = curve_fit(myLine,x4cal, y4cal, p0=[a,b])
        a,b=popt
        #Do the calibration etc
        xCalibrated = [a*ch+b for ch in range(len(mcaList))]
        totalList = [xCalibrated, mcaList]
        internDict['calBoolean']=True
    else:
        totalList=[range(len(mcaList)),mcaList]

    internDict["theList"]=totalList
    return internDict

def getDictFromGammaVision(gvFilename, calFlag=True):
    """Parses the .Txt files from gammaVision"""
    internDict = {}
    gvList=[]
    str2init = "SPECTRUM"
    appendBool = False
    internDict['calBoolean']=False
    for line in open(gvFilename):
        if not appendBool:
            semicolonI = line.find(":")
            if semicolonI != -1:
                newKey=line[:semicolonI]
                newVal=line[semicolonI+1:]
                internDict[newKey]=newVal.strip()
        if line.find(str2init) != -1:
            appendBool = True
        if appendBool:
            lineList=line.split()
            if len(lineList) == 5:
                gvList +=[float(e) for e in lineList[1:]]
    totalList=[range(len(gvList)),gvList]
    internDict["theList"]=totalList
    tStr="Real Time"
    if tStr in internDict:
        internDict["expoTime"]=float(internDict[tStr])
    return internDict

def CommandParser(lista):
    argvcp = lista.copy()
    argvcp.pop(0)
    FileList = []
    InstList = []
    NumList = []
    NameList = []
    if len(argvcp) != 0:
        for MainOpt in MainOptD:
            
            for arg in argvcp:
                if arg in MainOptD[MainOpt]:
                    InstList.append([arg])
                    for arg2 in argvcp:
                        if arg2 in SubOptD[MainOpt]:
                            InstList[-1].append(arg2)
                        elif isValidSpecFile(arg2):
                            FileList.append(arg2)
                        else:
                            try:
                                float(arg)
                                NumList.append(arg2)
                            except ValueError:
                                if arg2[0] != '-':
                                    NameList.append(arg2)

        if len(InstList) > 0:
            InstList[-1].extend(FileList)
            InstList[-1].extend(NumList)
            InstList[-1].extend(NameList)
        else:
            InstList = [argvcp.copy()]
    else:
        return ['shorthelp'] 

    return InstList

def getDictFromInfoFile(infoFileName):
    infoDict={}
    newTable=pd.read_table(infoFileName, delim_whitespace=True, index_col=0)
    infoDict=newTable.to_dict('index')
    return infoDict


functionDict = {"SPE": getDictFromSPE,"mca": getDictFromMCA,"Txt": getDictFromGammaVision,"info":getDictFromInfoFile}