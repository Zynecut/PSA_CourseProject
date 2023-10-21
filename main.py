from classes import *
from functions import *
import pandas as pd

def main():
    line_data = ReadCsvFile('./files/network_configuration_line_data.csv')
    bus_data = ReadCsvFile('./files/network_configuration_bus_data.csv')

    Sbase = 100 # MVA
    Ubase = 230 # kV
    num_buses = len(bus_data)
    line_admittances = []
    BusList = []

    for element in line_data:
        line_admittances.append(setupLineAdmittanceList(element))

    YBus = BuildYbusMatrix(line_admittances, num_buses)

    for element in bus_data:
        BusList.append(setupBusList(element, Sbase))

    bus_overview = setupBusType(bus_data)
    P, Q = findKnowns(bus_data, Sbase)
    v, diraq = findUnknowns(bus_overview, bus_data)
    
    jacobian_matrix = Jacobian(BusList, P, Q, v, diraq, YBus)

    df_test = pd.DataFrame(jacobian_matrix)
    df_ybus = pd.DataFrame(YBus)
    print(df_test, df_ybus)


if __name__ == '__main__':
    main()