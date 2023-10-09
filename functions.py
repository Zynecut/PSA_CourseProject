import math

class NewtonRaphsonLF:
    def funcPi(v_i, v_j, y_ij, theta_ij, delta_i, delta_j):
        P = abs(v_i*v_j*y_ij)*math.sin(theta_ij + delta_j - delta_i)
        return P


class DecouplingLF:
    def funcP():
        return None
    

class FastDecouplingLF:
    def funcPyay():
        return None
    

class DCLF:
    def funcPDC():
        return None
    

# Prøver hardkoding på første element
#def J11_diag_calc():


    