from __future__ import division, print_function
import numpy as np

import numpy as np
import matplotlib.pyplot as plt
import sys
import math
from scipy import sparse
from scipy.sparse.linalg import spsolve
from scipy.signal import savgol_filter

#This still needs to be improved!!
def peakFinder(theList):
    energy,counts=theList

    sg = savgol_filter(counts, 5, 1)

    ind=[]

    data = [0]*len(counts)
    filtered = [0]*len(counts)
    std = [0]*len(counts)
    sub = [0]*len(counts)

    peakheight=[]
    peakindex=[]

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
            ind.append((start+end)//2)

    return ind
