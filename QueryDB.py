import sqlite3

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
        IsotopesDict = {element:Isotopes}
        return IsotopesDict 

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

def Energy2Dict(Isotopes):
    EnergyDict = {}
    for Energy in Isotopes:
        EnergyDict[Energy[-1]] = (Energy[1])
    return EnergyDict

conexion = sqlite3.connect('RadioactiveIsotopes.db')
cursor = conexion.cursor()

#cursor.execute("SELECT * FROM Isotopes WHERE Energy >= 1000 and Energy <= 1400 and Element = '60Co' ORDER BY ENERGY DESC" )
#cursor.execute("SELECT * FROM Isotopes WHERE Element='60Co' ORDER BY Energy DESC")
#Isotopes = cursor.fetchall()

#Isotopes = EnergyRange(conexion,46.1,46.3,None,'DESC')
#EnergyDict = Energy2Dict(Isotopes)
Isotopes = LookForElement(conexion,'60Co',order = 'ASC')
#Isotopes = LookForElement(conexion,'210Pb',Field = None,order = 'ASC')
#for row in Isotopes['60Co']:
for row in Isotopes:
    print(row)

conexion.close()



