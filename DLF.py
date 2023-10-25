from functions import *

# standard
line_data = ReadCsvFile('./files/network_configuration_line_data.csv')
bus_data = ReadCsvFile('./files/network_configuration_bus_data.csv')

Sbase = 100 # MVA
Ubase = 230 # kV




def DLF():
    num_buses = len(bus_data)
    YBus = BuildYbusMatrix(line_data, num_buses)
    BusList = buildBusList(bus_data, Sbase)
    bus_overview = setupBusType(bus_data)
    P_spec, Q_spec = findKnowns(bus_data, Sbase)
    v_guess, diraq_guess = findUnknowns(bus_overview, bus_data)

    deltaP = calcP(BusList, P_spec, YBus, Sbase)
    deltaQ = calcQ(BusList, Q_spec, YBus, Sbase)
    knowns = np.concatenate((deltaP, deltaQ), axis= 0)

    # Decoupled Load Flow
    dlf_jacobian = calcDecoupledJacobian(BusList, P_spec, Q_spec, v_guess, diraq_guess, YBus)
    print(dlf_jacobian)
    dlf_unknowns= calcDecoupledDiraqVoltage(dlf_jacobian, knowns)
    print(dlf_unknowns)
    b = 1


if __name__ == '__main__':
    DLF()