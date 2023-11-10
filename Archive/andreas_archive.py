# print(Line_losses)

    # Line_losses = []
    # sumActivePowerloss = 0
    # sumReactivPowerloss = 0

    # for d in (line_data): 
    #     From_bus = int(d['From line'])
    #     To_bus = int(d['To line'])
    #     linename = f"L_{From_bus}{To_bus}"

    #     R_pu = float(d['R[pu]']) * Zbase

    #     X_pu = float(d['X[pu]']) * Zbase

    #     cd = (1/ (float(d['Half Line Charging Admittance']))) * Zbase


    #     voltage_from = float(BusList[From_bus - 1].voltage_magnitude) * Ubase *1000
    #     voltage_to = float(BusList[To_bus - 1].voltage_magnitude) * Ubase *1000

    #     voltage = voltage_from - voltage_to

    #     current = voltage / (R_pu + X_pu * 1j) - voltage / (cd * -1j)

    #     polar_current = cmath.polar(current)

    #     realPowerloss = 3 * polar_current[0]**2 * R_pu
    #     reactivePowerloss = 3 * polar_current[0]**2 * X_pu

    #     sumActivePowerloss += (realPowerloss / 10**6)
    #     sumReactivPowerloss += (reactivePowerloss / 10**6)
    #     Line_loss = {'Line': linename,
    #                     'Active Power Loss [MW]': realPowerloss / 10 ** 6,
    #                     'Reactive Power Loss [MVAr]': reactivePowerloss / 10 ** 6,
    #                     'Voltage [V]': voltage,
    #                     'Current [A]': polar_current[0]}
    #     Line_losses.append(Line_loss)
            

    # dfLineloss = pd.DataFrame(Line_losses)
    # dfLineloss.set_index('Line', inplace=True)

    # print(dfLineloss)
    # print("Sum of losses" , sumActivePowerloss,     sumReactivPowerloss)