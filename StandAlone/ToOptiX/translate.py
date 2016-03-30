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
# Local lib
from PyTopo3D import *
#from DefineInput import *


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


def create_element_set(eDic, solverFile):
    solverFile.write("*Elset, elset=Eall \n")
    count8 = 0
    for elem in eDic:
        if count8 == 7:
            solverFile.write("\n")
            count8 = 0
        solverFile.write(str(elem) + ",")
        count8 += 1
    solverFile.write("\n")




def translate_aba_ccx(solverFileName, iFilePath):
    '''The following creates an inputdeck

    I: IO-txtobject: File which should solved
    I: Dictonary: Boundary with nodes
    '''
    generateIsActive = False
    writingIsActivated = False
    NodeReadingIsDone = False
    partIsActive = False
    surfaceIsActive = False
    surfSetList = []
    nDic, eDic = import_elements_nodes_as_dic(iFilePath)
    inputFile = open(iFilePath, "r")
    solveFile = open(solverFileName, "w")
    for line in inputFile:
        words = line[0:-1].split(" ")
        words = delete_empty_list_elements(words)
        if len(words) >= 1:
            if words[0][0] == "*":
                writingIsActivated = False
                generateIsActive = False
                surfaceIsActive = False
            #----
            # Model definition
            #----
            # Define a nodeset with all nodes
            if words[0][0:5] == "*Node" and not NodeReadingIsDone:
                solveFile.write("*Node, Nset=Nall\n")
                writingIsActivated = True
                NodeReadingIsDone = True
                continue
            # Define a elementset with all elements
            if words[0][0:8] == "*Element":
                writingIsActivated = True
            if words[0][0:5] == "*Part":
                partIsActive = True
            if len(words) >= 2:
                if words[0][0:4] == "*End" and words[1][0:4] == "Part":
                    partIsActive = False
            # Material section
            if words[0][0:9] == "*Material":
                writingIsActivated = True
            if words[0][0:9] == "*Elastic":
                writingIsActivated = True
            if words[0][0:14] == "*Conductivity":
                writingIsActivated = True
            # Node element set section
            if generateIsActive:
                word1 = words[0].split(",")
                startNode = int(word1[0])
                word1 = words[1].split(",")
                lastNode = int(word1[0])
                nodeInc = int(words[2])
                count8 = 0
                while startNode <= lastNode:
                    if count8 == 8:
                        count8 = 0
                        solveFile.write("\n")
                    solveFile.write(str(startNode) + ", ")
                    startNode = startNode + nodeInc
                    count8 += 1
                solveFile.write("\n")
            if words[0][0:5] == "*Nset":
                writingIsActivated = True
                for word in words:
                    if word[0:9] == "generate":
                        generateIsActive = True
                setName = words[1].split(",")
                if partIsActive:
                    setName = setName[0] + "Part"
                else:
                    setName = setName[0]
                solveFile.write(words[0] + " " + setName + "\n")
                continue
            if words[0][0:6] == "*Elset":
                writingIsActivated = True
                for word in words:
                    if word[0:9] == "generate":
                        generateIsActive = True
                setName = words[1].split(",")
                setSplitName = setName[0].split("=")
                if setSplitName[1][0:5] == "_Surf":
                    surfSetList.append(setSplitName[1])
                if partIsActive:
                    setName = setName[0] + "Part"
                else:
                    setName = setName[0]
                solveFile.write(words[0] + " " + setName + "\n")
                continue
            if generateIsActive:
                continue
            # Solid section definition
            if len(words) >= 2:
                if words[0][0:6] == "*Solid" and words[1][0:7] == "Section":
                    solveFile.write("*Solid Section, elset=Eall, " + words[3])
                    writingIsActivated = True
                    continue
            #----
            # History definition
            #----
            if words[0][0:5] == "*Step":
                writingIsActivated = True
                create_element_set(eDic, solveFile)
            if words[0][0:7] == "*Static":
                writingIsActivated = True
            if surfaceIsActive:
                surfName = words[0][0:-1]
                value = words[2]
                for elSurfName in surfSetList:
                    if "_" + surfName == elSurfName[0: len(surfName) + 1]:
                        pName = elSurfName[-1]
                        solveFile.write(elSurfName + ", P" + pName + ", " + value + "\n")
                continue
            if words[0][0:7] == "*Dsload":
                writingIsActivated = True
                surfaceIsActive = True
            if words[0][0:6] == "*Cload":
                writingIsActivated = True
                writingIsActivated = True
            if words[0][0:6] == "*Dflux":
                writingIsActivated = True
            if words[0][0:7] == "*Dsflux":
                writingIsActivated = True
                surfaceIsActive = True
            if words[0][0:10] == "*Boundary":
                writingIsActivated = True
            #if words[0][0:8] == "*Surface":
            #    writingIsActivated = True
            if len(words) >= 2:
                if words[0][0:5] == "*End" and words[1][0:5] == "Step":
                    writingIsActivated = True
                if words[0][0:5] == "*Heat" and words[1][0:8] == "Transfer":
                    writingIsActivated = True
                if words[0][0:3] == "*EL" and words[1][0:4] == "File":
                    writingIsActivated = True
                if words[0][0:3] == "*EL" and words[1][0:5] == "Print":
                    writingIsActivated = True
                if words[0][0:5] == "*Node" and words[1][0:5] == "Print":
                    writingIsActivated = True
                if words[0][0:5] == "*Node" and words[1][0:4] == "File":
                    writingIsActivated = True

            if writingIsActivated:
                solveFile.write(line)
    solveFile.close()
    inputFile.close()


def main():
    '''The main function calls the differen topo optimizations

    I: Double: Volumenratio
    I: Double: penalty exponent
    I: Integer: number of material sections
    I: Integer: number of maximum iterations
    '''
    # Used files for the optimization
    # Input file wich boundary, loads, elements ...
    iFilePath = "Input.inp"
    jobName = "transFile"
    solverFileName = jobName + ".inp"
    print "translation started"
    # FEM-translation part
    translate_aba_ccx(solverFileName, iFilePath)
    print "translation ended"


if __name__ == "__main__":
    # Default input parameters
    main()
