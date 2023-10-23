import math, cmath
import re
import csv
import numpy as np

from classes import *

def ReadCsvFile(file):
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

def setupBusList(bus_dict, Sbase):
    bus = Bus(
            bus_id= int(bus_dict['Bus Code']),
            voltage_magnitude= float(bus_dict['Assumed bus voltage (pu)']),
            voltage_angle= float(bus_dict['Angle']),
            P_specified= (float(bus_dict['Generation (MW)']) - float(bus_dict['Load (MW)']))/Sbase if (bus_dict['Generation (MW)'] or bus_dict['Load (MW)']) != '-' else None,
            Q_specified= (float(bus_dict['Generation (MVAr)']) - float(bus_dict['Load (MVAr)']))/Sbase if (bus_dict['Generation (MVAr)'] or bus_dict['Load (MVAr)']) != '-' else None
        )
    return bus

def buildBusList(bus_data, Sbase):
    BusList = []
    for element in bus_data:
        BusList.append(setupBusList(element, Sbase))
    return BusList

def BuildYbusMatrix(line_data,num_buses):
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
            bus_info['Unknown_2'] = 'DIRAQ'
    
        elif bus_voltage != "-" and (generation_mw != "-" and load_mw != "-"):
            bus_info['Bus'] = i+1
            bus_info['Type'] = 'P' + 'V'
            bus_info['Known_1'] = 'P'
            bus_info['Known_2'] = 'V'
            bus_info['Unknown_1'] = 'Q' 
            bus_info['Unknown_2'] = 'DIRAQ'

        else:
            bus_info['Bus'] = i+1
            bus_info['Type'] = "Slack"
            bus_info['Known_1'] = 'V'
            bus_info['Known_2'] = 'DIRAQ'
            bus_info['Unknown_1'] = 'P'
            bus_info['Unknown_2'] = 'Q'
        
        bus_overview.append(bus_info)

    return bus_overview

def findKnowns(bus_data, Sbase):
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
    guess_data_dict_V = {}
    guess_data_dict_Diraq = {}

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
        if unknown2 == 'DIRAQ':
            new_name_unknown_diraq = f"DIRAQ_{k+1}"
            guessDiraq = float(bus_data[k]['Angle'])
            guess_data_dict_Diraq[new_name_unknown_diraq] = guessDiraq
        k += 1

    return guess_data_dict_V, guess_data_dict_Diraq

def extract_number(s):
    match = re.search(r'\d+', s)
    if match:
        return int(match.group())
    else:
        return None

def J1(BusList, P, diraq, YBus):
    '''
        Calculate the first jacobian matrix, refering to the power and voltages.
    '''
    # first_key = next(iter(P))
    # start_num = extract_number(first_key)
    # second_key = next(iter(diraq))
    # start_num_diraq = extract_number(second_key)

    count_P = len(P)
    count_diraq = len(diraq)
    # df_J1 = pd.DataFrame(0, index=range(1, count_P), columns=range(1, count_diraq), dtype=complex)
    J1_arr = np.zeros((count_P,count_diraq))

    for i in range(count_P):
        for j in range(count_diraq):
            PiDiraqi = 0
            if i != j:  
                # Off-diagonal elements of J1
                v_i = BusList[i].voltage_magnitude
                v_j = BusList[j].voltage_magnitude
                diraq_i = BusList[i].voltage_angle
                diraq_j = BusList[j].voltage_angle

                Y_ij_polar = cmath.polar(YBus[i][j])
                Y_ij = Y_ij_polar[0]
                theta_ij = Y_ij_polar[1]
                J1_arr[i][j] = - abs(v_i*v_j*Y_ij)*math.sin(theta_ij + diraq_j - diraq_i)
            else: 
                # Diagonal elements of J1
                v_i = BusList[i].voltage_magnitude
                diraq_i = BusList[i].voltage_angle
                for n in range(count_diraq):
                    if n != i:
                        v_n = BusList[n].voltage_magnitude
                        diraq_n = BusList[n].voltage_angle
                        Y_in_polar = cmath.polar(YBus[i][n])
                        Y_in = Y_in_polar[0]
                        theta_in = Y_in_polar[1]
                        PiDiraqi += abs(v_i*v_n*Y_in)*math.sin(theta_in + diraq_n - diraq_i)
                    else:
                        continue
                J1_arr[i][i] = PiDiraqi
    return J1_arr

def J2(BusList, P, v, YBus):
    '''
        Calculate the second jacobian matrix, refering to the power and voltages.
    '''
    count_P = len(P)
    count_v = len(v)
    # df_J2 = pd.DataFrame(0, index=range(1, count_P), columns=range(1, count_v), dtype=complex)
    J2_arr = np.zeros((count_P, count_v))

    for i in range(count_P):
        for j in range(count_v):
            if i != j:  
                # Off-diagonal elements of J2
                # Deklarere disse fra bus listen
                v_i = BusList[i].voltage_magnitude
                diraq_i = BusList[i].voltage_angle
                diraq_j = BusList[j].voltage_angle

                Y_ij_polar = cmath.polar(YBus[i][j])
                Y_ij = Y_ij_polar[0]
                theta_ij = Y_ij_polar[1]
                J2_arr[i][j] = abs(v_i*Y_ij)*math.cos(theta_ij + diraq_j - diraq_i)
            else: 
                # Diagonal elements of J2
                v_i = BusList[i].voltage_magnitude
                diraq_i = BusList[i].voltage_angle
                G_ii = complex(YBus[i][i]).real
                PiVi = 2*abs(v_i)*G_ii

                for n in range(count_v):
                    v_n = BusList[n].voltage_magnitude
                    diraq_n = BusList[n].voltage_angle
                    if n != i:
                        Y_in_polar = cmath.polar(YBus[i][n])
                        Y_in = Y_in_polar[0]
                        theta_in = Y_in_polar[1] # return radian value
                        PiVi += abs(v_n*Y_in)*math.cos(theta_in + diraq_n - diraq_i)
                    else:
                        continue
                J2_arr[i][i] = PiVi

    return J2_arr

def J3(BusList, Q, diraq, YBus):
    '''
        Calculate the third jacobian matrix, refering to the reactive power and voltages.
    '''
    count_Q = len(Q)
    count_diraq = len(diraq)
    # df_J3 = pd.DataFrame(0, index=range(1, count_Q), columns=range(1, count_diraq), dtype=complex)
    J3_arr = np.zeros((count_Q, count_diraq))

    for i in range(count_Q):
        for j in range(count_diraq):
            if i != j:  
                # Off-diagonal elements of J3
                v_i = BusList[i].voltage_magnitude
                v_j = BusList[j].voltage_magnitude
                diraq_i = BusList[i].voltage_angle
                diraq_j = BusList[j].voltage_angle

                Y_ij_polar = cmath.polar(YBus[i][j])
                Y_ij = Y_ij_polar[0]
                theta_ij = Y_ij_polar[1]
                J3_arr[i][j] = - abs(v_i*v_j*Y_ij)*math.cos(theta_ij + diraq_j - diraq_i)
            else: 
                # Diagonal elements of J3
                QiDiraqi = 0
                v_i = BusList[i].voltage_magnitude
                diraq_i = BusList[i].voltage_angle
                for n in range(count_diraq):
                    v_n = BusList[n].voltage_magnitude
                    diraq_n = BusList[n].voltage_angle
                    if n != i:
                        Y_in_polar = cmath.polar(YBus[i][n])
                        Y_in = Y_in_polar[0]
                        theta_in = Y_in_polar[1]
                        QiDiraqi += abs(v_i*v_n*Y_in)*math.cos(theta_in + diraq_n - diraq_i)
                    else:
                        continue
                J3_arr[i][i] = QiDiraqi
    return J3_arr

def J4(BusList, Q, v, YBus):
    '''
        Calculate the second jacobian matrix, refering to the power and voltages.
    '''
    count_Q = len(Q)
    count_v = len(v)
    # df_J4 = pd.DataFrame(0, index=range(1, count_Q), columns=range(1, count_v), dtype=complex)
    J4_arr = np.zeros((count_Q, count_v))

    for i in range(count_Q):
        for j in range(count_v):
            if i != j:  
                # Off-diagonal elements of J4
                v_i = BusList[i].voltage_magnitude
                diraq_i = BusList[i].voltage_angle
                diraq_j = BusList[j].voltage_angle

                Y_ij_polar = cmath.polar(YBus[i][j])
                Y_ij = Y_ij_polar[0]
                theta_ij = Y_ij_polar[1]
                J4_arr[i][j] = - abs(v_i*Y_ij)*math.sin(theta_ij + diraq_j - diraq_i)
            else: 
                # Diagonal elements of J4
                v_i = BusList[i].voltage_magnitude
                diraq_i = BusList[i].voltage_angle
                B_ii = complex(YBus[i][i]).imag
                QiVi = - 2*abs(v_i)*B_ii

                for n in range(count_v):
                    v_n = BusList[n].voltage_magnitude
                    diraq_n = BusList[n].voltage_angle
                    if n != i:
                        Y_in_polar = cmath.polar(YBus[i][n])
                        Y_in = Y_in_polar[0]
                        theta_in = Y_in_polar[1]
                        QiVi -= abs(v_n*Y_in)*math.sin(theta_in + diraq_n - diraq_i)
                    else:
                        continue
                J4_arr[i][i] = QiVi
    return J4_arr

def Jacobian(BusList, P, Q, v, diraq, YBus):
    Jac1 = J1(BusList, P, diraq, YBus)
    Jac2 = J2(BusList, P, v, YBus)
    Jac3 = J3(BusList, Q, diraq, YBus)
    Jac4 = J4(BusList, Q, v, YBus)
    J1J2 = np.concatenate((Jac1, Jac2), axis= 1)
    J3J4 = np.concatenate((Jac3, Jac4), axis= 1)
    Jac_arr = np.concatenate((J1J2, J3J4), axis= 0)
    return Jac_arr
  
def calcP(BusList, P_spec, YBus, Sbase):
    Pi_calc = np.zeros([len(P_spec), 1])
    start_val = len(BusList) - len(P_spec)
    for i in range(start_val, len(BusList)):
        v_i = BusList[i].voltage_magnitude
        diraq_i = BusList[i].voltage_angle
        G_ii = complex(YBus[i][i]).real
        Pi = 2*abs(v_i)**2*G_ii
        for n in range(1, len(BusList)):
            v_n = BusList[n].voltage_magnitude
            diraq_n = BusList[n].voltage_angle
            if n != i:
                Y_in_polar = cmath.polar(YBus[i][n])
                Y_in = Y_in_polar[0]
                theta_in = Y_in_polar[1]
                Pi += abs(v_i*v_n*Y_in)*math.cos(theta_in + diraq_n - diraq_i)
            else:
                continue
        Pi_calc[i-start_val] = Pi

    P_spec_arr = np.array(list(P_spec.values())).reshape(-1, 1)
    deltaP = P_spec_arr - Pi_calc/Sbase
    return deltaP

def calcQ(BusList, Q_spec, YBus, Sbase):
    Qi_calc = np.zeros([len(Q_spec), 1])
    start_val = len(BusList) - len(Q_spec)
    for i in range(start_val, len(BusList)):
        v_i = BusList[i].voltage_magnitude
        diraq_i = BusList[i].voltage_angle
        B_ii = complex(YBus[i][i]).imag
        Qi = -2*abs(v_i)**2*B_ii
        for n in range(1, len(BusList)):
            v_n = BusList[n].voltage_magnitude
            diraq_n = BusList[n].voltage_angle
            if n != i:
                Y_in_polar = cmath.polar(YBus[i][n])
                Y_in = Y_in_polar[0]
                theta_in = Y_in_polar[1]
                Qi -= abs(v_i*v_n*Y_in)*math.sin(theta_in + diraq_n - diraq_i)
            else:
                continue
        Qi_calc[i-start_val] = Qi

    Q_spec_arr = np.array(list(Q_spec.values())).reshape(-1, 1)
    deltaP = Q_spec_arr - Qi_calc/Sbase
    return deltaP

def calcDeltaUnknowns(jacobian_matrix, knowns):
    jac_inv = np.linalg.pinv(jacobian_matrix)
    unknowns = np.dot(jac_inv, knowns)
    return unknowns

def updateVoltageAndAngleList(unknowns, diraq_guess, v_guess):
    
    # Update DIRAQ guesses with values from the first four elements of unknowns
    for i in range(len(diraq_guess)):
        diraq_key = f'DIRAQ_{i+2}'  # Assuming it starts with 'DIRAQ_2'
        diraq_guess[diraq_key] += unknowns[i][0]

    # Update v guesses with values from the last three elements of unknowns
    for i in range(len(v_guess)):
        v_key = f'v_{i+3}'  # Assuming it starts with 'v_3'
        v_guess[v_key] += unknowns[i + len(diraq_guess)][0]

def updateBusList(BusList, diraq_guess, v_guess):
    # Update the voltage for the specified buses
    for bus_id in v_guess:
        v_num = extract_number(bus_id)
        for i in range(len(BusList)):
            if v_num == BusList[i].bus_id:
                BusList[i].update_bus_voltage(new_voltage_magnitude=v_guess[bus_id])
            else:
                continue

    for bus_id in diraq_guess:
        diraq_num = extract_number(bus_id)
        for i in range(len(BusList)):
            if diraq_num == BusList[i].bus_id:
                BusList[i].update_bus_voltage(new_voltage_angle=diraq_guess[bus_id])
            else:
                continue
