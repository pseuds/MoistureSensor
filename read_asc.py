# This code allows you to derive the numerical values of m and q, given the coordinates of the point of interest. 

# Define read ascii function
import pandas as pd
import math
import numpy as np
import matplotlib.pyplot as plt


def read_asc_to_dataframe(asc_file, first_6=False):
    # read the first 6 rows
    if first_6:
        df = pd.read_csv(asc_file, nrows=6, delim_whitespace=True, header=None)
    else: # read the body
        df = pd.read_csv(asc_file, delimiter=' ', skiprows=6, header=None)
        df.columns = range(len(df.columns))  # Assign column names as numbers
    return df

def gorun(source_folder, zone, VWC_files, FOS_files, ref_pt_x, ref_pt_y, sensor_svy_x, sensor_svy_y):

    # get dir of data
    FOS_paths = [f"{source_folder}/JF{zone}/FOS/{fos}" for fos in FOS_files]
    VWC_paths = [f"{source_folder}/JF{zone}/VWC/{vwc}" for vwc in VWC_files]

    # get nrows from any FOS file
    df_first6 = read_asc_to_dataframe(FOS_paths[0], first_6=True) 
    nrow = int(df_first6.loc[1,1]) 

    # Step 1: Extracting x and y values from ascii files
    column_svy = math.ceil(sensor_svy_x - ref_pt_x)
    row_svy = nrow - math.ceil(sensor_svy_y - ref_pt_y)  

    VWC_column_index = math.ceil(column_svy/5) - 1 
    VWC_row_index = math.ceil(row_svy/5) 

    extracted_x = []
    extracted_y = []
    

    for vwc_path in VWC_paths:
        k = read_asc_to_dataframe(vwc_path)
        try: 
            x = k.loc[VWC_row_index, VWC_column_index]
            extracted_x.append(x)
        except Exception as e:
            print(f"Exception occurred when reading {vwc_path}: {e}")
            print(f"df dimensions:{len(k)}, {len(k.columns)}")
            print(f"index to read:{VWC_row_index}, {VWC_column_index}")
            return None
        
    for fos_path in FOS_paths:
        k = read_asc_to_dataframe(fos_path)
        try:
            y = k.loc[row_svy, column_svy]
            extracted_y.append(y)
        except Exception as e:
            print(f"Exception occurred when reading {fos_path}: {e}")
            print(f"df dimensions:{len(k)}, {len(k.columns)}")
            print(f"index to read:{row_svy}, {column_svy}")
            return None

    x_1hr_i = [0,3,6,9,12,15]
    x_24hr_i = [1,4,7,10,13,16]
    x_48hr_i = [2,5,8,11,14,17]

    x_1hr = [extracted_x[i] for i in x_1hr_i]
    x_24hr = [extracted_x[i] for i in x_24hr_i]
    x_48hr = [extracted_x[i] for i in x_48hr_i]


    # Step 2: Calculate the average VWC for layers 1 to 6 
    x_1hr_mean = sum(x_1hr)/6
    x_24hr_mean = sum(x_24hr)/6
    x_48hr_mean = sum(x_48hr)/6


    # Step 3: Calculating X_avg and Y_avg
    X_avg = (x_1hr_mean + x_24hr_mean + x_48hr_mean)/3 # 48hr file corrupted! skip for now
    Y_avg = (sum(extracted_y))/3


    # Step 4: Calculating gradient, m 
    # TODO: verify formulae below (check any assumptions)
    m_top = ( (x_1hr_mean - X_avg)*(extracted_y[0] - Y_avg) + (x_24hr_mean - X_avg)*(extracted_y[1] - Y_avg) + (x_48hr_mean - X_avg)*(extracted_y[2] - Y_avg) )
    m_btm = ( (x_1hr_mean - X_avg)**2 + (x_24hr_mean - X_avg)**2 + (x_48hr_mean - X_avg)**2)

    m = m_top/m_btm

    # Step 5: Calculating intercept, q
    q = Y_avg - m*X_avg

    print('At the SVY21 coordinates of', sensor_svy_x,',', sensor_svy_y,':')
    print('X_avg is', X_avg)
    print('Y_avg is', Y_avg)
    print('m is', m)
    print('q is', q)
    print('')
    print('FS(real-time) =', m, '* VWC(real-time) +', q)

    # Step 6: Plotting the regression line
    x = [0.3, x_1hr_mean,x_24hr_mean,x_48hr_mean, 0.5,  0.6]
    midpoint_y = m*0.5+q
    y = [extracted_y[0]] + extracted_y + [midpoint_y]*2

    r = np.corrcoef(x[1:4], y[1:4])[0, 1]

    # plotting
    # from matplotlib import pyplot as plt
    plt.plot(x,y, color = 'red', label = "Z line")
    # plt.plot(X_avg, Y_avg)
    # plt.scatter(x, y, color='blue', label='Data Points')
    # plt.plot(x, np.poly1d(np.polyfit(x, y, 1))(x), color='red', label='Regression Line')

    for i, j in zip(x, y):
        plt.text(i, j, f'({i}, {j})', ha='right', va='bottom')

    # Set labels and title
    plt.xlabel('VWC')
    plt.ylabel('FOS')
    # plt.title('Correlation Coefficient (r): {:.2f}'.format(r))
    # plt.show()
    plt.savefig('assets/Z_plot.png', format='png')
    plt.cla()
    # plt.show()

    return m, q, x_1hr_mean, x_48hr_mean, extracted_y[0], midpoint_y, r**2, X_avg



