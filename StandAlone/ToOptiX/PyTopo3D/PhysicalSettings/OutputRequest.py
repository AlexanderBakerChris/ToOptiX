# -*- coding: utf-8 -*-
class OutputRequest:

    def __init__(self):
        self.outputTypeElemFrd = []
        self.outputTypeElemDat = []
        self.outputTypeNodeFrd = []
        self.outputTypeNodeDat = []

    def set_output_elem_Frd(self, outputTypeList):
        for outputType in outputTypeList:
            self.outputTypeElemFrd.append(outputType)

    def set_output_elem_Dat(self, outputTypeList):
        for outputType in outputTypeList:
            self.outputTypeElemDat.append(outputType)

    def set_output_node_Dat(self, outputTypeList):
        for outputType in outputTypeList:
            self.outputTypeNodeDat.append(outputType)

    def set_output_node_Frd(self, outputTypeList):
        for outputType in outputTypeList:
            self.outputTypeNodeFrd.append(outputType)


    def get_output_elem(self):
        return self.outputTypeElem


    def get_output_node(self, outputTypeList):
        return self.outputTypeNode


    def get_temp_load(self):
        return self.tempLoad

    def output_write_in_file(self, solverFile):
        '''The following method reads an a file and extracts the nodes
         and elements

        O: Dictonary: With all nodes and their position
        O: Dictonary: With all elements and their node IDs
        '''
        # Possible Types, U, NT
        if self.outputTypeNodeFrd:
            # alternative Node Print
            solverFile.write("*Node File, NSET = Nall, FREQUENCY= 999\n")
            for outputType in self.outputTypeNodeFrd:
                solverFile.write(str(outputType) +",\n")
        if self.outputTypeNodeDat:
            # alternative Node Print
            solverFile.write("*Node Print, NSET = Nall, FREQUENCY= 999\n")
            for outputType in self.outputTypeNodeDat:
                solverFile.write(str(outputType) +",\n")
        # Possible Types, S
        if self.outputTypeElemFrd:
            # alternative El Print
            solverFile.write("*EL File,ELSET=Eall,FREQUENCY=999 \n")
            for outputType in self.outputTypeElemFrd:
                solverFile.write(str(outputType) +",\n")
        if self.outputTypeElemDat:
            solverFile.write("*EL Print,ELSET=Eall,FREQUENCY=999 \n")
            for outputType in self.outputTypeElemDat:
                solverFile.write(str(outputType) +",\n")