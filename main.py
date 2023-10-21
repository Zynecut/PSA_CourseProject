import csv
from classes import *
# from functions import *
import math, cmath


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

def SortLineDictToList(line_dict):
    x = []
    impedance = complex(float(line_dict['R[pu]']), float(line_dict['X[pu]']))
    half_line_charging_admittance = complex(float(line_dict['Half Line Charging Admittance']))
    y_pq = complex(1 / impedance)
    x.append(int(line_dict['From line']))
    x.append(int(line_dict['To line']))
    x.append(complex(y_pq + half_line_charging_admittance)) #y11
    x.append(complex(-y_pq)) #y12
    x.append(complex(-y_pq)) #y21
    x.append(complex(y_pq + half_line_charging_admittance)) #y22
    return x

def BuildYbusMatrix(line_adm,num_buses):
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

def setupBusType(bus_data, Sbase):
    bus_overview = []
    knownP_dict = {}
    knownQ_dict = {}
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
            bus_info['Unknown_2'] = 'θ'
    
        elif bus_voltage != "-" and (generation_mw != "-" and load_mw != "-"):
            bus_info['Bus'] = i+1
            bus_info['Type'] = 'P' + 'V'
            bus_info['Known_1'] = 'P'
            bus_info['Known_2'] = 'V'
            bus_info['Unknown_1'] = 'Q' 
            bus_info['Unknown_2'] = 'θ'

        else:
            bus_info['Bus'] = i+1
            bus_info['Type'] = "Slack"
            bus_info['Known_1'] = 'V'
            bus_info['Known_2'] = 'θ'
            bus_info['Unknown_1'] = 'P'
            bus_info['Unknown_2'] = 'Q'
        
        bus_overview.append(bus_info)

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

    return bus_overview, knownP_dict, knownQ_dict


def J1(BusList, P, YBus):
    '''
        Calculate the first jacobian matrix, refering to the power and voltages.
    '''
    count_P = len(P)
    count_diraq = 3
    # df_J1 = pd.DataFrame(0, index=range(1, count_P), columns=range(1, count_diraq), dtype=complex)
    J1_arr = np.zeros((count_P,count_diraq), dtype=complex)

    for i in range(1, count_P):
        for j in range(1, count_diraq):
            if i != j:  
                # Off-diagonal elements of J1
                # Deklarere disse fra bus listen
                v_i = BusList[i]['voltage_magnitude']
                v_j = BusList[j]['voltage_magnitude']
                diraq_i = BusList[i]['voltage_angle']
                diraq_j = BusList[j]['voltage_angle']

                Y_ij_polar = cmath.polar(YBus[i][j])
                Y_ij = Y_ij_polar[0]
                theta_ij = Y_ij_polar[1]
                PiDiraqj = - abs(v_i*v_j*Y_ij)*math.sin(theta_ij + diraq_j - diraq_i)
                J1_arr[i][j] = PiDiraqj
            else: 
                # Diagonal elements of J1
                v_i = BusList[i]['voltage_magnitude']
                PiDiraqj = None
                N = 4 # blir vel count_v som skal inn her egentlig
                for n in range(1, N):
                    if n != i:
                        v_n = BusList[n]['voltage_magnitude']
                        diraq_n = BusList[n]['voltage_angle']
                        Y_in_polar = cmath.polar(YBus[i][n])
                        Y_in = Y_in_polar[0]
                        theta_in = Y_in_polar[1]
                        sumE = abs(v_i*v_n*Y_in)*math.sin(theta_in + diraq_n - diraq_i)
                        PiDiraqi += sumE
                    else:
                        continue
                J1_arr[i][i] = PiDiraqi

    return J1_arr

def main():
    line_data = ReadCsvFile('./files/network_configuration_line_data.csv')
    bus_data = ReadCsvFile('./files/network_configuration_bus_data.csv')
    Sbase = 100 # MVA
    num_buses = len(bus_data)
    line_admittances = []
    BusList = []

    for line_dict in line_data:
        line_admittances.append(SortLineDictToList(line_dict))
    
    YBus = BuildYbusMatrix(line_admittances, num_buses)
    print(YBus)
    # Makes a list of objects with Bus values in per unit [pu]
    for bus_dict in bus_data:
        bus = Bus(
            bus_id= int(bus_dict['Bus Code']),
            voltage_magnitude= float(bus_dict['Assumed bus voltage (pu)']),
            voltage_angle= float(bus_dict['Angle']),
            realP= (float(bus_dict['Generation (MW)']) - float(bus_dict['Load (MW)']))/Sbase if (bus_dict['Generation (MW)'] or bus_dict['Load (MW)']) != '-' else None,
            reaqQ= (float(bus_dict['Generation (MVAr)']) - float(bus_dict['Load (MVAr)']))/Sbase if (bus_dict['Generation (MVAr)'] or bus_dict['Load (MVAr)']) != '-' else None
        )
        BusList.append(bus)

    bus_overview, P, Q = setupBusType(bus_data, Sbase)
    
    Jac1 = J1(BusList, P, YBus)
    a = 1


if __name__ == '__main__':
    main()