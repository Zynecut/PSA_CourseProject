#resultat_matrix = df_result_matrix
    #imaginary_part_neg = df_imaginary_part_negated

    #result = result_matrix.dot(df_imaginary_part_negated)

# Opprett en ny DataFrame for resultatet
    #df_result = pd.DataFrame(result)

# Skriv ut den nye DataFrame
    #print(df_result)
    
    result2_matrix = np.abs(np.imag(df_ybus))
    df_result2_matrix = pd.DataFrame(result2_matrix)
    print(df_result2_matrix)

    index = 1
    col = 0
    cell_val = df_result2_matrix[index][col]
    print(cell_val)

    index = 0
    col = 0
    cell_val2 = df_result[index][col]
    print(cell_val2)

    index = 0
    col = 1
    cell_val3 = df_result[index][col]
    print(cell_val3)

    real_power_12 = cell_val * (cell_val2 - cell_val3 )
    print(real_power_12)


    result_matrix = pd.DataFrame()

# Loop over alle mulige linjekombinasjoner
    for i in range(len(df_result2_matrix.columns)):
        for j in range(i + 1, len(df_result2_matrix.columns)):
        # Beregn effekt for linjekombinasjon (i, j)
                diff_voltage = df_result2_matrix[i] - df_result2_matrix[j]
                current = df_result.iloc[i, 0] - df_result.iloc[j, 0]
                power = diff_voltage * current
                result_matrix[f'Line {i}-{j} Power'] = power

# Skriv ut resultatene
    

    # Loop over alle mulige linjekombinasjoner
    for i in range(len(df_result2_matrix.columns)):
        for j in range(i + 1, len(df_result2_matrix.columns)):
        # Sjekk om indeksene er gyldige
            if i < len(df_result) and j < len(df_result):
            # Beregn effekt for linjekombinasjon (i, j)
                voltage_i = df_result2_matrix[i].values[0]
                voltage_j = df_result2_matrix[i].values[0]
                #diff_voltage = df_result2_matrix[i] + df_result2_matrix[j]
                current = df_result.iloc[i, 0] - df_result.iloc[j, 0]
                power = voltage_i * current
                result_matrix[f'Line {i}-{j} Power'] = power

    print(result_matrix)   


P = np.zeros(len(df_result2_matrix), len(df_result2_matrix))

    for i in range(len(df_result2_matrix)):
        for j in range(len(df_result2_matrix)):
            if i != j:
                P.iloc[i, j] = df_result2_matrix.iloc[i, j] * (df_result.iloc[i, i] - df_result.iloc[i, 0])

    print(P)



    # k = 0
    # for i in range(len(df_result2_matrix)):
    #     for j in range(len(df_result2_matrix)):
    #          if 
             


 index = 1
    col = 0
    cell_val = df_result2_matrix[index][col]
    print(cell_val)

    index = 0  #skal alltid være 0
    col = 0  #skal være lik col til cell_val
    cell_val2 = df_result[index][col]
    print(cell_val2)

    index = 0 #skal alltid være null
    col = 1 #skal være lik index til cell_val
    cell_val3 = df_result[index][col]
    print(cell_val3)

    real_power_12 = cell_val * (cell_val2 - cell_val3 )*Sbase
    print('P1-2 = ', real_power_12)


    #lag program slik at real_power_12 blir en matrise med ulike svar for ulike verdier i index og col. de ulike verdiene i index og col kan være  col,index - 0,1 - 0,2 - 1,2 - 1,3 - 1,4 - 2,3 - 3,4
# Assuming you have Sbase defined somewhere

# Create an empty matrix to store the results
    real_power_12_matrix = []

# Define the combinations of index and col values you want to calculate
    combinations = [(0, 1), (0, 2), (1, 2), (1, 3), (1, 4), (2, 3), (3, 4)]

# Iterate over the combinations
    for index, col in combinations:
        cell_val = df_result2_matrix[index][col]
        cell_val2 = df_result[0][col]
        cell_val3 = df_result[index][1]
        real_power_12 = cell_val * (cell_val2 - cell_val3) * Sbase
        real_power_12_matrix.append(real_power_12)

# Print the results
    for i, (index, col) in enumerate(combinations):
        print(f'P{index}-{col} = {real_power_12_matrix[i]}')


    #lag program slik at real_power_12 blir en matrise med ulike svar for ulike verdier i index og col. de ulike verdiene i index og col kan være  col,index - 0,1 - 0,2 - 1,2 - 1,3 - 1,4 - 2,3 - 3,4



result_df = pd.DataFrame(columns=df_result2_matrix.columns, index=df_result2_matrix.index)

    for row in range(df_result2_matrix.shape[0]):
        for col in range(df_result2_matrix.shape[1]):
            if df_result2_matrix.iloc[row, col] != 0 and row != col:
                result_df.iloc[row,col] = df_result2_matrix.iloc[row,col]*df_result.iloc[row, 0]

    print(result_df)    


  if slack_bus_info is not None:
        print(slack_bus_info)
    else:
        print("No Slack bus type found in the bus overview.")
