# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-


import math


def delete_empty_list_elements(inputList):
    listWithoutEmptyElem = []
    for listElem in inputList:
        if listElem != "":
            listWithoutEmptyElem.append(listElem)
    return listWithoutEmptyElem


class Result:

    def __init__(self):
        self.strain = {}
        self.strainEXX = {}
        self.strainEYY = {}
        self.strainEZZ = {}
        self.strainEXY = {}
        self.strainEYZ = {}
        self.strainEZX = {}
        self.strainTotal = {}
        self.stressTotal = {}
        self.energyDens = {}
        self.disp = {}
        self.heatFlu = {}

    def get_total_strain(self):
        return self.strainTotal

    def get_total_stress(self):
        return self.stressTotal

    def get_mean_strain(self):
        sumStrain = 0
        numberCounter = 0
        #print self.strainTotal
        for elemID in self.strainTotal:
            sumStrain = sumStrain + self.strainTotal[elemID]
            numberCounter += 1
        return sumStrain / numberCounter

    def get_mean_energy_density(self):
        sumEnergy = 0
        numberCounter = 0
        #print self.strainTotal
        for elemID in self.energyDens:
            sumEnergy = sumEnergy + self.energyDens[elemID]
            numberCounter += 1
        return sumEnergy / numberCounter

    def get_energy_density(self):
        return self.energyDens

    def get_heat_flux(self):
        return self.heatFlu

    def get_disp(self):
        return self.disp

    def add_result_from_file_frd(self, resultFileName, resultType):
        readingResultsIsActive = False
        resultsAreReading = False
        inputFile = open(resultFileName, "r")
        for line in inputFile:
            words = line[0:-1].split(" ")
            words = delete_empty_list_elements(words)
            if len(words) < 2:
                continue
            if resultType == "E":
                if readingResultsIsActive and words[0] == "-1":
                    resultsAreReading = True
                    # Reading resultline
                    elementID = int(line[3:13])
                    self.strainEXX[elementID] = float(line[13:25])
                    self.strainEYY[elementID] = float(line[25:37])
                    self.strainEZZ[elementID] = float(line[37:49])
                    self.strainEXY[elementID] = float(line[49:61])
                    self.strainEYZ[elementID] = float(line[61:73])
                    self.strainEZX[elementID] = float(line[73:85])
                    self.strainTotal[elementID] = math.sqrt(
                        self.strainEXX[elementID] ** 2 +
                        self.strainEYY[elementID] ** 2 +
                        self.strainEZZ[elementID] ** 2)
                # Activation Part of resultreading
                if words[1] == "TOSTRAIN":
                    readingResultsIsActive = True
                if words[1] == "EXX":
                    readingResultsIsActive = True
                if resultsAreReading and words[0] != "-1":
                    resultsAreReading = False
                    readingResultsIsActive = False

    def add_result_from_file_dat(self, resultFileName, resultType):
        ''' The following part saves the results into dictioanrys

        I: IO-Object: Filename in wich are the results setted
        I: String: Type of result which should selected
        '''
        readingResultsIsActive = False
        inputFile = open(resultFileName, "r")
        spaceLineCount = 0
        for line in inputFile:
            words = line[0:-1].split(" ")
            words = delete_empty_list_elements(words)
            if len(words) < 2 and readingResultsIsActive:
                spaceLineCount = spaceLineCount + 1
            if spaceLineCount == 2:
                readingResultsIsActive = False
                spaceLineCount = 0
            if len(words) < 2:
                continue
            # Part for reading the energy density
            if resultType == "ENER":
                if readingResultsIsActive:
                    elemID = int(words[0])
                    nodeID = int(words[1])
                    energDensity = float(words[2])
                    if nodeID == 1:
                        self.energyDens[elemID] = energDensity
                    else:
                        self.energyDens[elemID] = self.energyDens[elemID]\
                                                  + energDensity
                # Activation Part of resultreading
                if (words[0] == "internal" and words[1] == "energy" and
                       words[2] == "density"):
                    readingResultsIsActive = True
            # Part for reading the energy density
            if resultType == "HFL":
                if readingResultsIsActive:
                    elemID = int(words[0])
                    nodeID = int(words[1])
                    heatFluxX = float(words[2])
                    heatFluxY = float(words[3])
                    heatFluxZ = float(words[4])
                    heatFlux = (heatFluxX ** 2 + heatFluxY ** 2 + heatFluxZ ** 2) ** 0.5 
                    if nodeID == 1:
                        self.heatFlu[elemID] = heatFlux
                    else:
                        self.heatFlu[elemID] = self.heatFlu[elemID]\
                                                  + heatFlux
                # Activation Part of resultreading
                if (words[0] == "heat" and words[1] == "flux"):
                    readingResultsIsActive = True
            # Part for reading temperature values
            if resultType == "NT":
                if readingResultsIsActive:
                    nodeID = int(words[0])
                    tempVal = float(words[1])
                    self.disp[nodeID] = [tempVal]
               # Activation Part of resultreading
                if (words[0] == "temperatures"):
                    readingResultsIsActive = True
            # Part for reading the displacements
            if resultType == "U":
                if readingResultsIsActive:
                    nodeID = int(words[0])
                    xDisp = float(words[1])
                    yDisp = float(words[2])
                    zDisp = float(words[3])
                    self.disp[nodeID] = [xDisp, yDisp, zDisp]
               # Activation Part of resultreading
                if (words[0] == "displacements"):
                    readingResultsIsActive = True
            if resultType == "S":
                if readingResultsIsActive:
                    elemID = int(words[0])
                    nodeID = int(words[1])
                    sxx = float(words[2])
                    syy = float(words[3])
                    szz = float(words[4])
                    sxy = float(words[5])
                    sxz = float(words[6])
                    syz = float(words[7])
                    misesStress = sxx * sxx + syy * syy + szz * szz \
                                - sxx * syy - sxx * szz - syy * szz \
                                + 3 * (sxy * sxy + sxz * sxz + syz * syz)
                    if nodeID == 1:
                        self.stressTotal[elemID] = misesStress ** 0.5
                    else:
                        self.stressTotal[elemID] = self.stressTotal[elemID]\
                                                  + misesStress ** 0.5
                # Activation Part of resultreading
                if (words[0] == "stresses"):
                    readingResultsIsActive = True
