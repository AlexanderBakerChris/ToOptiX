'''The following methods are extra methods for selecting elements
   or nodes

'''



# Abaqus and calculix inputfile example
# *Material
# * Node
# 1, 2.33, 1.23, 0.13
# 2, 1.23, 2.00, 0.52
# ...
# *Element, Type = C3D8R
#. 1, 2, 4, 23, 25, 26, 27, 9, 11
#. 21, 24, 14, 232, 251, 246, 217, 19, 13
# ...

def materialSettings(solverFile):
    '''The following method reads an a file and extracts the nodes
     and elements

    O: Dictonary: With all nodes and their position
    O: Dictonary: With all elements and their node IDs
    '''
    solverFile.write("*Material, name = Aluminium \n")
    solverFile.write("*Density \n")
    solverFile.write("2.7E-09 \n")
    solverFile.write("*Elastic \n")
    solverFile.write("70000, 0.33 \n")

class Material:

    def __init__(self):
        self.name = "Aluminium"
        self.pRatio = 0.33
        self.eModul = 70000
        self.density = 2.7E-09
        self.conduc = 274

    def set_eModul(self, newEModul):
        self.eModul = newEModul
    def set_density(self, newDensity):
        self.density = newDensity
    def set_pRatio(self, newPRatio):
        self.pRatio = newPRatio
    def set_name(self, newName):
        self.name = newName
    def set_conduc(self, newConduc):
        self.conduc = newConduc

    def get_eModul(self):
        return self.eModul
    def get_density(self):
        return self.density
    def get_pRatio(self):
        return self.pRatio
    def get_name(self):
        return self.name
    def get_conduc(self):
        return self.conduc

    def writeCCXAbaqus(self, solverFile):
        '''The following method reads an a file and extracts
        the nodes and elements
        '''
        solverFile.write("*Material, name = "+str(self.name) + " \n")
        solverFile.write("*Density \n")
        solverFile.write(str(self.density) + " \n")
        solverFile.write("*Elastic \n")
        solverFile.write(str(self.eModul) +", "+ str(self.pRatio) + "\n")
        solverFile.write("*Conductivity \n")
        solverFile.write(str(self.conduc) +"\n")


