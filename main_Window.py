import os, math, json
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QFileDialog, QMessageBox, QListWidgetItem
from PIL import Image
from asc_reader import *
from main_UI import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.uiMain = Ui_MainWindow()
        self.uiMain.setupUi(self)
        self.resize(1000, 600)
        self.centerOnScreen()
        self.setMaximumSize(1200, 900)

        self.source_folder = ""    # root folder that the user chose to read from
        self.VWC_required = [ # all {zone} folders should have these
            'VWCL0001N0001.asc','VWCL0001N0024.asc','VWCL0001N0048.asc',
            'VWCL0002N0001.asc','VWCL0002N0024.asc','VWCL0002N0048.asc',
            'VWCL0003N0001.asc','VWCL0003N0024.asc','VWCL0003N0048.asc',
            'VWCL0004N0001.asc','VWCL0004N0024.asc','VWCL0004N0048.asc',
            'VWCL0005N0001.asc','VWCL0005N0024.asc','VWCL0005N0048.asc',
            'VWCL0006N0001.asc','VWCL0006N0024.asc','VWCL0006N0048.asc'
            ]
        
        self.zone_ls = [
            "BT1", "BT2", "BT3", "BT4", "BT5", "BT6", "BT7", "BT8", "BT9", "BT10", 
            "BT11", "BT12", "BT13", "BT14", "BT15", "BT16", "BT17", "BT18", "BT19", "BT20", 
            "BT21", "BT22", "BT23", "BT24", "BT25", "BT26", "BT27a", "BT27b", "BT28", "BT29", "BT30a", 
            "BT30b", "BT31", "BT32", "BT33", "BT34", "BT35", "BT36", "BT37" "BT38", "BT39", "BT40", 
            "BT41", "BT42", "BT43", "BT44",
                        
            "JF1", "JF2a", "JF2b", "JF3a", "JF3b", "JF4", "JF5", "JF6a", "JF6b", "JF7", "JF8", "JF9", "JF10",
            "JF11", "JF12", "JF13", "JF14", "JF15", "JF16", "JF17", "JF18", "JF19", "JF20", 
            "JF21", "JF22", "JF23",

            "KF1", "KF2", "KF3", "KF4", "KF5", "KF6", "KF7", "KF8", "KF9a", "KF9b",
            
            "OA1", "OA2", "OA3a", "OA3b", "OA4", "OA5", "OA6", "OA7", "OA8", "OA9", "OA10", 
            "OA11", "OA12", "OA13", "OA14a", "OA14b", "OA15", "OA16", "OA17", "OA18", "OA19a", "OA19b", "OA20", 
            "OA21"
            ]

        self.savelocation = "" # dir where the slope data is saved.
        self.sensors_ls = []
    
        # dialogs
        self.progress_bar = None
        self.create_dialog = None

        # modes
        self.editSlopeName_mode = False
        
        self.initialise()


    def centerOnScreen (self):
        resolution = QDesktopWidget().screenGeometry()
        self.move((resolution.width() // 2) - (self.frameSize().width() // 2),
                  (resolution.height() // 2) - int(round(self.frameSize().height() / 1.67, 0)))

    def check_folder(self):
        zone = self.get_zone()
        print("Zone selected", zone)

        fos_row_counts, fos_col_counts = {}, {}
        vwc_row_counts, vwc_col_counts = {}, {}
        
        if self.source_folder != "": 
            root_contents = os.listdir(self.source_folder)
            if zone in root_contents:
                JF_contents = os.listdir(f"{self.source_folder}/{zone}")
                if "FOS" in JF_contents and "VWC" in JF_contents:
                    fos_contents = os.listdir(f"{self.source_folder}/{zone}/FOS")
                    vwc_contents = os.listdir(f"{self.source_folder}/{zone}/VWC")

                    # check that both folders contain the required files
                    lower = zone.lower()
                    self.FOS_required = [f'{lower}_gapfill_1hr.asc',f'{lower}_gapfill_24hr.asc',f'{lower}_gapfill_48hr.asc']

                    for fos in self.FOS_required:
                        if not fos in fos_contents:
                            return 1, fos
                        
                        #change reading part if first 6 rows info are not avaliable
                        # df = pd.read_csv(f"{self.source_folder}/{zone}/FOS/{fos}", delimiter=' ', header=None)
                        # nrow = int(df.loc[1,1])
                        # ncol = int(df.loc[0,1])

                        df_first6 = read_asc_to_dataframe(f"{self.source_folder}/{zone}/FOS/{fos}", first_6=True)
                        nrow = int(df_first6.loc[1,1])
                        ncol = int(df_first6.loc[0,1])
                        if fos == f'{lower}_gapfill_24hr.asc':
                            xslope = float(df_first6.loc[2,1])
                            yslope = float(df_first6.loc[3,1])

                        fos_row_counts[fos] = nrow
                        fos_col_counts[fos] = ncol
                        
                    for vwc in self.VWC_required:
                        if not vwc in vwc_contents:
                            return 1, vwc
                        
                        #change reading part if first 6 rows info are not avaliable
                        # df = pd.read_csv(f"{self.source_folder}/{zone}/VWC/{vwc}", delimiter=' ', hseader=None)
                        # nrow = int(df.loc[1,1])
                        # ncol = int(df.loc[0,1])

                        df_first6 = read_asc_to_dataframe(f"{self.source_folder}/{zone}/VWC/{vwc}", first_6=True)
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

                    self.uiMain.xslope_dbSpinBox.setValue(xslope)
                    self.uiMain.yslope_dbSpinBox.setValue(yslope)
                    return 0, ''
                
                else: # if {zone} does not have both FOS or VWC
                    return 2, ''
                
            else: # if source folder does not have zone
                return 3, f"{zone}"
            
        else: # user did not select source folder
            return 6, ''

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
            error_text = f"The number of data in the FOS asc file and the VWC asc file do not match multiples of 5"
        elif code == 6:
            error_text = f"No source folder selected.\n\nPlease select a folder containing relevant data inputs."
        
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
    
    def enable_sensorInputs(self, bool):
        self.uiMain.zone_comboBox.setEnabled(bool)
        self.uiMain.sensorName_lineEdit.setEnabled(bool)
        self.uiMain.xsensor_dbSpinbox.setEnabled(bool)
        self.uiMain.ysensor_dbSpinBox.setEnabled(bool)
        self.uiMain.openFolder_Button.setEnabled(bool)
        self.uiMain.calculate_Button.setEnabled(bool)
        self.uiMain.saveSensor_Button.setEnabled(bool)
        self.uiMain.deleteSensor_Button.setEnabled(bool)

    def get_sensorx(self): return self.uiMain.xsensor_dbSpinbox.value()
    def get_sensory(self): return self.uiMain.ysensor_dbSpinBox.value()
    def get_slopex(self): return self.uiMain.xslope_dbSpinBox.value()
    def get_slopey(self): return self.uiMain.yslope_dbSpinBox.value()
    def get_zone(self): return self.uiMain.zone_comboBox.currentText()

    def get_slope_name(self): return self.uiMain.slopeName_lineEdit.text()

    def initialise(self):
        # clear items
        self.uiMain.sensors_listWidget.clear()

        # disable things from Find from Graph first
        self.uiMain.inputVWC_dbSpinBox.setEnabled(False)
        self.uiMain.find_point_Button.setEnabled(False)

        # set test values cuz lazy key in 
        # self.uiMain.xslope_dbSpinBox.setValue(24483)
        # self.uiMain.yslope_dbSpinBox.setValue(28694)
        self.uiMain.xslope_dbSpinBox.setEnabled(False)
        self.uiMain.yslope_dbSpinBox.setEnabled(False)
        self.uiMain.xsensor_dbSpinbox.setValue(27060)
        self.uiMain.ysensor_dbSpinBox.setValue(29743)
        self.uiMain.zone_comboBox.addItems(self.zone_ls)

        # cannot do anything until slope is created/loaded
        self.set_editSlopeNameMode(False)
        self.enable_sensorInputs(False)

        # signals
        self.uiMain.sensors_listWidget.currentItemChanged.connect(self.select_sensor)
    
    def delete_sensor(self):
        if self.savelocation != "":
            item = self.uiMain.sensors_listWidget.currentItem()

            try:
                # Opening JSON file
                f = open(self.savelocation)
                # returns JSON object as dict
                data = json.load(f)
                sensors_dict = data['sensors']
                sensors_dict.pop(item.text())
                data['sensors'] = sensors_dict
                f.close()
                with open(self.savelocation, "w") as outfile: 
                    json.dump(data, outfile)

            except Exception as e: # problem with JSON file.
                print("Exception occurred when deleting sensor:", e)
                self.uiMain.statusbar.showMessage("Error when deleting sensor.")
                return

            # delete from listwidget
            self.uiMain.sensors_listWidget.takeItem(self.uiMain.sensors_listWidget.row(item))
            

    def display_results(self, values):
        try:
            [self.m, self.q, self.x1, self.x2, self.y1, self.y2, rsquared, vwc] = [v for v in values]
        except Exception as e: # values is None if fails
            print("Exception occurred when calculating:", e)
            self.uiMain.statusbar.showMessage("Calculation failed. See console log for details.")
            self.dialog_failed_calc()

        # display results
        self.uiMain.gradientResult_label.setText(self.make_bold_blue(str(round(self.m,3))))
        self.uiMain.interceptResult_label.setText(self.make_bold_blue(str(round(self.q,3))))
        self.uiMain.r2Result_label.setText(self.make_bold_blue(str(round(rsquared,3))))
        self.uiMain.vwcResult_label.setText(self.make_bold_blue(str(round(vwc,3))))
        self.uiMain.statusbar.showMessage("Calculation success.")
        self.uiMain.graphResult_label.setPixmap(QPixmap("assets/Z_plot.png").scaled(1200, 500, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        self.enable_findFromGraph()

    def load_slope(self):
        dir = self.savelocation if self.savelocation != "" else "/home"
        try:
            slope_path, file_type = QFileDialog.getOpenFileName(self, 'Open File', dir, 'JSON Files (*.json)')
        except:
            slope_path, file_type = QFileDialog.getOpenFileName(self, 'Open File', "/home", 'JSON Files (*.json)')

        if slope_path == '':
            print("Load cancelled.")
            return 1
        
        else: # if valid path chosen
            try:
                self.savelocation = slope_path

                # get slope name
                f = open(self.savelocation)
                data = json.load(f)
                saved_name = data['slope_name']
                f.close()

                self.uiMain.slopeName_lineEdit.setText(saved_name)
                self.uiMain.sensors_listWidget.clear()
                self.set_sensorList()
                self.enable_sensorInputs(True)
                self.set_editSlopeNameMode(False)
                return 0
            except:
                return 2
        
    # to display aligned version of the text
    def make_align(self, text, align=None):
        if align in ['left', 'right', 'center']:
            return f"<html><head/><body><p align=\"{align}\"><span>" + text + "</span></p></body></html>"
    
    def make_bold_blue(self, text, align='center'):
        if align in ['left', 'right', 'center']:
            return f"<html><head/><body><p align=\"{align}\"><span style=\" font-weight:600; color:#0000ff;\">{text}</span></p></body></html>"

    def make_bold_red(self, text, align='center'):
        if align in ['left', 'right', 'center']:
            return f"<html><head/><body><p align=\"{align}\"><span style=\" font-weight:600; color:#ff0000;\">{text}</span></p></body></html>"

    def open_folder(self):
        dir = self.source_folder if self.source_folder != "" else "/home"
        try:
            source_path = QFileDialog.getExistingDirectory(self, 'Open Folder', dir)
        except:
            source_path = QFileDialog.getExistingDirectory(self, 'Open Folder', '/home')

        if source_path == '':
            print("Load cancelled.")
            self.uiMain.sourceFolder_display.setText(self.make_align(source_path, 'right'))
            return False
        else: # if valid path chosen
            self.source_folder = source_path
            self.uiMain.sourceFolder_display.setText(self.make_align(source_path, 'right'))
            return True
    
    def report_final_progress(self, code):
        if code != 0:
            if code >= 1 and code < 19:
                bad_file = self.VWC_required[code-1]
            elif code >= 19 and code < 22:
                bad_file = self.FOS_required[code-19]
            # error_text = f"Calculation failed when reading {bad_file}." 
            error_text = "Zone and Coordinates of Slope do not match."
            error_MsgBox = QMessageBox(self)
            error_MsgBox.setWindowTitle("ERROR: Input File Error")
            error_MsgBox.setIcon(QMessageBox.Warning)
            error_MsgBox.setText(error_text)
            error_MsgBox.setStandardButtons(QMessageBox.Ok)
            return_value = error_MsgBox.exec_()
            if return_value == QMessageBox.Ok:
                pass
        else:
            self.uiMain.statusbar.showMessage("Calculation success.")

    def report_progress(self, count):
        if count >= 1 and count < 19:
            self.progress_bar.ui.progressBar.setValue(int(math.ceil(count/self.total_count * 100)))
            self.progress_bar.ui.progress_label.setText(f"Reading from {self.VWC_required[count-1]}...")
        elif count >= 19 and count < 22:
            self.progress_bar.ui.progressBar.setValue(int(math.ceil(count/self.total_count * 100)))
            self.progress_bar.ui.progress_label.setText(f"Reading from {self.FOS_required[count-19]}...")
        elif count == 22:
            self.progress_bar.ui.progressBar.setValue(int(math.ceil(count/self.total_count * 100)))
            self.progress_bar.ui.progress_label.setText(f"Calculating and plotting graph...")

    def save_sensor(self, values):
        if len(values) == 8 and self.savelocation != "":

            [self.m, self.q, self.x1, self.x2, self.y1, self.y2, rsquared, vwc] = [v for v in values]

            # Opening JSON file
            f = open(self.savelocation)

            # returns JSON object as dict
            data = json.load(f)
            sensors_dict = data['sensors']

            sensors_dict[self.uiMain.sensorName_lineEdit.text()] = {
                "coordinates": (self.get_sensorx(), self.get_sensory()),
                "m": self.m,
                "c": self.q,
                "zone": self.get_zone()
            }

            data['sensors'] = sensors_dict

            f.close()

             # Convert and write JSON object to file
            with open(self.savelocation, "w") as outfile: 
                json.dump(data, outfile)    
            
            # if new sensor name not in list, add to listwidget
            if not self.uiMain.sensorName_lineEdit.text() in [item.text() for item in [self.uiMain.sensors_listWidget.item(idx) for idx in range(self.uiMain.sensors_listWidget.count())]]:
                new_item = QListWidgetItem(self.uiMain.sensorName_lineEdit.text())
                self.uiMain.sensors_listWidget.addItem(new_item)
                self.uiMain.sensors_listWidget.sortItems()
                self.uiMain.sensors_listWidget.setCurrentItem(new_item)
            else:
                for item in [self.uiMain.sensors_listWidget.item(idx) for idx in range(self.uiMain.sensors_listWidget.count())]:
                    if item.text() == self.uiMain.sensorName_lineEdit.text():
                        self.uiMain.sensors_listWidget.setCurrentItem(item)
            
            self.uiMain.r2Result_label.setText(self.make_bold_blue(round(rsquared, 3)))
            self.uiMain.vwcResult_label.setText(self.make_bold_blue(round(vwc, 3)))
    
    def select_sensor(self):
        if self.savelocation != "" and self.uiMain.sensors_listWidget.currentItem() != None:
            selected_name = self.uiMain.sensors_listWidget.currentItem().text()

            # get sensor data
            f = open(self.savelocation)
            data = json.load(f)
            sensors_dict = data['sensors']
            f.close()

            data = sensors_dict[selected_name]

            try:
                # update UI with sensor data
                self.uiMain.sensorName_lineEdit.setText(selected_name)
                self.uiMain.zone_comboBox.setCurrentText(data['zone'])
                self.uiMain.xslope_dbSpinBox.setValue(0.00)
                self.uiMain.yslope_dbSpinBox.setValue(0.00)
                self.uiMain.xsensor_dbSpinbox.setValue(data['coordinates'][0])
                self.uiMain.ysensor_dbSpinBox.setValue(data['coordinates'][1])
                self.uiMain.gradientResult_label.setText(self.make_bold_blue(str(round(data['m'],3))))
                self.uiMain.interceptResult_label.setText(self.make_bold_blue(str(round(data['c'],3))))
                self.uiMain.r2Result_label.setText(self.make_bold_blue("-"))
                self.uiMain.vwcResult_label.setText(self.make_bold_blue("-"))
            except:
                print("ERROR: Retrieving selected sensor data failed.")
                self.uiMain.statusbar.showMessage("Error in retrieving selected sensor data.")

    def set_editSlopeNameMode(self, bool):
        self.editSlopeName_mode = bool
        icon = QtGui.QIcon()
        if bool:
            # change icon to tick
            icon.addPixmap(QtGui.QPixmap(".\\assets/tick.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        else:
            # change icon to edit
            icon.addPixmap(QtGui.QPixmap(".\\assets/edit.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.uiMain.slopeName_lineEdit.setEnabled(bool)
        self.uiMain.editSlopeName_Button.setIcon(icon)

        # for init
        if self.savelocation == "":
            self.uiMain.editSlopeName_Button.setEnabled(False)
        else:
            self.uiMain.editSlopeName_Button.setEnabled(True)

    def set_sensorList(self):
        # Opening JSON file
        if self.savelocation != "":
            f = open(self.savelocation)

            # returns JSON object as dict
            data = json.load(f)
            sensors_dict = data['sensors']
            f.close()

            sensor_names = sensors_dict.keys()
            self.uiMain.sensors_listWidget.addItems(sensor_names)

        
    def start_progress_dialog(self):
        if self.progress_bar != None:
            self.progress_bar.ui.progressBar.setValue(0)
            self.progress_bar.show()

    def update_slope_name(self):
        if self.savelocation != "":
            # Opening JSON file
            f = open(self.savelocation)

            # returns JSON object as dict
            data = json.load(f)
            saved_name = data['slope_name']

            if self.get_slope_name() != saved_name:
                data['slope_name'] = self.get_slope_name()

            f.close()

             # Convert and write JSON object to file
            with open(self.savelocation, "w") as outfile: 
                json.dump(data, outfile)            