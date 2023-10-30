from classes import *
from functions import *
import pandas as pd
import numpy as np
from NRLF import *
"""
    Real power loss PL
    PL is evidently the total I**2R loss in the transmission lines and transformers of the network. 
    The induvidual currents in the various transmission lines of the network cannot be calculated until after the
    voltage magnitude and angle are known at every bus of the system. Therefor PL is initially unknown and it is 
    not possible to prespecify alle the quantities in the summations of Equations. 
"""


def main():
    line_data = ReadCsvFile('./files/network_configuration_line_data.csv')
    bus_data = ReadCsvFile('./files/network_configuration_bus_data.csv')

    Sbase = 100 # MVA
    Ubase = 230 # kV
    num_buses = len(bus_data)
    breakpoint()
    YBus = BuildYbusMatrix(line_data, num_buses)
    BusList = buildBusList(bus_data, Sbase)

    bus_overview = setupBusType(bus_data)
    P_spec, Q_spec = findKnowns(bus_data, Sbase)
    v_guess, diraq_guess = findUnknowns(bus_overview, bus_data)
    jacobian_matrix = buildJacobian(BusList, P_spec, Q_spec, v_guess, diraq_guess, YBus)

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

    NewtonRaphson()







if __name__ == '__main__':
    main()