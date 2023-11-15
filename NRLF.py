from functions import *
import time


# Given data
line_data = ReadCsvFile('./files/given_network/network_configuration_line_data.csv')
# line_data = ReadCsvFile('./files/given_network/network_configuration_line_data_no_shunt.csv')
bus_data = ReadCsvFile('./files/given_network/network_configuration_bus_data_slack1.csv')

# bus_data = ReadCsvFile('./files/given_network/network_configuration_bus_data_slack2.csv')
# bus_data = ReadCsvFile('./files/given_network/network_configuration_bus_data_slack1_no_reactive_load.csv')

# Data from DCPF
# bus_data = ReadCsvFile('./files/given_network/network_configuration_bus_data_slack1_DCPF_Start.csv')

Sbase = 100 # MVA
Ubase = 230 # kV
max_iterations = 300
tolerance = 1e-6
Q_lim = 0.65 # To check PQ state, lower limit to 0.6
XR_ratio = None # Default None for standard system

def iterateNRLF(BusList, YBus, P_spec, Q_spec, v_guess, dirac_guess, max_iterations, tolerance, Q_lim):
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
            return f"The method did not converge after {k} iterations!"
        else:
            Q_spec, v_guess = checkTypeSwitch(BusList, YBus, Q_spec, v_guess, Q_lim)
            deltaP = calcP(BusList, P_spec, YBus)
            deltaQ = calcQ(BusList, Q_spec, YBus)
            delta_u = np.concatenate((deltaP, deltaQ), axis= 0)
            jacobian = buildJacobian(BusList, P_spec, Q_spec, v_guess, dirac_guess, YBus)
            delta_x= calcDeltaUnknowns(jacobian, delta_u)
            updateVoltageAndAngleList(delta_x, dirac_guess, v_guess)
            updateBusList(BusList, dirac_guess, v_guess)
            
            k += 1
    return f"The method converged after {k} iterations!"

def NewtonRaphson(bus_data, line_data, Sbase, max_iterations, tolerance, Q_lim, XR_ratio):
    """
        Values under must be defined in the funtion () before implementing in main()
        line_data, bus_data, Sbase, Ubase, max_iterations, tolerance
        delta_u is known values - ΔP, ΔQ
        delta_x is unknown values - Δδ, Δ|v|
    """
    start_time = time.time()
    num_buses = len(bus_data)
    YBus = BuildYbusMatrix(line_data, num_buses, XR_ratio)
    bus_overview = setupBusType(bus_data)
    BusList = buildBusList(bus_data, Sbase, bus_overview)
    LineList = buildLineList(line_data)
    P_spec, Q_spec = findKnowns(bus_data, Sbase)
    v_guess, dirac_guess = findUnknowns(bus_overview, bus_data)
    message = iterateNRLF(BusList= BusList, 
                    YBus= YBus, 
                    P_spec= P_spec, 
                    Q_spec= Q_spec, 
                    v_guess= v_guess, 
                    dirac_guess= dirac_guess, 
                    max_iterations= max_iterations, 
                    tolerance= tolerance,
                    Q_lim=Q_lim
                    )

    updateSlackAndPV(BusList=BusList, YBus=YBus, Sbase=Sbase) # Sjekk Qi på PV bus
    sump, sumq, flow, S_I_injections= PowerLossAndFlow(line_data, BusList, Sbase, Ubase, XR_ratio)
    df_NRLF = makeDataFrame(BusList, Sbase, Ubase)

    NRLF = df_NRLF.to_latex()
    print(NRLF)
    print("\n")
    flow2 = flow.to_latex()
    print(flow2)
    print("\n")
    S_I = S_I_injections.to_latex()
    print(S_I)
    print("\n")
    print(f"Active loss: {round(df_NRLF['P [pu]'].sum(),3)}, Reactive loss: {round(df_NRLF['Q [pu]'].sum(),3)}")
    print(message)
    print(f"Active powerloss = {round(sump,3)} [MW], Reactive powerloss =  {round(sumq,3)} [MVAr]")
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
              XR_ratio= XR_ratio
              )