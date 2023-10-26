from functions import *
import pandas as pd

line_data = ReadCsvFile('./files/network_configuration_line_data.csv')
bus_data = ReadCsvFile('./files/network_configuration_bus_data.csv')
Sbase = 100 # MVA
Ubase = 230 # kV

def DCPF():
    num_buses = len(bus_data)

    YBus = BuildYbusMatrix(line_data, num_buses)
    BusList = buildBusList(bus_data, Sbase)

    bus_overview = setupBusType(bus_data)
    P_spec, Q_spec = findKnowns(bus_data, Sbase)
    v_guess, diraq_guess = findUnknowns(bus_overview, bus_data)
    
    jacobian_matrix = buildJacobian(BusList, P_spec, Q_spec, v_guess, diraq_guess, YBus)

    df_jac = pd.DataFrame(jacobian_matrix)
    df_ybus = pd.DataFrame(YBus)
    print(df_ybus, "\n\n", df_jac)


if __name__ == '__main__':
    DCPF()