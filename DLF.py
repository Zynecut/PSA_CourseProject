from functions import *
import pandas as pd

# standard
line_data = ReadCsvFile('./files/network_configuration_line_data.csv')
bus_data = ReadCsvFile('./files/network_configuration_bus_data.csv')
# line_data = ReadCsvFile('./files/test_line_data.csv')
# bus_data = ReadCsvFile('./files/test_bus_data.csv')
Sbase = 100 # MVA
Ubase = 230 # kV
max_iterations = 100
tolerance = 0.001

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


def DLF():
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
    print(k, "\n\n" ,delta_u, "\n\n", delta_x, "\n\n")
    updateSlackAndPV(BusList=BusList, YBus=YBus, Sbase=Sbase) # Sjekk Qi på PV bus


if __name__ == '__main__':
    DLF()