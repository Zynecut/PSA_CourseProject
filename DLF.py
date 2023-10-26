from functions import *

# standard
line_data = ReadCsvFile('./files/network_configuration_line_data.csv')
bus_data = ReadCsvFile('./files/network_configuration_bus_data.csv')
Sbase = 100 # MVA
Ubase = 230 # kV
max_iterations = 30
tolerance = 0.01


def iterateDLF(BusList, YBus, Sbase, P_spec, Q_spec, v_guess, diraq_guess, max_iterations, tolerance):
    """
        Iterate the solution until convergance
    """
    
    deltaP = calcP(BusList, P_spec, YBus, Sbase)
    deltaQ = calcQ(BusList, Q_spec, YBus, Sbase)
    knowns = np.concatenate((deltaP, deltaQ), axis= 0)
    
    i = 0
    k = 0
    convergence = False
    while not convergence:
        # Decoupled Load Flow
        if abs(deltaP[i]) < tolerance:
            convergence = True
        elif max_iterations < k:
            break
        else:
            deltaP = calcP(BusList, P_spec, YBus, Sbase)
            deltaQ = calcQ(BusList, Q_spec, YBus, Sbase)
            knowns = np.concatenate((deltaP, deltaQ), axis= 0)
            jacobian = calcDecoupledJacobian(BusList, P_spec, Q_spec, v_guess, diraq_guess, YBus)
            unknowns= calcDecoupledDiraqVoltage(jacobian, knowns)
            updateVoltageAndAngleList(unknowns, diraq_guess, v_guess)
            updateBusList(BusList, diraq_guess, v_guess)
            k += 1

    return deltaP, deltaQ, knowns, jacobian, unknowns


def DLF():
    num_buses = len(bus_data)
    YBus = BuildYbusMatrix(line_data, num_buses)
    BusList = buildBusList(bus_data, Sbase)
    bus_overview = setupBusType(bus_data)
    P_spec, Q_spec = findKnowns(bus_data, Sbase)
    v_guess, diraq_guess = findUnknowns(bus_overview, bus_data)

    deltaP, deltaQ, knowns, jacobian, unknowns = iterateDLF(BusList, YBus, Sbase, P_spec, Q_spec, v_guess, diraq_guess, max_iterations, tolerance) 
    print(deltaP, deltaQ, knowns, jacobian, unknowns)



if __name__ == '__main__':
    DLF()