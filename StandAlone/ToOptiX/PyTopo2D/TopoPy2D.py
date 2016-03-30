# -*- coding: utf-8 -*-
# A 165 LINE TOPOLOGY OPTIMIZATION CODE BY NIELS AAGE AND VILLADS EGEDE JOHANSEN, JANUARY 2013
from __future__ import division
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve
from matplotlib import colors
import matplotlib.pyplot as plt
# MAIN DRIVER
def topo_start2d(nelx,nely,volfrac,penal,rmin):
    ft = 0
    print("Minimum compliance problem with OC")
    print("ndes: " + str(nelx) + " x " + str(nely))
    print("volfrac: " + str(volfrac) + ", rmin: " + str(rmin) + ", penal: " + str(penal))
    print("Filter method: " + ["Sensitivity based","Density based"][ft])
    # Max and min stiffness
    Emin = 1e-9
    Emax = 1.0
    # Degree of freedomes
    # For a 2D-problem 2 * (3 + 1) * (2 + 1) = 12
    #  *_____*______*______*
    #  |     |      |      |
    #  *_____*______*______*
    #  |     |      |      |
    #  *_____*______*______*
    ndof = 2 * (nelx + 1) * (nely + 1)
    # Allocate design variables (as array), initialize and allocate sens.
    x = volfrac * np.ones(nely * nelx, dtype=float)
    xold = x.copy()
    xPhys = x.copy()
    # must be initialized to use the NGuyen/Paulino OC approach
    g = 0
    # 0 Matrix with number of elements x, number of elements y
    dc = np.zeros((nely, nelx), dtype=float)
    # Stiffnes matrix of the elementtype with 8,8 (shell element)
    KE = lk()
    # 0 Matrix with number of elements, 8
    edofMat = np.zeros((nelx * nely, 8), dtype=int)
    for elx in range(nelx):
        for ely in range(nely):
            el = ely + elx * nely
            n1 = (nely + 1) * elx + ely
            n2 = (nely + 1) * (elx + 1) + ely
            edofMat[el, :] = np.array([2 * n1 + 2,
                                       2 * n1 + 3,
                                       2 * n2 + 2,
                                       2 * n2 + 3,
                                       2 * n2,
                                       2 * n2 + 1,
                                       2 * n1,
                                       2 * n1 + 1])

    # Construct the index pointers for the coo format
    # Using the Kronecker product (dimension must be the same)
    # Then collapse the vector into one dimension with flatten
    # In the end we have a 1-Dim array with the indexes

    iK = np.kron(edofMat, np.ones((8 ,1))).flatten()
    jK = np.kron(edofMat, np.ones((1 ,8))).flatten()
    # Generate the number of filters with ceil (ceiling of the input)
    # Filter: Build (and assemble) the index+data vectors for the
    # coo matrix format
    nfilter = nelx * nely * ((2 * (np.ceil(rmin) - 1) + 1) ** 2)
    iH = np.zeros(nfilter)
    jH = np.zeros(nfilter)
    sH = np.zeros(nfilter)
    cc = 0
    for i in range(nelx):
        for j in range(nely):
            row = i * nely + j
            kk1 = int(np.maximum(i - (np.ceil(rmin) - 1), 0))
            kk2 = int(np.minimum(i + np.ceil(rmin), nelx))
            ll1 = int(np.maximum(j - (np.ceil(rmin) - 1), 0))
            ll2 = int(np.minimum(j + np.ceil(rmin), nely))
            for k in range(kk1, kk2):
                for l in range(ll1, ll2):
                    col = k * nely + l
                    fac = rmin - np.sqrt(((i - k) * (i - k) +
                                         (j - l) * (j - l)))
                    iH[cc] = row
                    jH[cc] = col
                    sH[cc] = np.maximum(0.0, fac)
                    cc = cc + 1
    # Finalize assembly and convert to csc format
    H = coo_matrix((sH, (iH, jH)), shape = (nelx * nely, nelx * nely)).tocsc()
    Hs = H.sum(1)
    print(str(H)+"Filter method\n")
    # BC's and support
    dofs = np.arange(2 * (nelx + 1) * (nely + 1))
#    fixed=np.union1d(dofs[0 : 2 * (nely + 1) : 2],np.array([2 * (nelx + 1)
#                                                           * (nely + 1) - 1]))
    fixed=np.union1d(dofs[0 : 2 * (nely + 1) : 2],np.array([1]))

    #fixed=np.union1d(fixed,np.array([79]))
    free = np.setdiff1d(dofs, fixed)
    # Solution and RHS vectors
    f = np.zeros((ndof, 1))
    u = np.zeros((ndof, 1))
    # Set load
    f[ndof-1,0]= 5
    #f[ndof-2-2*nely+1,0]= 3
    #f[ndof-2-(nely)*(nelx)+nely-2+1,0]= 1
    #f[ndof-2-(nely)*(nelx)-0.2*int(nely)*(nelx)+1,0]= 1
    #f[2*nely*3,0]= 30
    # Initialize plot and plot the initial design
    # Ensure that redrawing is possible
    plt.ion()
    fig, ax = plt.subplots()
    im = ax.imshow(-xPhys. reshape((nelx, nely)).T, cmap='gray',\
    interpolation='none',norm=colors.Normalize(vmin=-1,vmax=0))
    fig.show()
    # Set loop counter and gradient vectors
    loop=0
    change=1

    dv = np.ones(nely*nelx)
    dc = np.ones(nely*nelx)
    ce = np.ones(nely*nelx)
    dcold = dc
    topoIsActive = True
    if (topoIsActive):
        while change>0.05 and loop<1000:
            loop=loop+1
            # Setup and solve FE problem
            sK=((KE.flatten()[np.newaxis]).T*(Emin+(xPhys)**penal*(Emax-Emin))).flatten(order='F')
            K = coo_matrix((sK,(iK,jK)),shape=(ndof,ndof)).tocsc()
            # Remove constrained dofs from matrix
            K = K[free,:][:,free]
            # Solve system
            u[free,0]=spsolve(K,f[free,0])
            # Objective and sensitivity
            ce[:] = (np.dot(u[edofMat].reshape(nelx*nely,8),KE) * u[edofMat].reshape(nelx*nely,8) ).sum(1)
            obj=( (Emin+xPhys**penal*(Emax-Emin))*ce ).sum()
            dc[:]=(-penal*xPhys**(penal-1)*(Emax-Emin))*ce; print ce
            dv[:] = np.ones(nely*nelx)
            # Sensitivity filtering:
            if loop > 1:
                dc = dc + dcold / 2
            if ft==0:
                dc[:] = np.asarray((H*(x*dc))[np.newaxis].T/Hs)[:,0] / np.maximum(0.001,x)
            elif ft==1:
                dc[:] = np.asarray(H*(dc[np.newaxis].T/Hs))[:,0]
                dv[:] = np.asarray(H*(dv[np.newaxis].T/Hs))[:,0]
            # Optimality criteria
            dcold = dc
            xold[:]=x
            (x[:])=oc(nelx,nely,x,volfrac,dc,dv)
            # Filter design variables
            if ft==0:   xPhys[:]=x
            elif ft==1:	xPhys[:]=np.asarray(H*x[np.newaxis].T/Hs)[:,0]
            # Compute the change by the inf. norm
            change=np.linalg.norm(x.reshape(nelx*nely,1)-xold.reshape(nelx*nely,1),np.inf)
            # Plot to screen
            im.set_array(-xPhys.reshape((nelx,nely)).T)
            fig.canvas.draw()
            # Make sure the plot stays and that the shell remains	
    plt.show()
    #raw_input("Press any key...")
#element stiffness matrix
def lk():
    E = 1
    nu = 0.3
    k = np.array([
             1 / 2 - nu / 6,
             1 / 8 + nu / 8,
           - 1 / 4 - nu / 12,
           - 1 / 8 + 3 * nu / 8,
           - 1 / 4 + nu / 12,
           - 1 / 8 - nu / 8,
             nu / 6,
           1 / 8 - 3 * nu / 8])
    # *_____l_____*
    # |           |
    # h           h
    # |           |
    # *_____l_____*
    # With a = l/h
    # With b = h/l
    # In our case a = b
    # If there are different sizes you must take different values for each
    # element into account
    #    k = 1/24 * np.array([8 * b + 4 * a *(1 - pRatio),
    #                          3*(1 + pRatio),
    #                         - 8 * b + 2 * a * (1 - pRatio),
    #                         - -3 * (1 - 3 * pRatio),
    #                         - b - 2 * a * (1 - pRatio),
    #                         - 3 * (1 + pRatio),
    #                         4 * b - 4 * a * (1 - pRatio),
    #                          3 * (1 - 3 * pRatio)])
    KE = E / (1 - nu ** 2) * np.array([
    [k[0], k[1], k[2], k[3], k[4], k[5], k[6], k[7]],
    [k[1], k[0], k[7], k[6], k[5], k[4], k[3], k[2]],
    [k[2], k[7], k[0], k[5], k[6], k[3], k[4], k[1]],
    [k[3], k[6], k[5], k[0], k[7], k[2], k[1], k[4]],
    [k[4], k[5], k[6], k[7], k[0], k[1], k[2], k[3]],
    [k[5], k[4], k[3], k[2], k[1], k[0], k[7], k[6]],
    [k[6], k[3], k[4], k[1], k[2], k[7], k[0], k[5]],
    [k[7], k[2], k[1], k[4], k[3], k[6], k[5], k[0]]]);
    return (KE)
# Optimality criterion
def oc(nelx,nely,x,volfrac,dc,dv):
    #l1=0
    #l2=1e9
    move=0.2
    # reshape to perform vector operations
    sens = dc/dv
    l2 = max(abs(sens))
    l1 = min(abs(sens))
    xnew=np.zeros(nelx*nely)
    while (l2-l1)/(l1+l2)>1e-3:
        lmid=0.5*(l2+l1)
        xnew[:]= np.maximum(0.0,np.maximum(x-move,np.minimum(1.0,np.minimum(x+move,x*np.sqrt(-dc/dv/lmid)))))
        #xnew[:] = np.maximum(0.00001, np.sign(-sens - lmid))
        #gt=g+np.sum((dv*(xnew-x)))
        if np.mean(xnew[:]) - volfrac > 0.0:
            l1 = lmid
        else:
            l2 = lmid
    return (xnew)


