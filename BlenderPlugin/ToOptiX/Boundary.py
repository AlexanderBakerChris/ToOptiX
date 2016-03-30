# -*- coding: utf-8 -*-

class Boundary:

    def __init__(self):
        self.b_u_dirich = {}
        self.b_temp = {}
        self.b_disp = {}

    def set_bound_u_dirichlet(self, nSet, direction):
        for node in nSet:
            self.b_u_dirich[node] = direction

    def get_bound_u_dirichlet(self):
        return self.b_u_dirich
    def get_bound_temp(self):
        return self.b_temp

    def set_bound_temp(self, nSet, temperature):
        for node in nSet:
            self.b_temp[node] = temperature
    def set_disp_bound(self, bound_disp):
        self.b_disp = bound_disp
    def set_temp_bound(self, bound_disp):
        self.b_temp = bound_disp


    def boundary_write_in_file(self, solverFile):
        '''The following method reads an a file and extracts the nodes
         and elements

        O: Dictonary: With all nodes and their position
        O: Dictonary: With all elements and their node IDs
        '''
        solverFile.write("*Boundary \n")
        for node in self.b_u_dirich:
            for direction in self.b_u_dirich[node]:
                solverFile.write(str(node) + ", " + str(direction) + "\n")
        for node in self.b_temp:
            solverFile.write(str(node) + ", 11, 11, "  + \
                             str(self.b_temp[node][0]) + "\n")
        #print self.b_disp
        for node in self.b_disp:
            #print self.b_disp[node]
            solverFile.write(str(node) + ", 1,1,"  + str(self.b_disp[node][0]) + "\n")
            solverFile.write(str(node) + ", 2,2,"  + str(self.b_disp[node][1]) + "\n")
            solverFile.write(str(node) + ", 3,3,"  + str(self.b_disp[node][2]) + "\n")
