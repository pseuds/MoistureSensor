# This code allows you to derive the numerical values of m and q, given the coordinates of the point of interest. 

# Define read ascii function
import pandas as pd
import math
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from PyQt5.QtCore import QObject, QThread, pyqtSignal

def read_asc_to_dataframe(asc_file, first_6=False):
    # read the first 6 rows
    if first_6:
        df = pd.read_csv(asc_file, nrows=6, delim_whitespace=True, header=None)
    else: # read the body
        df = pd.read_csv(asc_file, delimiter=' ', skiprows=6, header=None)
        df.columns = range(len(df.columns))  # Assign column names as numbers
    return df

class Calculator(QObject):
    finished = pyqtSignal(int)
    progress = pyqtSignal(int)
    result_values = pyqtSignal(list)

    def __init__(self, source_folder, zone, VWC_files, FOS_files, ref_pt_x, ref_pt_y, sensor_svy_x, sensor_svy_y):
        super().__init__()
        self.source_folder = source_folder
        self.zone = zone
        self.VWC_files = VWC_files
        self.FOS_files = FOS_files
        self.ref_pt_x = ref_pt_x
        self.ref_pt_y = ref_pt_y
        self.sensor_svy_x = sensor_svy_x
        self.sensor_svy_y = sensor_svy_y

        self.count = 0 # count progress

    def run(self):
        # get dir of data
        FOS_paths = [f"{self.source_folder}/{self.zone}/FOS/{fos}" for fos in self.FOS_files]
        VWC_paths = [f"{self.source_folder}/{self.zone}/VWC/{vwc}" for vwc in self.VWC_files]

        # get nrows from any FOS file
        df_first6 = read_asc_to_dataframe(FOS_paths[0], first_6=True)
        nrow = int(df_first6.loc[1,1]) 

        self.count += 1
        self.progress.emit(self.count)

        # Step 1: Extracting x and y values from ascii files
        column_svy = math.ceil(self.sensor_svy_x - self.ref_pt_x)
        row_svy = nrow - math.ceil(self.sensor_svy_y - self.ref_pt_y)  

        VWC_column_index = math.ceil(column_svy/5) - 1 
        VWC_row_index = math.ceil(row_svy/5) 

        extracted_x = []
        extracted_y = []
        
        for vwc_path in VWC_paths:
            k = read_asc_to_dataframe(vwc_path)
            try: 
                x = k.loc[VWC_row_index, VWC_column_index]
                extracted_x.append(x)

                self.count += 1
                self.progress.emit(self.count)
            except Exception as e:
                print(f"Exception occurred when reading {vwc_path}: {e}")
                print(f"df dimensions:{len(k)}, {len(k.columns)}")
                print(f"index to read:{VWC_row_index}, {VWC_column_index}")
                self.finished.emit(self.count)
                return None
            
        for fos_path in FOS_paths:
            k = read_asc_to_dataframe(fos_path)
            try:
                y = k.loc[row_svy, column_svy]
                extracted_y.append(y)

                self.count += 1
                self.progress.emit(self.count)
            except Exception as e:
                print(f"Exception occurred when reading {fos_path}: {e}")
                print(f"df dimensions:{len(k)}, {len(k.columns)}")
                print(f"index to read:{row_svy}, {column_svy}")
                self.finished.emit(self.count)
                return None

        self.count += 1
        self.progress.emit(self.count)

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
        m_top = ( (x_1hr_mean - X_avg)*(extracted_y[0] - Y_avg) + (x_24hr_mean - X_avg)*(extracted_y[1] - Y_avg) + (x_48hr_mean - X_avg)*(extracted_y[2] - Y_avg) )
        m_btm = ( (x_1hr_mean - X_avg)**2 + (x_24hr_mean - X_avg)**2 + (x_48hr_mean - X_avg)**2)

        m = m_top/m_btm

        # Step 5: Calculating intercept, q
        q = Y_avg - m*X_avg

        print('At the SVY21 coordinates of', self.sensor_svy_x,',', self.sensor_svy_y,':')
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

        # round values
        x = [round(i, 3) for i in x]
        y = [round(i, 3) for i in y]

        r = np.corrcoef(x[1:4], y[1:4])[0, 1]

        matplotlib.use('agg') # only write to files; so it doesn't print user warning

        # plotting
        # from matplotlib import pyplot as plt
        plt.plot(x,y, color = 'red', label = "Z line")

        for i, j in zip(x, y):
            plt.text(i, j, f'({i}, {j})', ha='right', va='bottom')

        # Set labels and title
        plt.xlabel('VWC')
        plt.ylabel('FOS')
        plt.savefig('assets/Z_plot.png', format='png')
        plt.cla()

        self.finished.emit(0)
        self.result_values.emit([m, q, x_1hr_mean, x_48hr_mean, extracted_y[0], midpoint_y, r**2, X_avg])


