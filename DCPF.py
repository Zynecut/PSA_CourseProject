from functions import *
import pandas as pd

line_data = ReadCsvFile('./files/given_network/network_configuration_line_data.csv')
bus_data = ReadCsvFile('./files/given_network/network_configuration_bus_data_slack1.csv')
Sbase = 100 # MVA
Ubase = 230 # kV



def DCPF(bus_data, line_data, Sbase):
    num_buses = len(bus_data)

    YBus = BuildYbusMatrix(line_data, num_buses)
    bus_overview = setupBusType(bus_data)
    BusList = buildBusList(bus_data, Sbase, bus_overview)

    bus_overview = setupBusType(bus_data)
    P_spec, Q_spec = findKnowns(bus_data, Sbase)

    # df_ybus = pd.DataFrame(YBus)

    # slack_bus_info = findSlackBusType(bus_overview)

    # index_to_remove = slack_bus_info -1

    # removeSlackElementYBus = np.delete(YBus, index_to_remove, axis=0)  # Remove the row
    # removeSlackElementYBus = np.delete(removeSlackElementYBus, index_to_remove, axis=1)  # Remove the column
    # df_removeslackElementYbus = pd.DataFrame(removeSlackElementYBus)
    # pd.set_option('display.max_columns', None)
    
    # df_Ydc = df_removeslackElementYbus.apply(lambda x: x.apply(lambda val: val.imag)) #create new DataFrame with only the imaginary part

    # df_Ydc_neg = df_Ydc * -1   #Negative of imaginary part

    # New shit bruv
    YBus_DC = YBusDC(BusList, YBus)

    print(YBus_DC)

    YBus_DC_inv = np.linalg.inv(YBus_DC) #Inverse of Ydc
    Pvalues = list(P_spec.values())
    P_arr = np.array(Pvalues).reshape(-1, 1)

    phaseangle = np.dot(YBus_DC_inv, P_arr)  #Using DCPF to find the phase angles
    df_phaseangle = pd.DataFrame(phaseangle)
    print(df_phaseangle)

    Ydc_absolute = np.abs(np.imag(YBus))
    df_Ydc_absolute = pd.DataFrame(Ydc_absolute)
    print(df_Ydc_absolute)

   
    result_df = pd.DataFrame(columns=df_Ydc_absolute.columns, index=df_Ydc_absolute.index)
    
    k = 0
    for rad in range(df_Ydc_absolute.shape[1]):
        #print(df_Ydc_absolute[kolonne])
        for kolonne in range(df_Ydc_absolute.shape[0]):
            tall = df_Ydc_absolute[kolonne][rad]
            if tall == 0:
                continue
            result_df.iloc[rad,kolonne] = tall*(df_phaseangle[0][0]-df_phaseangle[0][k])
            k += 1
            if k > df_phaseangle.shape[1]:
                k = 0
                
    result_df.fillna(0, inplace=True)
    print(result_df)            


            



def findSlackBusType(bus_overview):
    for bus_info in bus_overview:
        if bus_info['Type'] == 'Slack':
            return bus_info['Bus']


if __name__ == '__main__':
    DCPF(bus_data=bus_data,
         line_data=line_data,
         Sbase=Sbase
         )

