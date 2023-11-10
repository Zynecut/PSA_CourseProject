from functions import *
import pandas as pd

# standard
line_data = ReadCsvFile('./files/given_network/network_configuration_line_data.csv')
bus_data = ReadCsvFile('./files/given_network/network_configuration_bus_data_slack1.csv')
Sbase = 100 # MVA
Ubase = 230 # kV
max_iterations = 100
tolerance = 0.001
Q_lim = -0.6
V_lim = -0.1 # take 1 - V_lim for max and 1 - abs(V_lim) for min

def iterateDLF(BusList, YBus, P_spec, Q_spec, v_guess, dirac_guess, max_iterations, tolerance):
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
        # Decoupled Load Flow
        if checkConvergence(tolerance, delta_u):
            convergence = True
        elif max_iterations < k:
            break
        else:
            deltaP = calcP(BusList, P_spec, YBus)
            deltaQ = calcQ(BusList, Q_spec, YBus)
            delta_u = np.concatenate((deltaP, deltaQ), axis= 0)
            jacobian = calcDecoupledJacobian(BusList, P_spec, Q_spec, v_guess, dirac_guess, YBus)
            delta_x= calcDecoupledDiracVoltage(jacobian, delta_u)
            updateVoltageAndAngleList(delta_x, dirac_guess, v_guess)
            updateBusList(BusList, dirac_guess, v_guess)
            k += 1
    return delta_u, delta_x, k


def DLF(bus_data, line_data, Sbase, max_iterations, tolerance, Q_lim, V_lim):
    """
        delta_u is known values - ΔP, ΔQ
        delta_x is unknown values - Δδ, Δ|v|
    """
    num_buses = len(bus_data)
    YBus = BuildYbusMatrix(line_data, num_buses)
    bus_overview = setupBusType(bus_data)
    BusList = buildBusList(bus_data, Sbase, bus_overview)
    P_spec, Q_spec = findKnowns(bus_data, Sbase)
    v_guess, dirac_guess = findUnknowns(bus_overview, bus_data)
    delta_u, delta_x, k = iterateDLF(BusList= BusList, 
                                     YBus= YBus, 
                                     P_spec= P_spec, 
                                     Q_spec= Q_spec, 
                                     v_guess= v_guess, 
                                     dirac_guess= dirac_guess, 
                                     max_iterations= max_iterations, 
                                     tolerance= tolerance
                                     ) 
    print(f"The method converged after {k} iterations!\n")
    updateSlackAndPV(BusList=BusList, YBus=YBus, Sbase=Sbase) # Sjekk Qi på PV bus

    df_NRLF = makeDataFrame(BusList)
    print(df_NRLF)


if __name__ == '__main__':
    DLF(bus_data=bus_data, 
        line_data=line_data, 
        Sbase=Sbase, 
        max_iterations=max_iterations, 
        tolerance=tolerance, 
        Q_lim=Q_lim,
        V_lim=V_lim
        )