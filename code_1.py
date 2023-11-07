# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
# This code allows you to derive the numerical values of m and q, given the coordinates of the point of interest. 

# Define read ascii function
import pandas as pd
import math
import csv

def write_to_csv(filename, value):
    with open (filename, 'a', newline = '') as csvfile:
        writer = csv.writer(csvfile)
        writer.row([value])


def read_asc_to_dataframe(asc_file):
    df = pd.read_csv(asc_file, delimiter=' ', skiprows=6, header=None)
    df.columns = range(len(df.columns))  # Assign column names as numbers
    return df

ref_pt_x = 24483.000000  # [for user input] coordinates of reference left corner pixel
ref_pt_y = 28694.204819
nrow = 3175              # [for user input] total number of rows in the FOS ascii file
ncol = 3380

sensor_svy_x,sensor_svy_y = 27060.6, 29743.263 # [for user input] svy21 coordinates of point of interest

# Step 1: Extracting x and y values from ascii files
column_svy = 451 #math.ceil(sensor_svy_x - ref_pt_x)
row_svy = nrow - 1102 #math.ceil(sensor_svy_y - ref_pt_y)

VWC_column_index = math.ceil(column_svy/5) - 1 
VWC_row_index = math.ceil(row_svy/5)

VWC_folder = ['VWCL0001N0001.asc','VWCL0001N0024.asc','VWCL0001N0048.asc','VWCL0002N0001.asc','VWCL0002N0024.asc','VWCL0002N0048.asc','VWCL0003N0001.asc','VWCL0003N0024.asc','VWCL0003N0048.asc','VWCL0004N0001.asc','VWCL0004N0024.asc','VWCL0004N0048.asc','VWCL0005N0001.asc','VWCL0005N0024.asc','VWCL0005N0048.asc','VWCL0006N0001.asc','VWCL0006N0024.asc','VWCL0006N0048.asc']
FOS_folder = ['jf20_gapfill_1hr.asc','jf20_gapfill_24hr.asc','jf20_gapfill_48hr.asc']
extracted_x = []
extracted_y = []

df_m = pd.DataFrame()
df_q = pd.DataFrame()

for n in range(1,19):
    asc_file = VWC_folder[n-1]
    k = read_asc_to_dataframe(asc_file)

for n in range(1,4):
    asc_file = FOS_folder[n-1]
    k = read_asc_to_dataframe(asc_file)

for col in range (900,905):
    print ('This is number:', col)
    row_data_m = []
    row_data_q = []
    
    for row in range (0,nrow):
        
        for n in range(1,19):                      
            x = k.loc[row, col]
            extracted_x.append(x)
        
        for n in range(1,19):
            y = k.loc[row, col]
            extracted_y.append(y)
        
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
        X_avg = (x_1hr_mean + x_24hr_mean + x_48hr_mean)/3
        Y_avg = (sum(extracted_y))/3

    
        # Step 4: Calculating gradient, m 
        m_top = ( (x_1hr_mean - X_avg)*(extracted_y[0] - Y_avg) + (x_24hr_mean - X_avg)*(extracted_y[1] - Y_avg) + (x_48hr_mean - X_avg)*(extracted_y[2] - Y_avg) )
        m_btm = ( (x_1hr_mean - X_avg)**2 + (x_24hr_mean - X_avg)**2 + (x_48hr_mean - X_avg)**2)

        m = m_top/m_btm
        row_data_m.append(m)
        
        # Step 5: Calculating intercept, q
        q = Y_avg - m*X_avg
        row_data_q.append(q)
                
    df_q = df_q.append(pd.Series(row_data_q),ignore_index = True)
    df_m = df_m.append(pd.Series(row_data_m),ignore_index = True)
        
       

