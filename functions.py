import math, cmath
import re
import csv
import numpy as np
import pandas as pd
import jinja2 

from classes import *

def ReadCsvFile(file):
    """
        Read values from a csv file
    """
    data = []
    try:
        with open(file, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                data.append(row)
        return data
    except FileNotFoundError:
        print(f"File not found: {file}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def setupLineAdmittanceList(line_dict):
    """
        Setup Cutsem's algorithm, with 2x2 ybuses between each line.
    """
    x = []
    impedance = complex(float(line_dict['R[pu]']), float(line_dict['X[pu]']))
    half_line_charging_admittance = complex(0, float(line_dict['Half Line Charging Admittance']))
    y_pq = complex(1 / impedance)
    x.append(int(line_dict['From line']))
    x.append(int(line_dict['To line']))
    x.append(y_pq + half_line_charging_admittance) #y11
    x.append(-y_pq) #y12
    x.append(-y_pq) #y21
    x.append(y_pq + half_line_charging_admittance) #y22
    return x

def setupBusList(bus_dict, bus_type, Sbase):
    """
        Setup values for each bus object
    """
    bus = Bus(
            bus_id= bus_dict['Bus Code'],
            voltage_magnitude= bus_dict['Assumed bus voltage (pu)'],
            voltage_angle= bus_dict['Angle'],
            P_gen= bus_dict['Generation (MW)'],
            Q_gen= bus_dict['Generation (MVAr)'],
            P_load= bus_dict['Load (MW)'],
            Q_load=  bus_dict['Load (MVAr)'],
            Sbase= Sbase,
            BusType= bus_type
        )
    return bus

def buildBusList(bus_data, Sbase, bus_overview):
    """
        Building list of Bus objects
    """
    BusList = []
    i = 0
    for element in bus_data:
        bus_type = bus_overview[i]['Type']
        BusList.append(setupBusList(element, bus_type, Sbase))
        i += 1
    return BusList

def BuildYbusMatrix(line_data,num_buses):
    """
        Construct YBus Matrix for an N-bus system
    """
    line_adm = []
    for element in line_data:
        line_adm.append(setupLineAdmittanceList(element))

    Y_bus = np.zeros((num_buses,num_buses), dtype=complex)
    for i in range(1, num_buses + 1):
        for j in range(1, num_buses + 1):
            # Initialize the sum of admittances for the diagonal element (Yii)
            sum_of_admittances = 0
            if i == j:
                # Calculate the sum of admittances for the diagonal element
                for k in range(len(line_adm)):
                    if line_adm[k][0] == i or line_adm[k][1] == i:
                        sum_of_admittances += line_adm[k][2]

                # Set the diagonal element
                Y_bus[i-1,j-1] = sum_of_admittances
            else:
                for k in range(len(line_adm)):
                    if (line_adm[k][0] == i and line_adm[k][1] == j) or (line_adm[k][0] == j and line_adm[k][1] == i):
                        Y_bus[i-1][j-1] = line_adm[k][3]
    return Y_bus

def setupBusType(bus_data):
    """
        An overview of Known and Unknown values for each bus
    """
    bus_overview = []
    for i in range(len(bus_data)):
        try:
            generation_mw = bus_data[i]['Generation (MW)']
            load_mw = bus_data[i]['Load (MW)']
            generation_mvar = bus_data[i]['Generation (MVAr)']
            load_mvar = bus_data[i]['Load (MVAr)']
            bus_voltage = bus_data[i]['Assumed bus voltage (pu)']
        except ValueError:
            # Handle non-integer values
            generation_mw = "-"
            load_mw = "-"
            generation_mvar = "-"
            load_mvar = "-"
            bus_voltage = "-"

        bus_info = {}
        if generation_mw != "-" and load_mw != "-" and generation_mvar != "-" and load_mvar != "-":
            bus_info['Bus'] = i+1
            bus_info['Type'] = 'P' + 'Q'
            bus_info['Known_1'] = 'P'
            bus_info['Known_2'] = 'Q'
            bus_info['Unknown_1'] = 'V'
            bus_info['Unknown_2'] = 'DIRAC'
    
        elif bus_voltage != "-" and (generation_mw != "-" and load_mw != "-"):
            bus_info['Bus'] = i+1
            bus_info['Type'] = 'P' + 'V'
            bus_info['Known_1'] = 'P'
            bus_info['Known_2'] = 'V'
            bus_info['Unknown_1'] = 'Q' 
            bus_info['Unknown_2'] = 'DIRAC'

        else:
            bus_info['Bus'] = i+1
            bus_info['Type'] = "Slack"
            bus_info['Known_1'] = 'V'
            bus_info['Known_2'] = 'DIRAC'
            bus_info['Unknown_1'] = 'P'
            bus_info['Unknown_2'] = 'Q'
        
        bus_overview.append(bus_info)

    return bus_overview

def findKnowns(bus_data, Sbase):
    """
        Find known values of P_specified and Q_specified
    """
    knownP_dict = {}
    knownQ_dict = {}
    j = 0
    while j < len(bus_data):
        if bus_data[j]['Load (MW)'] == '-' or bus_data[j]['Generation (MW)'] == '-':
            j += 1
            continue
        # Create dynamic variable names
        new_name_P = f"P_{j+1}"
        valueP = float(bus_data[j]['Generation (MW)']) - float(bus_data[j]['Load (MW)'])
        knownP_dict[new_name_P] = valueP/Sbase
        j += 1
        
    k = 0
    while k < len(bus_data):
        if bus_data[k]['Load (MVAr)'] == '-' or bus_data[k]['Generation (MVAr)'] == '-':
            k += 1
            continue
        new_name_Q = f"Q_{k+1}"
        ValueQ = float(bus_data[k]['Generation (MVAr)']) - float(bus_data[k]['Load (MVAr)'])
        knownQ_dict[new_name_Q] = ValueQ/Sbase
        k += 1

    return knownP_dict, knownQ_dict

def findUnknowns(bus_overview, bus_data):
    """
        Fin unknown values Δδ and Δ|V|
    """
    guess_data_dict_V = {}
    guess_data_dict_Dirac = {}

    j = 0
    while j < len(bus_data):
        unknown1 = bus_overview[j].get('Unknown_1', '-')
        if unknown1 == 'V':
            new_name_unknown_V = f"v_{j+1}"
            guessV = float(bus_data[j]['Assumed bus voltage (pu)'])
            guess_data_dict_V[new_name_unknown_V] = guessV
        j += 1

    k = 0
    while k < len(bus_data):
        unknown2 = bus_overview[k].get('Unknown_2', '-')
        if unknown2 == 'DIRAC':
            new_name_unknown_dirac = f"DIRAC_{k+1}"
            guessDirac = float(bus_data[k]['Angle'])
            guess_data_dict_Dirac[new_name_unknown_dirac] = guessDirac
        k += 1

    return guess_data_dict_V, guess_data_dict_Dirac

def extract_number(s):
    """
        Extract number at end of variable name(str)
    """
    match = re.search(r'\d+', s)
    if match:
        return int(match.group())
    else:
        return None

# def J1(BusList, P, dirac, YBus):
#     '''
#         Calculate the first jacobian matrix, refering to the power and voltages.
#     '''
#     count_P = len(P)
#     P_start = extract_number(next(iter(P))) - 1
#     P_end = len(BusList)
#     count_dirac = len(dirac)
#     dirac_start = extract_number(next(iter(dirac))) - 1
#     dirac_end = len(BusList)
#     J1_arr = np.zeros((count_P,count_dirac))

#     for i in range(P_start, P_end):
#         for j in range(dirac_start, dirac_end):
#             PiDiraci = 0
#             key_P = f"P_{i+1}"
#             key_d = f"DIRAC_{j+1}"
#             if i != j:  
#                 if key_P in P and key_d in dirac:
#                 # Off-diagonal elements of J1
#                     v_i = BusList[i].voltage_magnitude
#                     v_j = BusList[j].voltage_magnitude
#                     dirac_i = BusList[i].voltage_angle
#                     dirac_j = BusList[j].voltage_angle

#                     Y_ij_polar = cmath.polar(YBus[i][j])
#                     Y_ij = Y_ij_polar[0]
#                     theta_ij = Y_ij_polar[1]
#                     J1_arr[i-P_start][j-dirac_start] = - abs(v_i*v_j*Y_ij)*math.sin(theta_ij + dirac_j - dirac_i)
#             else: 
#                 # Diagonal elements of J1
#                 if key_P in P:
#                     v_i = BusList[i].voltage_magnitude
#                     dirac_i = BusList[i].voltage_angle
#                     for n in range(dirac_end):
#                         if n != i:
#                             v_n = BusList[n].voltage_magnitude
#                             dirac_n = BusList[n].voltage_angle
#                             Y_in_polar = cmath.polar(YBus[i][n])
#                             Y_in = Y_in_polar[0]
#                             theta_in = Y_in_polar[1]
#                             PiDiraci += abs(v_i*v_n*Y_in)*math.sin(theta_in + dirac_n - dirac_i)
#                         else:
#                             continue
#                 J1_arr[i-P_start][i-dirac_start] = PiDiraci
            

#     return J1_arr


def J1(BusList, P, dirac, YBus):
    '''
        Calculate the first jacobian matrix, refering to the power and voltages.
    '''
    count_P = len(P)
    P_start = extract_number(next(iter(P))) - 1
    count_dirac = len(dirac)
    dirac_start = extract_number(next(iter(dirac))) - 1
    J1_arr = np.zeros((count_P,count_dirac))

    for i in range(P_start, count_P + P_start):
        for j in range(dirac_start, count_dirac + dirac_start):
            PiDiraci = 0
            if i != j:  
                # Off-diagonal elements of J1
                v_i = BusList[i].voltage_magnitude
                v_j = BusList[j].voltage_magnitude
                dirac_i = BusList[i].voltage_angle
                dirac_j = BusList[j].voltage_angle

                Y_ij_polar = cmath.polar(YBus[i][j])
                Y_ij = Y_ij_polar[0]
                theta_ij = Y_ij_polar[1]
                J1_arr[i-P_start][j-dirac_start] = - abs(v_i*v_j*Y_ij)*math.sin(theta_ij + dirac_j - dirac_i)
            else: 
                # Diagonal elements of J1
                v_i = BusList[i].voltage_magnitude
                dirac_i = BusList[i].voltage_angle
                for n in range(count_dirac + dirac_start):
                    if n != i:
                        v_n = BusList[n].voltage_magnitude
                        dirac_n = BusList[n].voltage_angle
                        Y_in_polar = cmath.polar(YBus[i][n])
                        Y_in = Y_in_polar[0]
                        theta_in = Y_in_polar[1]
                        PiDiraci += abs(v_i*v_n*Y_in)*math.sin(theta_in + dirac_n - dirac_i)
                    else:
                        continue
                J1_arr[i-P_start][i-dirac_start] = PiDiraci
    return J1_arr


def J2(BusList, P, v, YBus):
    '''
        Calculate the second jacobian matrix, refering to the power and voltages.
    '''
    count_P = len(P)
    P_start = extract_number(next(iter(P))) - 1
    count_v = len(v)
    v_start = extract_number(next(iter(v))) - 1
    J2_arr = np.zeros((count_P, count_v))

    for i in range(P_start, count_P + P_start):
        for j in range(v_start, count_v + v_start):
            if i != j:  
                # Off-diagonal elements of J2
                # Deklarere disse fra bus listen
                v_i = BusList[i].voltage_magnitude
                dirac_i = BusList[i].voltage_angle
                dirac_j = BusList[j].voltage_angle

                Y_ij_polar = cmath.polar(YBus[i][j])
                Y_ij = Y_ij_polar[0]
                theta_ij = Y_ij_polar[1]
                J2_arr[i-P_start][j-v_start] = abs(v_i*Y_ij)*math.cos(theta_ij + dirac_j - dirac_i)
            else: 
                # Diagonal elements of J2
                v_i = BusList[i].voltage_magnitude
                dirac_i = BusList[i].voltage_angle
                G_ii = complex(YBus[i][i]).real
                PiVi = 2*abs(v_i)*G_ii

                for n in range(count_v + v_start):
                    v_n = BusList[n].voltage_magnitude
                    dirac_n = BusList[n].voltage_angle
                    if n != i:
                        Y_in_polar = cmath.polar(YBus[i][n])
                        Y_in = Y_in_polar[0]
                        theta_in = Y_in_polar[1] # return radian value
                        PiVi += abs(v_n*Y_in)*math.cos(theta_in + dirac_n - dirac_i)
                    else:
                        continue
                J2_arr[i-P_start][i-v_start] = PiVi

    return J2_arr

def J3(BusList, Q, dirac, YBus):
    '''
        Calculate the third jacobian matrix, refering to the reactive power and voltages.
    '''
    count_Q = len(Q)
    Q_start = extract_number(next(iter(Q))) - 1
    count_dirac = len(dirac)
    dirac_start = extract_number(next(iter(dirac))) - 1
    J3_arr = np.zeros((count_Q, count_dirac))

    for i in range(Q_start, count_Q + Q_start):
        for j in range(dirac_start, count_dirac + dirac_start):
            if i != j:  
                # Off-diagonal elements of J3
                v_i = BusList[i].voltage_magnitude
                v_j = BusList[j].voltage_magnitude
                dirac_i = BusList[i].voltage_angle
                dirac_j = BusList[j].voltage_angle

                Y_ij_polar = cmath.polar(YBus[i][j])
                Y_ij = Y_ij_polar[0]
                theta_ij = Y_ij_polar[1]
                J3_arr[i-Q_start][j-dirac_start] = - abs(v_i*v_j*Y_ij)*math.cos(theta_ij + dirac_j - dirac_i)
            else: 
                # Diagonal elements of J3
                QiDiraci = 0
                v_i = BusList[i].voltage_magnitude
                dirac_i = BusList[i].voltage_angle
                for n in range(count_dirac + dirac_start):
                    v_n = BusList[n].voltage_magnitude
                    dirac_n = BusList[n].voltage_angle
                    if n != i:
                        Y_in_polar = cmath.polar(YBus[i][n])
                        Y_in = Y_in_polar[0]
                        theta_in = Y_in_polar[1]
                        QiDiraci += abs(v_i*v_n*Y_in)*math.cos(theta_in + dirac_n - dirac_i)
                    else:
                        continue
                J3_arr[i-Q_start][i-dirac_start] = QiDiraci
    return J3_arr

def J4(BusList, Q, v, YBus):
    '''
        Calculate the second jacobian matrix, refering to the power and voltages.
    '''
    count_Q = len(Q)
    Q_start = extract_number(next(iter(Q))) - 1
    count_v = len(v)
    v_start = extract_number(next(iter(v))) - 1
    J4_arr = np.zeros((count_Q, count_v))

    for i in range(Q_start, count_Q + Q_start):
        for j in range(v_start, count_v + v_start):
            if i != j:  
                # Off-diagonal elements of J4
                v_i = BusList[i].voltage_magnitude
                dirac_i = BusList[i].voltage_angle
                dirac_j = BusList[j].voltage_angle

                Y_ij_polar = cmath.polar(YBus[i][j])
                Y_ij = Y_ij_polar[0]
                theta_ij = Y_ij_polar[1]
                J4_arr[i-Q_start][j-v_start] = - abs(v_i*Y_ij)*math.sin(theta_ij + dirac_j - dirac_i)
            else: 
                # Diagonal elements of J4
                v_i = BusList[i].voltage_magnitude
                dirac_i = BusList[i].voltage_angle
                B_ii = complex(YBus[i][i]).imag
                QiVi = - 2*abs(v_i)*B_ii

                for n in range(count_v + v_start):
                    v_n = BusList[n].voltage_magnitude
                    dirac_n = BusList[n].voltage_angle
                    if n != i:
                        Y_in_polar = cmath.polar(YBus[i][n])
                        Y_in = Y_in_polar[0]
                        theta_in = Y_in_polar[1]
                        QiVi -= abs(v_n*Y_in)*math.sin(theta_in + dirac_n - dirac_i)
                    else:
                        continue
                J4_arr[i-Q_start][i-v_start] = QiVi
    return J4_arr

def buildJacobian(BusList, P, Q, v, dirac, YBus):
    Jac1 = J1(BusList, P, dirac, YBus)
    Jac2 = J2(BusList, P, v, YBus)
    Jac3 = J3(BusList, Q, dirac, YBus)
    Jac4 = J4(BusList, Q, v, YBus)
    J1J2 = np.concatenate((Jac1, Jac2), axis= 1)
    J3J4 = np.concatenate((Jac3, Jac4), axis= 1)
    Jac_arr = np.concatenate((J1J2, J3J4), axis= 0)
    return Jac_arr

def calcP(BusList, P_spec, YBus):
    """
        Calculate ΔP
    """ 
    P_start = extract_number(next(iter(P_spec))) - 1
    P_end = P_start + len(BusList)
    Pi_calc = np.zeros([len(P_spec), 1])
    for i in range(P_start, P_end):
        key = f"P_{i+1}"
        if key in P_spec:
            v_i = BusList[i].voltage_magnitude
            dirac_i = BusList[i].voltage_angle
            Pi = 0
            for n in range(len(BusList)):
                v_n = BusList[n].voltage_magnitude
                dirac_n = BusList[n].voltage_angle
                Y_in_polar = cmath.polar(YBus[i][n])
                Y_in = Y_in_polar[0]
                theta_in = Y_in_polar[1]
                Pi += abs(v_i*v_n*Y_in)*math.cos(theta_in + dirac_n - dirac_i)
            Pi_calc[i - P_start] = Pi
        else:
            P_start += 1

    P_spec_arr = np.array(list(P_spec.values())).reshape(-1, 1) #.T
    deltaP = P_spec_arr - Pi_calc
    return deltaP

def calcQ(BusList, Q_spec, YBus):
    """
        Calculate ΔQ
    """
    Q_start = extract_number(next(iter(Q_spec))) - 1
    Q_end = Q_start + len(BusList)
    Qi_calc = np.zeros([len(Q_spec), 1])

    for i in range(Q_start, Q_end):
        key = f"Q_{i+1}"
        if key in Q_spec:
            v_i = BusList[i].voltage_magnitude
            dirac_i = BusList[i].voltage_angle
            Qi = 0
            for n in range(len(BusList)):
                v_n = BusList[n].voltage_magnitude
                dirac_n = BusList[n].voltage_angle
                Y_in_polar = cmath.polar(YBus[i][n])
                Y_in = Y_in_polar[0]
                theta_in = Y_in_polar[1]
                Qi -= abs(v_i*v_n*Y_in)*math.sin(theta_in + dirac_n - dirac_i)
            Qi_calc[i-Q_start] = Qi
        else:
            Q_start += 1

    Q_spec_arr = np.array(list(Q_spec.values())).reshape(-1, 1)
    deltaQ = Q_spec_arr - Qi_calc
    return deltaQ

def calcDeltaUnknowns(jacobian_matrix, knowns):
    """
        Calculate Δδ and Δ|V|
    """
    jac_inv = np.linalg.pinv(jacobian_matrix)
    unknowns = np.dot(jac_inv, knowns)
    return unknowns

def updateVoltageAndAngleList(delta_x, dirac_guess, v_guess):
    """
        Update dirac and voltage lists for unknowns.
    """
    # Update DIRAC guesses with values from the first four elements of unknowns
    dirac_start = extract_number(next(iter(dirac_guess)))
    dirac_end = dirac_start + 1
    dirac_count = len(dirac_guess)
    for i in range(dirac_start, dirac_count + dirac_end):
        dirac_key = f'DIRAC_{i}'
        if dirac_key in dirac_guess:
            dirac_guess[dirac_key] += delta_x[i-dirac_start][0]
        else:
            dirac_start += 1

    # Update v guesses with values from the last three elements of unknowns
    v_start = extract_number(next(iter(v_guess)))
    v_end = v_start + 1
    count_v = len(v_guess)
    for i in range(v_start, count_v + v_end):
        v_key = f'v_{i}'
        if v_key in v_guess:
            v_guess[v_key] += delta_x[i-v_start+dirac_count][0]
        else:
            v_start +=1

def updateBusList(BusList, dirac_guess, v_guess):
    """
        Update the |V| and δ for the specified buses
    """
    for bus_id in v_guess:
        v_num = extract_number(bus_id)
        for i in range(len(BusList)):
            if v_num == BusList[i].bus_id:
                BusList[i].update_bus_voltage(new_voltage_magnitude=v_guess[bus_id])
            else:
                continue

    for bus_id in dirac_guess:
        dirac_num = extract_number(bus_id)
        for i in range(len(BusList)):
            if dirac_num == BusList[i].bus_id:
                BusList[i].update_bus_voltage(new_voltage_angle=dirac_guess[bus_id])
            else:
                continue

def checkTypeSwitch(BusList, YBus, Q_spec, v_guess, Q_lim, V_lim):
    for i in range(len(BusList)):
        if BusList[i].BusType == 'PV':
            Qi = 0
            v_i = BusList[i].voltage_magnitude
            dirac_i = BusList[i].voltage_angle
            for n in range(len(BusList)):
                v_n = BusList[n].voltage_magnitude
                dirac_n = BusList[n].voltage_angle
                Y_in_polar = cmath.polar(YBus[i][n])
                Y_in = Y_in_polar[0]
                theta_in = Y_in_polar[1]
                Qi -= abs(v_i*v_n*Y_in)*math.sin(theta_in + dirac_n - dirac_i)

            if Q_lim < Qi < abs(Q_lim):
                continue
            elif Qi >= abs(Q_lim):
                Qi = abs(Q_lim)
                BusList[i].typeSwitch("PQ")
                BusList[i].update_Pi_Qi(Q_spec=Qi, Q_gen= (Qi - BusList[i].Q_load))

                # Update Q_spec
                key_Q = f"Q_{i+1}"
                Q_spec_temp = {}
                if key_Q not in Q_spec:
                    Q_spec_temp[key_Q] = Qi
                for k in Q_spec:
                    Q_spec_temp[k] = Q_spec[k]
                Q_spec = Q_spec_temp

                # Update v_guess
                key_v = f"v_{i+1}"
                v_guess_temp = {}
                if key_v not in v_guess:
                    v_guess_temp[key_v] = BusList[i].voltage_magnitude
                for k in v_guess:
                    v_guess_temp[k] = v_guess[k]
                v_guess = v_guess_temp

            else:
                Qi = Q_lim
                BusList[i].typeSwitch("PQ")
                BusList[i].update_Pi_Qi(Q_spec=Qi, Q_gen= (Qi - BusList[i].Q_load))

                # Update Q_spec
                key_Q = f"Q_{i+1}"
                Q_spec_temp = {}
                if key_Q not in Q_spec:
                    Q_spec_temp[key_Q] = Qi
                for k in Q_spec:
                    Q_spec_temp[k] = Q_spec[k]
                Q_spec = Q_spec_temp

                # Update v_guess
                key_v = f"v_{i+1}"
                v_guess_temp = {}
                if key_v not in v_guess:
                    v_guess_temp[key_v] = BusList[i].voltage_magnitude
                for k in v_guess:
                    v_guess_temp[k] = v_guess[k]
                v_guess = v_guess_temp

    return Q_spec, v_guess
    

def checkConvergence(tol, delta_u):
    if np.all(abs(delta_u) < tol):
        return True
    else:
        return False

def updateSlackAndPV(BusList, YBus, Sbase):
    """
        Update Pi and Qi on SLACK bus and Qi on PV bus
    """
    for i in range(len(BusList)):
        if BusList[i].BusType == 'Slack':
            v_i = BusList[i].voltage_magnitude
            dirac_i = BusList[i].voltage_angle
            Pi = 0
            for n in range(len(BusList)):
                v_n = BusList[n].voltage_magnitude
                dirac_n = BusList[n].voltage_angle
                Y_in_polar = cmath.polar(YBus[i][n])
                Y_in = Y_in_polar[0]
                theta_in = Y_in_polar[1]
                Pi += abs(v_i*v_n*Y_in)*math.cos(theta_in + dirac_n - dirac_i)
            BusList[i].update_Pi_Qi(P_spec=Pi, P_gen= (Pi - BusList[i].P_load))

            Qi = 0
            for n in range(len(BusList)):
                v_n = BusList[n].voltage_magnitude
                dirac_n = BusList[n].voltage_angle
                Y_in_polar = cmath.polar(YBus[i][n])
                Y_in = Y_in_polar[0]
                theta_in = Y_in_polar[1]
                Qi -= abs(v_i*v_n*Y_in)*math.sin(theta_in + dirac_n - dirac_i)
            BusList[i].update_Pi_Qi(Q_spec=Qi, Q_gen= (Qi - BusList[i].Q_load))

        elif BusList[i].BusType == 'PV':
            Qi = 0
            v_i = BusList[i].voltage_magnitude
            dirac_i = BusList[i].voltage_angle
            for n in range(len(BusList)):
                v_n = BusList[n].voltage_magnitude
                dirac_n = BusList[n].voltage_angle
                Y_in_polar = cmath.polar(YBus[i][n])
                Y_in = Y_in_polar[0]
                theta_in = Y_in_polar[1]
                Qi -= abs(v_i*v_n*Y_in)*math.sin(theta_in + dirac_n - dirac_i)
            BusList[i].update_Pi_Qi(Q_spec=Qi, Q_gen= (Qi - BusList[i].Q_load))

def calcDecoupledJacobian(BusList, P, Q, v, dirac, YBus):
    Jac1 = J1(BusList, P, dirac, YBus)
    Jac2 = np.zeros((len(P), len(v)))
    Jac3 = np.zeros((len(Q), len(dirac)))
    Jac4 = J4(BusList, Q, v, YBus)
    J1J2 = np.concatenate((Jac1, Jac2), axis= 1)
    J3J4 = np.concatenate((Jac3, Jac4), axis= 1)
    Jac_arr = np.concatenate((J1J2, J3J4), axis= 0)
    return Jac_arr

def calcDecoupledDiracVoltage(dlf_jacobian, knowns):
    jac_inv = np.linalg.pinv(dlf_jacobian)
    dirac_voltage = np.dot(jac_inv, knowns)
    return dirac_voltage

def calcB_Prime(BusList, YBus):
    # Removes elements corresponding to SLACK bus
    B_sup1 = None
    B_sup2 = None
    for i in range(len(BusList)):
        if BusList[i].BusType == 'Slack':
            bus_index = BusList[i].bus_id - 1
            B_prime = np.delete(YBus, bus_index, axis=0)
            B_prime = np.delete(B_prime, bus_index, axis=1)
            # Removes real parts of elements
            B_prime = B_prime.imag * (-1)

        if BusList[i].BusType == 'PV':
            bus_index = BusList[i].bus_id - 2
            B_double_prime = np.delete(B_prime, bus_index, axis=0)
            B_double_prime = np.delete(B_double_prime, bus_index, axis=1)
    
    return B_prime, B_double_prime

    # Removes elements corresponding to PV buses from B_sup1
    
def calcDeltaPn_Vn(BusList, deltaP):
    diff = len(BusList) - len(deltaP)
    for i in range(len(BusList)):
        if BusList[i].BusType != "Slack":
            deltaP[i-diff] = deltaP[i-diff]/abs(BusList[i].voltage_magnitude)
    return deltaP

def calcDeltaQn_Vn(BusList, deltaQ):
    diff = len(BusList) - len(deltaQ)
    for i in range(len(BusList)):
        if BusList[i].BusType != "Slack":
            deltaQ[i-diff] = deltaQ[i-diff]/abs(BusList[i].voltage_magnitude)
    return deltaQ

def updateAngleFDLFandBusList(BusList, delta_dirac, dirac_guess=None):
    """
        Update angle list and angles in BusList, so that they can be used in ΔQn/|Vn|
    """
    dirac_start = extract_number(next(iter(dirac_guess)))
    dirac_count = len(dirac_guess)
    for i in range(dirac_start, dirac_count + dirac_start):
        dirac_key = f'DIRAC_{i}'
        dirac_guess[dirac_key] += delta_dirac[i-dirac_start][0]

    for bus_id in dirac_guess:
        dirac_num = extract_number(bus_id)
        for i in range(len(BusList)):
            if dirac_num == BusList[i].bus_id:
                BusList[i].update_bus_voltage(new_voltage_angle=dirac_guess[bus_id])
            else:
                continue

def updateVoltageFDLFandBusList(BusList, delta_v, v_guess=None):
    """
        Update voltage list and voltages in BusList.
    """
    count_v = len(v_guess)
    v_start = extract_number(next(iter(v_guess)))
    for i in range(v_start, count_v + v_start):
        v_key = f'v_{i}'
        v_guess[v_key] += delta_v[i-v_start][0]

    for bus_id in v_guess:
        v_num = extract_number(bus_id)
        for i in range(len(BusList)):
            if v_num == BusList[i].bus_id:
                BusList[i].update_bus_voltage(new_voltage_magnitude=v_guess[bus_id])
            else:
                continue

def makeDataFrame(BusList):
    data_to_add = []
    for i in range(len(BusList)):
        # print(f"#Bus: {BusList[i].bus_id}, Type: {BusList[i].BusType}, v: {BusList[i].voltage_magnitude:.3f} [pu], δ: {(180/math.pi)*BusList[i].voltage_angle:.3f} [deg], P: {BusList[i].P_specified:.3f} [pu], Q: {BusList[i].Q_specified:.3f} [pu]")
        dict_NRLF = {
            'Bus': BusList[i].bus_id,
            'Type': BusList[i].BusType,
            'Voltage [pu]': BusList[i].voltage_magnitude,
            'Angle [deg]': (180/math.pi)*BusList[i].voltage_angle,
            'P [pu]': BusList[i].P_specified,
            'Q [pu]': BusList[i].Q_specified
        }
        data_to_add.append(dict_NRLF)
    df_NRLF = pd.DataFrame(data_to_add)
    return df_NRLF

def print_dataframe_as_latex(dataframe):
    "Generates code to display a dataframe in LaTeX using the tabularx package."
    
    # Generate LaTeX code
    column_format_tabular = "c" * len(dataframe.columns)  # Create a "c" for each column using the tabular package
    latex_code = dataframe.to_latex(index=False,
                                    header=False,
                                    column_format=column_format_tabular,
                                    position="H",
                                    label="tab:change-me",
                                    caption="\color{red}Change me...")
    
    # Modify the LaTeX package
    latex_code = latex_code.replace("tabular", "tabularx") # Uses the tabularx package instead of the tabular one
    latex_code = latex_code.replace("\\caption", "\\centering\n\caption") # Adds the centering parameter to center the table

    # Modify the column format
    column_format_tabularx = "\n>{\\centering\\footnotesize\\arraybackslash}c" # First column uses the "c" parameter
    for i in range(1, len(dataframe.columns)):
        column_format_tabularx += "\n>{\\centering\\footnotesize\\arraybackslash}X" # All the other columns uses the "X" parameter
    latex_code = latex_code.replace(column_format_tabular, "0.9\\textwidth}{" + column_format_tabularx) # Replaces the column format

    # Use bold text for the header
    header_row = " & ".join(["\\textbf{" + col + "}" for col in dataframe.columns])
    latex_code = latex_code.replace("\\toprule", "\\toprule\n" + header_row + " \\\\")

    print("\n---------------- LaTeX Code -----------------")
    print(latex_code)

    # # Definer kolonnenavn
    # kolonner = ['Kolonne1', 'Kolonne2', 'Kolonne3', 'Kolonne4', 'Kolonne5']

    # # Generer tilfeldige data
    # data = np.random.rand(5, 5)

    # # Opprett DataFrame
    # df = pd.DataFrame(data, columns=kolonner)

    # # Skriv ut DataFrame
    # print_dataframe_as_latex(df)

