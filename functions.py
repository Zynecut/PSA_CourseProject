import math

class Functions:
    def funcPi(v_i, v_j, y_ij, theta_ij, delta_i, delta_j):
        P = abs(v_i*v_j*y_ij)*math.sin(theta_ij + delta_j - delta_i)
        return P
