from functions import *
import pandas as pd


# Given data
line_data = ReadCsvFile('./files/given_network/network_configuration_line_data.csv')
bus_data = ReadCsvFile('./files/given_network/network_configuration_bus_data_slack1.csv')
# bus_data = ReadCsvFile('./files/given_network/network_configuration_bus_data_slack2.csv')

# Test data
# line_data = ReadCsvFile('./files/test_network/test_line_data.csv')
# bus_data = ReadCsvFile('./files/test_network/test_bus_data.csv')

# line_data = ReadCsvFile('./files/test_network/network_configuration_line_data_Fellestest.csv')
# bus_data = ReadCsvFile('./files/test_network/network_configuration_bus_data_Fellestest.csv')

Sbase = 100 # MVA
Ubase = 230 # kV
Ibase = (Sbase*10**6)/(Ubase*10**3)
Zbase = (Ubase*1000)**2 / (Sbase*10**6) 
max_iterations = 30

tolerance = 1e-3
Q_lim = -0.6
V_lim = -0.1 # take 1 - V_lim for max and 1 - abs(V_lim) for min

def iterateNRLF(BusList, YBus, P_spec, Q_spec, v_guess, dirac_guess, max_iterations, tolerance, Q_lim, V_lim):
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
            break
        else:
            deltaP = calcP(BusList, P_spec, YBus)
            deltaQ = calcQ(BusList, Q_spec, YBus)
            delta_u = np.concatenate((deltaP, deltaQ), axis= 0)
            jacobian = buildJacobian(BusList, P_spec, Q_spec, v_guess, dirac_guess, YBus)
            delta_x= calcDeltaUnknowns(jacobian, delta_u)
            updateVoltageAndAngleList(delta_x, dirac_guess, v_guess)
            updateBusList(BusList, dirac_guess, v_guess)
            # Q_spec, v_guess = checkTypeSwitch(BusList, YBus, Q_spec, v_guess, Q_lim, V_lim)
            k += 1
    return delta_u, delta_x, k

def NewtonRaphson(bus_data, line_data, Sbase, max_iterations, tolerance, Q_lim, V_lim):
    """
        Values under must be defined in the funtion () before implementing in main()
        line_data, bus_data, Sbase, Ubase, max_iterations, tolerance
        delta_u is known values - ΔP, ΔQ
        delta_x is unknown values - Δδ, Δ|v|
    """
    line_data = ReadCsvFile('./files/network_configuration_line_data.csv')
    bus_data = ReadCsvFile('./files/network_configuration_bus_data.csv')

    num_buses = len(bus_data)
    YBus = BuildYbusMatrix(line_data, num_buses)
    bus_overview = setupBusType(bus_data)
    BusList = buildBusList(bus_data, Sbase, bus_overview)
    P_spec, Q_spec = findKnowns(bus_data, Sbase)
    v_guess, dirac_guess = findUnknowns(bus_overview, bus_data)
    delta_u, delta_x, k = iterateNRLF(BusList= BusList, 
                    YBus= YBus, 
                    P_spec= P_spec, 
                    Q_spec= Q_spec, 
                    v_guess= v_guess, 
                    dirac_guess= dirac_guess, 
                    max_iterations= max_iterations, 
                    tolerance= tolerance,
                    Q_lim=Q_lim,
                    V_lim=V_lim
                    )
    print(f"The method converged after {k} iterations!")
    updateSlackAndPV(BusList=BusList, YBus=YBus, Sbase=Sbase) # Sjekk Qi på PV bus
    
    tap, sump, sumq = Losses(line_data, BusList)

    print("\n")
    df_NRLF = makeDataFrame(BusList)
    print("\n")
    print(df_NRLF)
    print_dataframe_as_latex(df_NRLF)
    print(tap)
    print(sump, sumq)


    # Calculate line losses 
    # P = I^2 * R       R = r*Zbase
    # Q = I^2 * X       X = x*Zbase
    # Calc line flows 
    # P1-2 and P2-1
    # Q1-2 and Q2-1
    # Can also use this to check line losses


    # # Calculate line losses


def Losses(line_data, BusList):

    sumActivePowerloss = 0
    sumReactivPowerloss = 0

    Line_losses = []

    for d in (line_data): 
        busa = int(d['From line'])
        busb = int(d['To line'])
        Name = f"Line {busa}-{busb}"

        va = float(BusList[busa - 1].voltage_magnitude) 
        vb = float(BusList[busb - 1].voltage_magnitude) 

        dirac_a = float(BusList[busa - 1].voltage_angle)
        dirac_b = float(BusList[busb - 1].voltage_angle) 

        Va = cmath.rect(va, dirac_a)
        Vb = cmath.rect(vb, dirac_b)

        Yc = (-1j* float(d['Half Line Charging Admittance'])) 

        Zr = float(d['R[pu]']) 
        Zl = 1j*float(d['X[pu]']) 

        Yl = 1/ (Zr + Zl) 

        Iab = Yl * (Va -Vb) + Yc * Va
        Iba = Yl * (Vb -Va) + Yc * Vb

        Sab = Va * np.conj(Iab)
        Sba = Vb * np.conj(Iba)

        Pab = Sab.real
        Pba = Sba.real
        Qab = Sab.imag
        Qba = Sba.imag


        Ploss = Pab - Pba
        Qloss = Qab - Qba

        sumActivePowerloss += ( Ploss)
        sumReactivPowerloss += (Qloss)

        Line_loss = {'Line' : Name,
                        'Active Powerloss [MW]': Ploss,
                        'Reactive Powerloss [MVAr]': Qloss}

        Line_losses.append(Line_loss)
            

        dfLineloss = pd.DataFrame(Line_losses)
        dfLineloss.set_index('Line', inplace=True)


    return dfLineloss, sumActivePowerloss, sumReactivPowerloss








if __name__ == '__main__':
    NewtonRaphson(bus_data=bus_data, 
              line_data=line_data, 
              Sbase=Sbase, 
              max_iterations=max_iterations, 
              tolerance=tolerance, 
              Q_lim=Q_lim,
              V_lim=V_lim
              )