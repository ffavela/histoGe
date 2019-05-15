"""A series of parser functions for different ascii files that contain
spectrum information from germanium detectors. They accept a filename
parses the data accordinly and returns a dictionary with all the
internal values (it tries) including the spectrum and the exposition
time.

"""

import numpy as np

def getDictFromSPE(speFile):
    """Parses the .SPE file format that is used in Boulby"""
    internDict = {}
    myCounter=0
    aCoef,bCoef,cCoef=[0.0,0.0,0.0]
    myXvals=[]
    myYvals=[]
    calBool=False

    appendBool=False

    str2init = "DATA"
    for line in open(speFile):
        iFound = line.find("$")
        if iFound != -1: #iFound == 0
            fFound=line.find(":")
            newEntry=line[iFound+1:fFound] #Avoiding the :
            internDict[newEntry]=[]
            print("newEntry = ", newEntry)
            continue
        internDict[newEntry].append(line)

    print("Outside the for")

    myXvals=list(range(len(internDict["DATA"][1:])))
    myYvals=[float(yVal) for yVal in internDict["DATA"][1:]]

    if "ENER_FIT" in internDict:
        print("internDict['ENER_FIT']", internDict['ENER_FIT'])
        aCoef,bCoef,cCoef=[float(e) for e in\
                           internDict['ENER_FIT'][0].split()]
        #Assuming E=bCoef*bin+aCoef, as I understood aCoef is
        #always zero (I'm reading it anyway) and I don't know
        #what's cCoef for.

    #Creating calibrated in Energy bins
    if bCoef != 0:
        eBins=np.array([bCoef*xVal+bCoef for xVal in myXvals])
        internDict["theList"]=[eBins,myYvals]
    else:
        print("No calibration info, weird. Using normal bins.")
        internDict["theList"]=[myXvals,myYvals]

    tStr="MEAS_TIM"
    if tStr in internDict:
        internDict["expoTime"]=float(internDict[tStr][0]\
                                     .split()[0])

    return internDict

def getDictFromMCA(mcaFilename):
    """Parses the .mca file format comming from either the micro mca or
the px5, the later has a BUG while parsing so a few bins are not
read. Need to FIX this!!

    """
    internDict={}
    mcaList=[]
    str2init = "<<DATA>>"
    str2end = "<<END>>"
    strCal = "<<CALIBRATION>>"
    strIgn = "LABEL"
    strCalEnd = "<<"
    strExpTime= "REAL_TIME"
    appendBool = False

    calBool = False

    x4cal=[]
    y4cal=[]


    #Ignoring errors for now
    for line in open(mcaFilename, errors='ignore'):

        if line.find(strExpTime) != -1:
            tempList = line.split("-")
            internDict["expoTime"]=float(tempList[1])
            print("expo time=",internDict["expoTime"])

        if line.find(strCal) != -1:
            calBool = True
            continue

        if line.find(str2init) != -1:
            appendBool = True
            calBool = False
            continue

        if calBool:
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
        print("Entered the calibration part")
        print(x4cal,y4cal)
        a,b=getTentParams(x4cal,y4cal)
        print(a,b)
        popt,pcov = curve_fit(myLine,x4cal, y4cal, p0=[a,b])
        a,b=popt
        print(a,b)
        #Do the calibration etc
        xCalibrated = [a*ch+b for ch in range(len(mcaList))]
        totalList = [xCalibrated, mcaList]
    else:
        totalList=[range(len(mcaList)),mcaList]

    internDict["theList"]=totalList
    return internDict

def getDictFromGammaVision(gvFilename):
    """Parses the .Txt files from gammaVision"""
    internDict = {}
    gvList=[]
    str2init = "SPECTRUM"
    appendBool = False
    print("Starting the gammaVision loop")
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
        print("internDict[\"expoTime\"] = ",internDict["expoTime"])
    return internDict

