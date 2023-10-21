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