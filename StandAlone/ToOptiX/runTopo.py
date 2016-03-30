# -*- coding: utf-8 -*-

# Importing tkinter as a grafic user interface
# Global libs
import os
try:
    from Tkinter import *
##    import tkMessageBox as tkmsg
except:
    from tkinter import *
##    import tkinter.messagebox as tkmsg
# Local libs
from PyTopo3D import *
from PyTopo2D import *


def get_path(Type):
    ''' Path
    '''
# Install paths --------------
    if Type == "Octave":
        return "/usr/bin/octave"
    if Type == "CCX":
        return "/usr/bin/ccx"
    if Type == "Abaqus":
        return "/usr/local/bin/abaqus"
# Install paths --------------


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


def help_theoretical():
    print("Theorie: http://www.topopt.dtu.dk/")


def help_programming():
    print("Quellcode Hilfe: denkmartin@web.de")


def file_infomration():
    print ("Bei einer 2D-Analyse wird das Ergebnis als Grafik geplottet")
    print ("Bei einer 3D-Analyse müssen die Inputdecks mit")
    print ("InputS.inp ---> Strukturproblem")
    print ("InputT.inp ---> Thermalproblem")
    print ("In den Ordner in der das Pythonskript istgespeichert werden.")
    print ("Für beide Probleme muss das gleiche Netz verwendet werden")
    print ("Als Ergebnis entsteht ein neues Inputdeck in dem Ordner.")
    print ("Die einzel definierten Materialsets zeigen das Ergebnis.")

def param_all():
    print("1, 2, 3, 4 Parameter:")
    print("Om_L / Om_D: Verhältnis zwischen Lösungsgebiet und Desinggebiet")
    print("p: Bestrafungsexponent (Empfehlung: zwischen 3 und 5)")
    print("r_min: Filterradius in mm  3D bzw. Anzahl an Elementen 2D")
    print("\n")


def param_3DCCX():
    print("1 Parameter:")
    print("Mat Sets: Anzahl an Materialsets")
    print("skal.: n_max: Maximale Iterationen mit Skalierung")
    print("konst: n_max: Maximale Iterationen mit konst. Werten nach skal.")
    print("\n")


def param_2D():
    print("2, 3. Parameter:")
    print("e_x: Anzahl an Elementen in x-Richtung")
    print("e_y: Anzahl an Elementen in y-Richtung")
    print("\n")


def param_3Doctave():
    print("4, Parameter:")
    print("e_z: Anzahl an Elementen in z-Richtung")
    print("\n")


def param_multi():
    print("MultiOpt, Parameter:")
    print("n_change: Optimierungsiteration ab der die Adaption statt findet")
    print("Om_LAD/ Om_D: Lösungsgebieterweiterung bei der Adaption")
    print("n_ad,max: Maximale Anzahl an wechselnden Adaptionen")
    print("g_struc: Gewichtungsfaktor bezüglich der Strukturantwort")
    print("\n")


def param_strat():
    print("a) Reine thermale Optimierung")
    print("b) Reine strukturelle Optimierung")
    print("c) Die Sensivitäten werden bei einr Gewichtung gewichtet")
    print("d) Es wird eine Adaption durchgeführt keine reine Gewichtung")
    print("e) Als Startentwurf wird eine Strukturoptimierung gewählt")
    print("f) Die adaptierte Lösung ist eine gewichtete Lösung")
    print("g) Es wird mehrmals Adaptiert: Thermal-Struktur-Thermal ...")
    print("1) Auswahl von Mittelwert oder Median bei der Gewichtung")
    print("1) Auswahl von SIMP oder BESO Verfahren")
    print("1) Ergebnisexport im inp-Format")
    print("1) Ergebnisnetz Export im stl-Format")
    print("1) Solverauswahl Abauqs oder CalculiX")
    print("\n")


def start_topo3d():
    ''' This function starts the 3D topology optimization in python
    '''
    penal = float(textPenal.get())
    rmin = float(textRmin.get())
    volfrac = float(textVolfrac.get())
    matSets = int(textMatSet.get())
    numbIter = int(textIteration.get())
    numbIterAfter = int(textIterationLast.get())

    # Settings for multi physic topo
    volRatioAdd = float(textvolfracAdd.get())
    adapIter = int(textadapIter.get())
    adapchangeIter = int(textadapChIT.get())
    wFacStruc = float(textweighFac.get())
    xSelec = float(textxSelec.get())
    # Check control parameter
    ther = intTher.get()
    struc = intStruc.get()
    sens = intSens.get()
    adap = intAdap.get()
    startStruc = intStartStruc.get()
    adapWeight = intAdapWeight.get()
    IterAdap = intIterAdap.get()
    # Checkboxes only 3D
    midVal = intMidvalue.get()
    simp = intSimp.get()
    mExpoInp = intMExpoInp.get()
    mExpoStl = intMExpoStl.get()
    solverType = intSolType.get()
    noDes = intNoDes.get()
    disp = intDisp.get()
    filt = intFilt.get()
    # Start topology opti
    ccxPath = get_path("CCX")
    abaPath = get_path("Abaqus")
    topo_start3d(volfrac, penal, rmin, matSets, numbIter, numbIterAfter,
                   adapchangeIter, volRatioAdd, adapIter,
                   wFacStruc, ther, struc, sens, adap,
                   startStruc, adapWeight, IterAdap, midVal, simp, mExpoInp,
                   mExpoStl, ccxPath, abaPath, solverType, xSelec, noDes, disp,
                filt)


def start_topo2d():
    ''' This function starts the 2D topology optimization in python
    '''
    penal = float(textPenal.get())
    rmin = float(textRmin.get())
    volfrac = float(textVolfrac.get())
    nelx = int(textNelx.get())
    nely = int(textNely.get())
    if rmin <= 1:
        rmin = 1
    topo_start2d(nelx, nely, volfrac, penal, rmin)


def start_topo2d_m():
    ''' This function starts the 2D topology optimization in octave
    '''
    penal = float(textPenal.get())
    rmin = float(textRmin.get())
    volfrac = float(textVolfrac.get())
    nelx = int(textNelx.get())
    nely = int(textNely.get())
    if rmin <= 1:
        rmin = 1

    # Settings for multi physic topo
    volRatioAdd = float(textvolfracAdd.get())
    adapIter = int(textadapIter.get())
    adapchangeIter = int(textadapChIT.get())
    wFacStruc = float(textweighFac.get())
    # Check control parameter
    ther = intTher.get()
    struc = intStruc.get()
    sens = intSens.get()
    adap = intAdap.get()
    startStruc = intStartStruc.get()
    adapWeight = intAdapWeight.get()
    IterAdap = intIterAdap.get()
    ##cpSensA = intCpSensA.get()
    # File of the template of the matlabfile
    # It rewrites the octavefile so it starts with the setting
    iFilePath = "./MTopo2D/multi_topo.m"
    solveFilePath = "./MTopo2D/multi_topo_temp.m"
    inputFile = open(iFilePath, "r")
    solveFile = open(solveFilePath, "w")
    for line in inputFile:
        words = line[0:-1].split(" ")
        words = delete_empty_list_elements(words)
        if len(words) >= 1:
            if words[0][0:10] == "multi_topo":
                line = "multi_topo(" + str(nelx) + "," + str(nely) + "," + \
                 str(volfrac) + "," + str(penal) + "," + str(rmin) + \
                "," + str(adapchangeIter) + "," + str(volRatioAdd) + "," \
                 + str(adapIter) + "," + str(wFacStruc) + "," + str(ther) + \
                "," + str(struc) + "," + \
                str(sens) + "," + str(adap) + "," + str(startStruc)\
                + "," + str(adapWeight) + "," + str(IterAdap) + ")"
        solveFile.write(line)
    solveFile.close()
    inputFile.close()
    octavePath = "/usr/bin/octave "
    os.popen(octavePath + solveFilePath)


def start_topo3d_m():
    ''' This function starts the 3D topology optimization in octave
    '''
    print "result will disaper in 10 sec"
    penal = float(textPenal.get())
    rmin = float(textRmin.get())
    volfrac = float(textVolfrac.get())
    nelx = int(textNelx.get())
    nely = int(textNely.get())
    nelz = int(textNelz.get())
    if rmin <= 1:
        rmin = 1
    iFilePath = "./MTopo3D/topo3d.m"
    solveFilePath = "./MTopo3D/topo3d_temp.m"
    octavePath = "octave "
    inputFile = open(iFilePath, "r")
    solveFile = open(solveFilePath, "w")
    for line in inputFile:
        words = line[0:-1].split(" ")
        words = delete_empty_list_elements(words)
        if len(words) >= 1:
            if words[0][0:5] == "top3d":
                line = "top3d(" + str(nelx) + "," + str(nely) + "," + \
                     str(nelz) + "," + str(volfrac) + "," + str(penal) + \
                     "," + str(rmin) + ")"
        solveFile.write(line)
    solveFile.close()
    inputFile.close()
    os.popen(octavePath + solveFilePath)


class TopoToolbar:
    ''' This class creates the toolbar (buttons with headers)
    '''
    def __init__(self, root):
        self.bg_color = "blue"
        self.fg_color = "cyan"
        self.master = root

    def set_bg_color(self, color):
        self.bg_color = color

    def set_fg_color(self, color):
        self.fg_color = color

    def create_toolbar(self):
        toolbar = Frame(self.master, bg=self.bg_color)
        buttonLabel = Label(toolbar, text="               ", bg=self.bg_color,
                         fg=self.fg_color)
        buttonLabel.grid(row=1, column=2, sticky=W)

        buttonLabelUe = Label(toolbar,
                         text="Topologie Multi- Physik", bg=self.bg_color,
                         fg=self.fg_color)
        buttonLabelUe.grid(row=0, column=0, columnspan=2)

        buttonLabelUe2 = Label(toolbar,
                    text="Topologie Beispiele", bg=self.bg_color,
                    fg=self.fg_color)
        buttonLabelUe2.grid(row=0, column=3, columnspan=2)

        start3DButton = Button(toolbar, text="1) 3D-Multi-Physik Inputdecks",
                 command=start_topo3d, fg=self.fg_color, bg=self.bg_color)
        start3DButton.grid(row=1, column=0, sticky=E)
        start2DButton = Button(toolbar, text="3) 2D-Struktur Beispiel",
                 command=start_topo2d, fg=self.fg_color, bg=self.bg_color)
        start2DButton.grid(row=1, column=3, sticky=E)
        start2DOctaveButton = Button(toolbar,
                 text="2) 2D-Multi-Physik Beispiele",
                 command=start_topo2d_m, fg=self.fg_color, bg=self.bg_color)
        start2DOctaveButton.grid(row=1, column=1, sticky=E)
        start2DOctaveButton = Button(toolbar, text="4) 3D-Struktur Beispiel",
                 command=start_topo3d_m, fg=self.fg_color, bg=self.bg_color)
        start2DOctaveButton.grid(row=1, column=4, sticky=E)
        toolbar.pack(side=TOP, fill=X)


class TopoMenu(TopoToolbar):

    def __init__(self, root):
        self.master = root
        self.bg_color = "blue"
        self.fg_color = "cyan"

    def set_bg_color(self, color):
        self.bg_color = color

    def set_fg_color(self, color):
        self.fg_color = color

    def create_menue(self):
        # Main Menue
        mainMenu = Menu(self.master, bg=self.bg_color, fg=self.fg_color)
        self.master.config(menu=mainMenu)
        subMenu = Menu(mainMenu, bg=self.bg_color, fg=self.fg_color)
        parMenu = Menu(mainMenu, bg=self.bg_color, fg=self.fg_color)
        editMenu = Menu(mainMenu, bg=self.bg_color, fg=self.fg_color)
        # Cascades
        mainMenu.add_cascade(label="Datei", menu=subMenu)
        mainMenu.add_cascade(label="Parameter Info", menu=parMenu)
        mainMenu.add_cascade(label="Hilfe", menu=editMenu)

        # Different commandos
        subMenu.add_command(label="File Info", command=file_infomration)
        subMenu.add_separator()
        subMenu.add_command(label="Exit", command=mainMenu.quit)
        editMenu.add_command(label="Theorie", command=help_theoretical)
        editMenu.add_command(label="Programmierung", command=help_programming)

        parMenu.add_command(label="Parameter 1, 2, 3, 4", command=param_all)
        parMenu.add_command(label="Parameter 1", command=param_3DCCX)
        parMenu.add_command(label="Parameter 2, 3", command=param_2D)
        parMenu.add_command(label="Parameter 4", command=param_3Doctave)
        parMenu.add_command(label="Parameter Strategie", command=param_strat)
        parMenu.add_command(label="Parameter MultiOpt", command=param_multi)


class TopoLabel(TopoToolbar):

    def __init__(self, frame):
        self.topFrame = frame
        self.bg_color = "blue"
        self.fg_color = "cyan"

    def set_bg_color(self, color):
        self.bg_color = color

    def set_fg_color(self, color):
        self.fg_color = color

    def create_label(self):
        # Labeldefinition
        bothInputLabel = Label(self.topFrame, text="1) 2) 3) 4)",
                                              bg=self.bg_color, fg=self.fg_color)
        checkInputLabel = Label(self.topFrame, text="1) 2) Strategie",
                                              bg=self.bg_color, fg=self.fg_color)
        threeDInputLabel = Label(self.topFrame, text="1)",
                                              bg=self.bg_color, fg=self.fg_color)
        twoDInputLabel = Label(self.topFrame, text="2) 3)",
                                              bg=self.bg_color, fg=self.fg_color)
        threeDMInputLabel = Label(self.topFrame, text="4)",
                                              bg=self.bg_color, fg=self.fg_color)
        volfracLabel = Label(self.topFrame, text="Om_L / Om_D ",
                            bg=self.bg_color, fg=self.fg_color)
        penalLabel = Label(self.topFrame, text="p", bg=self.bg_color,
                          fg=self.fg_color)
        rminLabel = Label(self.topFrame, text="r_min", bg=self.bg_color,
                         fg=self.fg_color)
        matSetLabel = Label(self.topFrame, text="Mat Sets ",
                                         bg=self.bg_color, fg=self.fg_color)
        iterationLabel = Label(self.topFrame, text="skal.: n_max",
                                           bg=self.bg_color, fg=self.fg_color)
        iterationLastLabel = Label(self.topFrame, text="konst: n_max",
                                           bg=self.bg_color, fg=self.fg_color)

        nelxLabel = Label(self.topFrame, text="e_x", bg=self.bg_color,
                         fg=self.fg_color)
        nelyLabel = Label(self.topFrame, text="e_y", bg=self.bg_color,
                         fg=self.fg_color)
        nelzLabel = Label(self.topFrame, text="e_z", bg=self.bg_color,
                         fg=self.fg_color)
        # New input for additional topo "MultiOpt"
        coupelLabel = Label(self.topFrame, text="MultiOpt", bg=self.bg_color,
                         fg="white")
        adapChLabel = Label(self.topFrame, text="d,f,g) n_change",
                           bg=self.bg_color, fg=self.fg_color)
        volRatioAddLabel = Label(self.topFrame, text="d,f,g) Om_LAD / Om_D",
                                bg=self.bg_color, fg=self.fg_color)
        adapIterLabel = Label(self.topFrame, text="g) n_ad,max",
                             bg=self.bg_color, fg=self.fg_color)

        weighFacLabel = Label(self.topFrame, text="c,f) g_struc:",
                             bg=self.bg_color, fg=self.fg_color)
        xSelecLabel = Label(self.topFrame, text="d) f) g) Grenzdichte:",
                             bg=self.bg_color, fg=self.fg_color)
        # Checklabel
        checkInputLabel.grid(row=0, column=2, columnspan=2)
        coupelLabel.grid(row=0, column=4, columnspan=2)
        # Parameter 1, 2, 3, 4
        bothInputLabel.grid(row=0, column=1)
        volfracLabel.grid(row=1, sticky=E)
        penalLabel.grid(row=2, sticky=E)
        # Parameter 1
        threeDInputLabel.grid(row=3, column=1)
        matSetLabel.grid(row=4, sticky=E)
        iterationLabel.grid(row=5, sticky=E)
        iterationLastLabel.grid(row=6, sticky=E)
        # Parameter 2,3
        twoDInputLabel.grid(row=7, column=1)
        nelxLabel.grid(row=8, sticky=E)
        nelyLabel.grid(row=9, sticky=E)
        rminLabel.grid(row=10, sticky=E)
        # Parameter 4
        threeDMInputLabel.grid(row=11, column=1)
        nelzLabel.grid(row=12, sticky=E)
       # Adaption parameter
        adapChLabel.grid(row=1, column=4, sticky=W)
        volRatioAddLabel.grid(row=2, column=4, sticky=W)
        adapIterLabel.grid(row=4, column=4, sticky=W)
        weighFacLabel.grid(row=5, column=4, sticky=W)
        xSelecLabel.grid(row=6, column=4, sticky=W)

class TopoEntry(TopoToolbar):

    def __init__(self, frame):
        self.topFrame = frame

    def create_entry(self, textVolfrac, textPenal, textRmin, textMatSet,
           textIteration, textNelx, textNely, textNelz, textIterationLast,
           textadapChIT, textvolfracAdd, textadapIter, textweighFac,
           textxSelec):
        #Creating entrys for the standard settings
        matSetEntry = Entry(self.topFrame, textvariable=textMatSet)
        iterationEntry = Entry(self.topFrame, textvariable=textIteration)
        iterationLastEntry = Entry(self.topFrame,
                                  textvariable=textIterationLast)
        volfracEntry = Entry(self.topFrame, textvariable=textVolfrac)
        penalEntry = Entry(self.topFrame, textvariable=textPenal)
        rminEntry = Entry(self.topFrame, textvariable=textRmin)
        NelxEntry = Entry(self.topFrame, textvariable=textNelx)
        NelyEntry = Entry(self.topFrame, textvariable=textNely)
        NelzEntry = Entry(self.topFrame, textvariable=textNelz)
        # Creating entrys of the coupeled settings
        adapChEntry = Entry(self.topFrame, textvariable=textadapChIT)
        volRatioAddEntry = Entry(self.topFrame, textvariable=textvolfracAdd)
        adapIterEntry = Entry(self.topFrame, textvariable=textadapIter)
        weighFacEntry = Entry(self.topFrame, textvariable=textweighFac)
        xSelecEntry = Entry(self.topFrame, textvariable=textxSelec)
        # Position of the standard settings
        volfracEntry.grid(row=1, column=1)
        penalEntry.grid(row=2, column=1)
        matSetEntry.grid(row=4, column=1)
        iterationEntry.grid(row=5, column=1)
        iterationLastEntry.grid(row=6, column=1)
        NelxEntry.grid(row=8, column=1)
        NelyEntry.grid(row=9, column=1)
        rminEntry.grid(row=10, column=1)
        NelzEntry.grid(row=12, column=1)
        # Position of the coupeled settings
        adapChEntry.grid(row=1, column=5, sticky=E)
        volRatioAddEntry.grid(row=2, column=5, sticky=E)
        adapIterEntry.grid(row=4, column=5, sticky=E)
        weighFacEntry.grid(row=5, column=5, sticky=E)
        xSelecEntry.grid(row=6, column=5, sticky=E)
        # Default Values for the entrys
        volfracEntry.insert(0, 0.4)
        penalEntry.insert(0, 3)
        rminEntry.insert(0, 2)
        matSetEntry.insert(0, 20)
        iterationEntry.insert(0, 50)
        iterationLastEntry.insert(0, 20)
        NelxEntry.insert(0, 40)
        NelyEntry.insert(0, 20)
        NelzEntry.insert(0, 1)
        # Values for the coupeled settings
        adapChEntry.insert(0, 20)
        volRatioAddEntry.insert(0, 0.2)
        adapIterEntry.insert(0, 6)
        weighFacEntry.insert(0, 0.5)
        xSelecEntry.insert(0, 0.9)


class CheckBoxes(TopoToolbar):

    def __init__(self, frame):
        self.topFrame = frame
        self.bg_color = "blue"
        self.fg_color = "cyan"

    def set_bg_color(self, color):
        self.bg_color = color

    def set_fg_color(self, color):
        self.fg_color = color

    def create_checkbox(self, intTher, intStruc, intSens, intAdap,
                     intStartStruc, intAdapWeight, intIterAdap, intCpSensA,
                     intMidvalue, intSimp, intMExpoInp, intMExpoStl,
                     intSolType, intNoDes, intDisp, intFilt):

        cbThermAna = Checkbutton(self.topFrame, text="a) Thermal  ",
                                variable=intTher, bg=self.bg_color,
                                fg=self.fg_color)
        cbThermAna.grid(row=1, column=3, sticky=W)
        cbStrucAna = Checkbutton(self.topFrame, text="b) Struktur  ",
                                 variable=intStruc, bg=self.bg_color,
                                 fg=self.fg_color)
        cbStrucAna.grid(row=2, column=3, sticky=W)
        cbSensiv = Checkbutton(self.topFrame, text="c) Sensivitäten  ",
                                 variable=intSens, bg=self.bg_color,
                                 fg=self.fg_color)
        cbSensiv.grid(row=3, column=3, sticky=W)
        cbAdaption = Checkbutton(self.topFrame, text="d) Adaption  ",
                                 variable=intAdap, bg=self.bg_color,
                                 fg=self.fg_color)
        cbAdaption.grid(row=4, column=3, sticky=W)
        cbStartPhys = Checkbutton(self.topFrame,
                            text="e) Startentwurf Struktur  ",
                            variable=intStartStruc, bg=self.bg_color,
                            fg=self.fg_color)
        cbStartPhys.grid(row=5, column=3, sticky=W)
        cbAdaptWeigh = Checkbutton(self.topFrame,
                            text="f) Adaption Gewichtung  ",
                            variable=intAdapWeight, bg=self.bg_color,
                            fg=self.fg_color)
        cbAdaptWeigh.grid(row=6, column=3, sticky=W)
        cbIterativeAdap = Checkbutton(self.topFrame,
                            text="g) Iterative Adaption  ",
                            variable=intIterAdap, bg=self.bg_color,
                            fg=self.fg_color)
        cbIterativeAdap.grid(row=7, column=3, sticky=W)
        # Mid value checkbox
        cbMidvalue = Checkbutton(self.topFrame,
                            text="1) Mittelwert",
                            variable=intMidvalue, bg=self.bg_color,
                            fg=self.fg_color)
        cbMidvalue.grid(row=8, column=3, sticky=W)
        # Simp checkbox
        cbSimp = Checkbutton(self.topFrame,
                            text="1) SIMP",
                            variable=intSimp, bg=self.bg_color,
                            fg=self.fg_color)
        cbSimp.grid(row=9, column=3, sticky=W)
        # No Desingspace is active
        cbnoDes = Checkbutton(self.topFrame,
                            text="1) Nicht zu optimierende Bereiche aktiv",
                            variable=intNoDes, bg=self.bg_color,
                            fg=self.fg_color)
        cbnoDes.grid(row=10, column=3, sticky=W)
        # Mesh export stl checkbox
        cbMExpoStl = Checkbutton(self.topFrame,
                            text="1) Netz Export (stl)",
                            variable=intMExpoStl, bg=self.bg_color,
                            fg=self.fg_color)
        cbMExpoStl.grid(row=11, column=3, sticky=W)
        # Mesh export inp checkbox
        cbMExpoInp = Checkbutton(self.topFrame,
                            text="1) Netz Export (inp)",
                            variable=intMExpoInp, bg=self.bg_color,
                            fg=self.fg_color)
        cbMExpoInp.grid(row=12, column=3, sticky=W)
        # Solvertype
        cbSolType = Checkbutton(self.topFrame,
                            text="1) Solver Abaqus",
                            variable=intSolType, bg=self.bg_color,
                            fg=self.fg_color)
        cbSolType.grid(row=13, column=3, sticky=W)
        # Display
        cbDisp = Checkbutton(self.topFrame,
                            text="1) Display und STL jede It. (ca. 30% mehr Zeit)",
                            variable=intDisp, bg=self.bg_color,
                            fg=self.fg_color)
        cbDisp.grid(row=14, column=3, sticky=W)
        # Display
        cbFilt = Checkbutton(self.topFrame,
                            text="1) Filter ist aktiv",
                            variable=intFilt, bg=self.bg_color,
                            fg=self.fg_color)
        cbFilt.grid(row=15, column=3, sticky=W)


# Main Menue
bgColor = "white"
fgColor = "black"
master = Tk()
master.title("Topology Optimization")
master.config(bg=bgColor)
#
#photo2 = PhotoImage(file="./GUI/Strategie.png")
photo = PhotoImage(file="./GUI/Beispiel.png")
label = Label(master, image=photo, bg=bgColor)
#label2 = Label(master, image=photo2, bg=bgColor)
label.pack()
#label2.pack()
#master.iconbitmap(default="test3.bmp")
TopoTBar = TopoToolbar(master)
TopoTBar.set_bg_color(bgColor)
TopoTBar.set_fg_color(fgColor)
TopoTBar.create_toolbar()
# Statusbar
status = Label(master,
      text="Erstellt 2015 von Martin, Denk, DMST, unterstüzt von APWorks GmbH",
      bd=1, relief=SUNKEN, anchor=W, bg=bgColor, fg=fgColor)
status.pack(side=BOTTOM, fill=X)
# Menue bar with default values
MenueTBar = TopoMenu(master)
MenueTBar.set_bg_color(bgColor)
MenueTBar.set_fg_color(fgColor)
MenueTBar.create_menue()
# Frame with the entry
topFrame = Frame(master, bg=bgColor)
topFrame.pack(side=BOTTOM, )
# Label definition
topoLabel = TopoLabel(topFrame)
topoLabel.set_bg_color(bgColor)
topoLabel.set_fg_color(fgColor)
topoLabel.create_label()
# Entry definition
topoEntry = TopoEntry(topFrame)

# Global Variables for entrys
textVolfrac = StringVar()
textPenal = StringVar()
textRmin = StringVar()
textMatSet = StringVar()
textIteration = StringVar()
textIterationLast = StringVar()
textNelx = StringVar()
textNely = StringVar()
textNelz = StringVar()

textadapChIT = StringVar()
textvolfracAdd = StringVar()
textadapIter = StringVar()
textweighFac = StringVar()
textxSelec = StringVar()

topoEntry.create_entry(textVolfrac, textPenal, textRmin, textMatSet,
           textIteration, textNelx, textNely, textNelz, textIterationLast,
           textadapChIT, textvolfracAdd, textadapIter, textweighFac, textxSelec)
# Global Variables for checkboxes
intTher = IntVar()
intStruc = IntVar()
intSens = IntVar()
intAdap = IntVar()
intStartStruc = IntVar()
intAdapWeight = IntVar()
intIterAdap = IntVar()
intCpSensA = IntVar()
intMidvalue = IntVar()
intSimp = IntVar()
intMExpoInp = IntVar()
intMExpoStl = IntVar()
intSolType = IntVar()
intNoDes = IntVar()
intDisp = IntVar()
intFilt = IntVar()

# Checkboxes
topoCheckBox = CheckBoxes(topFrame)
topoCheckBox.set_bg_color(bgColor)
topoCheckBox.set_fg_color(fgColor)
topoCheckBox.create_checkbox(intTher, intStruc, intSens, intAdap,
                     intStartStruc, intAdapWeight, intIterAdap, intCpSensA,
                     intMidvalue, intSimp, intMExpoInp, intMExpoStl,
                     intSolType, intNoDes, intDisp, intFilt)
master.mainloop()
