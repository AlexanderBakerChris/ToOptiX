# -*- coding: utf-8 -*-

class NodeElemSet:
    '''This Class is used for defining elementsets

    '''
    def __init__(self, elementDic, nodeDic={}):
        self.nDic = nodeDic
        self.eDic = elementDic
        self.nAll = []

    def element_set_write_in_file(self, solverFile, elementList, name):

        '''The following method reads an a file and extracts the nodes
         and elements

        O: Dictonary: With all nodes and their position
        O: Dictonary: With all elements and their node IDs
        '''
        writeReturnIsActive = False
        elemLineCounter = 1
        solverFile.write("*ELSET, ELSET = " + name + " \n")
        for elemID in elementList:
            writeReturnIsActive = False
            solverFile.write(str(elemID)+ ",")
            if elemLineCounter == 8:
                writeReturnIsActive = True
                elemLineCounter = 0
            if writeReturnIsActive:
                solverFile.write("\n")
            elemLineCounter += 1
        if not writeReturnIsActive:
            solverFile.write("\n")

    def get_element_list_first_loop(self):
        elementList = []
        for elemID in self.eDic:
            elementList.append(elemID)
        return elementList


    def get_nodes_between_planes(self, minPos, maxPos, normVecType, nSet=[]):
        nodesBetweenPlanes = []
        if not nSet:
            self.__set_all_nodes()
            nSet.extend(self.nAll)
        for node in nSet:
            if normVecType == "x":
                xPosNode = self.nDic[node][0]
                if xPosNode < maxPos and xPosNode > minPos:
                    nodesBetweenPlanes.append(node)
            if normVecType == "y":
                yPosNode = self.nDic[node][1]
                if yPosNode < maxPos and yPosNode > minPos:
                    nodesBetweenPlanes.append(node)
            if normVecType == "z":
                zPosNode = self.nDic[node][2]
                if (zPosNode <= maxPos) and (zPosNode >= minPos):
                    nodesBetweenPlanes.append(node)
        return nodesBetweenPlanes

    def __set_all_nodes(self):

        for node in self.nDic:
            self.nAll.append(node)
