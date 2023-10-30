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


def solutionOuput(BusList):
    k = 1


def main():
    # line_data = ReadCsvFile('./files/network_configuration_line_data.csv')
    # bus_data = ReadCsvFile('./files/network_configuration_bus_data.csv')
    line_data = ReadCsvFile('./files/test_line_data.csv')
    bus_data = ReadCsvFile('./files/test_bus_data.csv')

    Sbase = 100 # MVA
    Ubase = 230 # kV
    Zbase = (Ubase**2)/Sbase
    num_buses = len(bus_data)
    breakpoint()
    YBus = BuildYbusMatrix(line_data, num_buses)
    bus_overview = setupBusType(bus_data)
    BusList = buildBusList(bus_data, Sbase, bus_overview)

    
    P_spec, Q_spec = findKnowns(bus_data, Sbase)
    v_guess, dirac_guess = findUnknowns(bus_overview, bus_data)
    # Initialization Completed

    # Values below are the ones that continuously update
    jacobian_matrix = buildJacobian(BusList, P_spec, Q_spec, v_guess, dirac_guess, YBus)
    deltaP = calcP(BusList, P_spec, YBus)
    deltaQ = calcQ(BusList, Q_spec, YBus)
    delta_u = np.concatenate((deltaP, deltaQ), axis= 0)
    delta_x = calcDeltaUnknowns(jacobian_matrix, delta_u)
    updateVoltageAndAngleList(delta_x, dirac_guess, v_guess)
    updateBusList(BusList, dirac_guess, v_guess)

    # Burde nok bytte navn på knowns til delta_u, og unknowns til delta_x
    # Dette som blir brukt i andre eksempler og lærebok


    df_jac = pd.DataFrame(jacobian_matrix)
    df_ybus = pd.DataFrame(YBus)
    print(df_ybus, "\n\n", df_jac)
    a = 1
    # NewtonRaphson()
    """
        When solution is complete we can use Equations (7.49) and (7.50) to calculate real and reactive power, P1 and Q1,
        at the slack bus, and reactive power Q2 at the voltage controlled bus 2. 
        Line flows can also be computed from the differences in the bus voltages and known parameters of the lines.
        
        We ougth to represent the solution of the system as shown in Figure 7.7 in the textbook or as shown in main.ipynb

    """






if __name__ == '__main__':
    main()