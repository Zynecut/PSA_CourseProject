from functions import *
import pandas as pd

line_data = ReadCsvFile('./files/network_configuration_line_data.csv')
bus_data = ReadCsvFile('./files/network_configuration_bus_data.csv')
Sbase = 100 # MVA
Ubase = 230 # kV
max_iteration = 30
tolerance = 1e-6

def NewtonRaphson():
    """
        Values under must be defined in the funtion () before implementing in main()
        line_data, bus_data, Sbase, Ubase, max_iterations, tolerance
    """
    num_buses = len(bus_data)
    YBus = BuildYbusMatrix(line_data, num_buses)
    BusList = buildBusList(bus_data, Sbase)

    bus_overview = setupBusType(bus_data)
    P_spec, Q_spec = findKnowns(bus_data, Sbase)
    v_guess, dirac_guess = findUnknowns(bus_overview, bus_data)

    deltaP = calcP(BusList, P_spec, YBus, Sbase)
    deltaQ = calcQ(BusList, Q_spec, YBus, Sbase)
    knowns = np.concatenate((deltaP, deltaQ), axis= 0)

    jacobian_matrix = buildJacobian(BusList, P_spec, Q_spec, v_guess, dirac_guess, YBus)
    unknowns = calcDeltaUnknowns(jacobian_matrix, knowns)
    # print(unknowns)

    # Visualize
    df_jac = pd.DataFrame(jacobian_matrix)
    df_ybus = pd.DataFrame(YBus)
    print(df_ybus, "\n\n", df_jac)

    updateVoltageAndAngleList(unknowns, dirac_guess, v_guess)
    updateBusList(BusList, dirac_guess, v_guess)


if __name__ == '__main__':
    NewtonRaphson()