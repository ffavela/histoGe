from matplotlib import pyplot as plt
import numpy as np
from myLibs.miscellaneus import closest
from myLibs.fitting import gaus,emptyFittingDict

def plotCos():
    t2 = np.arange(0.0, 5.0, 0.02)
    plt.plot(t2, np.cos(2*np.pi*t2), 'r--')
    plt.show()


def myPlotF(myDataList):
    plt.plot(myDataList[0],myDataList[1])
    #plt.show()
    
def simplePlot(mySubsList,logFlag,noCalFlag,Label=None,show=False,Title=None):
    plt.plot(mySubsList[0],mySubsList[1],label=Label)
    if logFlag:
        plt.yscale('log')
    if not noCalFlag:
            plt.xlabel('Energies [KeV]')
    else:
            plt.xlabel('Channels')
    plt.ylabel('Counts')
    if show == True:
        plt.title(Title)
        plt.show()

def complexPlot(mySpecialDict,idxPairL,gausdata=None,Anotation=True,logFlag=False,noCalFlag=True,Label=None,Show=True,Title = None,Fill=True,showPeaks=True,FitCurve=True,rebinFlag=False):
    
    if rebinFlag:
        mySpecialList = []
        mySpecialList.append(list(mySpecialDict['theRebinedList'][0]))
        mySpecialList.append(list(mySpecialDict['theRebinedList'][1]))
    else:
        mySpecialList = mySpecialDict['theList']

    if mySpecialDict['calBoolean']:
        idxPairLAux = []
        for idx in idxPairL:
            idxL = []
            for idele in idx:
                idxL.append(closest(mySpecialList[0],idele))
            idxPairLAux.append(idxL)
    else:
        idxPairLAux = idxPairL
    
    if Fill:
        _, ax = plt.subplots()
        for iPV in idxPairLAux:
            if mySpecialDict['calBoolean']:
                start = mySpecialList[0].index(iPV[0])
                end = mySpecialList[0].index(iPV[1])
            else:
                start, end = iPV
            
            ax.fill_between(mySpecialList[0][start:end+1],mySpecialList[1][start:end+1],facecolor='red')
    
    if Title == None:
        Title = ''
    else:
        Title += ', '
    if Label != None:
        plt.gcf().canvas.set_window_title(Label.split('.')[0])
    plt.title(Title + 'Exposure time = ' + str(mySpecialDict["expoTime"]) + '/s')
    plt.plot(mySpecialList[0],mySpecialList[1],label=Label)
    plt.ylabel('Counts')
    if logFlag:
        plt.yscale('log')
    if not noCalFlag and mySpecialDict['calBoolean'] == True:
        plt.xlabel('Energies [KeV]')
    else:
        plt.xlabel('Channels')
    
    if gausdata == None:
        gausdata = emptyFittingDict(len(idxPairLAux))

    try:
        for iPV,gd,e in zip(idxPairLAux,gausdata.values(),gausdata.keys()):
            if mySpecialDict['calBoolean']:
                start = mySpecialList[0].index(iPV[0])
                end = mySpecialList[0].index(iPV[1])
            else:
                start, end = iPV
            xVals = mySpecialList[0][start:end+1]    
            yVals = mySpecialList[1][start:end+1]    
            NoneFlag = all([ps != None for ps in gd])
            if FitCurve == True and NoneFlag:
                xNpArray = np.array(xVals)
                GausFun = gaus(xNpArray,gd[0],gd[1],gd[2],gd[3])
                plt.plot(xNpArray,GausFun,color='green')
                peakYVals = max(GausFun)
                peakXVals = xVals[list(GausFun).index(peakYVals)]
            else:
                peakYVals = max(yVals)
                peakXVals = xVals[yVals.index(peakYVals)]
            if NoneFlag:
                floatMean = gausdata[e][1]
            else:
                floatMean = peakXVals
            if showPeaks:
                plt.plot(peakXVals, peakYVals, 'ro', markersize=8)
            if Anotation:
                plt.annotate("%s,%2.1f" %(e,floatMean),xy=[peakXVals,peakYVals])
            else:
                plt.annotate(e, xy=[peakXVals,peakYVals])
    except:
        print('ERROR: Unexpected error during plotting. ')
        return 300
        #e += 1
    
    # try:
    #     for iPV in idxPairLAux:
    #         if gausdata != None:

    #             gd = gausdata[e-1]
            
    #         if mySpecialDict['calBoolean']:
    #             start = mySpecialList[0].index(iPV[0])
    #             end = mySpecialList[0].index(iPV[1])
    #         else:
    #             start, end = iPV
    #         xVals = mySpecialList[0][start:end+1]    
    #         yVals = mySpecialList[1][start:end+1]    
    #         if FitCurve and gausdata != None:
    #             xNpArray = np.array(xVals)
    #             GausFun = gaus(xNpArray,gd[0],gd[1],gd[2],gd[3])
    #             plt.plot(xNpArray,GausFun,color='green')
    #             peakYVals = max(GausFun)
    #             peakXVals = xVals[list(GausFun).index(peakYVals)]
    #         else:
                
    #             peakYVals = max(yVals)
    #             peakXVals = xVals[yVals.index(peakYVals)]
                
                    
    #         if gausdata != None:
    #             floatMean = gausdata[e-1][1]
    #         else:
    #             floatMean = peakXVals
    #         if showPeaks:
    #             plt.plot(peakXVals, peakYVals, 'ro', markersize=8)
    #         if Anotation:
    #             plt.annotate("%s,%2.1f" %(e,floatMean),xy=[peakXVals,peakYVals])
    #         else:
    #             plt.annotate(e, xy=[peakXVals,peakYVals])
    #         e += 1
    # except:
    #             print("\n\nThe {} file is not calibrated, please use --noCal option in line command\n\n".format(Label))

    if Show:
        if Label != None:
            plt.legend(loc='best')
        plt.show()
    return 0
