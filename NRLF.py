from functions import *
import pandas as pd

# line_data = ReadCsvFile('./files/network_configuration_line_data_Fellestest.csv')
# bus_data = ReadCsvFile('./files/network_configuration_bus_data_Fellestest.csv')
line_data = ReadCsvFile('./files/network_configuration_line_data.csv')
bus_data = ReadCsvFile('./files/network_configuration_bus_data.csv')
Sbase = 100 # MVA
Ubase = 132 # kV
max_iterations = 30
tolerance = 1e-3
Q_lim = -0.75
V_lim = -0.1 # take 1 - V_lim for max and 1 - abs(V_lim) for min


def iterateNRLF(BusList, YBus, P_spec, Q_spec, v_guess, dirac_guess, max_iterations, tolerance):
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

def NewtonRaphson():
    """
        Values under must be defined in the funtion () before implementing in main()
        line_data, bus_data, Sbase, Ubase, max_iterations, tolerance
        delta_u is known values - ΔP, ΔQ
        delta_x is unknown values - Δδ, Δ|v|
    """
    num_buses = len(bus_data)
    YBus = BuildYbusMatrix(line_data, num_buses)
    bus_overview = setupBusType(bus_data)
    BusList = buildBusList(bus_data, Sbase, bus_overview)
    P_spec, Q_spec = findKnowns(bus_data, Sbase)
    v_guess, dirac_guess = findUnknowns(bus_overview, bus_data)
    delta_u, delta_x, k = iterateNRLF(BusList= BusList, 
                    YBus= YBus, 
                    P_spec= P_spec, 
                    Q_spec= Q_spec, 
                    v_guess= v_guess, 
                    dirac_guess= dirac_guess, 
                    max_iterations= max_iterations, 
                    tolerance= tolerance
                    )
    print(k)
    updateSlackAndPV(BusList=BusList, YBus=YBus, Sbase=Sbase) # Sjekk Qi på PV bus



    # Calculate line losses 
    # P = I^2 * R       R = r*Zbase
    # Q = I^2 * X       X = x*Zbase
    # Calc line flows 
    # P1-2 and P2-1
    # Q1-2 and Q2-1
    # Can also use this to check line losses
    print("\n")
    df_NRLF = makeDataFrame(BusList)
    print("\n")
    print(df_NRLF)
    print_dataframe_as_latex(df_NRLF)

if __name__ == '__main__':
    NewtonRaphson()