# -*- coding: utf-8 -*-
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



class InertialCondition:

    def __init__(self):
        self.temperature = 15

    def set_temperature_all(self, newICTemperature):
        self.temperature = newICTemperature

    def get_temperature_all(self):
        return self.temperature

    def writeCCXAbaqus(self, solverFile):
        '''The following method reads an a file and extracts
        the nodes and elements
        '''
        solverFile.write("*Initial Condition, Type = Temperature \n")
        solverFile.write("Nall," + str(self.temperature) + " \n")
