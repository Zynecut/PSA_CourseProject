from functions import *

line_data = ReadCsvFile('./files/network_configuration_line_data.csv')
bus_data = ReadCsvFile('./files/network_configuration_bus_data.csv')
Sbase = 100 # MVA
Ubase = 230 # kV
num_buses = len(bus_data)

def FDLF():
    """
        Stratety:
        1. Calculate the initial mismatches ΔP/|V|
        2. Solve Equation (7.95) for Δδ
        3. Update the angles δ and use them to calculate mismatches ΔQ/|V|
        4. Solve Equation (7.96) for Δ|V| and update the magnitudes |V|, and
        5. Return to Equation (7.95) to repeat the iteration until all mismatches are within specified tolerances
    """

    YBus = BuildYbusMatrix(line_data, num_buses)
    BusList = buildBusList(bus_data, Sbase)

    # Initialize FDLF buses
    B_sup1, B_sup2 = initializeFastDecoupled(YBus)


if __name__ == '__main__':
    FDLF()