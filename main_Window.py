import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QFileDialog, QMessageBox, QTableWidgetItem
from PIL import Image
from read_asc import *
from main_UI import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.uiMain = Ui_MainWindow()
        self.uiMain.setupUi(self)
        self.resize(1000, 600)
        self.centerOnScreen()
        self.setMaximumSize(1200, 800)

        self.initialise()

        self.source_folder = ""    # root folder that the user chose to read from
        self.VWC_required = [ # all JF{zone} folders should have these
            'VWCL0001N0001.asc','VWCL0001N0024.asc','VWCL0001N0048.asc',
            'VWCL0002N0001.asc','VWCL0002N0024.asc','VWCL0002N0048.asc',
            'VWCL0003N0001.asc','VWCL0003N0024.asc','VWCL0003N0048.asc',
            'VWCL0004N0001.asc','VWCL0004N0024.asc','VWCL0004N0048.asc',
            'VWCL0005N0001.asc','VWCL0005N0024.asc','VWCL0005N0048.asc',
            'VWCL0006N0001.asc','VWCL0006N0024.asc','VWCL0006N0048.asc'
            ]


    def centerOnScreen (self):
        resolution = QDesktopWidget().screenGeometry()
        self.move((resolution.width() // 2) - (self.frameSize().width() // 2),
                  (resolution.height() // 2) - int(round(self.frameSize().height() / 1.67, 0)))
        
    def calculate_and_display(self):
        try:
            self.m, self.q, self.x1, self.x2, self.y1, self.y2, rsquared, vwc = gorun(
                self.source_folder, self.get_zone(), self.VWC_required, self.FOS_required, 
                self.get_slopex(), self.get_slopey(), self.get_sensorx(), self.get_sensory()
            )
        except Exception as e: # gorun() returns None if fails. 
            print("Exception occurred when calculating.")
            return 1
        
        # display results
        self.uiMain.gradientResult_label.setText(self.make_bold_blue(str(round(self.m,3))))
        self.uiMain.interceptResult_label.setText(self.make_bold_blue(str(round(self.q,3))))
        self.uiMain.r2Result_label.setText(self.make_bold_blue(str(round(rsquared,3))))
        self.uiMain.vwcResult_label.setText(self.make_bold_blue(str(round(vwc,3))))
        return 0

    def check_folder(self):
        zone = self.get_zone()

        fos_row_counts, fos_col_counts = {}, {}
        vwc_row_counts, vwc_col_counts = {}, {}

        if self.source_folder != "": 
            root_contents = os.listdir(self.source_folder)
            if f"JF{zone}" in root_contents:
                JF_contents = os.listdir(f"{self.source_folder}/JF{zone}")
                if "FOS" in JF_contents and "VWC" in JF_contents:
                    fos_contents = os.listdir(f"{self.source_folder}/JF{zone}/FOS")
                    vwc_contents = os.listdir(f"{self.source_folder}/JF{zone}/VWC")

                    # check that both folders contain the required files
                    self.FOS_required = [f'jf{zone}_gapfill_1hr.asc',f'jf{zone}_gapfill_24hr.asc',f'jf{zone}_gapfill_48hr.asc']

                    for fos in self.FOS_required:
                        if not fos in fos_contents:
                            return 1, fos
                        
                        df_first6 = read_asc_to_dataframe(f"{self.source_folder}/JF{zone}/FOS/{fos}", first_6=True)
                        nrow = int(df_first6.loc[1,1])
                        ncol = int(df_first6.loc[0,1])
                        fos_row_counts[fos] = nrow
                        fos_col_counts[fos] = ncol
                        
                    for vwc in self.VWC_required:
                        if not vwc in vwc_contents:
                            return 1, vwc
                        
                        df_first6 = read_asc_to_dataframe(f"{self.source_folder}/JF{zone}/VWC/{vwc}", first_6=True)
                        nrow = int(df_first6.loc[1,1])
                        ncol = int(df_first6.loc[0,1])
                        vwc_row_counts[vwc] = nrow
                        vwc_col_counts[vwc] = ncol

                    
                    #checking max
                    max_fos_rows = max(fos_row_counts.values())
                    max_fos_cols = max(fos_col_counts.values())
                    max_vwc_rows = max(vwc_row_counts.values())
                    max_vwc_cols = max(vwc_col_counts.values())

                    #checking not equal rows and cols for each fos and vwc files
                    fos_problems_rows = [filename for filename, count in fos_row_counts.items() if count != max_fos_rows]
                    fos_problems_col = [filename for filename, count in fos_col_counts.items() if count != max_fos_cols]
                    vwc_problems_rows = [filename for filename, count in vwc_row_counts.items() if count != max_vwc_rows]
                    vwc_problems_col = [filename for filename, count in vwc_col_counts.items() if count != max_vwc_cols]

                    if fos_problems_col or fos_problems_rows or vwc_problems_rows or vwc_problems_col:
                        return 4, ', '.join(fos_problems_rows + fos_problems_col + vwc_problems_rows + vwc_problems_col)
                    
                    if (max_fos_cols != max_vwc_cols*5) or (max_fos_rows != max_vwc_rows*5):
                        return 5, ''
                    
                    print("ALL good")
                    return 0, ''
                
                else: # if JF{zone} does not have both FOS or VWC
                    print(JF_contents)
                    return 2, ''
                
            else: # if source folder does not have JF{zone}
                return 3, f"JF{zone}"
        
    def dialog_bad_source_folder(self, code, missing=''):
        if code == 1:
            error_text = f"The following file could not be found: {missing}.\n\nPlease make sure the source folder contain relevant .asc files."
        elif code == 2:
            error_text = "'FOS' and/or 'VWC' folder(s) not found.\n\nPlease make sure your JF folder contains these folders."
        elif code == 3:
            error_text = f"The following folder could not be found: {missing}.\n\nPlease make sure the folder you choose contains the required JF folder."

        elif code == 4:
            error_text = f"There is missing data in the {missing} files"

        elif code == 5:
            error_text = f"The number of data in the fos asc file and the vwc asc file do not match multiples of 5"
        
        error_MsgBox = QMessageBox(self)
        error_MsgBox.setWindowTitle("ERROR: Missing Inputs")
        error_MsgBox.setIcon(QMessageBox.Warning)
        error_MsgBox.setText(error_text)
        error_MsgBox.setStandardButtons(QMessageBox.Ok)
        return_value = error_MsgBox.exec_()
        if return_value == QMessageBox.Ok:
            pass
        pass

    def dialog_failed_calc(self):
        error_text = f"Calculation failed when reading input data.\n\nSee console log for details." 
        error_MsgBox = QMessageBox(self)
        error_MsgBox.setWindowTitle("ERROR: Missing Inputs")
        error_MsgBox.setIcon(QMessageBox.Warning)
        error_MsgBox.setText(error_text)
        error_MsgBox.setStandardButtons(QMessageBox.Ok)
        return_value = error_MsgBox.exec_()
        if return_value == QMessageBox.Ok:
            pass
        pass

    def enable_findFromGraph(self):
        self.uiMain.inputVWC_dbSpinBox.setEnabled(True)
        self.uiMain.find_point_Button.setEnabled(True)

    def get_sensorx(self): return self.uiMain.xsensor_dbSpinbox.value()
    def get_sensory(self): return self.uiMain.ysensor_dbSpinBox.value()
    def get_slopex(self): return self.uiMain.xslope_dbSpinBox.value()
    def get_slopey(self): return self.uiMain.yslope_dbSpinBox.value()
    def get_zone(self): return self.uiMain.zoneNo_spinBox.value()

    def initialise(self):
        # disable things from Find from Graph first
        self.uiMain.inputVWC_dbSpinBox.setEnabled(False)
        self.uiMain.find_point_Button.setEnabled(False)

        # set test values cuz lazy key in 
        self.uiMain.xslope_dbSpinBox.setValue(24483)
        self.uiMain.yslope_dbSpinBox.setValue(28694)
        self.uiMain.xsensor_dbSpinbox.setValue(27060)
        self.uiMain.ysensor_dbSpinBox.setValue(29743)


    # to display aligned version of the text
    def make_align(self, text, align=None):
        if align in ['left', 'right', 'center']:
            return f"<html><head/><body><p align=\"{align}\"><span>" + text + "</span></p></body></html>"
    
    def make_bold_blue(self, text, align='center'):
        if align in ['left', 'right', 'center']:
            return f"<html><head/><body><p align=\"{align}\"><span style=\" font-weight:600; color:#0000ff;\">{text}</span></p></body></html>"

    def open_folder(self):
        source_path = QFileDialog.getExistingDirectory(self, 'Open Folder', '/home')

        if source_path == '':
            print("Load cancelled.")
            self.uiMain.sourceFolder_display.setText(self.make_align(source_path, 'right'))
            return False
        else: # if valid path chosen
            self.source_folder = source_path
            self.uiMain.sourceFolder_display.setText(self.make_align(source_path, 'right'))
            return True
        
        """
        else: # if valid path chosen
            # check if chosen folder meets requirements
            fail = self.check_folder(source_path)

            if not fail: # if meets requirements, update UI
                self.source_folder = source_path
                self.uiMain.sourceFolder_display.setText(self.make_align(source_path, 'right'))
                return True
            else:
                self.dialog_bad_source_folder(fail) # display alert dialog
                return False
        """
        