# -*- coding: utf-8 -*-




class Load:

    def __init__(self):
        self.tempLoad= {}
        self.forceLoad = {}
        self.dispLoad = {}
    def set_temp_load_konst_value(self, nSet, value):
        for node in nSet:
            self.tempLoad[node] = value
    def set_temp_load_list_value(self, nSet, value):
        # The commented method is faster
        #listValueCount = 0
        if len(nSet) != len(value):
            print("Dimension of nodes and listvalues must match")
            print("No listtemperatur is used")
            return
        for node in nSet:
            listValueCount = nSet.index(node)
            self.tempLoad[node] = value[listValueCount]
        #   self.tempLoad[node] = value[listValueCount]
        #    listValueCount += 1

    def set_force_load(self, nSet, value, direction="x"):
        for node in nSet:
            self.forceLoad[node] = [value, direction]

    def get_force_load(self):
        return self.forceLoad
    def get_temp_load(self):
        return self.tempLoad

    def temp_load_write_in_file(self, solverFile):
        '''The following method reads an a file and extracts the nodes
         and elements

        O: Dictonary: With all nodes and their position
        O: Dictonary: With all elements and their node IDs
        '''
        solverFile.write("*Temperature \n")
        for node in self.tempLoad:
            solverFile.write(str(node) + ", " + \
                             str(self.tempLoad[node]) + "\n")

    def force_load_write_in_file(self, solverFile):
        solverFile.write("*Cload \n")
        for node in self.forceLoad:
            direction = self.forceLoad[node][1]
            value = self.forceLoad[node][0]
            if direction == "x":
                solverFile.write(str(node) + ", 1," + str(value) + "\n")
            if direction == "y":
                solverFile.write(str(node) + ", 2," + str(value) + "\n")
            if direction == "z":
                solverFile.write(str(node) + ", 3," + str(value) + "\n")