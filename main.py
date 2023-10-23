from classes import *
from functions import *
import pandas as pd
import spicy as sp
import numpy as np

def main():
    line_data = ReadCsvFile('./files/network_configuration_line_data.csv')
    bus_data = ReadCsvFile('./files/network_configuration_bus_data.csv')

    Sbase = 100 # MVA
    Ubase = 230 # kV
    num_buses = len(bus_data)

    YBus = BuildYbusMatrix(line_data, num_buses)
    BusList = buildBusList(bus_data, Sbase)

    bus_overview = setupBusType(bus_data)
    P_spec, Q_spec = findKnowns(bus_data, Sbase)
    v_guess, diraq_guess = findUnknowns(bus_overview, bus_data)
    
    jacobian_matrix = Jacobian(BusList, P_spec, Q_spec, v_guess, diraq_guess, YBus)

    df_jac = pd.DataFrame(jacobian_matrix)
    df_ybus = pd.DataFrame(YBus)
    print(df_ybus, "\n\n", df_jac)

    deltaP = calcP(BusList, P_spec, YBus, Sbase)
    deltaQ = calcQ(BusList, Q_spec, YBus, Sbase)
    knowns = np.concatenate((deltaP, deltaQ), axis= 0)

    # df_inv_jac = pd.DataFrame(np.linalg.pinv(df_jac))
    # print(df_inv_jac)
    unknowns = calcDeltaUnknowns(jacobian_matrix, knowns)
    print(unknowns)

    updateVoltageAndAngleList(unknowns, diraq_guess, v_guess)
    updateBusList(BusList, diraq_guess, v_guess)
    b = 1

if __name__ == '__main__':
    main()