from functions import *

line_data = ReadCsvFile('./files/given_network/network_configuration_line_data.csv')
bus_data = ReadCsvFile('./files/given_network/network_configuration_bus_data_slack1.csv')
Sbase = 100 # MVA
Ubase = 230 # kV
num_buses = len(bus_data)
max_iterations = 10
tolerance = 0.00001

def iterateFDLF(BusList, YBus, P_spec, Q_spec, v_guess, dirac_guess, max_iterations, tolerance, B_prime, B_double_prime):

    deltaP = calcP(BusList, P_spec, YBus)
    deltaPn_Vn = calcDeltaPn_Vn(BusList, deltaP)
    delta_Dirac = np.dot(B_prime, deltaPn_Vn)
    updateAngleFDLFandBusList(BusList, delta_Dirac, dirac_guess)

    deltaQ = calcQ(BusList, Q_spec, YBus)
    deltaQn_Vn = calcDeltaQn_Vn(BusList, deltaQ)
    delta_v = np.dot(B_double_prime, deltaQn_Vn)
    updateVoltageFDLFandBusList(BusList, delta_v, v_guess)
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
            deltaPn_Vn = calcDeltaPn_Vn(BusList, deltaP)
            delta_Dirac = np.dot(B_prime, deltaPn_Vn)
            updateAngleFDLFandBusList(BusList, delta_Dirac, dirac_guess)

            deltaQ = calcQ(BusList, Q_spec, YBus)
            deltaQn_Vn = calcDeltaQn_Vn(BusList, deltaQ)
            delta_v = np.dot(B_double_prime, deltaQn_Vn)
            updateVoltageFDLFandBusList(BusList, delta_v, v_guess)
            delta_u = np.concatenate((deltaP, deltaQ), axis= 0)
            k += 1
    return k

def FDLF(bus_data, line_data, Sbase, max_iterations, tolerance):
    """
        Stratety:
        1. Calculate the initial mismatches ΔP/|V|
        2. Solve Equation (7.95) for Δδ
        3. Update the angles δ and use them to calculate mismatches ΔQ/|V|
        4. Solve Equation (7.96) for Δ|V| and update the magnitudes |V|, and
        5. Return to Equation (7.95) to repeat the iteration until all mismatches are within specified tolerances
    """
    num_buses = len(bus_data)
    YBus = BuildYbusMatrix(line_data, num_buses)
    bus_overview = setupBusType(bus_data)
    BusList = buildBusList(bus_data, Sbase, bus_overview)
    P_spec, Q_spec = findKnowns(bus_data, Sbase)
    v_guess, dirac_guess = findUnknowns(bus_overview, bus_data)
    B_prime, B_double_prime = calcB_Prime(BusList, YBus)
    B_prime_inv = np.linalg.inv(B_prime)
    B_double_prime_inv = np.linalg.inv(B_double_prime)
    k = iterateFDLF(BusList= BusList, 
                    YBus= YBus, 
                    P_spec= P_spec, 
                    Q_spec= Q_spec, 
                    v_guess= v_guess, 
                    dirac_guess= dirac_guess, 
                    max_iterations= max_iterations, 
                    tolerance= tolerance,
                    B_prime= B_prime_inv,
                    B_double_prime= B_double_prime_inv
                    )
    updateSlackAndPV(BusList=BusList, YBus=YBus, Sbase=Sbase) # Sjekk Qi på PV bus
    print(f"The method converged after {k} iterations!\n")
    df_NRLF = makeDataFrame(BusList)
    print(df_NRLF)


if __name__ == '__main__':
    FDLF(bus_data=bus_data, 
        line_data=line_data, 
        Sbase=Sbase, 
        max_iterations=max_iterations, 
        tolerance=tolerance
        )