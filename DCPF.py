from functions import *
import pandas as pd

line_data = ReadCsvFile('./files/network_configuration_line_data.csv')
bus_data = ReadCsvFile('./files/network_configuration_bus_data.csv')
Sbase = 100 # MVA
Ubase = 230 # kV



def DCPF():
    num_buses = len(bus_data)

    YBus = BuildYbusMatrix(line_data, num_buses)
    BusList = buildBusList(bus_data, Sbase)

    bus_overview = setupBusType(bus_data)
    P_spec, Q_spec = findKnowns(bus_data, Sbase)
    v_guess, diraq_guess = findUnknowns(bus_overview, bus_data)
    
    jacobian_matrix = buildJacobian(BusList, P_spec, Q_spec, v_guess, diraq_guess, YBus)

    df_jac = pd.DataFrame(jacobian_matrix)
    df_ybus = pd.DataFrame(YBus)
    print(df_ybus, "\n\n", df_jac)

    slack_bus_info = findSlackBusType(bus_overview)

    index_to_remove = slack_bus_info -1

    removeSlackElementYBus = np.delete(YBus, index_to_remove, axis=0)  # Remove the row
    removeSlackElementYBus = np.delete(removeSlackElementYBus, index_to_remove, axis=1)  # Remove the column
    df_removeslackElementYbus = pd.DataFrame(removeSlackElementYBus)
    pd.set_option('display.max_columns', None)
    
    df_Ydc = df_removeslackElementYbus.apply(lambda x: x.apply(lambda val: val.imag)) #create new DataFrame with only the imaginary part

    df_Ydc_neg = df_Ydc * -1   #Negative of imaginary part

    print(df_Ydc_neg)
    df_Ydc_inv = np.linalg.inv(df_Ydc_neg) #Inverse of Ydc
    Pvalues = list(P_spec.values())
    Pmatrix = np.array(Pvalues).reshape(-1, 1)
    df_Pmatrix = pd.DataFrame(Pmatrix)
    print(df_Pmatrix)

    phaseangle = np.dot(df_Ydc_inv, df_Pmatrix)  #Using DCPF to find the phase angles
    
    phaseangle_degree = np.degrees(phaseangle) #phase angles in degrees
    df_phaseangle_degree = pd.DataFrame(phaseangle_degree)
    print(df_phaseangle_degree)
    df_phaseangle = pd.DataFrame(phaseangle)
    print(df_phaseangle) #Phase angles in rad

    Ydc_absolute = np.abs(np.imag(df_ybus))
    df_Ydc_absolute = pd.DataFrame(Ydc_absolute)
    print(df_Ydc_absolute)


    index = 1
    col = 0
    cell_val = df_Ydc_absolute[index][col]
    print(cell_val)

    index = 0  #skal alltid være 0
    col = 0  #skal være lik col til cell_val
    cell_val2 = df_phaseangle[index][col]
    print(cell_val2)

    index = 0 #skal alltid være null
    col = 1 #skal være lik index til cell_val
    cell_val3 = df_phaseangle[index][col]
    print(cell_val3)

    real_power_12 = cell_val * (cell_val2 - cell_val3 )*Sbase
    print('P1-2 = ', real_power_12)

   


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
    print(result_df)            

    # for row in range(df_Ydc_absolute.shape[0]):
    #     for col in range(df_Ydc_absolute.shape[1]):
    #         if df_Ydc_absolute.iloc[row, col] != 0 and row != col:
    #             result_df.iloc[row,col] = df_Ydc_absolute.iloc[row,col]*df_phaseangle.iloc[row, 0]

    # print(result_df) 

            


    


   
   


          




    
    









def findSlackBusType(bus_overview):
    for bus_info in bus_overview:
        if bus_info['Type'] == 'Slack':
            return bus_info['Bus']



    #print(bus_overview[1]['Type'])  #løkke fra 1 til len() av bus_overview og finne posisjon for slack bus. 

    #runDCPF()

if __name__ == '__main__':
    DCPF()


def runDCPF():


    return


