from functions import *
import pandas as pd
import time


# Given data
line_data = ReadCsvFile('./files/given_network/network_configuration_line_data.csv')
bus_data = ReadCsvFile('./files/given_network/network_configuration_bus_data_slack1.csv')
# bus_data = ReadCsvFile('./files/given_network/network_configuration_bus_data_slack2.csv')

# Test data
# line_data = ReadCsvFile('./files/test_network/test_line_data.csv')
# bus_data = ReadCsvFile('./files/test_network/test_bus_data.csv')

# line_data = ReadCsvFile('./files/test_network/network_configuration_line_data_Fellestest.csv')
# bus_data = ReadCsvFile('./files/test_network/network_configuration_bus_data_Fellestest.csv')

Sbase = 100 # MVA
Ubase = 230 # kV
Zbase = (Ubase**2)/Sbase
max_iterations = 300
tolerance = 1e-3
Q_lim = -0.6
V_lim = -0.1 # take 1 - V_lim for max and 1 - abs(V_lim) for min

def iterateNRLF(BusList, YBus, P_spec, Q_spec, v_guess, dirac_guess, max_iterations, tolerance, Q_lim, V_lim):
    """
        Iterate the solution until convergance
        delta_u is known values - ΔP, ΔQ
        delta_x is unknown values - Δδ, Δ|v|
    """
    deltaP = calcP(BusList, P_spec, YBus)
    deltaQ = calcQ(BusList, Q_spec, YBus)
    delta_u = np.concatenate((deltaP, deltaQ), axis= 0)
    k = 0
    convergence = False
    while not convergence:
        if checkConvergence(tolerance, delta_u):
            convergence = True
        elif max_iterations < k:
            break
        else:
            deltaP = calcP(BusList, P_spec, YBus)
            deltaQ = calcQ(BusList, Q_spec, YBus)
            delta_u = np.concatenate((deltaP, deltaQ), axis= 0)
            jacobian = buildJacobian(BusList, P_spec, Q_spec, v_guess, dirac_guess, YBus)
            delta_x= calcDeltaUnknowns(jacobian, delta_u)
            updateVoltageAndAngleList(delta_x, dirac_guess, v_guess)
            updateBusList(BusList, dirac_guess, v_guess)
            # Q_spec, v_guess = checkTypeSwitch(BusList, YBus, Q_spec, v_guess, Q_lim, V_lim)
            k += 1
    return delta_u, delta_x, k

def NewtonRaphson(bus_data, line_data, Sbase, max_iterations, tolerance, Q_lim, V_lim):
    """
        Values under must be defined in the funtion () before implementing in main()
        line_data, bus_data, Sbase, Ubase, max_iterations, tolerance
        delta_u is known values - ΔP, ΔQ
        delta_x is unknown values - Δδ, Δ|v|
    """
    start_time = time.time()
    num_buses = len(bus_data)
    YBus = BuildYbusMatrix(line_data, num_buses)
    bus_overview = setupBusType(bus_data)
    BusList = buildBusList(bus_data, Sbase, bus_overview)
    LineList = buildLineList(line_data)
    P_spec, Q_spec = findKnowns(bus_data, Sbase)
    v_guess, dirac_guess = findUnknowns(bus_overview, bus_data)
    delta_u, delta_x, k = iterateNRLF(BusList= BusList, 
                    YBus= YBus, 
                    P_spec= P_spec, 
                    Q_spec= Q_spec, 
                    v_guess= v_guess, 
                    dirac_guess= dirac_guess, 
                    max_iterations= max_iterations, 
                    tolerance= tolerance,
                    Q_lim=Q_lim,
                    V_lim=V_lim
                    )
    print(f"The method converged after {k} iterations!")
    updateSlackAndPV(BusList=BusList, YBus=YBus, Sbase=Sbase) # Sjekk Qi på PV bus

    # Calculate line losses 
    # P = I^2 * R       R = r*Zbase
    # Q = I^2 * X       X = x*Zbase
    # Calc line flows 
    # P1-2 and P2-1
    # Q1-2 and Q2-1
    # Can also use this to check line losses
    df_NRLF = makeDataFrame(BusList)
    print(df_NRLF)
    # print_dataframe_as_latex(df_NRLF)
    test = df_NRLF["P [pu]"].sum()
    print(test)
    print("--- %s seconds ---" % (time.time() - start_time))

    """
        If voltage magnitude violation, change (P2, change gen PG2 or load demand PL2, mostly PG2)
    """

if __name__ == '__main__':
    NewtonRaphson(bus_data=bus_data, 
              line_data=line_data, 
              Sbase=Sbase, 
              max_iterations=max_iterations, 
              tolerance=tolerance, 
              Q_lim=Q_lim,
              V_lim=V_lim
              )