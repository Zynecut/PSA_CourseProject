import math
import cmath
from classes import *


def J1(PV_and_PQ_buses: list[Bus], YBus) -> pd.DataFrame:
    '''
        Calculate the first jacobian matrix, refering to the power and voltages.
    '''
    count_P = 4
    count_diraq = 3
    df_J1 = pd.DataFrame(0, index=range(1, count_P), columns=range(1, count_diraq), dtype=complex)

    for i in range(1, count_P):
        for j in range(1, count_diraq):
            if i != j:  
                # Off-diagonal elements of J1
                # Deklarere disse fra bus listen
                v_i = None
                v_j = None
                diraq_i = None
                diraq_j = None

                Y_ij_polar = cmath.polar(complex(YBus[i][j]))
                Y_ij = Y_ij_polar[0]
                theta_ij = Y_ij_polar[1]
                PiDiraqj = - abs(v_i*v_j*Y_ij)*math.sin(theta_ij + diraq_j - diraq_i)
                df_J1[i][j] = PiDiraqj
            else: 
                # Diagonal elements of J1
                v_i = None
                v_n = None
                diraq_n = None
                PiDiraqj = None
                N = 4 # blir vel count_v som skal inn her egentlig
                for n in range(1, N):
                    if n != i:
                        Y_in_polar = cmath.polar(complex(YBus[i][n]))
                        Y_in = Y_in_polar[0]
                        theta_in = Y_in_polar[1]
                        sumE = abs(v_i*v_n*Y_in)*math.sin(theta_in + diraq_n - diraq_i)
                        PiDiraqi += sumE
                    else:
                        continue
                df_J1[i][i] = PiDiraqi

    return df_J1

def J2(PV_and_PQ_buses: list[Bus], YBus) -> pd.DataFrame:
    '''
        Calculate the second jacobian matrix, refering to the power and voltages.
    '''
    count_P = 4
    count_v = 3
    df_J2 = pd.DataFrame(0, index=range(1, count_P), columns=range(1, count_v), dtype=complex)

    for i in range(1, count_P):
        for j in range(1, count_v):
            if i != j:  
                # Off-diagonal elements of J2
                # Deklarere disse fra bus listen
                v_i = None
                diraq_i = None
                diraq_j = None

                Y_ij_polar = cmath.polar(complex(YBus[i][j]))
                Y_ij = Y_ij_polar[0]
                theta_ij = Y_ij_polar[1]
                PiVj = abs(v_i*Y_ij)*math.cos(theta_ij + diraq_j - diraq_i)
                df_J2[i][j] = PiVj
            else: 
                # Diagonal elements of J2
                v_i = None
                v_n = None
                diraq_n = None
                G_ii = complex(YBus[i][i]).real()
                PiVi = 2*abs(v_i)*G_ii

                N = 4 # blir vel count_v som skal inn her egentlig
                for n in range(1, N):
                    Y_in_polar = cmath.polar(complex(YBus[i][n]))
                    Y_in = Y_in_polar[0]
                    theta_in = Y_in_polar[1]
                    sumE = abs(v_n*Y_in)*math.cos(theta_in + diraq_n - diraq_i)
                    PiVi += sumE

                df_J2[i][i] = PiVi

    return df_J2

def J3(PV_and_PQ_buses: list[Bus], YBus) -> pd.DataFrame:
    '''
        Calculate the second jacobian matrix, refering to the power and voltages.
    '''
    count_Q = 4
    count_diraq = 3
    df_J3 = pd.DataFrame(0, index=range(1, count_Q), columns=range(1, count_diraq), dtype=complex)

    for i in range(1, count_Q):
        for j in range(1, count_diraq):
            if i != j:  
                # Off-diagonal elements of J3
                v_i = None
                v_j = None
                diraq_i = None
                diraq_j = None
                Y_ij_polar = cmath.polar(complex(YBus[i][j]))
                Y_ij = Y_ij_polar[0]
                theta_ij = Y_ij_polar[1]
                QiDiraqj = - abs(v_i*v_j*Y_ij)*math.cos(theta_ij + diraq_j - diraq_i)
                df_J3[i][j] = QiDiraqj
            else: 
                # Diagonal elements of J3
                v_i = None
                v_n = None
                diraq_n = None
                QiDiraqi = None
                N = 4 # blir vel count_v som skal inn her egentlig
                for n in range(1, N):
                    if n != i:
                        Y_in_polar = cmath.polar(complex(YBus[i][n]))
                        Y_in = Y_in_polar[0]
                        theta_in = Y_in_polar[1]
                        sumE = abs(v_i*v_n*Y_in)*math.cos(theta_in + diraq_n - diraq_i)
                        QiDiraqi += sumE
                    else:
                        continue
                df_J3[i][i] = QiDiraqi

    return df_J3

def J4(PV_and_PQ_buses: list[Bus], YBus) -> pd.DataFrame:
    '''
        Calculate the second jacobian matrix, refering to the power and voltages.
    '''
    count_Q = 4
    count_v = 3
    df_J4 = pd.DataFrame(0, index=range(1, count_Q), columns=range(1, count_v), dtype=complex)

    for i in range(1, count_Q):
        for j in range(1, count_v):
            if i != j:  
                # Off-diagonal elements of J4
                v_i = None
                diraq_i = None
                diraq_j = None
                Y_ij_polar = cmath.polar(complex(YBus[i][j]))
                Y_ij = Y_ij_polar[0]
                theta_ij = Y_ij_polar[1]
                QiVj = abs(v_i*Y_ij)*math.cos(theta_ij + diraq_j - diraq_i)
                df_J4[i][j] = QiVj
            else: 
                # Diagonal elements of J4
                v_i = None
                v_n = None
                diraq_n = None
                B_ii = complex(YBus[i][i]).imag()
                QiVi = 2*abs(v_i)*B_ii

                N = 4 # blir vel count_v som skal inn her egentlig
                for n in range(1, N):
                    Y_in_polar = cmath.polar(complex(YBus[i][n]))
                    Y_in = Y_in_polar[0]
                    theta_in = Y_in_polar[1]
                    sumE = abs(v_n*Y_in)*math.cos(theta_in + diraq_n - diraq_i)
                    QiVi += sumE

                df_J4[i][i] = QiVi

    return df_J4

def Jacobian(J1, J2, J3, J4) -> pd.DataFrame:
    df_jacobian = pd.DataFrame()
    J1J2 = pd.concat(J1, J2, axis=0)
    J3J4 = pd.concat(J3, J4, axis=0)
    df_jacobian = pd.concat(J1J2, J3J4, axis=1)
    return df_jacobian



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
    




    