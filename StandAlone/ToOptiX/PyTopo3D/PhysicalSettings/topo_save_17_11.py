'''The following program uses any fem-program with an
inputdeck for topology optimisation

There are several classes which are needed for the initializing of
the nodes and elements. If you want to add a fem-program which does
not exist, just implement an ascci-file. And change the output ascci.
The whole optimisation process works with several dictonarys in
which are nodes and elements are saved.

Source code:
             Name: Denk, Martin
             Date: 10.2015
             Accronym: DMST
'''
# Global lib
import sys
import os
import numpy as np
# Local lib
from PhysicalSettings import *
#from DefineInput import *


def delete_empty_list_elements(inputList):
    '''The main function calls the differen topo optimizations

    I: List: Inputlist with empty elements
    O: List: List without empty elements
    '''
    listWithoutEmptyElem = []
    for listElem in inputList:
        if listElem != "":
            listWithoutEmptyElem.append(listElem)
    return listWithoutEmptyElem


def define_material_sets(solverFile, matSets, penal, youngModule):
    '''The following part creates the material settings.

    I: IO-txtobject: File which should solved
    I: Integer: Number of materialsets
    I: Double: Penalty factor
    I: Double: elasticity module
    O: List: Materiallist with all settings
    '''
    matSec = []
    matCount = 1
    while matCount <= matSets:
        Aluminium = Material()
        Aluminium.set_eModul(youngModule * (float(matCount) /
                                            float(matSets)) ** penal)
        Aluminium.set_pRatio(0.33)
        Aluminium.set_name("TopoMat_" + str(matCount))
        Aluminium.writeCCXAbaqus(solverFile)
        matCount += 1
        matSec.append(Aluminium)
    return matSec


def define_elem_sets_material(eDic, matSets, solverFile):
    '''The following part creats all material sets

    I: IO-txtobject: File which should solved
    I: Integer: Number of materialsets
    I: Double: Penalty factor
    I: Double: elasticity module
    O: List: Integerlist with information which Set is used
    '''
    matSetDef = NodeElemSet(eDic)
    usedMatSets = []
    matCount = 1
    matRange = 1.0 / matSets
    setCount = 1
    # The following part sorts the element into sets
    # by using the densitiy
    for elemID in eDic:
        setCount = 0
        while setCount <= matSets - 1:
            if eDic[elemID][0] >= setCount * matRange:
                eDic[elemID][1] = setCount + 1
            else:
                break
            setCount += 1
    # Creating the materialsets
    while matCount <= matSets:
        elementList = []
        for elemID in eDic:
            if eDic[elemID][1] == matCount:
                elementList.append(elemID)
        if not elementList:
            usedMatSets.append(0)
            matCount += 1
            continue
        name = "matSet" + str(matCount)
        matSetDef.element_set_write_in_file(solverFile,
                                                              elementList, name)
        usedMatSets.append(1)
        matCount += 1
    return usedMatSets


def define_solid_section(solverFile, matSec, usedMatSets):
    '''The following part creates the solid sections

    I: IO-txtobject: File which should solved
    I: List: With all materials
    I: List: 0 -> matset is used, 1-> matset is not used
    '''
    secCounter = 1
    for material in matSec:
        if (usedMatSets[secCounter - 1]):
            solverFile.write("*Solid Section, ELSET=matSet" +
                                      str(secCounter) + ", material=" +
                                      str(material.get_name()) + "\n")
        secCounter += 1


def run_calculix(calculixPath, jobName):
    ''' This function starts calculix

    I: String: pathVariable of Calculix
    I: STring: Name of the job
    '''
    os.popen(calculixPath + " " + jobName)


def read_calculix_base(jobName):
    ''' This function reads the displacement

    I: STring: Name of the job
    '''
    #resultFileNameFrd =  jobName + ".frd"
    resultFileNameDat = jobName + ".dat"
    boundResult = Result()
    boundResult.add_result_from_file_dat(resultFileNameDat, "U")
    boundDisp = boundResult.get_disp()
    return boundDisp


def read_calculix(jobName):
    resultFileNameDat = jobName + ".dat"
    strainEner = Result()
    strainEner.add_result_from_file_dat(resultFileNameDat, "ENER")
    energyDensity = strainEner.get_energy_density()
    return energyDensity


def define_boundary(solverFile, boundDic):
    '''The following part creates the material settings.

    I: IO-txtobject: File which should solved
    I: Dictonary: Boundary with nodes
    '''
    modelBound = Boundary()
    modelBound.set_disp_bound(boundDic)
    modelBound.boundary_write_in_file(solverFile)


def get_string_after_sele_string(line, selString):
    '''The following part searches for a string

    I: String: Line which is selected in a IO-File
    I: List: Keywords for selecting the searced string type=C3D8R
    '''
    valueAfterEqIsActive = False
    valueBeforeEqIsActive = False
    valueBeforeWithEqIsActive = False
    stringIsWithEqIsActive = False
    oneStatementIsActive = False
    words = line[0:-1].split(" ")
    for word in words:
        if valueBeforeWithEqIsActive or valueAfterEqIsActive:
            if stringIsWithEqIsActive:
                word = word.split("=")
                word = word[0]
            elemType = word.split(",")
            if len(elemType) != 1:
                elemType = elemType[0]
            valueAfterEqIsActive = False
            valueBeforeEqIsActive = False
            valueBeforeWithEqIsActive = False
            stringIsWithEqIsActive = False
        for string in selString:
            if word[0:(len(string) + 1)] == (string + "="):
                valueBeforeWithEqIsActive = True
                if len(word) != len(string + "="):
                    oneStatementIsActive = True
        if oneStatementIsActive:
            elemType = word.split("=")
            elemType = elemType[1]
        for string in selString:
            if word == string:
                valueBeforeEqIsActive = True
        if valueBeforeEqIsActive and len(word) > 1:
            stringIsWithEqIsActive = True
        if word == "=" and valueBeforeEqIsActive:
            valueAfterEqIsActive = True
    return elemType


def FEM_struc(solverFileName, jobName, iFilePath, calculixPath,
                volfrac, penal, matSets, iterValue, eDic):
    '''The following creates an inputdeck

    I: IO-txtobject: File which should solved
    I: Dictonary: Boundary with nodes
    '''
    ElementReadingIsActive = False
    MaterialSectionCardIsActive = False
    ElasticIsActive = False
    DefineMaterialSetsIsActive = False
    ElementSetDefinitionIsActive = False
    SetMaterialSetsIsActive = False
    SolidSectionIsActive = False
    SolidSetIsActive = False
    NodeReadingIsDone = False
    nextCardJumpIsActive = False
    inputFile = open(iFilePath, "r")
    solveFile = open(solverFileName, "w")
    for line in inputFile:
        words = line[0:-1].split(" ")
        words = delete_empty_list_elements(words)
        if len(words) >= 1:
            # Define a nodeset with all nodes
            if words[0][0:5] == "*Node" and not NodeReadingIsDone:
                solveFile.write("*Node, Nset = Nall\n")
                NodeReadingIsDone = True
                continue
            # Define a elementset with all elements
            if words[0][0:8] == "*Element":
                elemType = get_string_after_sele_string(line,
                        ["type", "Type", "TYPE"])
                solveFile.write("*Element, type = " + str(elemType) +
                                ", Elset = Eall\n")
                ElementReadingIsActive = True
                continue
            if ElementReadingIsActive and words[0][0] == "*":
                ElementReadingIsActive = False
                ElementSetDefinitionIsActive = True
            if ElementReadingIsActive and iterValue == 1:
                wordsNoSemi = words[0].split(",")
                eDic[int(wordsNoSemi[0])] = [volfrac, int(volfrac * matSets)]
            # Define Material Part
            if ElasticIsActive:
                wordsNoSemi = words[0].split(",")
                youngModule = float(wordsNoSemi[0])
                ##if len(words) > 1:
                ##    wordsNoSemi = words[1].split(",")
                ##    ratio = wordsNoSemi[0]
                ElasticIsActive = False
                DefineMaterialSetsIsActive = True
            if MaterialSectionCardIsActive:
                if words[0][0:8] == "*Elastic":
                    ElasticIsActive = True
            if words[0][0:9] == "*Material":
                MaterialSectionCardIsActive = True
            if (DefineMaterialSetsIsActive) and words[0][0:5] == "*Step":
                matSec = define_material_sets(solveFile, matSets,
                                          penal, youngModule)
                DefineMaterialSetsIsActive = False
                SetMaterialSetsIsActive = True
            # Define elementsets for the material part
            if ElementSetDefinitionIsActive and SetMaterialSetsIsActive:
                usedMatSets =\
                         define_elem_sets_material(eDic, matSets, solveFile)
                ElementSetDefinitionIsActive = False
                SetMaterialSetsIsActive = False
                SolidSetIsActive = True
            # Define solid Sections
            if words[0][0:6] == "*Solid" and words[1][0:7] == "Section":
                SolidSectionIsActive = True
                continue
            if SolidSectionIsActive and SolidSetIsActive:
                define_solid_section(solveFile, matSec, usedMatSets)
                SolidSectionIsActive = False
                SolidSetIsActive = False
            # Output definition
            if words[0][0:1] == "*" and nextCardJumpIsActive:
                nextCardJumpIsActive = False
            if words[0] == "*Node" and words[1] == "Print":
                print "*Node Print output is changed for topoopti"
                nextCardJumpIsActive = True
                continue
            if words[0][0:5] == "*End" and words[1][0:5] == "Step":
                solveFile.write("*Node Print, NSET = Nall, FREQUENCY= 999\n")
                solveFile.write("U,\n")
            if nextCardJumpIsActive:
                continue
            solveFile.write(line)
    solveFile.close()
    inputFile.close()
    print "solver call"
    run_calculix(calculixPath, jobName)
    print "solver end"
    boundDic = read_calculix_base(jobName)
    return boundDic, youngModule


def sens_struc(solverFileNameKE, jobNameKE, iFilePath,
                                 calculixPath, boundDic):
    '''The following part creates the material settings.

    I: IO-txtobject: File which should solved
    I: Dictonary: Boundary with nodes
    '''
    BoundaryReadingIsActive = False
    NodeReadingIsDone = False
    inputFile = open(iFilePath, "r")
    solveFile = open(solverFileNameKE, "w")
    for line in inputFile:
        words = line[0:-1].split(" ")
        words = delete_empty_list_elements(words)
        if len(words) >= 1:
            # Define a nodeset with all nodes for the output
            if words[0][0:5] == "*Node" and not(NodeReadingIsDone):
                solveFile.write("*Node, Nset = Nall\n")
                NodeReadingIsDone = True
                continue
            # Define a elementset with all elements for the output
            if words[0][0:8] == "*Element":
                elemType = get_string_after_sele_string(line,
                        ["type", "Type", "TYPE"])
                solveFile.write("*Element, type = " + str(elemType) +
                                ", Elset = Eall\n")
                continue
            # Creates the boundarys
            if words[0][0] == "*" and BoundaryReadingIsActive:
                BoundaryReadingIsActive = False
            if words[0][0:9] == "*Boundary":
                BoundaryReadingIsActive = True
                define_boundary(solveFile, boundDic)
                continue
            # Output definition
            if words[0][0:5] == "*End" and words[1][0:5] == "Step":
                solveFile.write("*EL Print,ELSET=Eall,FREQUENCY=999\n")
                solveFile.write("ENER\n")
            solveFile.write(line)
    solveFile.close()
    inputFile.close()
    print "solver sensivity call"
    run_calculix(calculixPath, jobNameKE)
    print "solver sensivity end"
    elementValue = read_calculix(jobNameKE)
    return elementValue


def density_filter(nodeDic, elemDic):

    rmin = 3
    elemLoc = {}
    elemWeight = []
    print "Calculating density filter this one is only one time needed"
    for elemID in elemDic:
        #print elemDic
        nodeList = elemDic[elemID]
        x = 0
        y = 0
        z = 0
        for node in nodeList:
            x = x + nodeDic[node][0]
            y = y + nodeDic[node][1]
            z = z + nodeDic[node][2]
        xCent = x / len(nodeList)
        yCent = y / len(nodeList)
        zCent = z / len(nodeList)
        elemLoc[elemID] = [xCent, yCent, zCent]
    for elemID in elemLoc:
        weightList = []
        for elemID1 in elemLoc:
            x0 = elemLoc[elemID][0]
            y0 = elemLoc[elemID][1]
            z0 = elemLoc[elemID][2]
            x1 = elemLoc[elemID1][0]
            y1 = elemLoc[elemID1][1]
            z1 = elemLoc[elemID1][2]
            re = ((x0 - x1) ** 2 + (y0 - y1) ** 2 + (z0 - z1) ** 2) ** 0.5
            if rmin >= re:
                weightList.append([elemID1, rmin - re])
        elemWeight.append(weightList)
    return elemWeight


def filtered_dens_vec(filterVec, filterVal):
    counter = 0
    for weightSet in filterVal:
        wSum = 0
        temSens = 0
        for weightFac in weightSet:
            temSens = temSens + filterVec[weightFac[0] - 1] * weightFac[1]
            wSum = weightFac[1] + wSum
        filterVec[counter] = temSens / wSum
        counter += 1
    return filterVec

def change_density(eDic, elemRes, sensVecOld,
                   penal, volFrac, E0, iterValue, filterVal):
    '''The following part creates the material settings.

    I: IO-txtobject: File which should solved
    I: Dictonary: Boundary with nodes
    '''
    #l2 = 0
    Emin = 0.0
    move = 0.2
    densVec = []
    sensVec = []
    for elemID in elemRes:
        sensVec.append(elemRes[elemID])
    for elemID in eDic:
        densVec.append(eDic[elemID][0])
    sensVec = np.array(sensVec)
    densVec = np.array(densVec)
    #move = 0.2
    residuum = 0.0001
    sensVec = (0.5 * penal * densVec ** (penal - 1) * (E0 - Emin)) * sensVec
    # Stabilization for the process
    if iterValue > 1:
        sensVec = 0.5 * (sensVec + sensVecOld)
    densOld = densVec
    #l2 = E0 / np.mean(np.mean(abs(sensVec)))
    l2 = max((sensVec))
    l1 = min((sensVec))
    newDens = densOld
    while abs((l2 - l1)) / (l2) > residuum:
        lmid = 0.5 * (l2 + l1)
        # Criteria like M.P. Bendsoe SIMP
        newDens = np.maximum(0.0, np.maximum(densOld - move, np.minimum(1.0,
            np.minimum(densOld + move, densOld * (sensVec / lmid) ** 0.5))))
        # Criteria like X. Huang ESO/BESO
        sensVec = filtered_dens_vec(sensVec, filterVal)
        #newDens = np.maximum(0.001, np.sign(sensVec - lmid))
        if np.mean(newDens) - volFrac > 0.0:
            l1 = lmid
        else:
            l2 = lmid
        #print np.mean(newDens)
    print "filtering density"
    #newDens = filtered_dens_vec(newDens, filterVal)
    vecCount = 0
    for elemID in eDic:
        eDic[elemID][0] = newDens[vecCount]
        vecCount += 1
    print "mean density energy " + str(np.mean(densVec))
    print "mean densitiy " + str(np.mean(newDens))
    return eDic, sensVec


def main(volfrac, penal, matSets, numbIter):
    '''The main function calls the differen topo optimizations

    I: Double: Volumenratio
    I: Double: penalty exponent
    I: Integer: number of material sections
    I: Integer: number of maximum iterations
    '''
    # Used files for the optimization
    # Input file wich boundary, loads, elements ...
    calculixPath = "/usr/local/bin/ccx"
    iFilePath = "Input.inp"
    jobName = "topoK"
    jobNameKE = "topoKE"
    solverFileName = jobName + ".inp"
    solverFileNameKE = jobNameKE + ".inp"
    NodeElem = NodesElement()
    NodeElem.add_element_node_from_file(iFilePath, "Calculix")
    nodeDic = NodeElem.get_node_dic()
    elemDic = NodeElem.get_elem_dic()
    filterVal = density_filter(nodeDic, elemDic)
    eDic = {}
    iterValue = 1
    sensVecOld = []
    volfracbase = volfrac
    while iterValue <= numbIter:
        # FEM-Part of structural analysis
        volfrac = (1.0 - float(iterValue) / float(numbIter) * (1 - volfracbase))
        if iterValue > 1:
            sensVecOld = sensVec
        boundDic, youngModule = FEM_struc(solverFileName, jobName,
                        iFilePath, calculixPath, volfrac, penal, matSets,
                        iterValue, eDic)
        # Sensitivity analysis
        elementValue = sens_struc(solverFileNameKE, jobNameKE,
                                        iFilePath, calculixPath, boundDic)
        # Opti criteria (change of the densitiy value)
        eDic, sensVec = change_density(eDic, elementValue, sensVecOld,
                   penal, volfrac, youngModule, iterValue, filterVal)
        iterValue += 1


if __name__ == "__main__":
    # Default input parameters
    volfrac = 0.4
    penal = 4
    matSets = 1000
    numbIter = 40
    if len(sys.argv) > 1:
        volfrac = float(sys.argv[1])
    if len(sys.argv) > 2:
        penal = float(sys.argv[2])
    if len(sys.argv) > 3:
        matSets = int(sys.argv[3])
    if len(sys.argv) > 4:
        numbIter = int(sys.argv[4])
    main(volfrac, penal, matSets, numbIter)
