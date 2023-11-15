import math, cmath
import re
import csv
import numpy as np
import pandas as pd

from classes import *

def ReadCsvFile(file):
    """
        Function to read values from a csv file

        Parameters:
        - file (csv)

        Returns:
        - data (list(dict))
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

def setupLineAdmittanceList(line_dict, XR_ratio = None, tap=None, phase=None):
    """
        Setup Cutsem's algorithm, with 2x2 y-buses between each line.

        Parameters:
        - line_dict (dict): information of values on line between two buses.

        Returns:
        - x (list): list of admittances in 2x2 ybus on a line.

        Note:
        - Tap changing and phase shifting transformer is added to function. All that is needed is to implement it
          in the input file.
    """
    if tap is not None:
        # tap = a , line_dict['Tap']
        x = []
        impedance = complex(float(line_dict['R[pu]']), float(line_dict['X[pu]']))
        half_line_charging_admittance = complex(0, float(line_dict['Half Line Charging Admittance']))
        y_pq = complex(1 / impedance)
        x.append(int(line_dict['From line']))
        x.append(int(line_dict['To line']))
        x.append((y_pq + half_line_charging_admittance)/tap**2) #y11
        x.append(-y_pq/tap) #y12
        x.append(-y_pq/tap) #y21
        x.append(y_pq + half_line_charging_admittance) #y22
        return x
    elif phase is not None:
        # phase = a + jb, line_dict['phase']
        phase_a = phase.real
        phase_b = phase.imag
        x = []
        impedance = complex(float(line_dict['R[pu]']), float(line_dict['X[pu]']))
        half_line_charging_admittance = complex(0, float(line_dict['Half Line Charging Admittance']))
        y_pq = complex(1 / impedance)
        x.append(int(line_dict['From line']))
        x.append(int(line_dict['To line']))
        x.append((y_pq + half_line_charging_admittance)/complex(phase_a**2, phase_b**2)) #y11
        x.append(-y_pq/complex(phase_a, -phase_b)) #y12
        x.append(-y_pq/complex(phase_a, phase_b)) #y21
        x.append(y_pq + half_line_charging_admittance) #y22
        return x
    elif XR_ratio is not None:
        x = []
        impedance = complex(float(line_dict['R[pu]']), float(line_dict['R[pu]'])*XR_ratio)
        half_line_charging_admittance = complex(0, float(line_dict['Half Line Charging Admittance']))
        y_pq = complex(1 / impedance)
        x.append(int(line_dict['From line']))
        x.append(int(line_dict['To line']))
        x.append(y_pq + half_line_charging_admittance) #y11
        x.append(-y_pq) #y12
        x.append(-y_pq) #y21
        x.append(y_pq + half_line_charging_admittance) #y22
        return x
    else:
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

        Parameters: 
        - bus_dict (dict): information on a specific bus.
        - bus_type (str): information of type of bus (PV, PQ or SLACK).
        - Sbase (int): S base value

        Returns:
        - bus (object): Information on specific bus returned as an object.
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

        Parameters:
        - bus_data (list(dict)): data from each bus in the system.
        - Sbase (int): S base value.
        - bus_overview (list(dict)): an overview of bus type, knowns and unknowns on each bus.

        Returns:
        - BusList (list(object)): All bus objects returned in a list.
    """
    BusList = []
    i = 0
    for element in bus_data:
        bus_type = bus_overview[i]['Type']
        BusList.append(setupBusList(element, bus_type, Sbase))
        i += 1
    return BusList

def setupLineList(line_dict):
    line = Line(
        from_line= line_dict["From line"],
        to_line= line_dict["To line"],
        R_pu= line_dict["R[pu]"],
        X_pu= line_dict["X[pu]"],
        half_line_adm= line_dict["Half Line Charging Admittance"]
    )
    return line

def buildLineList(line_data):
    LineList = []
    for element in line_data:
        LineList.append(setupLineList(element))
    return LineList

def BuildYbusMatrix(line_data, num_buses, XR_ratio):
    """
        Construct YBus Matrix for an N-bus system
        Tap changing and phase shifting transformer data can be added if needed. 

        Parameters: 
        - line_data (list(dict)): data from each line in the system.
        - num_buses (int): number of buses in the system.
    """
    line_adm = []
    for element in line_data:
        line_adm.append(setupLineAdmittanceList(line_dict=element, XR_ratio=XR_ratio, tap=None, phase=None))

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
        An overview of Known(delta_x) and Unknown(delta_u) values for each bus, as well as type of bus (PV, PQ of SLACK).
        This overview is without values, and is only a symbolic overview.

        Parameters:
        - bus_data (list(dict)): data from each bus in the system.

        Returns:
        - bus_overview (list(dict)) 
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
        Find known values of P_specified and Q_specified.

        Parameters:
        - bus_data (list(dict)): data from each bus in the system.
        - Sbase (int): S base value.

        Returns:
        - knownP_dict (dict): P_specified values with keys denoted to specific bus.
        - knownQ_dict (dict): Q_specified values with keys denoted to specific bus.
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
        Find unknown values Δδ and Δ|V|

        Parameters: 
        - bus_overview (list(dict)): an overview of bus type, knowns and unknowns on each bus.
        - bus_data (list(dict)): data from each bus in the system.

        Returns:
        - guess_data_dict_V (dict): initial voltage values with keys denoted to specific bus.
        - guess_data_dict_Dirac (dict): initial angle values with keys denoted to specific bus.
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

def J1(BusList, P, dirac, YBus):
    '''
        Calculate the first jacobian matrix, refering to the power and voltages.

        Parameters:
        - BusList (list(objects)): List of buses containing voltage magnitude and angle information.
        - P (dict): Dictionary to specify index length, position and bus number of PV and PQ buses.
        - dirac (dict): Dictionary to specify column length, position and bus number of PV and PQ buses.
        - YBus (array): Admittance matrix representing the power system network.

        Returns:
        - J1_arr (array):  matrix array containing the first jacobian section.

        Note:
        - If SLACK bus is on bus 2 or higher, this means the indexing on J1_arr must be adjusted.
          This is the reason the algorithm check the keys in each iteration.
    '''
    count_P = len(P)
    P_start = extract_number(next(iter(P))) - 1
    count_dirac = len(dirac)
    dirac_start = extract_number(next(iter(dirac))) - 1
    J1_arr = np.zeros((count_P,count_dirac))
    end = len(BusList)

    for i in range(P_start, end):
        d_pos = dirac_start
        key_P = f"P_{i+1}"
        if key_P in P: 
            for j in range(dirac_start, end):
                key_d = f"DIRAC_{j+1}"
                if key_d in dirac:
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
                        J1_arr[i-P_start][j-d_pos] = - abs(v_i*v_j*Y_ij)*math.sin(theta_ij + dirac_j - dirac_i)
                    else: 
                        # Diagonal elements of J1
                        v_i = BusList[i].voltage_magnitude
                        dirac_i = BusList[i].voltage_angle
                        for n in range(end):
                            if n != i:
                                v_n = BusList[n].voltage_magnitude
                                dirac_n = BusList[n].voltage_angle
                                Y_in_polar = cmath.polar(YBus[i][n])
                                Y_in = Y_in_polar[0]
                                theta_in = Y_in_polar[1]
                                PiDiraci += abs(v_i*v_n*Y_in)*math.sin(theta_in + dirac_n - dirac_i)
                            else:
                                continue
                        J1_arr[i-P_start][i-d_pos] = PiDiraci
                else:
                    d_pos += 1        
        else:
            P_start += 1 
            d_pos -= 1  
    return J1_arr

def J2(BusList, P, v, YBus):
    '''
        Calculate the second jacobian matrix, refering to the power and voltages.

        Parameters:
        - BusList (list(object)): List of buses containing voltage magnitude and angle information.
        - P (dict): Dictionary to specify index length, position and bus number of PV and PQ buses.
        - v (dict): Dictionary to specify column length, position and bus number of PQ buses.
        - YBus (array): Admittance matrix representing the power system network.

        Returns:
        - J2_arr (array):  matrix array containing the second jacobian section.

        Note: 
        - If SLACK bus is on bus 2 or higher, this means the indexing on J2_arr must be adjusted.
          This is the reason the algorithm check the keys in each iteration.
    '''
    count_P = len(P)
    P_start = extract_number(next(iter(P))) - 1
    count_v = len(v)
    v_start = extract_number(next(iter(v))) - 1
    J2_arr = np.zeros((count_P, count_v))
    end = len(BusList)
    
    for i in range(P_start, end):
        v_pos = v_start
        key_P = f"P_{i+1}"
        if key_P in P:
            for j in range(v_start, end):
                key_v = f"v_{j+1}"
                if key_v in v:
                    if i != j:  
                        # Off-diagonal elements of J2
                        # Deklarere disse fra bus listen
                        v_i = BusList[i].voltage_magnitude
                        dirac_i = BusList[i].voltage_angle
                        dirac_j = BusList[j].voltage_angle

                        Y_ij_polar = cmath.polar(YBus[i][j])
                        Y_ij = Y_ij_polar[0]
                        theta_ij = Y_ij_polar[1]
                        J2_arr[i-P_start][j-v_pos] = abs(v_i*Y_ij)*math.cos(theta_ij + dirac_j - dirac_i)
                    else: 
                        # Diagonal elements of J2
                        v_i = BusList[i].voltage_magnitude
                        dirac_i = BusList[i].voltage_angle
                        G_ii = complex(YBus[i][i]).real
                        PiVi = 2*abs(v_i)*G_ii

                        for n in range(end):
                            if n != i:
                                v_n = BusList[n].voltage_magnitude
                                dirac_n = BusList[n].voltage_angle
                                Y_in_polar = cmath.polar(YBus[i][n])
                                Y_in = Y_in_polar[0]
                                theta_in = Y_in_polar[1] # return radian value
                                PiVi += abs(v_n*Y_in)*math.cos(theta_in + dirac_n - dirac_i)
                            else:
                                continue
                        J2_arr[i-P_start][i-v_pos] = PiVi
                else:
                    v_pos += 1        
        else:
            P_start += 1  
            v_pos -= 1                       
    return J2_arr

def J3(BusList, Q, dirac, YBus):
    '''
        Calculate the third jacobian matrix, refering to the reactive power and voltage angles.

        Parameters:
        - BusList (list(object)): List of buses (objects)
        - Q (dict): Dictionary to specify index length, position and bus number of PQ buses.
        - dirac (dict): Dictionary to specify column length, position and bus number of PV and PQ buses.
        - YBus (array): Admittance matrix representing the power system network.

        Returns:
        - J3_arr (array): matrix array containing the third jacobian section.

        Note: 
        - If SLACK bus is on bus 2 or higher, this means the indexing on J3_arr must be adjusted.
          This is the reason the algorithm check the keys in each iteration.
    '''
    count_Q = len(Q)
    Q_start = extract_number(next(iter(Q))) - 1
    count_dirac = len(dirac)
    dirac_start = extract_number(next(iter(dirac))) - 1
    J3_arr = np.zeros((count_Q, count_dirac))
    end = len(BusList)

    for i in range(Q_start, end):
        d_pos = dirac_start
        key_Q = f"Q_{i+1}"
        if key_Q in Q:
            for j in range(dirac_start, end):
                key_d = f"DIRAC_{j+1}"
                if key_d in dirac:
                    if i != j:  
                        # Off-diagonal elements of J3
                        v_i = BusList[i].voltage_magnitude
                        v_j = BusList[j].voltage_magnitude
                        dirac_i = BusList[i].voltage_angle
                        dirac_j = BusList[j].voltage_angle

                        Y_ij_polar = cmath.polar(YBus[i][j])
                        Y_ij = Y_ij_polar[0]
                        theta_ij = Y_ij_polar[1]
                        J3_arr[i-Q_start][j-d_pos] = - abs(v_i*v_j*Y_ij)*math.cos(theta_ij + dirac_j - dirac_i)
                    else: 
                        # Diagonal elements of J3
                        QiDiraci = 0
                        v_i = BusList[i].voltage_magnitude
                        dirac_i = BusList[i].voltage_angle
                        for n in range(end):
                            if n != i:
                                v_n = BusList[n].voltage_magnitude
                                dirac_n = BusList[n].voltage_angle
                                Y_in_polar = cmath.polar(YBus[i][n])
                                Y_in = Y_in_polar[0]
                                theta_in = Y_in_polar[1]
                                QiDiraci += abs(v_i*v_n*Y_in)*math.cos(theta_in + dirac_n - dirac_i)
                            else:
                                continue
                        J3_arr[i-Q_start][i-d_pos] = QiDiraci
                else:
                    d_pos += 1        
        else:
            Q_start += 1  
            d_pos -= 1
    return J3_arr

def J4(BusList, Q, v, YBus):
    '''
        Calculate the fourth jacobian matrix, refering to the reactive power and voltages.

        Parameters:
        - BusList (list(object)): List of buses containing voltage magnitude and angle information.
        - Q (dict): Dictionary to specify index length, position and bus number of PQ buses.
        - v (dict): Dictionary to specify column length, position and bus number of PQ buses.
        - YBus (array): Admittance matrix representing the power system network.

        Returns:
        - J4_arr (array):  matrix array containing the fourth jacobian section.

        Note: 
        - If SLACK bus is on bus 2 or higher, this means the indexing on J4_arr must be adjusted.
          This is the reason the algorithm check the keys in each iteration.
    '''
    count_Q = len(Q)
    Q_start = extract_number(next(iter(Q))) - 1
    count_v = len(v)
    v_start = extract_number(next(iter(v))) - 1
    J4_arr = np.zeros((count_Q, count_v))
    end = len(BusList)

    for i in range(Q_start, end):
        v_pos = v_start
        key_Q = f"Q_{i+1}"
        if key_Q in Q:
            for j in range(v_start, end):
                key_v = f"v_{j+1}"
                if key_v in v:
                    if i != j:  
                        # Off-diagonal elements of J4
                        v_i = BusList[i].voltage_magnitude
                        dirac_i = BusList[i].voltage_angle
                        dirac_j = BusList[j].voltage_angle

                        Y_ij_polar = cmath.polar(YBus[i][j])
                        Y_ij = Y_ij_polar[0]
                        theta_ij = Y_ij_polar[1]
                        J4_arr[i-Q_start][j-v_pos] = - abs(v_i*Y_ij)*math.sin(theta_ij + dirac_j - dirac_i)
                    else: 
                        # Diagonal elements of J4
                        v_i = BusList[i].voltage_magnitude
                        dirac_i = BusList[i].voltage_angle
                        B_ii = complex(YBus[i][i]).imag
                        QiVi = - 2*abs(v_i)*B_ii
                        for n in range(end):
                            if n != i:
                                v_n = BusList[n].voltage_magnitude
                                dirac_n = BusList[n].voltage_angle
                                Y_in_polar = cmath.polar(YBus[i][n])
                                Y_in = Y_in_polar[0]
                                theta_in = Y_in_polar[1]
                                QiVi -= abs(v_n*Y_in)*math.sin(theta_in + dirac_n - dirac_i)
                            else:
                                continue
                        J4_arr[i-Q_start][i-v_pos] = QiVi
                else:
                    v_pos += 1        
        else:
            Q_start += 1  
            v_pos -= 1
    return J4_arr

def buildJacobian(BusList, P_spec, Q_spec, v_guess, dirac_guess, YBus):
    '''
        Function that build entire jacobian matrix. This takes into account J1, J2, J3 and J4, and concatinate them together. 

        Parameters:
        - BusList (list(object)): List of buses
        - P_spec (dict): Dictionary to specify index length, position and bus number of PV and PQ buses for matrix J1 and J2.
        - Q_spec (dict): Dictionary to specify index length, position and bus number of PQ buses for matrix J3 and J4.
        - v_guess (dict): Dictionary to specify column length, position and bus number of PQ buses for matrix J2 and J4.
        - dirac_guess (dict): Dictionary to specify column length, position and bus number of PV and PQ buses for matrix J1 and J3.
        - YBus (array): Admittance matrix representing the power system network.

        P_spec, Q_spec, v_guess and dirac_guess are primarily used for matrix size and positional purposes on given matrix.

        Returns:
        - jacobianMatrix (array): matrix array containing calculated jacobian values.
    '''
    Jac1 = J1(BusList, P_spec, dirac_guess, YBus)
    Jac2 = J2(BusList, P_spec, v_guess, YBus)
    Jac3 = J3(BusList, Q_spec, dirac_guess, YBus)
    Jac4 = J4(BusList, Q_spec, v_guess, YBus)
    J1J2 = np.concatenate((Jac1, Jac2), axis= 1)
    J3J4 = np.concatenate((Jac3, Jac4), axis= 1)
    jacobianMatrix = np.concatenate((J1J2, J3J4), axis= 0)
    return jacobianMatrix

def calcP(BusList, P_spec, YBus):
    """
        The function calculates the mismatches in active power (ΔP) for PV and PQ buses. For each specified bus, 
        it computes the change in active power by performing calculations involving the voltage magnitudes, 
        voltage angles, and the admittance matrix.

        Parameters:
        - BusList (list(object)): List of buses (object)
        - P_spec (dict): Dictionary specifying initial active power injections or demands for PV and PQ buses. Keys are used to 
                         ensure correct calculations and position.
        - YBus (array): Admittance matrix representing the power system network.

        Returns:
        - deltaQ (array): Array containing the new mismatches in active power (ΔP). 
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

    P_spec_arr = np.array(list(P_spec.values())).reshape(-1, 1) #.Transpose to match Pi_calc
    deltaP = P_spec_arr - Pi_calc
    return deltaP

def calcQ(BusList, Q_spec, YBus):
    """
        The function calculates the mismatches in reactive power (ΔQ) for PQ buses. For each specified bus, 
        it computes the change in reactive power by performing calculations involving the voltage magnitudes, 
        voltage angles, and the admittance matrix.

        Parameters:
        - BusList (list(object)): List of buses (object)
        - Q_spec (dict): Dictionary specifying initial reactive power injections or demands for PQ buses. Keys are used to 
                         ensure correct calculations and position.
        - YBus (array): Admittance matrix representing the power system network.

        Returns:
        - deltaQ (array): Array containing the new mismatches in reactive power (ΔQ). 
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

    Q_spec_arr = np.array(list(Q_spec.values())).reshape(-1, 1) #.Transpose to match Qi_calc
    deltaQ = Q_spec_arr - Qi_calc
    return deltaQ

def calcDeltaUnknowns(jacobian_matrix, delta_u):
    """
        Calculate Δδ and Δ|V|

        Parameters:
        - jacobian_matrix (array): full jacobian matrix
        - delta_u (array): mismatch values comprised of ΔP and ΔQ

        Return:
        - delta_x (array): calculated mismatches of Δδ and Δ|V| 
    """
    jac_inv = np.linalg.pinv(jacobian_matrix)
    delta_x = np.dot(jac_inv, delta_u)
    return delta_x

def updateVoltageAndAngleList(delta_x, dirac_guess, v_guess):
    """
        Update dirac and voltage lists for voltage and angle dictionaries.

        Parameters:
        - delta_x (array): newly calculated mismatches of voltage and angles.
        - dirac_guess (dict): old mismatch angles.
        - v_guess (dict):  old mismatch voltages.

        Returns:
        - Updated dirac_guess and v_guess with new values from delta_x.

        Trust the process!
    """
    # Update DIRAC guesses with values from the angle elements of delta_x
    dirac_start = extract_number(next(iter(dirac_guess)))
    dirac_end = dirac_start + 1
    dirac_count = len(dirac_guess)
    for i in range(dirac_start, dirac_count + dirac_end):
        dirac_key = f'DIRAC_{i}'
        if dirac_key in dirac_guess:
            dirac_guess[dirac_key] += delta_x[i-dirac_start][0]
        else:
            dirac_start += 1

    # Update v guesses with values from the voltage elements of delta_x
    v_start = extract_number(next(iter(v_guess)))
    v_end = v_start + 1
    count_v = len(v_guess)
    for i in range(v_start, count_v + v_end):
        v_key = f'v_{i}'
        if v_key in v_guess:
            v_guess[v_key] += delta_x[i-v_start+dirac_count][0]
        else:
            v_start +=1

def updateBusList(BusList, dirac_guess=None, v_guess=None):
    """
        Update the |V| and δ for the specified buses.

        Parameters:
        - BusList (list(object)): List of buses.
        - dirac_guess (dict): the now updated values of angles.
        - v_guess (dict): the now updated values of voltages.

        Returns:
        - BusList with updated voltages and angles.
    """
    if v_guess is not None:
        for bus_id in v_guess:
            v_num = extract_number(bus_id)
            for i in range(len(BusList)):
                if v_num == BusList[i].bus_id:
                    BusList[i].update_bus_voltage(new_voltage_magnitude=v_guess[bus_id])
                else:
                    continue

    if dirac_guess is not None:
        for bus_id in dirac_guess:
            dirac_num = extract_number(bus_id)
            for i in range(len(BusList)):
                if dirac_num == BusList[i].bus_id:
                    BusList[i].update_bus_voltage(new_voltage_angle=dirac_guess[bus_id])
                else:
                    continue

def checkTypeSwitch(BusList, YBus, Q_spec, v_guess, Q_lim):
    """
        Function to typeSwitch a bus either from PV to PQ bus or PQ to PV bus.

        Parameters:
        - BusList (list(object)): List of buses (object)
        - YBus (array): Admittance matrix representing the power system network.
        - Q_spec (dict): to be updated if typeSwitched to PQ
        - v_guess (dict): to be updated if typeSwitched to PQ
        - Q_lim (float): Reactive generator limits, used to check PV buses.
        - V_lim (float): Voltage limits, used to check PQ bus, that has already been typeSwitched.

        Returns:
        - Updated bus type in BusList
        - Q_spec (dict): add or remove Q_{bus_num} based on which bus is typeSwitched
        - v_guess (dict): add or remove v_{bus_num} based on wich bus is typeSwitched
    """

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
                
            gen = Qi + BusList[i].Q_load # by definition

            if -abs(Q_lim) < gen < abs(Q_lim):
                continue
            elif gen >= abs(Q_lim):
                gen = abs(Q_lim)
                BusList[i].typeSwitch("PQ_ts")
                BusList[i].update_Pi_Qi(Q_specified= gen - BusList[i].Q_load, Q_gen= gen)

                # Update Q_spec
                key_Q = f"Q_{i+1}"
                Q_spec_temp = {}
                if key_Q not in Q_spec:
                    Q_spec_temp[key_Q] = BusList[i].Q_specified
                for k in Q_spec:
                    Q_spec_temp[k] = Q_spec[k]
                Q_spec = Q_spec_temp

                # Update v_guess
                key_v = f"v_{i+1}"
                v_guess_temp = {}
                if key_v not in v_guess:
                    v_guess_temp[key_v] = BusList[i].voltage_magnitude
                    BusList[i].update_bus_voltage(new_previous_voltage= BusList[i].voltage_magnitude)
                for k in v_guess:
                    v_guess_temp[k] = v_guess[k]
                v_guess = v_guess_temp

            else:
                gen = -abs(Q_lim)
                BusList[i].typeSwitch("PQ_ts")
                BusList[i].update_Pi_Qi(Q_specified= gen - BusList[i].Q_load, Q_gen= gen)

                # Update Q_spec
                key_Q = f"Q_{i+1}"
                Q_spec_temp = {}
                if key_Q not in Q_spec:
                    Q_spec_temp[key_Q] = BusList[i].Q_specified
                for k in Q_spec:
                    Q_spec_temp[k] = Q_spec[k]
                Q_spec = Q_spec_temp

                # Update v_guess
                key_v = f"v_{i+1}"
                v_guess_temp = {}
                if key_v not in v_guess:
                    v_guess_temp[key_v] = BusList[i].voltage_magnitude
                    BusList[i].update_bus_voltage(new_previous_voltage= BusList[i].voltage_magnitude)
                for k in v_guess:
                    v_guess_temp[k] = v_guess[k]
                v_guess = v_guess_temp

        elif BusList[i].BusType == 'PQ_ts':
            Qi = 0
            gen_old = BusList[i].Q_gen
            v_i = BusList[i].voltage_magnitude
            dirac_i = BusList[i].voltage_angle
            for n in range(len(BusList)):
                v_n = BusList[n].voltage_magnitude
                dirac_n = BusList[n].voltage_angle
                Y_in_polar = cmath.polar(YBus[i][n])
                Y_in = Y_in_polar[0]
                theta_in = Y_in_polar[1]
                Qi -= abs(v_i*v_n*Y_in)*math.sin(theta_in + dirac_n - dirac_i)

            gen = Qi + BusList[i].Q_load

            # if BusList[i].voltage_magnitude >= BusList[i].previous_voltage:
            #     BusList[i].typeSwitch("PV")
            #     BusList[i].update_bus_voltage(new_previous_voltage= BusList[i].voltage_magnitude)

            #     # Update Q_spec
            #     key_Q = f"Q_{i+1}"
            #     Q_spec.pop(key_Q, None)
                
            #     # Update v_guess
            #     key_v = f"v_{i+1}"
            #     v_guess.pop(key_v, None)

            if gen_old == -abs(Q_lim): # lower limit
                if BusList[i].voltage_magnitude >= BusList[i].previous_voltage:
                    gen = -abs(Q_lim)
                    BusList[i].update_Pi_Qi(Q_specified= gen - BusList[i].Q_load, Q_gen= gen)
                else:
                    if gen >= abs(Q_lim): # upper limit
                        gen = abs(Q_lim)
                        BusList[i].update_Pi_Qi(Q_specified= gen - BusList[i].Q_load, Q_gen= gen)
                    elif gen <= -abs(Q_lim):    # lower limit
                        gen = -abs(Q_lim)
                        BusList[i].update_Pi_Qi(Q_specified= gen - BusList[i].Q_load, Q_gen= gen)
                    else:   # Q_lim < gen < abs(Q_lim)
                        BusList[i].typeSwitch("PV")
                        temp = BusList[i].previous_voltage
                        BusList[i].update_bus_voltage(new_previous_voltage= BusList[i].voltage_magnitude)
                        BusList[i].update_bus_voltage(new_voltage_magnitude= temp)
                        BusList[i].update_Pi_Qi(Q_specified= gen - BusList[i].Q_load, Q_gen= gen)
                        # Update Q_spec
                        key_Q = f"Q_{i+1}"
                        Q_spec.pop(key_Q, None)
                        # Update v_guess
                        key_v = f"v_{i+1}"
                        v_guess.pop(key_v, None)

            elif gen_old == abs(Q_lim):
                if BusList[i].voltage_magnitude <= BusList[i].previous_voltage:
                    gen = abs(Q_lim)
                    BusList[i].update_Pi_Qi(Q_specified= gen - BusList[i].Q_load, Q_gen= gen)
                else:
                    if gen >= abs(Q_lim): # upper limit
                        gen = abs(Q_lim)
                        BusList[i].update_Pi_Qi(Q_specified= gen - BusList[i].Q_load, Q_gen= gen)
                    elif gen <= -abs(Q_lim):    # lower limit
                        gen = -abs(Q_lim)
                        BusList[i].update_Pi_Qi(Q_specified= gen - BusList[i].Q_load, Q_gen= gen)
                    else:   # Q_lim < gen < abs(Q_lim)
                        BusList[i].typeSwitch("PV")
                        # BusList[i].update_bus_voltage(new_voltage_magnitude= BusList[i].previous_voltage)
                        temp = BusList[i].previous_voltage
                        BusList[i].update_bus_voltage(new_previous_voltage= BusList[i].voltage_magnitude)
                        BusList[i].update_bus_voltage(new_voltage_magnitude= temp)
                        BusList[i].update_Pi_Qi(Q_specified= gen - BusList[i].Q_load, Q_gen= gen)
                        # Update Q_spec
                        key_Q = f"Q_{i+1}"
                        Q_spec.pop(key_Q, None)
                        # Update v_guess
                        key_v = f"v_{i+1}"
                        v_guess.pop(key_v, None)

    return Q_spec, v_guess
    
def checkConvergence(tol, delta_u):
    """
        Function to check convergence. Checks if all values in array are less than tolerance.

        Parameters:
        - tol (float): Tolerance of convergence.
        - delta_u (array): array to be checked.
        '
        Returns:
        - (bool): True or False 
    """
    if np.all(abs(delta_u) < tol):
        return True
    else:
        return False

def updateSlackAndPV(BusList, YBus, Sbase):
    """
        Update Pi and Qi on SLACK bus and Qi on PV bus

        Parameters:
        - BusList (list(object)): List of buses (object)
        - YBus (array): Admittance matrix representing the power system network.
        - Sbase (int): S base value

        Returns:
        - Updated BusList 
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
            BusList[i].update_Pi_Qi(P_specified=Pi, P_gen= (Pi + BusList[i].P_load))

            Qi = 0
            for n in range(len(BusList)):
                v_n = BusList[n].voltage_magnitude
                dirac_n = BusList[n].voltage_angle
                Y_in_polar = cmath.polar(YBus[i][n])
                Y_in = Y_in_polar[0]
                theta_in = Y_in_polar[1]
                Qi -= abs(v_i*v_n*Y_in)*math.sin(theta_in + dirac_n - dirac_i)
            BusList[i].update_Pi_Qi(Q_specified=Qi, Q_gen= (Qi + BusList[i].Q_load))

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
            BusList[i].update_Pi_Qi(Q_specified=Qi, Q_gen= (Qi + BusList[i].Q_load))

def calcDecoupledJacobian(BusList, P, Q, v, dirac, YBus):
    """
        Fundtion to calculate Jacobian matrix used in decoupled load flow. J2 and J3 are all zero matrices.

        Parameters:
        - BusList (list(object)): List of buses
        - P_spec (dict): Dictionary to specify index length, position and bus number of PV and PQ buses for matrix J1 and J2.
        - Q_spec (dict): Dictionary to specify index length, position and bus number of PQ buses for matrix J3 and J4.
        - v_guess (dict): Dictionary to specify column length, position and bus number of PQ buses for matrix J2 and J4.
        - dirac_guess (dict): Dictionary to specify column length, position and bus number of PV and PQ buses for matrix J1 and J3.
        - YBus (array): Admittance matrix representing the power system network.

        P_spec, Q_spec, v_guess and dirac_guess are primarily used for matrix size and positional purposes on given matrix.

        Returns:
        - jacobianMatrix (array): matrix array containing calculated jacobian values.
    """
    Jac1 = J1(BusList, P, dirac, YBus)
    Jac2 = np.zeros((len(P), len(v)))
    Jac3 = np.zeros((len(Q), len(dirac)))
    Jac4 = J4(BusList, Q, v, YBus)
    J1J2 = np.concatenate((Jac1, Jac2), axis= 1)
    J3J4 = np.concatenate((Jac3, Jac4), axis= 1)
    Jac_arr = np.concatenate((J1J2, J3J4), axis= 0)
    return Jac_arr

def calcDecoupledDiracVoltage(dlf_jacobian, delta_u):
    """
        Calculate Δδ and Δ|V| for decoupled conditions

        Parameters:
        - dlf_jacobian (array): decoupled jacobian matrix
        - delta_u (array): mismatch values comprised of ΔP and ΔQ

        Return:
        - delta_x (array): calculated mismatches of Δδ and Δ|V| 
    """
    jac_inv = np.linalg.pinv(dlf_jacobian)
    dirac_voltage = np.dot(jac_inv, delta_u)
    return dirac_voltage

def calcB_Prime(BusList, YBus):
    """
        Function to make B' and B'', used for decoupled

        Parameters:
        - BusList (list(object)): List of buses (object)
        - YBus (array): Admittance matrix representing the power system network.
    """
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


    for i in range(len(BusList)):
        if BusList[i].bus_id == 1 and BusList[i].BusType == 'PV':
            bus_index = BusList[i].bus_id - 1
            B_double_prime = np.delete(B_prime, bus_index, axis=0)
            B_double_prime = np.delete(B_double_prime, bus_index, axis=1)

        elif BusList[i].BusType == 'PV':
            bus_index = BusList[i].bus_id - 2
            B_double_prime = np.delete(B_prime, bus_index, axis=0)
            B_double_prime = np.delete(B_double_prime, bus_index, axis=1)

    
    return B_prime, B_double_prime
    
def calcDeltaPn_Vn(BusList, deltaP):
    """
        Takes mismatches P and devides them with the voltage magnitudes ΔPn/|Vn|

        Parameters:
        - BusList (list(object)): List of buses
        - deltaP (array): mismatches of P
    """
    diff = len(BusList) - len(deltaP)
    for i in range(len(BusList)):
        if BusList[i].BusType != "Slack":
            deltaP[i-diff] = deltaP[i-diff]/abs(BusList[i].voltage_magnitude)
    return deltaP

def updateAngleFDLFandBusList(BusList, delta_dirac, dirac_guess=None):
    """
        Update angle list and angles in BusList, so that they can be used in ΔQn/|Vn|

        Parameters:
        - BusList (list(object)): List of buses
        - delta_dirac (array): mismatches of angles
        - dirac_guess (dict): angles
    """
    dirac_start = extract_number(next(iter(dirac_guess)))
    dirac_count = len(dirac_guess)
    for i in range(dirac_start, dirac_count + dirac_start):
        dirac_key = f'DIRAC_{i}'
        if dirac_key in dirac_guess:
            dirac_guess[dirac_key] += delta_dirac[i-dirac_start][0]
        else:
            dirac_start += 1

    for bus_id in dirac_guess:
        dirac_num = extract_number(bus_id)
        for i in range(len(BusList)):
            if dirac_num == BusList[i].bus_id:
                BusList[i].update_bus_voltage(new_voltage_angle=dirac_guess[bus_id])
            else:
                continue

def calcDeltaQn_Vn(BusList, deltaQ):
    """
        Takes mismatches Q and devides them with the voltage magnitudes ΔQn/|Vn|, with updated voltages.

        Parameters:
        - BusList (list(object)): List of buses
        - deltaQ (array): mismatches of Q
    """
    diff = len(BusList) - len(deltaQ)
    for i in range(len(BusList)):
        if BusList[i].BusType != "Slack":
            deltaQ[i-diff] = deltaQ[i-diff]/abs(BusList[i].voltage_magnitude)
    return deltaQ

def updateVoltageFDLFandBusList(BusList, delta_v, v_guess=None):
    """
        Update voltage list and voltages in BusList.

        Parameters:
        - BusList (list(object)): List of buses
        - delta_v (array): mismatches of voltage
        - v_guess (dict): voltage
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

def YBusDC(BusList, YBus):
    YBus_DC = None
    for i in range(len(BusList)):
        if BusList[i].BusType == 'Slack':
            bus_index = BusList[i].bus_id - 1
            YBus_DC = np.delete(YBus, bus_index, axis=0)
            YBus_DC = np.delete(YBus_DC, bus_index, axis=1)
            # Removes real parts of elements
            YBus_DC = YBus_DC.imag * (-1)
    return YBus_DC

def makeDataFrame(BusList, Sbase, Ubase):
    """
        Function to make BusList into a DataFrame

        Parameters:
        - BusList (list(object)): List of buses

        Returns:
        - df_NRLF (DataFrame)
    """
    
    data_to_add = []
    for i in range(len(BusList)):
        dict_NRLF = {
            'Bus': BusList[i].bus_id,
            'Type': BusList[i].BusType,
            'Voltage [pu]': round(BusList[i].voltage_magnitude * Ubase, 3),
            'Angle [deg]': round((180/math.pi)*BusList[i].voltage_angle, 3),
            'P [pu]': round(BusList[i].P_specified * Sbase, 3),
            'Q [pu]': round(BusList[i].Q_specified * Sbase, 3)
        }
        data_to_add.append(dict_NRLF)
    df_NRLF = pd.DataFrame(data_to_add)
    return df_NRLF

def print_dataframe_as_latex(dataframe):
    """
        Generates code to display a dataframe in LaTeX using the tabularx package.
    """
    
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

def PowerLossAndFlow(line_data, BusList, Sbase, Ubase, XR_ratio=None):
    sumP = 0
    sumQ = 0
    PLine_flow = []
    S_I_lsit = []
    Ibase = (Sbase*1e6)/(Ubase*1e3)

    for d in (line_data): 

        busa = int(d['From line'])
        busb = int(d['To line'])
        Name = f"Line {busa}-{busb}"

        va = float(BusList[busa - 1].voltage_magnitude) 
        vb = float(BusList[busb - 1].voltage_magnitude) 

        dirac_a = float(BusList[busa - 1].voltage_angle)
        dirac_b = float(BusList[busb - 1].voltage_angle) 

        Va = cmath.rect(va, dirac_a)
        Vb = cmath.rect(vb, dirac_b)

        Yc = 1j* float(d['Half Line Charging Admittance'])

        Zr = float(d['R[pu]']) 
        if XR_ratio is not None:
            Zx = 1j*float(d['R[pu]']) * XR_ratio 
        else:
            Zx = 1j*float(d['X[pu]'])

        Yl = 1 / (Zr + Zx) 

        Iab = Yl * (Va -Vb) + Yc * Va
        Iba = Yl * (Vb -Va) + Yc * Vb
        I_line = Yl * (Va-Vb)
        I_line_polar = cmath.polar(I_line)
        if XR_ratio is not None:
            Q_loss = I_line_polar[0]**2 * float(d['R[pu]']) * XR_ratio * Sbase
        else:
            Q_loss = I_line_polar[0]**2 * float(d['X[pu]']) * Sbase

        Sab = Va * np.conj(Iab)
        Sba = Vb * np.conj(Iba)

        Pab = Sab.real
        Pba = Sba.real
        Qab = Sab.imag
        Qba = Sba.imag

        Pab = (Pab * Sbase)
        Pba = (Pba * Sbase)
        Qab = (Qab * Sbase)
        Qba = (Qba * Sbase)

        sumP += (abs(Pab) - abs(Pba))
        sumQ += (abs(Qab) - abs(Qba))

        PLine_direction = {'From bus' : busa,
                            'To bus': busb,
                            'P ij[MW]' : round(Pab,3),
                            'Q ij[MVAr]' : round(Qab, 3),
                            'P ji[MW]' : round(Pba,3),
                            'Q ji[MVAr]' : round(Qba,3),
                            'P Loss[MW]' : round(abs(Pab) - abs(Pba),3),
                            'Q Loss[MVAR]' : round(abs(Qab)- abs(Qba),3)
                            }
        PLine_flow.append(PLine_direction)


        Iab_polar = cmath.polar(Iab)
        Iba_polar = cmath.polar(Iba)

        S_I = {'From bus' : busa,
                'To bus': busb,
                'S_ij [MVA]': Sbase*math.sqrt((Sab.real**2) + (Sab.imag)**2),
                'I_ij [A]':  Ibase*Iab_polar[0],
                'S_ji [MVA]': Sbase*math.sqrt((Sba.real**2) + (Sba.imag)**2),
                'I_ji [A]': Ibase*Iba_polar[0]
        }

        S_I_lsit.append(S_I)
                

        
            
    dfPowerflow = pd.DataFrame(PLine_flow)
    df_S_I = pd.DataFrame(S_I_lsit)

    sumP = round(sumP,3)
    sumQ = round(sumQ,3)


    return sumP, sumQ, dfPowerflow, df_S_I

