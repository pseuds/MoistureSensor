import sys, json
from main_Window import MainWindow
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from asc_reader import Calculator
from dialogs import ProgressDialog, CreateSlopeDialog

#TODO Got some unknown property align whenever running the gui
# ignoring it until theres visible error in the GUI.

class AMS(MainWindow):
    def __init__(self, parent):
        super(AMS, self).__init__(parent)

        # connect buttons
        self.uiMain.calculate_Button.clicked.connect(self.calculateButton_clicked)
        self.uiMain.openFolder_Button.clicked.connect(self.openFolderButton_clicked)
        self.uiMain.find_point_Button.clicked.connect(self.findFOSButton_clicked)

        # NEW
        self.uiMain.createSlope_Button.clicked.connect(self.createSlopeButton_clicked)
        self.uiMain.deleteSensor_Button.clicked.connect(self.deleteSensorButton_clicked)
        self.uiMain.loadSlope_Button.clicked.connect(self.loadSlopeButton_clicked)
        self.uiMain.saveSensor_Button.clicked.connect(self.saveSensorButton_clicked)
        self.uiMain.editSlopeName_Button.clicked.connect(self.editSlopeNameButton_clicked)

        self.show()



    #------------ BUTTON CLICKS ------------ #

    def calculateButton_clicked(self, save=False):
        # Check if source folder has required data
        fail, missing_file = self.check_folder()

        if not fail:
            self.thread = QThread()
            self.worker = Calculator(
                self.source_folder, self.get_zone(), self.VWC_required, self.FOS_required, 
                self.get_slopex(), self.get_slopey(), self.get_sensorx(), self.get_sensory()
            )
            self.worker.moveToThread(self.thread)

            self.total_count = len(self.VWC_required) + len(self.FOS_required) + 2
            self.progress_bar = ProgressDialog(self)
            self.progress_bar.ui.progress_label.setText("Initialising...")

            # connect signals
            self.thread.started.connect(self.start_progress_dialog)
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.worker.progress.connect(self.report_progress)
            
            # start thread
            self.uiMain.calculate_Button.setEnabled(False)
            self.uiMain.find_point_Button.setEnabled(False)
            self.thread.start()

            # when complete
            self.worker.finished.connect(self.report_final_progress)
            self.worker.result_values.connect(self.display_results)
            self.thread.finished.connect(lambda: self.uiMain.calculate_Button.setEnabled(True))
            self.thread.finished.connect(lambda: self.uiMain.find_point_Button.setEnabled(True))
            self.thread.finished.connect(self.progress_bar.accept)
            if save:
                self.worker.result_values.connect(self.save_sensor)
            return 0
        
        else: # cannot calculate due to missing data. show relevant error popup.
            self.uiMain.statusbar.showMessage("Calculation failed. Missing input data.")
            self.dialog_bad_source_folder(fail, missing_file)
            return 1

    def createSlopeButton_clicked(self):
        # create slope dialog
        self.create_dialog = CreateSlopeDialog(self)
        self.create_dialog.ui.chooseDir_Button.clicked.connect(self.choose_create_dir)
        self.create_dialog.ui.create_Button.clicked.connect(self.create_slope) 
        self.create_dialog.show()

    def deleteSensorButton_clicked(self):
        # dialog to confirm delete
        response = QMessageBox.question(self, "Confirm Sensor Deletion", 
                                        f"The sensor {self.uiMain.sensors_listWidget.currentItem().text()} will be deleted.\n\nAre you sure?",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if response == QMessageBox.Yes: 
            self.delete_sensor()
        else: 
            return

    def editSlopeNameButton_clicked(self):        
        if not self.editSlopeName_mode and self.savelocation != "": # if off, let user type new name
            self.set_editSlopeNameMode(True)

        else: # if on, save new name if not empty 
            # if not empty, update in json
            if self.get_slope_name() != "" or not self.get_slope_name().isspace():
                self.update_slope_name()
                self.set_editSlopeNameMode(False)
            else: # if empty, show error
                error_text = f"Empty slope name.\n\nPlease enter a slope name." 
                error_MsgBox = QMessageBox(self)
                error_MsgBox.setWindowTitle("ERROR: Empty Slope Name")
                error_MsgBox.setIcon(QMessageBox.Warning)
                error_MsgBox.setText(error_text)
                error_MsgBox.setStandardButtons(QMessageBox.Ok)
                return_value = error_MsgBox.exec_()
                if return_value == QMessageBox.Ok:
                    pass
                pass


    def findFOSButton_clicked(self):
        
        print(self.x1, self.x2, self.y1, self.y2)
        x_value = self.uiMain.inputVWC_dbSpinBox.value()
        if x_value <= self.x1:
            y_value = self.y1
        elif x_value >= self.x2:
            y_value = self.y2
        else:
            y_value = self.m * x_value + self.q

        alert_level = self.uiMain.alert_level_dbSpinBox.value()
        if y_value > alert_level:
            self.uiMain.fosResult_label.setText(self.make_bold_blue(str(round(y_value,3))))
        else:
            self.uiMain.fosResult_label.setText(self.make_bold_red(str(round(y_value,3))))
        pass

    def loadSlopeButton_clicked(self):
        fail = self.load_slope()

        if not fail: 
            self.uiMain.statusbar.showMessage("Load slope success.")
        elif fail == 1:
            self.uiMain.statusbar.showMessage("Load slope cancelled.")
        elif fail == 2:
            self.uiMain.statusbar.showMessage("Load slope failed.")
            error_text = f"Error when reading .json file.\n\nPlease make sure the file is valid." 
            error_MsgBox = QMessageBox(self)
            error_MsgBox.setWindowTitle("ERROR: Invalid Slope File")
            error_MsgBox.setIcon(QMessageBox.Warning)
            error_MsgBox.setText(error_text)
            error_MsgBox.setStandardButtons(QMessageBox.Ok)
            return_value = error_MsgBox.exec_()
            if return_value == QMessageBox.Ok:
                pass
            pass

    def openFolderButton_clicked(self):
        success = self.open_folder()

        if success: 
            self.uiMain.statusbar.showMessage("Open folder success.")
            # TODO: check if required files exist
        else:
            self.uiMain.statusbar.showMessage("Open folder failed/cancelled.")

    def saveSensorButton_clicked(self):
        print("self.uiMain.sensorName_lineEdit.text()")
        print(self.uiMain.sensorName_lineEdit.text())
        print(self.uiMain.sensorName_lineEdit.text() != "")
        print(self.uiMain.sensorName_lineEdit.text().isspace())
        if self.uiMain.sensorName_lineEdit.text() != "" and not self.uiMain.sensorName_lineEdit.text().isspace():
            fail = self.calculateButton_clicked(save=True)
            print(fail, ', calculate button funct done.')
            if not fail:
                pass
            else: 
                error_text = f"Calculation failed.\n\nCould not save sensor." 
                error_MsgBox = QMessageBox(self)
                error_MsgBox.setWindowTitle("ERROR: Save Sensor Failed")
                error_MsgBox.setIcon(QMessageBox.Warning)
                error_MsgBox.setText(error_text)
                error_MsgBox.setStandardButtons(QMessageBox.Ok)
                return_value = error_MsgBox.exec_()
                if return_value == QMessageBox.Ok:
                    pass
                pass
        else: 
            error_text = f"Empty sensor name.\n\nPlease enter a sensor name." 
            error_MsgBox = QMessageBox(self)
            error_MsgBox.setWindowTitle("ERROR: Empty Sensor Name")
            error_MsgBox.setIcon(QMessageBox.Warning)
            error_MsgBox.setText(error_text)
            error_MsgBox.setStandardButtons(QMessageBox.Ok)
            return_value = error_MsgBox.exec_()
            if return_value == QMessageBox.Ok:
                pass
            pass



    #------------ FUNCTIONS ------------ #

    def choose_create_dir(self):
        # choose dir to save slope data (.json)
        file_name = self.create_dialog.get_slope_name()
        self.savelocation, save_type = QFileDialog.getSaveFileName(self, 'Save File', f'/home/{file_name}.json', 'JSON (*.json)')
        self.create_dialog.ui.dir_label.setText(self.savelocation)

    def create_slope(self):
        # check for valid inputs
        if self.create_dialog.get_dir() != "" and self.create_dialog.get_slope_name() != "":
            # create if valid
            self.savelocation = self.create_dialog.get_dir()
            try:
                # Define dictionary
                slope_details = { 
                    "slope_name": self.create_dialog.get_slope_name(), 
                    "sensors": {}, # dict where key is sensor name, value is dict of sensor details
                } 
                    
                # Convert and write JSON object to file
                with open(self.savelocation, "w") as outfile: 
                    json.dump(slope_details, outfile)

            except:
                print("Saving slope failed.")

            # show new slope name on UI and close dialog
            self.uiMain.slopeName_lineEdit.setText(self.create_dialog.get_slope_name())
            self.enable_sensorInputs(True)
            self.set_editSlopeNameMode(False)
            self.uiMain.sensors_listWidget.clear()
            self.create_dialog.accept()

        else:
            self.create_dialog.dialog_empty()



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    ams = AMS(main_window)
    sys.exit(app.exec_())