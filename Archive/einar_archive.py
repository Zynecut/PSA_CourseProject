# from classes import *

# Line_13 = Line(bus_p="1", bus_q="3", impedance=complex(0.08, 0.24), half_line_charging_admittance=complex(0.0, 0.025))
# Line_12 = Line(bus_p="1", bus_q="2", impedance=complex(0.02, 0.06), half_line_charging_admittance=complex(0.0, 0.03))

# display(Line_13.build_Line_pq())
# display(Line_12.build_Line_pq())

# bus1 = Bus(bus_id=1, voltage_magnitude=20, voltage_angle=0)
# bus2 = Bus(bus_id=2, voltage_magnitude=30, voltage_angle=5)
# print(bus1)
# print(bus2)


# Hente fra excel
# Lager liste over linjer
# Lager liste over spenninger med vinkler


# list_power_syst_data = [{'V1': 1, 'delta1': 5, 'P1': 32, 'Q1': 1},
#                        {'V2': 1.05, 'delta2': 2, 'P2': 28, 'Q2': 1},
#                        {'V3': 1.06, 'delta3': 3, 'P3': 15, 'Q3': 2},
#                        {'V4': 1.07, 'delta4': 4, 'P4': 17, 'Q4': 3},
#                        {'V5': 1.08, 'delta5': 5, 'P5': 19, 'Q5': 4}]

# list_line_data = [
#     {'Z12': 0.02 + 0.06j},
#     {'Z13': 0.08 + 0.24j},
#     {'Z23': 0.06 + 0.18j},
#     {'Z24': 0.06 + 0.18j},
#     {'Z25': 0.04 + 0.12j},
#     {'Z34': 0.01 + 0.03j},
#     {'Z45': 0.08 + 0.24j}
#]

# from main.pynb import *

# display(bus_data)
# display(line_data)


# display(line_admittences)
#display(Line_13.build_Line_pq())

#bus1 = Bus(bus_id=1, voltage_magnitude=20, voltage_angle=0)
#print(bus1)


# Manuelt lagt inn Y-bus
# test_YBUS = pd.DataFrame(0, index=range(1, 6), columns=range(1,6))
# test_YBUS[1] = [complex(25/4,-3739/200), complex(-5, 15), complex(-5/4, 15/4), 0, 0]
# test_YBUS[2] = [complex(-5, 15), complex(65/6, -6483/200), complex(-5/3, 5), complex(-5/3, 5), complex(-5/2, 15/2)]
# test_YBUS[3] = [complex(-5/4, 15/4), complex(-5/3, 5), complex(155/12, -7739/200), complex(-10, 30), 0]
# test_YBUS[4] = [0, complex(-5/3, 5), complex(-10, 30), complex(155/12, -7739/200), complex(-5/4, 15/4)]
# test_YBUS[5] = [0, complex(-5/2, 15/2), 0, complex(-5/4, 15/4), complex(15/4, -1121/100)]

# value = test_YBUS.at[1, 2].imag


# display(value)

#  # Iterate through each row and column of the J11 array
#     for i in range(row_count):
#         for j in range(col_count):
#             if i == j:
#                 continue
#                     # Set the element value

#             vi = abs(bus_data[i]['Assumed bus voltage (pu)'])
#             vj = abs(bus_data[j]['Assumed bus voltage (pu)'])
#             gij = YBus.at[i, j].real
#             sin_ij = math.sin(bus_data[i]['Angle'] - bus_data[j]['Angle'])
#             bij = YBus.at[i, j].imag
#             cos_ij = math.cos(bus_data[i]['Angle'] - bus_data[j]['Angle'])

#             df_J11.at[i + 1, j + 1] = vi * vj *(gij *sin_ij - bij * sin_ij)

#     return df_J11


            
# test = J11_calc(bus_data=bus_data,
#          YBus=YBus,
#          list_dict_power=list_dict_power)

# print(test)





# for i in range(1, row_count+1):
#     for j in range(1, col_count+1):
#         if i == j:
#             continue



### VEUM

# def J2(PV_and_PQ_buses: list[Bus], YBus) -> pd.DataFrame:
#     '''
#         Calculate the second jacobian matrix, refering to the power and voltages.
#     '''
#     count_P = 4
#     count_v = 3
#     df_J2 = pd.DataFrame(0, index=range(1, count_P), columns=range(1, count_v), dtype=complex)
#     # Off-diagonal variables
#     v_i = None
#     diraq_i = None
#     diraq_j = None

#     # Diagonal variables
#     v_n = None
#     diraq_n = None

#     for i in range(1, count_P):
#         for j in range(1, count_v):
#             if i != j:
# #Off-diagonal elements of J2
#                 Y_ij_polar = cmath.polar(complex(YBus[i][j]))
#                 Y_ij = Y_ij_polar[0]
#                 theta_ij = Y_ij_polar[1]
#                 PiVj = abs(v_iY_ij)math.cos(theta_ij + diraq_j - diraq_i)
#                 df_J2[i][j] = PiVj
#             else: 
#                 # Diagonal elements of J2
#                 G_ii = complex(YBus[i][i]).real()
#                 PiVi = 2abs(v_i)G_ii

#                 N = 4 # blir vel count_v som skal inn her egentlig
#                 for n in range(1, N):
#                     Y_in_polar = cmath.polar(complex(YBus[i][n]))
#                     Y_in = Y_in_polar[0]
#                     theta_in = Y_in_polar[1]
#                     sumE = abs(v_nY_in)math.cos(theta_in + diraq_n - diraq_i)
#                     PiVi += sumE

#                 df_J2[i][i] = PiVi

#     return df_J2






















    # dPi_dDj = Vi_mag * Vj_mag * (y_line_ij.real * math.sin(Vi_ang-Vj_ang) - y_line_ij.imag * math.cos(Vi_ang-Vj_ang))


    # if (bus_i == bus_j):     # Diagonal
    #     # Lager variabler inni funksjonen
  
    # else:                   # Off-diagonal
    #     Vi_mag = bus_i.voltage_magnitude
    #     Vi_ang = bus_i.voltage_angle
    #     Vj_mag = bus_j.voltage_magnitude
    #     Vj_ang = bus_j.voltage_angle

    #     y_line_ij = 1/line_ij.impedance

    #     dPi_dDj = Vi_mag * Vj_mag * (y_line_ij.real * math.sin(Vi_ang-Vj_ang) - y_line_ij.imag * math.cos(Vi_ang-Vj_ang))
    #     return dPi_dDj



    # # Loop through all pairs of nodes
    # for node_from in range(1, true_count + 1):
    #     for node_to in range(1, true_count + 1):
    #         if node_from == node_to:
    #             continue  # Skip self-connections

    #         connection_found = False

    #         for line_dict in line_data:
    #             if (line_dict['From line'] == node_from and line_dict['To line'] == node_to):
                   

    #                 connection_found = True
    #                 r_value = line_dict['R[pu]']
    #                 x_value = line_dict['X[pu]']
    #                 # Perform your action with r_value and x_value
    #                 print(f"Connection between {node_from} and {node_to}")
    #                 # Exit the loop since you found a connection
    #                 break

    #         if not connection_found:
    #             # No connection between node_from and node_to is found
    #             # Continue with other actions if needed
    #             pass

# J11_calc(bus_data, line_data, list_dict_power)


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



#     dPi_dDj = Vi_mag * Vj_mag * (y_line_ij.real * math.sin(Vi_ang-Vj_ang) - y_line_ij.imag * math.cos(Vi_ang-Vj_ang))


#     from_line = 1
#     to_line = 3

#     desired_R_value = None      # Zero value kun for å initialisere

#     for line_dict in line_data:
#         if line_dict['From line'] == from_line and line_dict['To line'] == to_line:
#             desired_R_value = line_dict['R[pu]']
#             break

#     if desired_R_value is not None:
#         print(f"The 'R[pu]' value for Line 1 to 3 is: {desired_R_value}")
#     else:
#         print("Line not found in line_data.")


#     return J11

# print(J11_calc(bus_data, line_data, P_known))

import math




# def J11_calc(buses: List[classes.Bus], lines: List[classes.Line]):





#    for dictionary in line_data:
#         for key, value in dictionary.items():
#             if key.startswith('Z12'):
#                 print(value)





#         Vi_mag = bus_i.voltage_magnitude
#         Vi_ang = bus_i.voltage_angle
#         Vj_mag = bus_j.voltage_magnitude
#         Vj_ang = bus_j.voltage_angle



#     if (bus_i == bus_j):     # Diagonal
#         # Lager variabler inni funksjonen
  
#     else:                   # Off-diagonal
#         Vi_mag = bus_i.voltage_magnitude
#         Vi_ang = bus_i.voltage_angle
#         Vj_mag = bus_j.voltage_magnitude
#         Vj_ang = bus_j.voltage_angle

#         y_line_ij = 1/line_ij.impedance

#         dPi_dDj = Vi_mag * Vj_mag * (y_line_ij.real * math.sin(Vi_ang-Vj_ang) - y_line_ij.imag * math.cos(Vi_ang-Vj_ang))
#         return dPi_dDj

def J11_off_diag_calc(bus_i, bus_j, line_ij):    # MIXED FORM: Voltage in polar, impedance in cartesian
    
#     if (bus_i == bus_j):     # Diagonal
#         # Lager variabler inni funksjonen
#         Vi_mag = bus_i.voltage_magnitude
#         Vi_ang = bus_i.voltage_angle
#         Vj_mag = bus_j.voltage_magnitude
#         Vj_ang = bus_j.voltage_angle

#         y_line_ij = 1/line_ij.impedance

#         dPi_dDj = Vi_mag * Vj_mag * (y_line_ij.real * math.sin(Vi_ang-Vj_ang) - y_line_ij.imag * math.cos(Vi_ang-Vj_ang))
#         return dPi_dDj
#     else:                   # Off-diagonal


# # Bruker grader! Dobbelsjekk at det er rett.
# # Plasser i tabell/ liste/ dataframe?
# J11_off_diag_calc(bus1, bus2, Line_12)


# ######################################################################################


# # Sett inn liste med spenning og vinkel på alle busser
# # Sett inn liste med impedanser på alle linjer

# def J11_diag_calc(buses: List[classes.Bus], lines: List[classes.Line]):    # MIXED FORM: Voltage in polar, impedance in cartesian







#     num_busses = size.buses

#     List[classes.Bus], buses

#     # Bruker grader! Sjekk at det er rett.
#         for i in range(1, num_busses + 1):
#             if i == int(bus_i.bus_id):
#                 continue
#             else:
#                 dPi_dDi = 2 #Må få laget en liste over spenninger og vinkler i alle busser før formel kan legges inn her.


#         return dPi_dDi

#     # Plasser i tabell/ liste/ dataframe?
#     J11_diag_calc(bus1, bus2, Line_12)