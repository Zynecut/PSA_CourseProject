# dict_var = {
#     'V1' : 24,
#     'V2' : 0,
#     'V3' : 0
# }
# n = 1
# list_var = [{'V1': 2, 'P1' : 1, 'Q1': 1}, {'V2' : 1, 'P2':2, 'Q2':1}]
# for i in list_var[n-1]:
#     print(list_var[i][f'P{i}'])
#     n += 1

# list_var = [{'V1': 2, 'P1': 32, 'Q1': 1}, {'V2': 1, 'P2': 28, 'Q2': 1}, {'V3': 3, 'P3': 13, 'Q3': 1}]

# for dictionary in list_var:
#     for key, value in dictionary.items():
#         if key.startswith('P'):
#             print(value)

# print(dict_var['V1'])


# Test for ybus creation:

#         for i in range(1, num_buses + 1):
#             sum_of_admittances = 0
#             for j in range(num_buses):
#                 key1 = f'Y{i}{i}'
# #                 key2 = f'Y{i}{j+1}'
# #                 key3 = f'Y{j+1}{i}'

        # Fill in the diagonal elements with sums of admittances going into that specific bus.
        # for i in range(1, num_buses + 1):

        #     Y_bus.loc[i, i] = sum(self.line_adm[j][f'Y{i}{i}'] for j in range(num_buses))

        # # Fill in the off-diagonal elements with negative admittances.
        # for i in range(1, num_buses + 1):
        #     for j in range(1, num_buses + 1):
        #         if i != j:
        #             Y_bus.loc[i, j] = -self.line_adm[i-1][f'Y{i}{j}']


# for i in range(1, num_buses + 1):
#             sum_of_admittances = 0
#             for j in range(num_buses):
#                 key1 = f'Y{i}{i}'
#                 key2 = f'Y{i}{j+1}'
#                 key3 = f'Y{j+1}{i}'
                
#                 if key1 in self.line_adm[j]:
#                     sum_of_admittances += self.line_adm[j][key1]
#                 elif key2 in self.line_adm[j]:
#                     sum_of_admittances += self.line_adm[j][key2]
#                 elif key3 in self.line_adm[j]:
#                     sum_of_admittances += self.line_adm[j][key3]
                
#             Y_bus.loc[i, i] = sum_of_admittances

#         # Fill in the off-diagonal elements with negative admittances.
#         for i in range(1, num_buses + 1):
#             for j in range(1, num_buses + 1):
#                 if i != j:
#                     key = f'Y{i}{j}'
#                     for k in range(num_buses):
#                         if key in self.line_adm[k]:
#                             Y_bus.loc[i, j] = -self.line_adm[k][key]

#         # Format complex numbers as strings
#         for i in range(1, num_buses + 1):
#             for j in range(1, num_buses + 1):
#                 Y_bus.loc[i, j] = f"{Y_bus.loc[i, j].real:.6f}+{Y_bus.loc[i, j].imag:.6f}j"



# bus_num = 5

# def J11_calc(bus_data, line_data, bus_num):

#     J11 = np.zeros((bus_num, bus_num))

#     # Loop through all pairs of nodes
#     for node_from in range(1, bus_num + 1):
#         for node_to in range(1, bus_num + 1):
#             if node_from == node_to:
#                 continue  # Skip self-connections

#             connection_found = False

#             for line_dict in line_data:
#                 if (line_dict['From line'] == node_from and line_dict['To line'] == node_to):
                   

#                     connection_found = True
#                     r_value = line_dict['R[pu]']
#                     x_value = line_dict['X[pu]']
#                     # Perform your action with r_value and x_value
#                     print(f"Connection between {node_from} and {node_to}")
#                     # Exit the loop since you found a connection
#                     break

#             if not connection_found:
#                 # No connection between node_from and node_to is found
#                 # Continue with other actions if needed
#                 pass

# J11_calc(bus_data, line_data, bus_num)



# def J1(PV_and_PQ_buses: list[Bus], P, YBus):
#     '''
#         Calculate the first jacobian matrix, refering to the power and voltages.
#     '''
#     count_P = len(P)
#     count_dirac = 3
#     df_J1 = pd.DataFrame(0, index=range(1, count_P), columns=range(1, count_dirac), dtype=complex)
#     J1_arr = np.zeros(count_P, count_dirac, dtype=complex)

#     for i in range(1, count_P):
#         for j in range(1, count_dirac):
#             if i != j:  
#                 # Off-diagonal elements of J1
#                 # Deklarere disse fra bus listen
#                 v_i = None
#                 v_j = None
#                 dirac_i = None
#                 dirac_j = None

#                 Y_ij_polar = cmath.polar(complex(YBus[i][j]))
#                 Y_ij = Y_ij_polar[0]
#                 theta_ij = Y_ij_polar[1]
#                 PiDiracj = - abs(v_i*v_j*Y_ij)*math.sin(theta_ij + dirac_j - dirac_i)
#                 df_J1[i][j] = PiDiracj
#             else: 
#                 # Diagonal elements of J1
#                 v_i = None
#                 v_n = None
#                 dirac_n = None
#                 PiDiracj = None
#                 N = 4 # blir vel count_v som skal inn her egentlig
#                 for n in range(1, N):
#                     if n != i:
#                         Y_in_polar = cmath.polar(complex(YBus[i][n]))
#                         Y_in = Y_in_polar[0]
#                         theta_in = Y_in_polar[1]
#                         sumE = abs(v_i*v_n*Y_in)*math.sin(theta_in + dirac_n - dirac_i)
#                         PiDiraci += sumE
#                     else:
#                         continue
#                 df_J1[i][i] = PiDiraci

#     return df_J1


# def J2(PV_and_PQ_buses: list[Bus], YBus):
#     '''
#         Calculate the second jacobian matrix, refering to the power and voltages.
#     '''
#     count_P = 4
#     count_v = 3
#     df_J2 = pd.DataFrame(0, index=range(1, count_P), columns=range(1, count_v), dtype=complex)

#     for i in range(1, count_P):
#         for j in range(1, count_v):
#             if i != j:  
#                 # Off-diagonal elements of J2
#                 # Deklarere disse fra bus listen
#                 v_i = None
#                 dirac_i = None
#                 dirac_j = None

#                 Y_ij_polar = cmath.polar(complex(YBus[i][j]))
#                 Y_ij = Y_ij_polar[0]
#                 theta_ij = Y_ij_polar[1]
#                 PiVj = abs(v_i*Y_ij)*math.cos(theta_ij + dirac_j - dirac_i)
#                 df_J2[i][j] = PiVj
#             else: 
#                 # Diagonal elements of J2
#                 v_i = None
#                 v_n = None
#                 dirac_n = None
#                 G_ii = complex(YBus[i][i]).real()
#                 PiVi = 2*abs(v_i)*G_ii

#                 N = 4 # blir vel count_v som skal inn her egentlig
#                 for n in range(1, N):
#                     Y_in_polar = cmath.polar(complex(YBus[i][n]))
#                     Y_in = Y_in_polar[0]
#                     theta_in = Y_in_polar[1]
#                     sumE = abs(v_n*Y_in)*math.cos(theta_in + dirac_n - dirac_i)
#                     PiVi += sumE

#                 df_J2[i][i] = PiVi

#     return df_J2


# def J3(PV_and_PQ_buses: list[Bus], YBus):
#     '''
#         Calculate the second jacobian matrix, refering to the power and voltages.
#     '''
#     count_Q = 4
#     count_dirac = 3
#     df_J3 = pd.DataFrame(0, index=range(1, count_Q), columns=range(1, count_dirac), dtype=complex)

#     for i in range(1, count_Q):
#         for j in range(1, count_dirac):
#             if i != j:  
#                 # Off-diagonal elements of J3
#                 v_i = None
#                 v_j = None
#                 dirac_i = None
#                 dirac_j = None
#                 Y_ij_polar = cmath.polar(complex(YBus[i][j]))
#                 Y_ij = Y_ij_polar[0]
#                 theta_ij = Y_ij_polar[1]
#                 QiDiracj = - abs(v_i*v_j*Y_ij)*math.cos(theta_ij + dirac_j - dirac_i)
#                 df_J3[i][j] = QiDiracj
#             else: 
#                 # Diagonal elements of J3
#                 v_i = None
#                 v_n = None
#                 dirac_n = None
#                 QiDiraci = None
#                 N = 4 # blir vel count_v som skal inn her egentlig
#                 for n in range(1, N):
#                     if n != i:
#                         Y_in_polar = cmath.polar(complex(YBus[i][n]))
#                         Y_in = Y_in_polar[0]
#                         theta_in = Y_in_polar[1]
#                         sumE = abs(v_i*v_n*Y_in)*math.cos(theta_in + dirac_n - dirac_i)
#                         QiDiraci += sumE
#                     else:
#                         continue
#                 df_J3[i][i] = QiDiraci

#     return df_J3

# def J4(PV_and_PQ_buses: list[Bus], YBus):
#     '''
#         Calculate the second jacobian matrix, refering to the power and voltages.
#     '''
#     count_Q = 4
#     count_v = 3
#     df_J4 = pd.DataFrame(0, index=range(1, count_Q), columns=range(1, count_v), dtype=complex)

#     for i in range(1, count_Q):
#         for j in range(1, count_v):
#             if i != j:  
#                 # Off-diagonal elements of J4
#                 v_i = None
#                 dirac_i = None
#                 dirac_j = None
#                 Y_ij_polar = cmath.polar(complex(YBus[i][j]))
#                 Y_ij = Y_ij_polar[0]
#                 theta_ij = Y_ij_polar[1]
#                 QiVj = abs(v_i*Y_ij)*math.cos(theta_ij + dirac_j - dirac_i)
#                 df_J4[i][j] = QiVj
#             else: 
#                 # Diagonal elements of J4
#                 v_i = None
#                 v_n = None
#                 dirac_n = None
#                 B_ii = complex(YBus[i][i]).imag()
#                 QiVi = 2*abs(v_i)*B_ii

#                 N = 4 # blir vel count_v som skal inn her egentlig
#                 for n in range(1, N):
#                     Y_in_polar = cmath.polar(complex(YBus[i][n]))
#                     Y_in = Y_in_polar[0]
#                     theta_in = Y_in_polar[1]
#                     sumE = abs(v_n*Y_in)*math.cos(theta_in + dirac_n - dirac_i)
#                     QiVi += sumE

#                 df_J4[i][i] = QiVi

#     return df_J4


# class Line:
#     def __init__(self, bus_p, bus_q, impedance, half_line_charging_admittance):
#         self.bus_p = bus_p
#         self.bus_q = bus_q
#         self.impedance = impedance
#         self.half_line_charging_admittance = half_line_charging_admittance


#     def build_Line_Y_bus(self) -> pd.DataFrame:
#         y_pq = complex(1 / self.impedance)
#         # Line_pq = pd.DataFrame(np.empty((2, 2), dtype=complex), index=[self.bus_p, self.bus_q], columns=[self.bus_p, self.bus_q])
#         # Line_pq.loc[self.bus_p, self.bus_p] = complex(y_pq + self.half_line_charging_admittance)
#         # Line_pq.loc[self.bus_q, self.bus_q] = complex(y_pq + self.half_line_charging_admittance)
#         # Line_pq.loc[self.bus_p, self.bus_q] = complex(-y_pq)
#         # Line_pq.loc[self.bus_q, self.bus_p] = complex(-y_pq)
#         Line_pq = {
#                 f'Y{self.bus_p}{self.bus_p}' : complex(y_pq + self.half_line_charging_admittance),
#                 f'Y{self.bus_p}{self.bus_q}' : complex(-y_pq),
#                 f'Y{self.bus_q}{self.bus_p}' : complex(-y_pq),
#                 f'Y{self.bus_q}{self.bus_q}' : complex(y_pq + self.half_line_charging_admittance),
#                 'From Bus: ' : self.bus_p,
#                 'To Bus: ' : self.bus_q
#                 }
#         return Line_pq


# class Y_Bus:
#     def __init__(self, line_adm):
#         self.line_adm = line_adm

#     def build_YBUS(self, num_buses) -> pd.DataFrame:
#         '''
#             This function will build a YBus for any N-Bus system, taking into account the number of lines going into each bus.
#         '''
#         # Initialize an empty Y-Bus matrix with zeros
#         Y_bus = pd.DataFrame(0, index=range(1, num_buses + 1), columns=range(1, num_buses + 1), dtype=complex)

#         for i in range(1, num_buses + 1):
#             for j in range(1, num_buses + 1):
#                 # Initialize the sum of admittances for the diagonal element (Yii)
#                 sum_of_admittances = 0
#                 if i == j:
#                     # Calculate the sum of admittances for the diagonal element
#                     for k in range(len(self.line_adm)):
#                         if self.line_adm[k]['From Bus: '] == i or self.line_adm[k]['To Bus: '] == i:
#                             key = f'Y{i}{i}'
#                             if key in self.line_adm[k]:
#                                 sum_of_admittances += self.line_adm[k][key]
#                     # Set the diagonal element
#                     Y_bus.loc[i, i] = complex(sum_of_admittances)
#                 else:
#                     # Calculate the off-diagonal elements (Yij) if i != j
#                     key = f'Y{i}{j}'
#                     for k in range(len(self.line_adm)):
#                         if key in self.line_adm[k]:
#                             Y_bus.loc[i, j] = self.line_adm[k][key]
#         return Y_bus

# def Jacobian
# J1J2 = np.hstack((Jac1, Jac2))
# J3J4 = np.hstack((Jac3, Jac4))
# Jac_arr = np.vstack((J1J2, J3J4))


# def setupLineAdmittanceList(line_dict):
#     x = []
#     impedance = complex(float(line_dict['R[pu]']), float(line_dict['X[pu]']))
#     half_line_charging_admittance = complex(0, float(line_dict['Half Line Charging Admittance']))
#     y_pq = complex(1 / impedance)
#     x.append(int(line_dict['From line']))
#     x.append(int(line_dict['To line']))
#     y11 = y_pq + half_line_charging_admittance
#     y11_round_real = round(y11.real, 6)
#     y11_round_imag = round(y11.imag, 3)
#     x.append(complex(y11_round_real, y11_round_imag)) #y11
#     y12 = - y_pq
#     y12_round_real = round(y12.real, 6)
#     y12_round_imag = round(y12.imag, 3)
#     x.append(complex(y12_round_real, y12_round_imag)) #y12
#     y21 = - y_pq
#     y21_round_real = round(y21.real, 6)
#     y21_round_imag = round(y21.imag, 3)
#     x.append(complex(y21_round_real, y21_round_imag)) #y21
#     y22 = y_pq + half_line_charging_admittance
#     y22_round_real = round(y22.real, 6)
#     y22_round_imag = round(y22.imag, 3)
#     x.append(complex(y22_round_real, y22_round_imag)) #y22
#     return x


# self.P_specified = (float(self.P_gen) - float(self.P_load))/SBase if (self.P_gen or self.P_load) != None else None
# self.Q_specified = (float(self.Q_gen) - float(self.Q_load))/SBase if (self.Q_gen or self.Q_load) != None else None

# def update_voltage(self, new_voltage_magnitude, new_voltage_angle):
#     self.voltage_magnitude = new_voltage_magnitude
#     self.voltage_angle = new_voltage_angle


#creating a list of all the P_i equations 
# def P_power_flow_equations(P_list, Y_bus_polar, buses):
#     P_eq_vector = []

#     for i in range(len(P_list)):
#         n=P_list[i][0] #For example, we want n=2 for P2
#         P_i = 0
#         for k in range(0,len(buses)):
#             P_i += buses[n-1].voltage_magnitude * buses[k].voltage_magnitude * Y_bus_polar[n-1][k][0] * sym.cos((((Y_bus_polar[n-1][k][1] - buses[n-1].voltage_angle + buses[k].voltage_angle))))
#         P_eq_vector.append(P_i)
#     return P_eq_vector


# for i in range(P_start, P_count + P_start):
#     v_i = BusList[i].voltage_magnitude
#     dirac_i = BusList[i].voltage_angle
#     G_ii = complex(YBus[i][i]).real
#     Pi = 2*abs(v_i)**2*G_ii
#     for n in range(len(BusList)):
#         v_n = BusList[n].voltage_magnitude
#         dirac_n = BusList[n].voltage_angle
#         if n != i:
#             Y_in_polar = cmath.polar(YBus[i][n])
#             Y_in = Y_in_polar[0]
#             theta_in = Y_in_polar[1]
#             Pi += abs(v_i*v_n*Y_in)*math.cos(theta_in + dirac_n - dirac_i)
#         else:
#             continue
#     Pi_calc[i - P_start] = Pi