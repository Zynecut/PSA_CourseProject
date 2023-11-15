from functions import *
import time

# standard
line_data = ReadCsvFile('./files/given_network/network_configuration_line_data.csv')
# line_data = ReadCsvFile('./files/given_network/network_configuration_line_data_no_shunt.csv')
bus_data = ReadCsvFile('./files/given_network/network_configuration_bus_data_slack1.csv')
# bus_data = ReadCsvFile('./files/given_network/network_configuration_bus_data_slack2.csv')
Sbase = 100 # MVA
Ubase = 230 # kV
max_iterations = 100
tolerance = 1e-6
Q_lim = 0.65

def iterateDLF(BusList, YBus, P_spec, Q_spec, v_guess, dirac_guess, max_iterations, tolerance, Q_lim):
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
            Q_spec, v_guess = checkTypeSwitch(BusList, YBus, Q_spec, v_guess, Q_lim)
            deltaP = calcP(BusList, P_spec, YBus)
            deltaQ = calcQ(BusList, Q_spec, YBus)
            delta_u = np.concatenate((deltaP, deltaQ), axis= 0)
            jacobian = calcDecoupledJacobian(BusList, P_spec, Q_spec, v_guess, dirac_guess, YBus)
            delta_x= calcDecoupledDiracVoltage(jacobian, delta_u)
            updateVoltageAndAngleList(delta_x, dirac_guess, v_guess)
            updateBusList(BusList, dirac_guess, v_guess)
            k += 1
    return delta_u, delta_x, k


def DLF(bus_data, line_data, Sbase, max_iterations, tolerance, Q_lim):
    """
        delta_u is known values - ΔP, ΔQ
        delta_x is unknown values - Δδ, Δ|v|
    """
    start_time = time.time()
    num_buses = len(bus_data)
    YBus = BuildYbusMatrix(line_data, num_buses, None)
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
                                     tolerance= tolerance,
                                     Q_lim= Q_lim
                                     ) 
    
    updateSlackAndPV(BusList=BusList, YBus=YBus, Sbase=Sbase) # Sjekk Qi på PV bus

    sump, sumq, flow, S_I_injections, flow_pu= PowerLossAndFlow(line_data, BusList, Sbase, Ubase)
    df_DLF, df_DLF_pu = makeDataFrame(BusList, Sbase, Ubase)
    DLF = df_DLF.to_latex()
    print(DLF)
    print("\n")
    DLF_pu = df_DLF_pu.to_latex()
    print(DLF_pu)
    print("\n") 
    flow2 = flow.to_latex()
    print(flow2)
    print("\n")
    flow_pu2 = flow_pu.to_latex()
    print(flow_pu2)
    print("\n")
    S_I = S_I_injections.to_latex()
    print(S_I)
    print("\n")
    print(f"Active loss: {round(df_DLF['P [pu]'].sum(),3)}, Reactive loss: {round(df_DLF['Q [pu]'].sum(),3)}")
    print(f"The method converged after {k} iterations!")
    print(f"Active powerloss = {round(sump,3)} [MW], Reactive powerloss =  {round(sumq,3)} [MVAr]")
    print("--- %s seconds ---" % (time.time() - start_time))
    

if __name__ == '__main__':
    DLF(bus_data=bus_data, 
        line_data=line_data, 
        Sbase=Sbase, 
        max_iterations=max_iterations, 
        tolerance=tolerance,
        Q_lim=Q_lim
        )