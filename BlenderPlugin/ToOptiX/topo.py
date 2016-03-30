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

# *FileFormat, ASCII
# Global lib
import os
import os.path
import shutil
import numpy as np
import logging
import bpy.ops
#import subprocess
#from stl import mesh
#from mpl_toolkits import mplot3d
#from matplotlib import pyplot
# Local lib
from . import ElementNodes
from . import Material
from . import NodeElemSet
from . import Result
from . import Boundary
from . import ExportTopoFile

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


def define_material_sets(solverFile, matSets, penal, matValue, sType="Struc"):
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
        Aluminium = Material.Material()
        if sType == "Struc":
            Aluminium.set_eModul(matValue * (float(matCount) /
                                 float(matSets)) ** penal)
        else:
            Aluminium.set_conduc(matValue * (float(matCount) /
                                 float(matSets)) ** penal)
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
    matSetDef = NodeElemSet.NodeElemSet(eDic)
    usedMatSets = []
    matCount = 1
    # The following part sorts the element into sets
    # by using the densitiy
    for elemID in eDic:
        eDic[elemID][1] = int(round((matSets - 1) * eDic[elemID][0])) + 1
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
    #os.popen(calculixPath + " " + jobName)
    os.system(calculixPath + " " + jobName)
    #proc = subprocess.Popen(calculixPath + " " + jobName)
    #proc.wait()


def read_calculix_sysanswer(jobName, sType):
    ''' This function reads the displacement

    I: STring: Name of the job
    '''
    #resultFileNameFrd =  jobName + ".frd"

    resultFileNameDat = jobName + ".dat"
    boundResult = Result.Result()
    if sType == "Struc":
        boundResult.add_result_from_file_dat(resultFileNameDat, "U")
        boundDisp = boundResult.get_disp()
    else:
        boundResult.add_result_from_file_dat(resultFileNameDat, "NT")
        boundDisp = boundResult.get_disp()
    return boundDisp


def read_calculix_sens(jobName, sType):
    resultFileNameDat = jobName + ".dat"
    ResultValues = Result.Result()
    #strainEner.add_result_from_file_dat(resultFileNameDat, "S")
    #stressValue = strainEner.get_total_stress()
    if sType == "Struc":
        ResultValues.add_result_from_file_dat(resultFileNameDat, "ENER")
        sensRes = ResultValues.get_energy_density()
    else:
        ResultValues.add_result_from_file_dat(resultFileNameDat, "HFL")
        sensRes = ResultValues.get_heat_flux()
    return sensRes


def define_boundary(solverFile, boundDic, sType):
    '''The following part creates the material settings.

    I: IO-txtobject: File which should solved
    I: Dictonary: Boundary with nodes
    '''
    modelBound = Boundary.Boundary()
    if sType == "Struc":
        modelBound.set_disp_bound(boundDic)
    else:
        modelBound.set_temp_bound(boundDic)
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


def save_solution(eDic, eDicNew, volfrac, xSelect):

    xSelect = 0.9
    for elemID in eDic:
        if eDic[elemID][0] >= xSelect:
            eDicNew[elemID] = 1.0
        else:
            eDicNew[elemID] = -1.0
    for elemID in eDicNew:
        if eDicNew[elemID] > 0:
            eDic[elemID][0] = eDicNew[elemID]
        else:
            eDic[elemID][0] = volfrac
    return eDicNew, eDic


def add_old_solution(eDicNew, eDic):

    for elemID in eDicNew:
        if eDicNew[elemID] > 0:
            eDic[elemID][0] = eDicNew[elemID]
    return eDic


def FEM_calc_ccx(solverFileName, jobName, iFilePath, calculixPath,
           volfrac, penal, matSets, iterValue, eDic, solverTypeisAba,
            sType="Struc"):
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
    conducIsActive = False
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
                solveFile.write(line)
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
                matValue = float(wordsNoSemi[0])
                ElasticIsActive = False
                DefineMaterialSetsIsActive = True
            if conducIsActive:
                wordsNoSemi = words[0].split(",")
                matValue = float(wordsNoSemi[0])
                conducIsActive = False
                DefineMaterialSetsIsActive = True
            if MaterialSectionCardIsActive:
                if words[0][0:8] == "*Elastic" and sType == "Struc":
                    ElasticIsActive = True
            if MaterialSectionCardIsActive:
                if words[0][0:13] == "*Conductivity" and sType == "Therm":
                    conducIsActive = True
            if words[0][0:9] == "*Material":
                MaterialSectionCardIsActive = True
            if (DefineMaterialSetsIsActive) and words[0][0:5] == "*Step":
                matSec = define_material_sets(solveFile, matSets,
                                          penal, matValue, sType)
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
                nextCardJumpIsActive = True
                continue
            if words[0][0:5] == "*End" and words[1][0:5] == "Step":
                solveFile.write("*Node Print, NSET = Nall, FREQUENCY= 999\n")
                if sType == "Struc":
                    solveFile.write("U,\n")
                else:
                    solveFile.write("NT,\n")
            if nextCardJumpIsActive:
                continue
            solveFile.write(line)
    solveFile.close()
    inputFile.close()
    print("solver call")
    run_calculix(calculixPath, jobName)
    print("solver end")
    boundDic = read_calculix_sysanswer(jobName, sType)
    return boundDic, matValue


def sens_calc_ccx(solverFileNameKE, jobNameKE, iFilePath,
                   calculixPath, boundDic, solverTypeisAba, sType="Struc"):
    '''The following part creates the material settings.

    I: IO-txtobject: File which should solved
    I: Dictonary: Boundary with nodes
    '''
    BoundaryReadingIsActive = False
    nextCardJumpIsActive = False
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
                solveFile.write(line)
                continue
            # Creates the boundarys
            if words[0][0] == "*" and BoundaryReadingIsActive:
                BoundaryReadingIsActive = False
            if words[0][0:9] == "*Boundary":
                BoundaryReadingIsActive = True
                define_boundary(solveFile, boundDic, sType)
                continue
            # Output definition
            if words[0][0:1] == "*" and nextCardJumpIsActive:
                nextCardJumpIsActive = False
            if words[0] == "*El" and words[1] == "Print":
                nextCardJumpIsActive = True
                continue
            if words[0][0:5] == "*End" and words[1][0:5] == "Step":
                solveFile.write("*EL Print,ELSET=Eall,FREQUENCY=999\n")
                if sType == "Struc":
                    solveFile.write("ENER, S\n")
                else:
                    solveFile.write("HFL\n")
            if nextCardJumpIsActive:
                continue
            solveFile.write(line)
    solveFile.close()
    inputFile.close()
    print("solver sensivity call")
    run_calculix(calculixPath, jobNameKE)
    print("solver sensivity end")
    elementValue = read_calculix_sens(jobNameKE, sType)
    return elementValue



def sort_element_to_node_dic( elemDic):
    ''' The following function is used for selecting elements around an elem.

    I: Dictonary: [elementID] [Class: Element]

    '''
    # Saves [node] = [elem1, elem2, elem3 ...]
    nodeElem = {}
    # Saves [elemID] = [[elemIDFilt][scaleFac]]
    elemScale = {}
    # This factor sets the purgency
    # The selected element will weight 0.5
    weightOwnElem = 0.5
    for elemID in elemDic:
        element = elemDic[elemID]
        nodeList = element.nodeList
        for node in nodeList:
            try:
                nodeElem[node.ID].add(element.ID)
            except:
                nodeElem[node.ID] = set()
                nodeElem[node.ID].add(element.ID)

    # Scaling the distances and
    for elemID in elemDic:
        elementInRegion = set()
        element = elemDic[elemID]
        xc = element.xc
        yc = element.yc
        zc = element.zc
        nodeList = element.nodeList
        for node in nodeList:
            elementInRegion = elementInRegion | nodeElem[node.ID]
        dist = []
        eleList = []
        # Element for filtering 2 lists with elemID and 1/distance
        for elemR in elementInRegion:
            element1 = elemDic[elemR]
            xc1 = element1.xc
            yc1 = element1.yc
            zc1 = element1.zc
            ele1ID = element1.ID
            if ele1ID == element.ID:
                continue
            dist.append(1/((xc1-xc)**2 + (yc1-yc)**2 + (zc1-zc)**2)**0.5)
            eleList.append(ele1ID)
        norm = 0
        for distan in dist:
            norm = distan + norm
        distNorm = []
        for distnorm in dist:
            distNorm.append((1-weightOwnElem) * 1/norm * (distnorm))
        distNorm.append(weightOwnElem)
        eleList.append(element.ID)
        elemScale[elemID] = [distNorm, eleList]
    return elemScale

def filter_sens_vec(elemSens, filterVal, resElemSet):
    elemRes = elemSens.copy()
    for elemID in resElemSet:
        filterList = filterVal[elemID]
        scaleList = filterList[0]
        eleIDList = filterList[1]
        counter = 0
        scaledSens = 0
        for eleID in eleIDList:
            scaledSens = scaledSens + scaleList[counter] * elemRes[elemID]
            counter += 1
        elemSens[elemID] = scaledSens
    return elemSens

def filter_dens_vec(eDic, filterVal, resElemSet):
    elemDens = eDic.copy()
    for elemID in resElemSet:
        filterList = filterVal[elemID]
        scaleList = filterList[0]
        eleIDList = filterList[1]
        counter = 0
        scaledSens = 0
        for eleID in eleIDList:
            scaledSens = scaledSens + scaleList[counter] * elemDens[eleID][0]
            counter += 1
        eDic[elemID][0] = scaledSens
    return eDic


def change_density(eDic, elemRes,
                   penal, volFrac, matVal, iterValue, filterVal,
                   filterIsActive, simpIsActive, noDesSpaceIsActive):
    '''The following part creates the material settings.

    I: IO-txtobject: File which should solved
    I: Dictonary: Boundary with nodes
    '''

    noDesignFile = "InputND.inp"
    noDesSet = set()
    allElemSet = set()
    if noDesSpaceIsActive:
        noDesSet = get_element_set_out_of_file(noDesignFile)
        print("Number of Element in no desing space: {}".format(len(noDesSet)))
    for elemID in elemRes:
        allElemSet.add(elemID)
    resElemSet = allElemSet
    #l2 = 0
    matMin = 0.00001
    move = 0.2
    densVec = []
    sensVec = []
    #if filterIsActive:
     #   print "filtering sensitivity"
      #  elemRes = filter_sens_vec(elemRes, filterVal, resElemSet)
    for elemID in resElemSet:
        sensVec.append(elemRes[elemID])
    for elemID in resElemSet:
        densVec.append(eDic[elemID][0])
    sensVec = np.array(sensVec)
    densVec = np.array(densVec)
    #move = 0.2
    residuum = 0.0001
    sensVec = (0.5 * penal * densVec ** (penal - 1) * (matVal - matMin)) \
              * sensVec
    # Stabilization for the process

    if iterValue == 1:
        sensPath = "Sensitivity.log"
        sensFile = open(sensPath, "w")
        sensFile.write("Change of density and sensitivity \n")
        sensFile.write("Iter, Sensi, Density \n")
        sensFile.close()
    #    sensVec = 0.5 * (sensVec + sensVecOld)
    densOld = densVec
    #l2 = E0 / np.mean(np.mean(abs(sensVec)))
    l2 = max((sensVec))
    l1 = min((sensVec))
    newDens = densOld
    #densitiyFilterIsActive = False
    sensPath = "Sensitivity.log"
    sensFile = open(sensPath, "a")
    while abs((l2 - l1)) / (l2) > residuum:
        lmid = 0.5 * (l2 + l1)

        if simpIsActive:
            # Criteria like M.P. Bendsoe SIMP
            newDens = np.maximum(0.0, np.maximum(densOld - move, np.minimum(1.0,
                np.minimum(densOld + move, densOld * (sensVec / lmid) ** 0.5))))
        else:
            # Criteria like X. Huang ESO/BESO
            newDens = np.maximum(0.00001, np.sign(sensVec - lmid))
        if np.mean(newDens) - volFrac > 0.0:
            l1 = lmid
        else:
            l2 = lmid
        #print np.mean(newDens)
    #if filterIsActive and densitiyFilterIsActive:
     #   print "filtering density"
      #  #newDens = filter_dens_vec(newDens, filterVal)
    vecCount = 0
    for elemID in resElemSet:
        eDic[elemID][0] = newDens[vecCount]
        vecCount += 1
    for elemID in noDesSet:
        eDic[elemID][0] = 1.0
    print("mean density energy " + str(np.mean(sensVec)))
    print("mean densitiy " + str(np.mean(newDens)))
    sensFile.write(str(iterValue) + "   " + str(np.mean(sensVec)) + "   "
                    + str(np.mean(newDens)) + " \n")
    sensFile.close()
    if filterIsActive:
        print("filtering densitys")
        eDic = filter_dens_vec(eDic, filterVal, resElemSet)
    return eDic


def structural_topo(solverFileNameS, jobNameS,
                    iFilePathS, calculixPath, volfrac, penal, matSets,
                    iteration, eDic, solverFileNameKES, jobNameKES, filterVal,
                    filterIsActive, simpIsActive, solverTypeisAba,
                    noDesSpaceIsActive):
    boundDic, matValue = FEM_calc_ccx(solverFileNameS, jobNameS,
                    iFilePathS, calculixPath, volfrac, penal, matSets,
                    iteration, eDic, solverTypeisAba, "Struc")
    # Sensitivity analysis
    elementValue = sens_calc_ccx(solverFileNameKES, jobNameKES,
                              iFilePathS, calculixPath, boundDic, solverTypeisAba,
                               "Struc")
    # Opti criteria (change of the densitiy value)
    eDicOld = eDic
    try:
        eDic = change_density(eDic, elementValue,
               penal, volfrac, matValue, iteration, filterVal,
               filterIsActive, simpIsActive, noDesSpaceIsActive)
    except:
        print("Sensitivity analyiss failed: kill some material")
        eDic = eDicOld
    return eDic


def thermal_topo(solverFileNameT, jobNameT,
                 iFilePathT, calculixPath, volfrac, penal, matSets,
                 iteration, eDic, solverFileNameKET, jobNameKET, filterVal,
                 filterIsActive, simpIsActive, solverTypeisAba,
                 noDesSpaceIsActive):
    boundDic, matValue = FEM_calc_ccx(solverFileNameT, jobNameT,
                 iFilePathT, calculixPath, volfrac, penal, matSets,
                 iteration, eDic, solverTypeisAba, "Therm")
    # Sensitivity thermal analysis
    elementValue = sens_calc_ccx(solverFileNameKET, jobNameKET,
                   iFilePathT, calculixPath, boundDic, solverTypeisAba, "Therm")

    # Opti criteria (change of the densitiy value)
    try:
        eDic = change_density(eDic, elementValue,
               penal, volfrac, matValue, iteration, filterVal,
               filterIsActive, simpIsActive, noDesSpaceIsActive)
    except:
        print("Sensitivity analyiss failed: kill some material")
        eDic = eDicOld
    return eDic


def coupled_topo(solverFileNameS, jobNameS,
                    iFilePathS, calculixPath, volfrac, penal, matSets,
                    iteration, eDic, solverFileNameKES, jobNameKES, filterVal,
                    filterIsActive, solverFileNameT, jobNameT, iFilePathT,
                    solverFileNameKET, jobNameKET, weightFactorStruc,
                    midValueIsActive, simpIsActive, solverTypeisAba,
                    noDesSpaceIsActive):
    boundDic, matValue = FEM_calc_ccx(solverFileNameS, jobNameS,
                iFilePathS, calculixPath, volfrac, penal, matSets,
                iteration, eDic, solverTypeisAba, "Struc")
    # Sensitivity analysis structural
    elementValueS = sens_calc_ccx(solverFileNameKES, jobNameKES,
                              iFilePathS, calculixPath, boundDic, solverTypeisAba,
                               "Struc")

    boundDic, matValue = FEM_calc_ccx(solverFileNameT, jobNameT,
             iFilePathT, calculixPath, volfrac, penal, matSets,
             iteration, eDic, solverTypeisAba, "Therm")
    # Sensitivity thermal analysis
    elementValueT = sens_calc_ccx(solverFileNameKET, jobNameKET,
                   iFilePathT, calculixPath, boundDic, solverTypeisAba, "Therm")
    elementValue = {}
    # Norming elemS
    if midValueIsActive:
        sumElemS = 0
        sumElemT = 0
        for elemID in elementValueS:
            sumElemS = sumElemS + abs(elementValueS[elemID])
            sumElemT = sumElemT + abs(elementValueT[elemID])
        meanElemS = sumElemS / len(elementValueS)
        meanElemT = sumElemT / len(elementValueT)
    else:
        listElemS = []
        listElemT = []
        for elemID in elementValueS:
            listElemS.append(abs(elementValueS[elemID]))
            listElemT.append(abs(elementValueT[elemID]))
        meanElemS = np.median(listElemS)
        meanElemT = np.median(listElemT)
    for elemID in elementValueS:
        elementValue[elemID] = 1 / meanElemS * elementValueS[elemID] * \
            weightFactorStruc + 1 / meanElemT * elementValueT[elemID] * \
            (1 - weightFactorStruc)
    # Opti criteria (change of the densitiy value)
    eDicOld = eDic
    try:
        eDic = change_density(eDic, elementValue,
               penal, volfrac, matValue, iteration, filterVal,
               filterIsActive, simpIsActive, noDesSpaceIsActive)
    except:
        print("Sensitivity analyiss failed: kill some material")
        eDic = eDicOld
    return eDic


def get_element_set_out_of_file(noDesignPath):
    nDesignList = set()
    noDesignFile = open(noDesignPath, "r")
    for line in noDesignFile:
        words = line[0:-1].split(",")
        for word in words:
            try:
                nDesignList.add(int(word))
            except:
                pass
    noDesignFile.close()
    return nDesignList




def topo_start3d(volfrac, penal, rmin, matSets, lastStepIter, numbIterAfter,
                   adaptChangeIteration, adapVolfrac, NumberOfAdapChanges,
                   weightFactorStruc, ThermalIsActive,
                   StructIsActive, SensitivIsActive, AdaptionIsActive,
                   StartStrucAdap, WeightAdapIsActive, IterativeAdapIsActive,
                   midValueIsActive, simpIsActive, mExpoInpIsActive,
                   mExpoStlIsActive, ccxPath, abaPath, solverTypeisAba, xSelec,
                   noDesSpaceIsActive, dispResultIsActive,filterIsActive):
    '''The main function calls the differen topo optimizations

    I: Double: Volumenratio
    I: Double: penalty exponent
    I: Integer: number of material sections
    I: Integer: number of maximum iterations
    '''
    # Used files for the optimization
    # Input file wich boundary, loads, elements ...
    if solverTypeisAba:
        calculixPath = abaPath
    else:
        calculixPath = ccxPath
    guiPath = "PyTopo3D/"
    # Structural files
    iFilePathS = "InputS.inp"
    # Directory of the results of stl
    if os.path.isdir("./STLResults"):
        shutil.rmtree("./STLResults")
        os.mkdir("./STLResults")
    else:
        os.mkdir("./STLResults")
    # directory of the calculation
    if os.path.isdir("./PyTopo3D"):
        shutil.rmtree("./PyTopo3D")
        os.mkdir("./PyTopo3D")
    else:
        os.mkdir("./PyTopo3D")
    # Creating a new log-file
    if os.path.isfile('topo.log'):
        os.remove('topo.log')
        logging.basicConfig(filename='topo.log', level=logging.INFO)
    else:
        logging.basicConfig(filename='topo.log', level=logging.INFO)
    jobNameS = guiPath + "topoStrucSys"
    jobNameKES = guiPath + "topoStrucSens"
    solverFileNameS = jobNameS + ".inp"
    solverFileNameKES = jobNameKES + ".inp"
    # Thermal files
    iFilePathT = "InputT.inp"
    jobNameT = guiPath + "topoThermSys"
    jobNameKET = guiPath + "topoThermSens"
    solverFileNameT = jobNameT + ".inp"
    solverFileNameKET = jobNameKET + ".inp"
    # Nodes and elements for the filter

    if ThermalIsActive:
        [nodeDic, elemDic] = ElementNodes.import_elements_nodes_as_dic(iFilePathT)
    elif StructIsActive:
        [nodeDic, elemDic] = ElementNodes.import_elements_nodes_as_dic(iFilePathS)
    else:
        print("Wrong input")
    filterVal = None
    if filterIsActive:
        filterVal = sort_element_to_node_dic(elemDic)
    eDic = {}
    iteration = 0
    volfracbase = volfrac
    eDicNew = {}
    # Controlparameter for the optimization type
    OnlyThermalIA = False
    OnlyStrucIA = False
    WeightDensIA = False
    WeightSensIA = False
    AdapStrucStartIA = False
    AdapThermStartIA = False
    ItAdapStrucStartIA = False
    ItAdapThermStartIA = False
    AdapWeighSensStrucStartIA = False
    AdapWeighDensStrucStartIA = False
    AdapWeighSensThermStartIA = False
    AdapWeighDensThermStartIA = False
    StructIsOutActive = False
    ThermalOutIsActive = False

    if ThermalIsActive and not StructIsActive:
        print('Thermal Optimization is selected \n')
        iterEndAnaOpti = lastStepIter
        OnlyThermalIA = True
    elif not ThermalIsActive and StructIsActive:
        print('Structural Optimization is selected \n')
        iterEndAnaOpti = lastStepIter
        OnlyStrucIA = True
    # Only weight factors
    elif ThermalIsActive and StructIsActive and not SensitivIsActive and not AdaptionIsActive:
        print('Weight optimization is selected (Densitys)\n')
        iterEndAnaOpti = lastStepIter
        WeightDensIA = True
    elif ThermalIsActive and StructIsActive and SensitivIsActive and not AdaptionIsActive:
        print('Weight optimization is selected (Sensitives)\n')
        iterEndAnaOpti = lastStepIter
        WeightSensIA = True
    # Adaption part pending
    elif ThermalIsActive and StructIsActive and AdaptionIsActive and StartStrucAdap and not WeightAdapIsActive and IterativeAdapIsActive:
        print('Iterative Adaption with Struc start is selected\n')
        iterEndAnaOpti = adaptChangeIteration
        ItAdapStrucStartIA = True
    elif ThermalIsActive and StructIsActive and AdaptionIsActive and not StartStrucAdap and not WeightAdapIsActive and IterativeAdapIsActive:
        print('Iterative Adaption with thermal start is selected\n')
        iterEndAnaOpti = adaptChangeIteration
        ItAdapThermStartIA = True
    # Adaption not pending
    elif ThermalIsActive and StructIsActive and AdaptionIsActive and StartStrucAdap and not WeightAdapIsActive and not IterativeAdapIsActive:
        print('Adaption with Struc start is selected\n')
        iterEndAnaOpti = adaptChangeIteration
        AdapStrucStartIA = True
    elif ThermalIsActive and StructIsActive and AdaptionIsActive and not StartStrucAdap and not WeightAdapIsActive and not IterativeAdapIsActive:
        print('Adaption with thermal start is selected\n')
        iterEndAnaOpti = adaptChangeIteration
        AdapThermStartIA = True
    # Weight Adaption struc start
    elif ThermalIsActive and StructIsActive and SensitivIsActive and AdaptionIsActive and StartStrucAdap and WeightAdapIsActive:
        print('Weighted (Sensitives) Adaption with structural start is selected\n')
        iterEndAnaOpti = adaptChangeIteration
        AdapWeighSensStrucStartIA = True
    elif ThermalIsActive and StructIsActive and not SensitivIsActive and AdaptionIsActive and StartStrucAdap and WeightAdapIsActive:
        print('Weighted (Density) Adaption with structural start is selected\n')
        iterEndAnaOpti = adaptChangeIteration
        AdapWeighDensStrucStartIA = True
    # Weight adaption therm start
    elif ThermalIsActive and StructIsActive and SensitivIsActive and AdaptionIsActive and not StartStrucAdap and WeightAdapIsActive:
        print('Weighted (Sensitives) Adaption with thermal start is selected\n');
        iterEndAnaOpti = adaptChangeIteration
        AdapWeighSensThermStartIA = True
    elif ThermalIsActive and StructIsActive and not SensitivIsActive and AdaptionIsActive and not StartStrucAdap and WeightAdapIsActive:
        print('Weighted (Density) Adaption with thermal is selected\n')
        iterEndAnaOpti = adaptChangeIteration
        AdapWeighDensThermStartIA = True
    else:
        print('No optimization selection\n')

    changePhysType = False
    addOldSolu = False
    adapCounter = 1

    while iteration <= iterEndAnaOpti + numbIterAfter:
        iteration += 1
        if adapCounter >= NumberOfAdapChanges and (ItAdapThermStartIA or ItAdapStrucStartIA):
            adapCounter = NumberOfAdapChanges
        # additional part not in 2D
        print ("iteration: " + str(iteration))
        if iteration <= iterEndAnaOpti:
            volfrac = (1.0 - float(iteration) / float(iterEndAnaOpti) *
                      (1 - volfracbase))
        print ("volfrac: " + str(volfrac))
        logging.info("iteration: {} volRatio: {}".format(iteration, volfrac))
        if OnlyThermalIA:
            eDic = thermal_topo(solverFileNameT, jobNameT,
                 iFilePathT, calculixPath, volfrac, penal, matSets,
                 iteration, eDic, solverFileNameKET, jobNameKET, filterVal,
                 filterIsActive, simpIsActive, solverTypeisAba,
                 noDesSpaceIsActive)
            ThermalOutIsActive = True
        elif OnlyStrucIA:
            eDic = structural_topo(solverFileNameS, jobNameS,
                    iFilePathS, calculixPath, volfrac, penal, matSets,
                    iteration, eDic, solverFileNameKES, jobNameKES, filterVal,
                    filterIsActive, simpIsActive, solverTypeisAba,
                    noDesSpaceIsActive)
            StructIsOutActive = True
        elif WeightDensIA:
            eDicT = thermal_topo(solverFileNameT, jobNameT,
                 iFilePathT, calculixPath, volfrac, penal, matSets,
                 iteration, eDic, solverFileNameKET, jobNameKET, filterVal,
                 filterIsActive, simpIsActive, solverTypeisAba, noDesSpaceIsActive)
            eDicS = structural_topo(solverFileNameS, jobNameS,
                    iFilePathS, calculixPath, volfrac, penal, matSets,
                    iteration, eDic, solverFileNameKES, jobNameKES, filterVal,
                    filterIsActive, simpIsActive, solverTypeisAba, noDesSpaceIsActive)
            StructIsOutActive = True
            ThermalOutIsActive = True
            for elemID in eDicS:
                eDic[elemID][0] = weightFactorStruc * eDicS[elemID][0] \
                          + (1 - weightFactorStruc) * eDicT[elemID][0]
        elif WeightSensIA:
            eDic = coupled_topo(solverFileNameS, jobNameS,
                iFilePathS, calculixPath, volfrac, penal, matSets,
                iteration, eDic, solverFileNameKES, jobNameKES, filterVal,
                filterIsActive, solverFileNameT, jobNameT, iFilePathT,
                solverFileNameKET, jobNameKET, weightFactorStruc,
                midValueIsActive, simpIsActive, solverTypeisAba, noDesSpaceIsActive)
            StructIsOutActive = True
            ThermalOutIsActive = True
        elif AdapStrucStartIA:
            if not changePhysType:
                eDic = structural_topo(solverFileNameS, jobNameS,
                     iFilePathS, calculixPath, volfrac, penal, matSets,
                     iteration, eDic, solverFileNameKES, jobNameKES, filterVal,
                     filterIsActive, simpIsActive, solverTypeisAba, noDesSpaceIsActive)
                StructIsOutActive = True
                ThermalOutIsActive = False
            else:
                eDic = thermal_topo(solverFileNameT, jobNameT,
                     iFilePathT, calculixPath, volfrac, penal, matSets,
                     iteration, eDic, solverFileNameKET, jobNameKET, filterVal,
                     filterIsActive, simpIsActive, solverTypeisAba, noDesSpaceIsActive)
                StructIsOutActive = False
                ThermalOutIsActive = True
            if addOldSolu:
                eDic = add_old_solution(eDicNew, eDic)
            if iteration == adaptChangeIteration:
                iterEndAnaOpti = 2 * adaptChangeIteration
                changePhysType = True
                addOldSolu = True
                eDicNew, eDic = save_solution(eDic, eDicNew, volfrac, xSelec)
                volfracbase = volfracbase + adapVolfrac
        elif AdapThermStartIA:
            if not changePhysType:
                eDic = thermal_topo(solverFileNameT, jobNameT,
                     iFilePathT, calculixPath, volfrac, penal, matSets,
                     iteration, eDic, solverFileNameKET, jobNameKET, filterVal,
                     filterIsActive, simpIsActive, solverTypeisAba, noDesSpaceIsActive)
                StructIsOutActive = False
                ThermalOutIsActive = True
            else:
                eDic = structural_topo(solverFileNameS, jobNameS,
                     iFilePathS, calculixPath, volfrac, penal, matSets,
                     iteration, eDic, solverFileNameKES, jobNameKES, filterVal,
                     filterIsActive, simpIsActive, solverTypeisAba, noDesSpaceIsActive)
                StructIsOutActive = True
                ThermalOutIsActive = False
            if addOldSolu:
                eDic = add_old_solution(eDicNew, eDic)
            if iteration == adaptChangeIteration:
                iterEndAnaOpti = 2 * adaptChangeIteration
                changePhysType = True
                addOldSolu = True
                eDicNew, eDic = save_solution(eDic, eDicNew, volfrac, xSelec)
                volfracbase = volfracbase + adapVolfrac
        elif ItAdapStrucStartIA:
            if not changePhysType:
                eDic = structural_topo(solverFileNameS, jobNameS,
                     iFilePathS, calculixPath, volfrac, penal, matSets,
                     iteration, eDic, solverFileNameKES, jobNameKES, filterVal,
                     filterIsActive, simpIsActive, solverTypeisAba, noDesSpaceIsActive)
                StructIsOutActive = True
                ThermalOutIsActive = False
            else:
                eDic = thermal_topo(solverFileNameT, jobNameT,
                     iFilePathT, calculixPath, volfrac, penal, matSets,
                     iteration, eDic, solverFileNameKET, jobNameKET, filterVal,
                     filterIsActive, simpIsActive, solverTypeisAba, noDesSpaceIsActive)
                StructIsOutActive = False
                ThermalOutIsActive = True
            if addOldSolu:
                eDic = add_old_solution(eDicNew, eDic)
            if iteration == adaptChangeIteration * adapCounter:
                iterEndAnaOpti = (adapCounter) * adaptChangeIteration
                adapCounter += 1
                iterEndAnaOpti = (adapCounter) * adaptChangeIteration
                if changePhysType:
                    changePhysType = False
                else:
                    changePhysType = True
                addOldSolu = True
                eDicNew, eDic = save_solution(eDic, eDicNew, volfrac, xSelec)
                volfracbase = volfracbase + adapVolfrac
        elif ItAdapThermStartIA:
            if not changePhysType:
                eDic = thermal_topo(solverFileNameT, jobNameT,
                     iFilePathT, calculixPath, volfrac, penal, matSets,
                     iteration, eDic, solverFileNameKET, jobNameKET, filterVal,
                     filterIsActive, simpIsActive, solverTypeisAba, noDesSpaceIsActive)
                StructIsOutActive = False
                ThermalOutIsActive = True
            else:
                eDic = structural_topo(solverFileNameS, jobNameS,
                     iFilePathS, calculixPath, volfrac, penal, matSets,
                     iteration, eDic, solverFileNameKES, jobNameKES, filterVal,
                     filterIsActive, simpIsActive, solverTypeisAba, noDesSpaceIsActive)
                StructIsOutActive = True
                ThermalOutIsActive = False
            if addOldSolu:
                eDic = add_old_solution(eDicNew, eDic)
            if iteration == adaptChangeIteration * adapCounter:
                adapCounter += 1
                iterEndAnaOpti = (adapCounter) * adaptChangeIteration
                if changePhysType:
                    changePhysType = False
                else:
                    changePhysType = True
                addOldSolu = True
                eDicNew, eDic = save_solution(eDic, eDicNew, volfrac, xSelec)
                volfracbase = volfracbase + adapVolfrac
        elif AdapWeighSensStrucStartIA:
            if not changePhysType:
                eDic = structural_topo(solverFileNameS, jobNameS,
                     iFilePathS, calculixPath, volfrac, penal, matSets,
                     iteration, eDic, solverFileNameKES, jobNameKES, filterVal,
                     filterIsActive, simpIsActive, solverTypeisAba, noDesSpaceIsActive)
                StructIsOutActive = True
                ThermalOutIsActive = False
            else:
                eDic = coupled_topo(solverFileNameS, jobNameS,
                    iFilePathS, calculixPath, volfrac, penal, matSets,
                    iteration, eDic, solverFileNameKES, jobNameKES, filterVal,
                    filterIsActive, solverFileNameT, jobNameT, iFilePathT,
                    solverFileNameKET, jobNameKET, weightFactorStruc,
                    midValueIsActive, simpIsActive, solverTypeisAba, noDesSpaceIsActive)
                StructIsOutActive = True
                ThermalOutIsActive = True
            if addOldSolu:
                eDic = add_old_solution(eDicNew, eDic)
            if iteration == adaptChangeIteration:
                iterEndAnaOpti = 2 * adaptChangeIteration
                changePhysType = True
                addOldSolu = True
                eDicNew, eDic = save_solution(eDic, eDicNew, volfrac, xSelec)
                volfracbase = volfracbase + adapVolfrac
        elif AdapWeighSensThermStartIA:
            if not changePhysType:
                eDic = thermal_topo(solverFileNameT, jobNameT,
                     iFilePathT, calculixPath, volfrac, penal, matSets,
                     iteration, eDic, solverFileNameKET, jobNameKET, filterVal,
                     filterIsActive, simpIsActive, solverTypeisAba, noDesSpaceIsActive)
                StructIsOutActive = False
                ThermalOutIsActive = True
            else:
                eDic = coupled_topo(solverFileNameS, jobNameS,
                    iFilePathS, calculixPath, volfrac, penal, matSets,
                    iteration, eDic, solverFileNameKES, jobNameKES, filterVal,
                    filterIsActive, solverFileNameT, jobNameT, iFilePathT,
                    solverFileNameKET, jobNameKET, weightFactorStruc,
                    midValueIsActive, simpIsActive, solverTypeisAba, noDesSpaceIsActive)
                StructIsOutActive = True
                ThermalOutIsActive = True
            if addOldSolu:
                eDic = add_old_solution(eDicNew, eDic)
            if iteration == adaptChangeIteration:
                iterEndAnaOpti = 2 * adaptChangeIteration
                changePhysType = True
                addOldSolu = True
                eDicNew, eDic = save_solution(eDic, eDicNew, volfrac, xSelec)
                volfracbase = volfracbase + adapVolfrac
        elif AdapWeighDensStrucStartIA:
            if not changePhysType:
                eDic = structural_topo(solverFileNameS, jobNameS,
                     iFilePathS, calculixPath, volfrac, penal, matSets,
                     iteration, eDic, solverFileNameKES, jobNameKES, filterVal,
                     filterIsActive, simpIsActive, solverTypeisAba, noDesSpaceIsActive)
                StructIsOutActive = True
                ThermalOutIsActive = False
            else:
                eDicT = thermal_topo(solverFileNameT, jobNameT,
                     iFilePathT, calculixPath, volfrac, penal, matSets,
                     iteration, eDic, solverFileNameKET, jobNameKET, filterVal,
                     filterIsActive, solverTypeisAba)
                eDicS = structural_topo(solverFileNameS, jobNameS,
                    iFilePathS, calculixPath, volfrac, penal, matSets,
                    iteration, eDic, solverFileNameKES, jobNameKES, filterVal,
                    filterIsActive, simpIsActive, solverTypeisAba, noDesSpaceIsActive)
                for elemID in eDicS:
                    eDic[elemID][0] = weightFactorStruc * eDicS[elemID][0] \
                              + (1 - weightFactorStruc) * eDicT[elemID][0]
                StructIsOutActive = True
                ThermalOutIsActive = True
            if addOldSolu:
                eDic = add_old_solution(eDicNew, eDic)
            if iteration == adaptChangeIteration:
                iterEndAnaOpti = 2 * adaptChangeIteration
                changePhysType = True
                addOldSolu = True
                eDicNew, eDic = save_solution(eDic, eDicNew, volfrac, xSelec)
                volfracbase = volfracbase + adapVolfrac
        elif AdapWeighDensThermStartIA:
            if not changePhysType:
                eDic = thermal_topo(solverFileNameT, jobNameT,
                     iFilePathT, calculixPath, volfrac, penal, matSets,
                     iteration, eDic, solverFileNameKET, jobNameKET, filterVal,
                     filterIsActive, simpIsActive, solverTypeisAba, noDesSpaceIsActive)
                StructIsOutActive = False
                ThermalOutIsActive = True
            else:
                eDicT = thermal_topo(solverFileNameT, jobNameT,
                     iFilePathT, calculixPath, volfrac, penal, matSets,
                     iteration, eDic, solverFileNameKET, jobNameKET, filterVal,
                     filterIsActive, simpIsActive, solverTypeisAba, noDesSpaceIsActive)
                eDicS = structural_topo(solverFileNameS, jobNameS,
                    iFilePathS, calculixPath, volfrac, penal, matSets,
                    iteration, eDic, solverFileNameKES, jobNameKES, filterVal,
                    filterIsActive, simpIsActive, solverTypeisAba, noDesSpaceIsActive)
                for elemID in eDicS:
                    eDic[elemID][0] = weightFactorStruc * eDicS[elemID][0] \
                              + (1 - weightFactorStruc) * eDicT[elemID][0]
                StructIsOutActive = True
                ThermalOutIsActive = True
            if addOldSolu:
                eDic = add_old_solution(eDicNew, eDic)
            if iteration == adaptChangeIteration:
                iterEndAnaOpti = 2 * adaptChangeIteration
                changePhysType = True
                addOldSolu = True
                eDicNew, eDic = save_solution(eDic, eDicNew, volfrac, xSelec)
                volfracbase = volfracbase + adapVolfrac
        # 3D Plot works but this one takes too much time
        if dispResultIsActive:
            print("Start plotting Display")
            surf = ExportTopoFile.SurfaceTopo(elemDic)
            triMesh = surf.get_triangle_surface_reduced(xSelec, eDic)
            triNumber = len(triMesh)
            stlExpo = ExportTopoFile.STLFile(triMesh)
            stlExpo.write_stl_file("./STLResults/ResultSTL" +
                                      str(iteration) + ".stl")
            try:
                bpy.ops.import_mesh.stl(filepath="./STLResults/ResultSTL" +
                                          str(iteration) + ".stl")
            except:
                pass
            if triNumber == 0:
                continue
            print("Number of triangles {}".format(triNumber))
            try:
                '''

                pyplot.ion()

                stlExpo.write_stl_file("./STLResults/ResultSTL" +
                                       str(iteration) + ".stl")
                # Create a new plot
                fig = pyplot.figure()
                axes = mplot3d.Axes3D(fig)
                # Load the STL files and add the vectors to the plot
                your_mesh = mesh.Mesh.from_file("./STLResults/ResultSTL" +
                                            str(iteration) + ".stl")
                axes.add_collection3d(mplot3d.art3d.Poly3DCollection(
                                                        your_mesh.vectors))
                # Auto scale to the mesh size
                scale = your_mesh.points.flatten(-1)
                axes.auto_scale_xyz(scale, scale, scale)
                # Show the plot to the screen
                pyplot.draw(fig)
                '''
                print ("Start show result plot")


            except:
                print("Plot is build up")

    print ("Export results are in TopoResults.inp")
    OutputFileName = "ResultDen.inp"
    if StructIsOutActive:
        resFile = jobNameS + ".inp"
    elif ThermalOutIsActive:
        resFile = jobNameT + ".inp"
    os.rename(resFile, OutputFileName)
    if mExpoInpIsActive:
        inpMeshFile = ExportTopoFile.ExportInpMesh("ResultFEMesh.inp", elemDic)
        inpMeshFile.set_output_mesh_reducte_by_density(xSelec, eDic)
    if mExpoStlIsActive:
        print ("Start stl export")
        surf = ExportTopoFile.SurfaceTopo(elemDic)
        triMesh = surf.get_triangle_surface_reduced(xSelec, eDic)
        print("Number of triangles {}".format(len(triMesh)))
        stlExpo = ExportTopoFile.STLFile(triMesh)
        stlExpo.write_stl_file("ResultSTL.stl")
        bpy.ops.import_mesh.stl(filepath="ResultSTL.stl")
    print (("Calculation is finished: Density mesh is saved in {}".format
                                                      (OutputFileName)))
