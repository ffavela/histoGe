#import sys
#import os.path
from os.path import basename
#import re
#import pandas as pd #para imprimir en forma de tabla
#from matplotlib import pyplot as plt
#import numpy as np
#from scipy.optimize import curve_fit
#from scipy import asarray as ar,exp
#from math import sqrt, pi
#import time
#import signal
#import keyboard

# mainPath=sys.path[0] # sources dir
#from myLibs.parsers import *
#from myLibs.gilmoreStats import *
#from myLibs.fitting import *
#from myLibs.autoPeakFunk import *
#from myLibs.QueryDB import *
#from myLibs.plotting import *



def helpFun(argv, functionDict, extBool=False):
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
        print("\t--autoPeak:\tFind peaks in histogram and, with them,")
        print("\t\t\tmake an .info file. It should be used with rebin option.\n")
        print("\t--query:\tQuery the database RadioactiveIsoptopes.db using a range of energies.\n")
        print("\t--isotope:\tLook for that isotope in the database.")
        print("\t--Rank: Make ranking of isotopes to obtain the most probables isotopes\n")
        print("\t\t\tthat explains peaks. It needs and .info file.")
        print("\t--energyRanges: Using the .info file, it displays the isotopes that\n")
        print("\t\t\tthat can be found in the ranges of each peak.\n")
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
        print("\t--log:\t\tprint Y axis with Log scale.\n")
        print("\t--all: --Rank and --energyRanges displays all the isotopes and")
        print("\t\t\tnot only the first 10 entries.")
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
    return 0