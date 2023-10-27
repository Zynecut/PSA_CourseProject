from functions import *
import pandas as pd

# standard
line_data = ReadCsvFile('./files/network_configuration_line_data.csv')
bus_data = ReadCsvFile('./files/network_configuration_bus_data.csv')
Sbase = 100 # MVA
Ubase = 230 # kV
max_iterations = 10000
tolerance = 0.001


def iterateDLF(BusList, YBus, Sbase, P_spec, Q_spec, v_guess, dirac_guess, max_iterations, tolerance):
    """
        Iterate the solution until convergance
    """
    deltaP = calcP(BusList, P_spec, YBus, Sbase)
    deltaQ = calcQ(BusList, Q_spec, YBus, Sbase)
    knowns = np.concatenate((deltaP, deltaQ), axis= 0)
    max_valueP = deltaP[0]
    max_valueQ = deltaQ[0]
    k = 0
    convergence = False
    while not convergence:
        # Decoupled Load Flow

        for element in deltaP:
            if abs(element) > max_valueP:
                max_valueP = element

        for element in deltaQ:
            if abs(element) > max_valueQ:
                max_valueQ = element

        if abs(max_valueP) < tolerance or abs(max_valueQ) < tolerance:
            convergence = True
        elif max_iterations < k:
            break
        else:
            deltaP = calcP(BusList, P_spec, YBus, Sbase)
            deltaQ = calcQ(BusList, Q_spec, YBus, Sbase)
            knowns = np.concatenate((deltaP, deltaQ), axis= 0)
            jacobian = calcDecoupledJacobian(BusList, P_spec, Q_spec, v_guess, dirac_guess, YBus)
            unknowns= calcDecoupledDiracVoltage(jacobian, knowns)
            updateVoltageAndAngleList(unknowns, dirac_guess, v_guess)
            updateBusList(BusList, dirac_guess, v_guess)
            k += 1

    return deltaP, deltaQ, knowns, jacobian, unknowns, k


def DLF():
    num_buses = len(bus_data)
    YBus = BuildYbusMatrix(line_data, num_buses)
    BusList = buildBusList(bus_data, Sbase)
    bus_overview = setupBusType(bus_data)
    P_spec, Q_spec = findKnowns(bus_data, Sbase)
    v_guess, dirac_guess = findUnknowns(bus_overview, bus_data)

    deltaP, deltaQ, knowns, jacobian, unknowns, k = iterateDLF(BusList, YBus, Sbase, P_spec, Q_spec, v_guess, dirac_guess, max_iterations, tolerance) 
    print(pd.DataFrame(bus_overview))
    a = 1


if __name__ == '__main__':
    DLF()