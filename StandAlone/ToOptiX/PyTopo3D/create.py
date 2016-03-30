'''The following program uses any fem-program with an inputdeck for topology optimisation

There are several classes which are needed for the initializing of the nodes and elements.
If you want to add a fem-program which does not exist, just implement an ascci-file. And
change the output ascci.
The whole optimisation process works with several dictonarys in which are nodes and elements
are saved.

Source code:
             Name: Denk, Martin
             Date: 10.2015
             Accronym: DMST
'''

# Global lib
from logging import *
import os
from datetime import *
# Local lib
from PhysicalSettings import *

def write_solve_file_head(solverFile):
    '''The following part creates the head of the solverdeck

    I: IO-txtobject: File which should solved
    '''
    solverFile.write("** Topology optimisation master thesis \n")
    solverFile.write("** Code: DMST, Martin, Denk, Apworks \n")
    solverFile.write("** Date: " + str(date.today()) + " \n")

def define_material_base(solverFile):
    Aluminium = Material()
    Aluminium.set_eModul(71000)
    Aluminium.set_pRatio(0.33)
    Aluminium.set_density(2.7E-09)
    Aluminium.set_name("Aluminium6061")
    Aluminium.writeCCXAbaqus(solverFile)

def define_boundary(solverFile, boundNodeSet):
    '''The following part creates the material settings.

    I: IO-txtobject: File which should solved
    '''
    modelBound = Boundary()
    modelBound.set_bound_u_dirichlet(boundNodeSet, [1,2,3])
    #modelBound.set_bound_u_dirichlet([13, 24, 101, 302, 403], [1])
    #modelBound.set_bound_temp([20, 41, 5, 1], 10)
    modelBound.boundary_write_in_file(solverFile)

def define_load(solverFile):
    '''The following part creates the material settings.

    I: IO-txtobject: File which should solved
    '''
    #tempLoad = Load()
    #tempLoad.set_temp_load_konst_value([33, 21, 42, 51], 20)
    #tempLoad.set_temp_load_list_value([1, 2, 9, 5], [10, 15, 12, 24])
    #tempLoad.temp_load_write_in_file(solverFile)
    forceLoad = Load()
    forceLoad.set_force_load([2, 3],1000, "y")
    forceLoad.force_load_write_in_file(solverFile)


def define_inertial_condition(solverFile):

    icModel = InertialCondition()
    icModel.set_temperature_all(20)
    icModel.writeCCXAbaqus(solverFile)


def define_output_request(solverFile):
    '''The following part creates the material settings.

    I: IO-txtobject: File which should solved
    '''
    outputElNode = OutputRequest()
    #outputElNode.set_output_node(["E"])
    outputElNode.set_output_node_Dat(["U"])
    outputElNode.set_output_elem_Dat(["ENER"])
    outputElNode.set_output_elem_Frd(["E,ENER, S"])
    outputElNode.output_write_in_file(solverFile)

def define_step(solverFile, boundNodeSet):

    solverFile.write("*Step, name=Step-1, nlgeom=NO\n")
    solverFile.write("*Static\n")
    solverFile.write("1., 1., 1e-05, 1.\n")
    define_boundary(solverFile, boundNodeSet)
    define_load(solverFile)
    define_output_request(solverFile)
    solverFile.write("*End Step\n")

def define_node_elem_sets(nDic, eDic):

    workSet = NodeElemSet(eDic,nDic)
    boundNodeSet = workSet.get_nodes_between_planes(-1, 1, "z")
    #loadNodeSet = workSet.get_nodes_between_planes(0, 10, "y")
    return (boundNodeSet)

def define_solid_section_base(solverFile):

    solverFile.write("*Solid Section, ELSET=EALL, Material = Aluminium6061\n")

def read_calculix_base(jobName):
    resultFileNameFrd =  jobName + ".frd"
    resultFileNameDat =  jobName + ".dat"
    boundResult = Result()
    boundResult.add_result_from_file_dat_disp(resultFileNameDat, "U")
    boundDisp = boundResult.get_disp()
    #totalStrain = strainResult.get_total_strain()
    #meanStrain = strainResult.get_mean_strain()
    #return totalStrain, meanStrain
    return boundDisp

def main_program():
    '''The main function leads all nessecarry parts

    '''
    inputFileName = "Input.inp"
    jobName = "transOne"
    transFileName = jobName + ".inp"
    #Linux Path
    calculixPath = "/usr/local/bin/ccx"
    #Windows Path
    #calculixPath = "C:/Users/mdenk/Desktop/bConverged/CalculiX/ccx/ccx.exe"
    # Checks if an old log file is in the current folder and delets it
    if(os.access("main.log", os.F_OK)):
        os.remove("main.log")

    if(os.access(calculixPath, os.F_OK)):
        print "Calculix is found"
        print "Translation of an abaqus file"
    basicConfig(filename = "main.log", level = DEBUG)
    info("Logfile for the main process")
    info("Sourcecode written by Denk, Martin (DMST)")
    info("_____Date: "+ str(date.today()) +"______")
    info("Start reading the input file")
    # Creating object FEMModelNodesElement
    # Imports nodes and elements from a calculix inputfile
    # Extracting a node dictonary and element dictonary of all IDs
    TopoModel = NodesElement()
    TopoModel.add_element_node_from_file(inputFileName, "Calculix")
    nDic = TopoModel.get_node_dic()
    eDic = TopoModel.get_elem_dic()
    if len(nDic) == 0:
        error("No nodes are initialized")
    else:
        info("Number of nodes:" + str(len(nDic)))
    if len(eDic) == 0:
        logging.error("No elements are initialized")
    else:
        info("Number of elements:" + str(len(eDic)))
    boundDisp = {}
    transFile = open(transFileName, "w")
    # Calling methods for creating a solver deck (Abaqus, Calculix)
    boundNodeSet = define_node_elem_sets(nDic, eDic)
    write_solve_file_head(transFile)
    define_material_base(transFile)
    TopoModel.elem_node_write_in_file(transFile)
    define_solid_section_base(transFile)
    define_step(transFile, boundNodeSet)
    transFile.close()

main_program()
