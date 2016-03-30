# -*- coding: utf-8 -*-
import numpy as np

def sort_element_by_type(eDic):
    ''' This function sotrs the element into an elementtype by counting
    '''
    eExpo = set()
    eExpoHexa = set()
    eExpoTetra = set()
    eExpoWed = set()
    for elemID in eDic:
        eExpo.add(elemID)
        if len(eDic[elemID]) == 8 or len(eDic[elemID]) == 20:
            eExpoHexa.add(elemID)
        if len(eDic[elemID]) == 6 or len(eDic[elemID]) == 15:
            eExpoWed.add(elemID)
        if len(eDic[elemID]) == 4 or len(eDic[elemID]) == 10:
            eExpoTetra.add(elemID)
    return [eExpo, eExpoHexa, eExpoTetra, eExpoWed]


class ExportInpMesh:
    '''This class exports an ccx mesh if the mesh is given

        I: String: Name of the file
        I: Dictonary: Node dic with coordinates [nodeID] : [x,y,z]
        I: Dictonary: Element with node id [elemID] : [node1, node2 ... ]

    '''

    def __init__(self, outputName, EDic):
        self.eDic = EDic
        self.eExpoHexa = set()
        self.eExpoTetra = set()
        self.eExpoWed = set()
        self.nExpo = set()
        self.fileName = outputName

    def set_output_mesh_reducte_by_density(self, xSelect, eDenDic):
        ''' Exporting of a mesh with reduced number by xSelec

        I: Double: Value which splittes the selection (higher will selected)
        I: Dictonary: Elements which should selected by Value [elemID][Value]
        '''
        for elemID in eDenDic:
            if eDenDic[elemID][0] > xSelect:
                element = self.eDic[elemID]
                eleShape = element.shape
                if eleShape == 'Hexaeder':
                    self.eExpoHexa.add(elemID)
                if eleShape == 'Wedge':
                    self.eExpoWed.add(elemID)
                if eleShape == 'Tetraeder':
                    self.eExpoTetra.add(elemID)
                nodeList = element.nodeList
                for node in nodeList:
                    self.nExpo.add(node)
        self.__export_inp_mesh__()

    def __export_element_in_inp__(self, expoFile, eSet):
        cardNameIsActive = False
        for elemID in eSet:
            element = self.eDic[elemID]
            if not cardNameIsActive:
                elemType = str(element.type)
                expoFile.write("*Element, type=" + elemType +
                               ", Elset=Eall" + elemType + " \n")
                cardNameIsActive = True
            nodeList = element.nodeList
            nodeNumber = len(nodeList)
            expoFile.write(str(elemID) + ", ")
            nodeCounter = 0
            for node in nodeList:
                nodeCounter += 1
                nID = node.ID
                if nodeNumber == nodeCounter:
                    expoFile.write(str(nID) + " \n")
                else:
                    expoFile.write(str(nID) + ", ")

    def __export_inp_mesh__(self):
        ''' The following part exportes the mesh by seperating the elements
        '''
        print ("start exporting mesh in abaqus format")
        print ("Higher element order will reduced to 1")
        print ("Elementtype is set to static types: C3D...")
        print ("The solution mesh is saved in {}".format(self.fileName))
        # Export of the nodes
        expoFile = open(self.fileName, "w")
        expoFile.write("*Node \n")
        for node in self.nExpo:
            nID = node.ID
            xP = node.x
            yP = node.y
            zP = node.z
            expoFile.write(str(nID) + ", " + str(xP) + ", " + str(yP) +
                           ", " + str(zP) + " \n")
        # Export of all hexahedral elements
        if len(self.eExpoHexa) > 0:
            self.__export_element_in_inp__(expoFile, self.eExpoHexa)
        if len(self.eExpoTetra) > 0:
            self.__export_element_in_inp__(expoFile, self.eExpoTetra)
        if len(self.eExpoWed) > 0:
            self.__export_element_in_inp__(expoFile, self.eExpoWed)
        expoFile.close()



class SurfaceTopo():
    ''' The following class is used for selecting the surface of an fe-mesh

    '''

    def __init__(self, EDic):
        self.eDic = EDic

    def get_triangle_surface_reduced(self, xSelec, eDenDic):
        ''' This method returns the faces on the surface

        I: Dictonary: Element with density value [elemID][density]
        I: Double: Value for seperating the FE-Mesh
        O: List: Triangle facelist with Nodes object [face][Node, Node, Node]
        '''
        eFace = {}
        triFaceList = []
        for elemID in self.eDic:
            element = self.eDic[elemID]
            if eDenDic[elemID][0] < xSelec:
                continue
            if element.shape == "Hexaeder":
                nL = element.nodeList
                n1 = nL[0]
                n2 = nL[1]
                n3 = nL[2]
                n4 = nL[3]
                n5 = nL[4]
                n6 = nL[5]
                n7 = nL[6]
                n8 = nL[7]
                # Face1
                f = sorted([n1.ID, n2.ID, n3.ID, n4.ID])
                try:
                    eFace[f[0], f[1], f[2], f[3]] = eFace[f[0], f[1], f[2], f[3]] + 1
                except:
                    eFace[f[0], f[1], f[2], f[3]] = 1
                # Face2
                f = sorted([n5.ID, n8.ID, n7.ID, n6.ID])
                try:
                    eFace[f[0], f[1], f[2], f[3]] = eFace[f[0], f[1], f[2], f[3]] + 1
                except:
                    eFace[f[0], f[1], f[2], f[3]] = 1
                # Face3
                f = sorted([n1.ID, n5.ID, n6.ID, n2.ID])
                try:
                    eFace[f[0], f[1], f[2], f[3]] = eFace[f[0], f[1], f[2], f[3]] + 1
                except:
                    eFace[f[0], f[1], f[2], f[3]] = 1
                # Face4
                f = sorted([n2.ID, n6.ID, n7.ID, n3.ID])
                try:
                    eFace[f[0], f[1], f[2], f[3]] = eFace[f[0], f[1], f[2], f[3]] + 1
                except:
                    eFace[f[0], f[1], f[2], f[3]] = 1
                # Face5
                f = sorted([n3.ID, n7.ID, n8.ID, n4.ID])
                try:
                    eFace[f[0], f[1], f[2], f[3]] = eFace[f[0], f[1], f[2], f[3]] + 1
                except:
                    eFace[f[0], f[1], f[2], f[3]] = 1
                # Face6
                f = sorted([n4.ID, n8.ID, n5.ID, n1.ID])
                try:
                    eFace[f[0], f[1], f[2], f[3]] = eFace[f[0], f[1], f[2], f[3]] + 1
                except:
                    eFace[f[0], f[1], f[2], f[3]] = 1
            elif element.shape == "Wedge":
                nL = element.nodeList
                n1 = nL[0]
                n2 = nL[1]
                n3 = nL[2]
                n4 = nL[3]
                n5 = nL[4]
                n6 = nL[5]
                # Face1
                f = sorted([n1.ID, n2.ID, n3.ID])
                try:
                    eFace[f[0], f[1], f[2]] = eFace[f[0], f[1], f[2]] + 1
                except:
                    eFace[f[0], f[1], f[2]] = 1
                # Face2
                f = sorted([n4.ID, n6.ID, n5.ID])
                try:
                    eFace[f[0], f[1], f[2]] = eFace[f[0], f[1], f[2]] + 1
                except:
                    eFace[f[0], f[1], f[2]] = 1
                # Face3
                f = sorted([n1.ID, n4.ID, n5.ID, n2.ID])
                try:
                    eFace[f[0], f[1], f[2], f[3]] = eFace[f[0], f[1], f[2], f[3]] + 1
                except:
                    eFace[f[0], f[1], f[2], f[3]] = 1
                # Face4
                f = sorted([n2.ID, n5.ID, n6.ID, n3.ID])
                try:
                    eFace[f[0], f[1], f[2], f[3]] = eFace[f[0], f[1], f[2], f[3]] + 1
                except:
                    eFace[f[0], f[1], f[2], f[3]] = 1
                # Face5
                f = sorted([n3.ID, n6.ID, n4.ID, n1.ID])
                try:
                    eFace[f[0], f[1], f[2], f[3]] = eFace[f[0], f[1], f[2], f[3]] + 1
                except:
                    eFace[f[0], f[1], f[2], f[3]] = 1
            elif element.shape == "Tetraeder":
                nL = element.nodeList
                n1 = nL[0]
                n2 = nL[1]
                n3 = nL[2]
                n4 = nL[3]
                # Face1
                f = sorted([n1.ID, n2.ID, n3.ID])
                try:
                    eFace[f[0], f[1], f[2]] = eFace[f[0], f[1], f[2]] + 1
                except:
                    eFace[f[0], f[1], f[2]] = 1
                # Face2
                f = sorted([n1.ID, n4.ID, n2.ID])
                try:
                    eFace[f[0], f[1], f[2]] = eFace[f[0], f[1], f[2]] + 1
                except:
                    eFace[f[0], f[1], f[2]] = 1
                # Face3
                f = sorted([n2.ID, n4.ID, n3.ID])
                try:
                    eFace[f[0], f[1], f[2]] = eFace[f[0], f[1], f[2]] + 1
                except:
                    eFace[f[0], f[1], f[2]] = 1
                # Face4
                f = sorted([n3.ID, n4.ID, n1.ID])
                try:
                    eFace[f[0], f[1], f[2]] = eFace[f[0], f[1], f[2]] + 1
                except:
                    eFace[f[0], f[1], f[2]] = 1

        for elemID in self.eDic:
            if eDenDic[elemID][0] < xSelec:
                continue
            element = self.eDic[elemID]
            if element.shape == "Hexaeder":
                nL = element.nodeList
                n1 = nL[0]
                n2 = nL[1]
                n3 = nL[2]
                n4 = nL[3]
                n5 = nL[4]
                n6 = nL[5]
                n7 = nL[6]
                n8 = nL[7]
                # Face1
                f = sorted([n1.ID, n2.ID, n3.ID, n4.ID])
                if eFace[f[0], f[1], f[2], f[3]] == 1:
                    triFaceList.append([n1, n2, n3])
                    triFaceList.append([n3, n4, n1])
                # Face2
                f = sorted([n5.ID, n8.ID, n7.ID, n6.ID])
                if eFace[f[0], f[1], f[2], f[3]] == 1:
                    triFaceList.append([n5, n8, n7])
                    triFaceList.append([n7, n6, n5])
                # Face3
                f = sorted([n1.ID, n5.ID, n6.ID, n2.ID])
                if eFace[f[0], f[1], f[2], f[3]] == 1:
                    triFaceList.append([n1, n5, n6])
                    triFaceList.append([n6, n2, n1])
                # Face4
                f = sorted([n2.ID, n6.ID, n7.ID, n3.ID])
                if eFace[f[0], f[1], f[2], f[3]] == 1:
                    triFaceList.append([n2, n6, n7])
                    triFaceList.append([n7, n3, n2])
                # Face5
                f = sorted([n3.ID, n7.ID, n8.ID, n4.ID])
                if eFace[f[0], f[1], f[2], f[3]] == 1:
                    triFaceList.append([n3, n7, n8])
                    triFaceList.append([n8, n4, n3])
                # Face6
                f = sorted([n4.ID, n8.ID, n5.ID, n1.ID])
                if eFace[f[0], f[1], f[2], f[3]] == 1:
                    triFaceList.append([n4, n8, n5])
                    triFaceList.append([n5, n1, n4])
            if element.shape == "Wedge":
                nL = element.nodeList
                n1 = nL[0]
                n2 = nL[1]
                n3 = nL[2]
                n4 = nL[3]
                n5 = nL[4]
                n6 = nL[5]
                # Face1
                f = sorted([n1.ID, n2.ID, n3.ID])
                if eFace[f[0], f[1], f[2]] == 1:
                    triFaceList.append([n1, n2, n3])
                # Face2
                f = sorted([n4.ID, n6.ID, n5.ID])
                if eFace[f[0], f[1], f[2]] == 1:
                    triFaceList.append([n4, n6, n5])
                # Face3
                f = sorted([n1.ID, n4.ID, n5.ID, n2.ID])
                if eFace[f[0], f[1], f[2], f[3]] == 1:
                    triFaceList.append([n1, n4, n5])
                    triFaceList.append([n5, n2, n1])
                # Face4
                f = sorted([n2.ID, n5.ID, n6.ID, n3.ID])
                if eFace[f[0], f[1], f[2], f[3]] == 1:
                    triFaceList.append([n2, n5, n6])
                    triFaceList.append([n6, n3, n2])
                # Face5
                f = sorted([n3.ID, n6.ID, n4.ID, n1.ID])
                if eFace[f[0], f[1], f[2], f[3]] == 1:
                    triFaceList.append([n3, n6, n4])
                    triFaceList.append([n4, n1, n3])
            if element.shape == "Tetraeder":
                nL = element.nodeList
                n1 = nL[0]
                n2 = nL[1]
                n3 = nL[2]
                n4 = nL[3]
                # Face1
                f = sorted([n1.ID, n2.ID, n3.ID])
                if eFace[f[0], f[1], f[2]] == 1:
                    triFaceList.append([n1, n2, n3])
                # Face2
                f = sorted([n1.ID, n4.ID, n2.ID])
                if eFace[f[0], f[1], f[2]] == 1:
                    triFaceList.append([n1, n4, n2])
                # Face3
                f = sorted([n2.ID, n4.ID, n3.ID])
                if eFace[f[0], f[1], f[2]] == 1:
                    triFaceList.append([n2, n4, n3])
                # Face4
                f = sorted([n3.ID, n4.ID, n1.ID])
                if eFace[f[0], f[1], f[2]] == 1:
                    triFaceList.append([n3, n4, n1])
        return triFaceList


class STLFile:

    def __init__(self, triMesh):
        self.triMesh = triMesh

    def write_stl_file(self, fileName):
        stlFile = open(fileName, "w")
        stlFile.write("solid Exported by DMST\n")
        #This part counts the used faces
        for face in self.triMesh:
                n1 = face[0]
                n2 = face[1]
                n3 = face[2]
                nVec = np.cross([n1.x, n1.y, n1.z], [n2.x, n2.y, n3.z])
                noVec = 1/(nVec[0]**2 + nVec[1]**2 + nVec[2]**2)*nVec
                stlFile.write("facet normal {} {} {} \n".format(noVec[0], noVec[1], noVec[2]))
                stlFile.write("outer loop \n")
                stlFile.write("vertex " + str(n1.x) + " " + str(n1.y) + " " + str(n1.z) + " \n")
                stlFile.write("vertex " + str(n2.x) + " " + str(n2.y) + " " + str(n2.z) + " \n")
                stlFile.write("vertex " + str(n3.x) + " " + str(n3.y) + " " + str(n3.z) + " \n")
                stlFile.write("endloop \n")
                stlFile.write("endfacet \n")
        stlFile.write("endsolid Exported by DMST \n")
        stlFile.close()



