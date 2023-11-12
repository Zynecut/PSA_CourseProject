from functions import *
import pandas as pd
import time

line_data = ReadCsvFile('./files/given_network/network_configuration_line_data.csv')
bus_data = ReadCsvFile('./files/given_network/network_configuration_bus_data_slack1.csv')
Sbase = 100 # MVA
Ubase = 230 # kV



def DCPF(bus_data, line_data, Sbase):
    start_time = time.time()
    num_buses = len(bus_data)

    YBus = BuildYbusMatrix(line_data, num_buses)
    bus_overview = setupBusType(bus_data)
    BusList = buildBusList(bus_data, Sbase, bus_overview)

    bus_overview = setupBusType(bus_data)
    P_spec, Q_spec = findKnowns(bus_data, Sbase)

    # New shit bruv
    YBus_DC = YBusDC(BusList, YBus)
    YBus_DC_inv = np.linalg.inv(YBus_DC) #Inverse of Ydc
    Pvalues = list(P_spec.values())
    P_arr = np.array(Pvalues).reshape(-1, 1)

    phaseangle = np.dot(YBus_DC_inv, P_arr)  #Using DCPF to find the phase angles
    df_phaseangle = pd.DataFrame(phaseangle)

    angle = {}
    for i, num in enumerate(P_spec, 0):
        key = f"Dirac_{extract_number(num)}"
        angle[key] = (180/math.pi)*phaseangle[i][0]

    for bus_id in angle:
        angle_num = extract_number(bus_id)
        for i in range(len(BusList)):
            if angle_num == BusList[i].bus_id:
                BusList[i].update_bus_voltage(new_voltage_angle=angle[bus_id])
            else:
                continue
       


    print("\n", angle, "\n")

    YBus_DC_absolute = np.abs(np.imag(YBus))
    df_Ydc_absolute = pd.DataFrame(YBus_DC_absolute)
    # print(df_Ydc_absolute)

   
    res = np.zeros((len(BusList), len(BusList)))
    for i in range(len(BusList)):
        for j in range(len(BusList)):
            Y_ij = YBus_DC_absolute[i][j]
            if Y_ij == 0:
                continue
            dirac_i = BusList[i].voltage_angle
            dirac_j = BusList[j].voltage_angle
            res[i][j] = Y_ij*(dirac_i - dirac_j)

    print(res)
    

    result_df = pd.DataFrame(columns=df_Ydc_absolute.columns, index=df_Ydc_absolute.index)
    
    k = 0
    for rad in range(df_Ydc_absolute.shape[1]):
        #print(df_Ydc_absolute[kolonne])
        for kolonne in range(df_Ydc_absolute.shape[0]):
            tall = df_Ydc_absolute[kolonne][rad]
            if tall == 0:
                continue
            result_df.iloc[rad,kolonne] = tall*(df_phaseangle[0][0]-df_phaseangle[0][k])*Sbase
            k += 1
            if k > df_phaseangle.shape[1]:
                k = 0
                
    result_df.fillna(0, inplace=True)
    print(result_df)

    res_df = pd.DataFrame(res)
    rest = res_df.to_latex()
    print(rest)        
    print("--- %s seconds ---" % (time.time() - start_time))

            



def findSlackBusType(bus_overview):
    for bus_info in bus_overview:
        if bus_info['Type'] == 'Slack':
            return bus_info['Bus']


if __name__ == '__main__':
    DCPF(bus_data=bus_data,
         line_data=line_data,
         Sbase=Sbase
         )

