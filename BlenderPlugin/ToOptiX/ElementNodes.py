# -*- coding: utf-8 -*-

__metaclass__ = type
# This class is not in use #


class GetSetAttributes():

    def __init__(self):
        pass

    def set_attributes(self, key, value):
        self._attributes[key] = value
        return

    def get_attributes(self, key):
        return self._attributes.get(key, None)


class Node_old(GetSetAttributes):

    __nodeID = None
    __x = None
    __y = None
    __z = None

    def __init__(self, **kvargs):
        self._attributes = kvargs

    def __str__(self):
        return "ID: {} x: {} y: {} z: {}".format(
                                  self._attributes.get('__nodeID', None),
                                  self._attributes.get('__x', None),
                                  self._attributes.get('__y', None),
                                  self._attributes.get('__z', None))


class Element_old(GetSetAttributes):

    # Static variables
    __elementID = None
    __nodeList = None
    __elementType = None
    __elementOrder = None

    def __init__(self, **kvargs):
        self._attributes = kvargs

    def __str__(self):
        nodeIDList = []
        nodeList = self._attributes.get('__nodeList', None)
        for node in nodeList:
            nodeIDList.append(node._attributes.get('__nodeID', None))
        return "ID: {}    ElementType: {}    Nodes: {}     Order {} ".format(
                                  self._attributes.get('__elementID', None),
                                  self._attributes.get('__elementType', None),
                                 nodeIDList,
                                 self._attributes.get('__elementOrder', None))




class Node():

    def __init__(self):
        self.ID = None
        self.x = None
        self.y = None
        self.z = None

    @property
    def ID(self):
        return self.__ID

    @ ID.setter
    def ID(self, ID):
        self.__ID = ID

    @property
    def x(self):
        return self.__x

    @ x.setter
    def x(self, x):
        self.__x = x

    @property
    def y(self):
        return self.__y

    @ y.setter
    def y(self, y):
        self.__y = y

    @property
    def z(self):
        return self.__z

    @ z.setter
    def z(self, z):
        self.__z = z




class __Element():


    def __init__(self):
        self.ID = None
        self.type = None
        self.order = None
        self.nodeList = []
        self.shape = None
        self.den = None
        self.eModul = None
        self.heatKoeff = None
        self.xc = None
        self.yc = None
        self.zc = None

    @property
    def xc(self):
        return self.__xc

    @ xc.setter
    def xc(self, xc):
        self.__xc =  xc

    @property
    def yc(self):
        return self.__yc

    @ yc.setter
    def yc(self, yc):
        self.__yc =  yc

    @property
    def zc(self):
        return self.__zc

    @ zc.setter
    def zc(self, zc):
        self.__zc =  zc

    @property
    def ID(self):
        return self.__ID

    @ ID.setter
    def ID(self, ID):
        self.__ID =  ID

    # Type of the element (thermal, mechanic)
    @property
    def type(self):
        return self.__type

    @ type.setter
    def type(self, type):
        self.__type = type
    # Order of the element
    @property
    def order(self):
        return self.__order

    @ order.setter
    def order(self, order):
        self.__order = order
    # Nodes in Element
    @property
    def nodeList(self):
        return self.__nodeList

    @ nodeList.setter
    def nodeList(self, nodeList):
        self.__nodeList = nodeList
    # Shape of the element
    @property
    def shape(self):
        return self.__shape

    @ shape.setter
    def shape(self, shape):
        self.__shape = shape

    # Density
    @property
    def den(self):
        return self.__den

    @ den.setter
    def den(self, den):
        self.__den = den

    # eModul
    @property
    def eModul(self):
        return self.__eModul

    @ eModul.setter
    def eModul(self, eModul):
        self.__eModul = eModul

    # Heat koeff
    @property
    def heatKoeff(self):
        return self.__heatKoeff

    @ heatKoeff.setter
    def heatKoeff(self, heatKoeff):
        self.__heatKoeff = heatKoeff



class TetElement(__Element):

    def __init__(self):
        self.ID = None
        self.type = None
        self.order = None
        self.nodeList = []
        self.shape = 'Tetraeder'
        self.den = None
        self.eModul = None
        self.heatKoeff = None

class WedElement(__Element):

    def __init__(self):
        self.ID = None
        self.type = None
        self.order = None
        self.nodeList = []
        self.shape = 'Wedge'
        self.den = None
        self.eModul = None
        self.heatKoeff = None

class HexElement(__Element):

    def __init__(self):
        self.ID = None
        self.type = None
        self.order = None
        self.nodeList = []
        self.shape = 'Hexaeder'
        self.den = None
        self.eModul = None
        self.heatKoeff = None

def get_element_type(line):
    nodeNumber = 0
    elementListOrder1 = ["C3D4", "C3D6", "C3D8",
                        "DC3D4", "DC3D6", "DC3D8",
                        "DCC3D4", "DCC3D6", "DCC3D8"]
    elementListOrder2 = ["C3D10", "C3D15", "C3D20",
                        "DC3D10", "DC3D15", "DC3D20",
                        "DCC3D10", "DCC3D15", "DCC3D20"]
    for elemType in elementListOrder1:
        if elemType in line:
            nodeNumber = int(elemType[-1])
            return elemType, nodeNumber, 1
    for elemType in elementListOrder2:
        if elemType in line:
            nodeNumber = int(elemType[-2] + elemType[-1])
            return elemType, nodeNumber, 2
    return 0, 0, 0


def get_center_of_elem(nodeList):

    xc = 0
    yc = 0
    zc = 0
    for node in nodeList:
        xc = node.x + xc
        yc = node.y + yc
        zc = node.z + zc
    n = len(nodeList)
    return [xc / n, yc / n, zc / n]




def import_elements_nodes_as_dic(FilePath):
    '''The following method reads an a file and extracts the nodes
     and elements

    O: Dictonary: With all nodes and their position
    O: Dictonary: With all elements and their node IDs
    '''
    nodeDic = {}  # nodeID, xPos, yPos, zPos
    elemDic = {}  # elemID, NodeID1, NodeID2 ... NodeID8
    NodeReadingIsActivated = False
    ElementReadingIsActivated = False
    NodeLineReadingIsActivated = False
    inputFile = open(FilePath, "r")
    for line in inputFile:
        words = line[0:-1].split(",")
        firstWord = words[0]
        if len(firstWord) == 0:
            continue
        firstLetter = firstWord[0]
        if (firstWord[0:5] == "*Node"):
            NodeReadingIsActivated = True
            ElementReadingIsActivated = False
            continue
        elif (firstWord[0:8] == "*Element"):
            ElementReadingIsActivated = True
            elemType, nodeInEleType, eleOrder = get_element_type(line)
            print ("Elementtype {} is used".format(elemType))
            NodeReadingIsActivated = False
            continue
        elif (firstLetter == "*"):
            NodeReadingIsActivated = False
            ElementReadingIsActivated = False
            continue
        if ElementReadingIsActivated:
            if not (NodeLineReadingIsActivated):
                nodeList = []
            counter = 0
            for word in words:
                counter += 1
                if counter == 1 and not(NodeLineReadingIsActivated):
                    elemID = int(word)
                else:
                    nodeList.append(nodeDic[int(word)])
            if not(nodeInEleType == len(nodeList)):
                NodeLineReadingIsActivated = True
                continue
            NodeLineReadingIsActivated = False
            nodeNumber = len(nodeList)
            if nodeNumber == 4 or nodeNumber == 10:
                elem = TetElement()
            elif  nodeNumber == 6 or nodeNumber == 15:
                elem = WedElement()
            elif nodeNumber == 8 or nodeNumber == 20:
                elem = HexElement()
            elem.ID = elemID
            elem.nodeList = nodeList
            centerElem = get_center_of_elem(nodeList)
            elem.xc = centerElem[0]
            elem.yc = centerElem[1]
            elem.zc = centerElem[2]
            elem.type = elemType
            elem.order = eleOrder
            elemDic[elemID] = elem
            continue
        if NodeReadingIsActivated and len(words) >= 4:
            nID = int(firstWord)
            nPosX = float(words[1])
            nPosY = float(words[2])
            nPosZ = float(words[3])
            node = Node()
            node.x = nPosX
            node.y = nPosY
            node.z = nPosZ
            node.ID = nID
            nodeDic[nID] = node
            continue
    inputFile.close()
    print ("Used nodes: " + str(len(nodeDic)))
    print ("Used elements: " + str(len(elemDic)))
    return nodeDic, elemDic


def elem_node_write_in_file(self, solverFile):
    '''The following method reads an a file and extracts the nodes
     and elements

    O: Dictonary: With all nodes and their position
    O: Dictonary: With all elements and their node IDs
    '''
    solverFile.write("*Node, NSET=Nall \n")
    for NodeID in self.nDic:
        xPos = self.nDic[NodeID][0]
        yPos = self.nDic[NodeID][1]
        zPos = self.nDic[NodeID][2]
        solverFile.write(str(NodeID) + ", " + str(xPos) + ", " +
                         str(yPos) + ", " + str(zPos) + "\n")
    solverFile.write("*Element, TYPE = C3D8, ELSET=Eall\n")
    for ElementID in self.eDic:
        solverFile.write(str(ElementID))
        for NodeID in self.eDic[ElementID]:
            solverFile.write(", " + str(NodeID))
        solverFile.write("\n")







# Old class object
class NodesElement:

    def __init__(self):
        self.nDic = {}
        self.eDic = {}

    def get_node_dic(self):
        return self.nDic

    def get_elem_dic(self):
        return self.eDic

    def set_nDic(self, newNodeDic):
        self.nDic = newNodeDic

    def set_eDic(self, newElemDic):
        self.eDic = newElemDic

    def add_node(self, ID, positionList):
        self.nDic[ID] = positionList

    def add_elem(self, ID, nodeList):
        self.eDic[ID] = nodeList



    def set_nDic_empty(self):
        self.nDic = {}

    def set_eDic_empty(self):
        self.eDic = {}

    def add_element_node_from_file(self, inputFileName, Type="Calculix"):
        '''The following method reads an a file and extracts the nodes
         and elements

        O: Dictonary: With all nodes and their position
        O: Dictonary: With all elements and their node IDs
        '''
        nodeDic = {}  # nodeID, xPos, yPos, zPos
        elemDic = {}  # elemID, NodeID1, NodeID2 ... NodeID8
        # Activation parameter for start saving elements and nodes
        if Type == "Calculix" or Type == "Abaqus":
            NodeReadingIsActivated = False
            ElementReadingIsActivated = False
            inputFile = open(inputFileName, "r")
            for line in inputFile:
                words = line[0:-1].split(",")
                firstWord = words[0]
                if len(firstWord) == 0:
                    continue
                firstLetter = firstWord[0]
                if (firstWord[0:5] == "*Node"):
                    NodeReadingIsActivated = True
                    ElementReadingIsActivated = False
                    continue
                elif (firstWord == "*Element"):
                    ElementReadingIsActivated = True
                    NodeReadingIsActivated = False
                    continue
                elif (firstLetter == "*"):
                    NodeReadingIsActivated = False
                    ElementReadingIsActivated = False
                    continue
                if ElementReadingIsActivated:
                    nodeList = []
                    counter = 0
                    for word in words:
                        counter += 1
                        if counter == 1:
                            elemID = int(word)
                        else:
                            nodeList.append(int(word))
                    elemDic[elemID] = nodeList
                    continue
                if NodeReadingIsActivated and len(words) >= 4:
                    nodeID = int(firstWord)
                    nodePosX = float(words[1])
                    nodePosY = float(words[2])
                    nodePosZ = float(words[3])
                    nodeDic[nodeID] = [nodePosX, nodePosY, nodePosZ]
                    continue
            inputFile.close()
            for nodeID in nodeDic:
                self.nDic[nodeID] = nodeDic[nodeID]
            for elemID in elemDic:
                self.eDic[elemID] = elemDic[elemID]