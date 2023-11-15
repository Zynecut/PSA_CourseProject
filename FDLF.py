from functions import *
import time

# Given data
line_data = ReadCsvFile('./files/given_network/network_configuration_line_data.csv')
# line_data = ReadCsvFile('./files/given_network/network_configuration_line_data_no_shunt.csv')
bus_data = ReadCsvFile('./files/given_network/network_configuration_bus_data_slack1.csv')
# bus_data = ReadCsvFile('./files/given_network/network_configuration_bus_data_slack2.csv')
# bus_data = ReadCsvFile('./files/given_network/network_configuration_bus_data_slack1_no_reactive_load.csv')
Sbase = 100 # MVA
Ubase = 230 # kV
num_buses = len(bus_data)
max_iterations = 100
tolerance = 1e-6
Q_lim = 1.2
iterate_partial_orEnd = True # True for calculation partially through iteration or False for calculation at end of iteration
XR_ratio = 2

def iterateFDLF(BusList, YBus, P_spec, Q_spec, v_guess, dirac_guess, max_iterations, tolerance, B_prime, B_double_prime, Q_lim, iterate_partial_orEnd):
    """
        Function that iterates the FDLF method. 
    """
    if iterate_partial_orEnd:
        deltaP = calcP(BusList, P_spec, YBus)
        deltaPn_Vn = calcDeltaPn_Vn(BusList, deltaP)
        delta_Dirac = np.dot(B_prime, deltaPn_Vn)
        updateAngleFDLFandBusList(BusList, delta_Dirac, dirac_guess)

        deltaQ = calcQ(BusList, Q_spec, YBus)
        deltaQn_Vn = calcDeltaQn_Vn(BusList, deltaQ)
        if len(deltaQ) != len(B_double_prime):      
            delta_v = np.dot(B_prime, deltaQn_Vn)   # If typeSwitched
        else:
            delta_v = np.dot(B_double_prime, deltaQn_Vn)    # Calculate Δ|V|

        updateVoltageFDLFandBusList(BusList, delta_v, v_guess)
        delta_u = np.concatenate((deltaP, deltaQ), axis= 0)
        k = 0
        convergence = False
        while not convergence:
            if checkConvergence(tolerance, delta_u):
                convergence = True
            elif max_iterations < k:
                return f"The method did not converge after {k} iterations!"
            else:
                Q_spec, v_guess = checkTypeSwitch(BusList, YBus, Q_spec, v_guess, Q_lim)
                deltaP = calcP(BusList, P_spec, YBus)           # Calculate ΔP
                deltaPn_Vn = calcDeltaPn_Vn(BusList, deltaP)    # Calculate ΔP/|V|
                delta_Dirac = np.dot(B_prime, deltaPn_Vn)       # Calculate Δδ
                updateAngleFDLFandBusList(BusList, delta_Dirac, dirac_guess)

                deltaQ = calcQ(BusList, Q_spec, YBus)           # Calculate ΔQ
                deltaQn_Vn = calcDeltaQn_Vn(BusList, deltaQ)    # Calculate ΔQ/|V|
                if len(deltaQ) != len(B_double_prime):      
                    delta_v = np.dot(B_prime, deltaQn_Vn)   # If typeSwitched
                else:
                    delta_v = np.dot(B_double_prime, deltaQn_Vn)    # Calculate Δ|V|
                
                updateVoltageFDLFandBusList(BusList, delta_v, v_guess)
                delta_u = np.concatenate((deltaP, deltaQ), axis= 0)
                k += 1
        return f"The method converged after {k} iterations, with partially updated values through each iteration!"
    
    else:
        deltaP = calcP(BusList, P_spec, YBus)
        deltaPn_Vn = calcDeltaPn_Vn(BusList, deltaP)
        delta_Dirac = np.dot(B_prime, deltaPn_Vn)
        
        deltaQ = calcQ(BusList, Q_spec, YBus)
        deltaQn_Vn = calcDeltaQn_Vn(BusList, deltaQ)
        if len(deltaQ) != len(B_double_prime):      
            delta_v = np.dot(B_prime, deltaQn_Vn)   # If typeSwitched
        else:
            delta_v = np.dot(B_double_prime, deltaQn_Vn)    # Calculate Δ|V|

        updateAngleFDLFandBusList(BusList, delta_Dirac, dirac_guess)
        updateVoltageFDLFandBusList(BusList, delta_v, v_guess)
        delta_u = np.concatenate((deltaP, deltaQ), axis= 0)
        k = 0
        convergence = False
        while not convergence:
            if checkConvergence(tolerance, delta_u):
                convergence = True
            elif max_iterations < k:
                return f"The method did not converge after {k} iterations!"
            else:
                Q_spec, v_guess = checkTypeSwitch(BusList, YBus, Q_spec, v_guess, Q_lim)
                deltaP = calcP(BusList, P_spec, YBus)           # Calculate ΔP
                deltaPn_Vn = calcDeltaPn_Vn(BusList, deltaP)    # Calculate ΔP/|V|
                delta_Dirac = np.dot(B_prime, deltaPn_Vn)       # Calculate Δδ
                
                deltaQ = calcQ(BusList, Q_spec, YBus)           # Calculate ΔQ
                deltaQn_Vn = calcDeltaQn_Vn(BusList, deltaQ)    # Calculate ΔQ/|V|
                if len(deltaQ) != len(B_double_prime):      
                    delta_v = np.dot(B_prime, deltaQn_Vn)   # If typeSwitched
                else:
                    delta_v = np.dot(B_double_prime, deltaQn_Vn)    # Calculate Δ|V|
                
                updateAngleFDLFandBusList(BusList, delta_Dirac, dirac_guess)
                updateVoltageFDLFandBusList(BusList, delta_v, v_guess)
                delta_u = np.concatenate((deltaP, deltaQ), axis= 0)
                k += 1
        return f"The method converged after {k} iterations, with updated values at end of each iteration!"

def FDLF(bus_data, line_data, Sbase, max_iterations, tolerance, Q_lim, iterate_partial_orEnd, XR_ratio):
    """
        R on line is neglected, thus a new YBus must be calculated.
        Stratety:
        1. Calculate the initial mismatches ΔP/|V|
        2. Solve Equation (7.95) for Δδ
        3. Update the angles δ and use them to calculate mismatches ΔQ/|V|
        4. Solve Equation (7.96) for Δ|V| and update the magnitudes |V|, and
        5. Return to Equation (7.95) to repeat the iteration until all mismatches are within specified tolerances
    """
    start_time = time.time()
    num_buses = len(bus_data)
    YBus = BuildYbusMatrix(line_data, num_buses, XR_ratio)
    bus_overview = setupBusType(bus_data)
    BusList = buildBusList(bus_data, Sbase, bus_overview)
    P_spec, Q_spec = findKnowns(bus_data, Sbase)
    v_guess, dirac_guess = findUnknowns(bus_overview, bus_data)
    B_prime, B_double_prime = calcB_Prime(BusList, YBus)
    B_prime_inv = np.linalg.inv(B_prime)
    B_double_prime_inv = np.linalg.inv(B_double_prime)
    message = iterateFDLF(BusList= BusList, 
                    YBus= YBus, 
                    P_spec= P_spec, 
                    Q_spec= Q_spec, 
                    v_guess= v_guess, 
                    dirac_guess= dirac_guess, 
                    max_iterations= max_iterations, 
                    tolerance= tolerance,
                    B_prime= B_prime_inv,
                    B_double_prime= B_double_prime_inv,
                    Q_lim= Q_lim,
                    iterate_partial_orEnd= iterate_partial_orEnd
                    )
    updateSlackAndPV(BusList=BusList, YBus=YBus, Sbase=Sbase) # Sjekk Qi på PV bus

    sump, sumq, flow, S_I_injections= PowerLossAndFlow(line_data, BusList, Sbase, Ubase, XR_ratio)
    df_FDLF = makeDataFrame(BusList, Sbase, Ubase)
    FDLF = df_FDLF.to_latex()
    print(FDLF)
    print("\n")
    flow2 = flow.to_latex()
    print(flow2)
    print("\n")
    S_I = S_I_injections.to_latex()
    print(S_I)
    print("\n")
    print(f"Active loss: {round(df_FDLF['P [pu]'].sum(),3)}, Reactive loss: {round(df_FDLF['Q [pu]'].sum(),3)}")
    print(message)
    print(f"Active powerloss = {round(sump,3)} [MW], Reactive powerloss =  {round(sumq,3)} [MVAr]")
    print("--- %s seconds ---" % (time.time() - start_time))


if __name__ == '__main__':
    FDLF(bus_data=bus_data, 
        line_data=line_data, 
        Sbase=Sbase, 
        max_iterations=max_iterations, 
        tolerance=tolerance,
        Q_lim=Q_lim,
        iterate_partial_orEnd= iterate_partial_orEnd,
        XR_ratio=XR_ratio
        )