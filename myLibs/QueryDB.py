import sqlite3
import os

def OpenDatabase(pathfile):
    dbpath = pathfile + '/myDatabase/RadioactiveIsotopes.db'
    conexion = sqlite3.connect(dbpath)
    return conexion

def EnergyRange(conexion,min,max,element = None,order = None):
    Command = 'SELECT * FROM Isotopes WHERE Energy >= ' + str(min) + ' and Energy <= ' + str(max)
    if element != None:
        Command += ' and Element = ' + "'" + element + "'" 
    
    if order == None:
        cursor = conexion.cursor()
        cursor.execute(Command)
        Isotopes = cursor.fetchall()
        return Isotopes

    elif order == 'ASC' or order == 'DESC':
        cursor = conexion.cursor()
        Command += ' ORDER BY Energy ' + order
        cursor.execute(Command)
        Isotopes = cursor.fetchall()
        return Isotopes

def LookForElement(conexion,element,Field = None,order = None):
    Command = 'SELECT * FROM Isotopes WHERE Element = ' + "'" + element + "'"
    if order == None:
        cursor = conexion.cursor()
        cursor.execute(Command)
        Isotopes = cursor.fetchall()
        return Isotopes
        #IsotopesDict = {element:Isotopes}
        #return IsotopesDict

    if (order == 'ASC' or order == 'DESC') and Field == None:
        cursor = conexion.cursor()
        Command += ' ORDER BY Energy ' + order
        cursor.execute(Command)
        Isotopes = cursor.fetchall()
        return Isotopes

    if (order == 'ASC' or order == 'DESC') and Field != None:
        cursor = conexion.cursor()
        Command += ' ORDER BY ' + "'" + Field + "'" + order
        cursor.execute(Command)
        Isotopes = cursor.fetchall()
        return Isotopes

def CloseDatabase(conexion):
    conexion.close()

def Energy2Dict(Dict,Isotope):
    pass
    
def meanLifeUnit(Ele):
    y=31536000
    d=8640
    h=3600
    m=60
    if Ele[7] == 'y':
        meanLife=Ele[6]*y
    elif Ele[7] == 'd':
        meanLife=Ele[6]*d
    elif Ele[7] == 'h':
        meanLife=Ele[6]*h
    elif Ele[7] == 'm':
        meanLife=Ele[6]*m
    elif Ele[7] == 'ms':
        meanLife=Ele[6]/1000
    else: meanLife=Ele[6]
    
    units=str(meanLife)+ ' [s] ' + str(Ele[6]) +' ' +str(Ele[7]) + ' ('+str(Ele[8])+')'
    return units 

#df = pd.DataFrame(list(zip(Eg,Ig,Decay,Half,Parent)),columns=['Eg [keV]','Ig (%)','Decay mode','Half Life','Parent'])#crea  la tabla



