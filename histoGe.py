#!/usr/bin/python3

import sys
#import os.path
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
from myLibs.parsers import CommandParser,MainOptD
#from myLibs.gilmoreStats import *
#from myLibs.fitting import *
#from myLibs.autoPeakFunk import *
#from myLibs.QueryDB import *
#from myLibs.plotting import *
from autoPeak import autoPeakFun
from Help import helpFun
from shortHelp import shortHelpFun
from query import QueryFun
from test import TestFun
from isotope import isotopeFun
from Sum import SumFun
from rank import rankFun
from Sub import SubFun
from energy import energyFun
from stats import statsFun
from noOption import noOption

def main(argv): 
    Commands = CommandParser(argv)
    Command = Commands[0]
    if Command == 'shorthelp':
        exitcode = helpFun(argv,['.Txt','.SPA','.mca','.info'],extBool=False)
        return exitcode
        
    elif Command[0] in MainOptD['help']:
        exitcode = helpFun(argv,['.Txt','.SPA','.mca','.info'],extBool=True)  
        return exitcode
        
    elif Command[0] in MainOptD['autoPeak']:
        exitcode = autoPeakFun(Command)
        return exitcode
        
    elif Command[0] in MainOptD['query']:
        exitcode = QueryFun(Command)
        return exitcode
        
    elif Command[0] in MainOptD['test']:
        exitcode = TestFun()
        return exitcode
        
    elif Command[0] in MainOptD['isotope']:
        exitcode = isotopeFun(Command)
        return exitcode
        
    elif Command[0] in MainOptD['sum']:
        exitcode = SumFun(Command)
        return exitcode
        
    elif Command[0] in MainOptD['rank']:
        exitcode = rankFun(Command)
        return exitcode
        
    elif Command[0] in MainOptD['sub']:
        exitcode = SubFun(Command)
        return exitcode
        
    elif Command[0] in MainOptD['stats']:
        exitcode = statsFun(Command)
        return exitcode
        
    elif Command[0] in MainOptD['energy']:
        exitcode = energyFun(Command)
        return exitcode
    else:
        exitcode = noOption(Command)
        return exitcode

if __name__ == "__main__":
    argv = sys.argv
    exitcode = main(argv)
    exit(code=exitcode)








