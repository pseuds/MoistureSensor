import sys, math
from main_Window import MainWindow
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from asc_reader import Calculator
from progress_dialog import ProgressDialog
from PyQt5.QtGui import QPixmap

#TODO Got some unknown property align whenever running the gui
# ignoring it until theres visible error in the GUI.

class AMS(MainWindow):
    def __init__(self, parent):
        super(AMS, self).__init__(parent)

        # connect buttons
        # self.uiMain.calculate_Button.clicked.connect(self.calculateButton_clicked)
        self.uiMain.calculate_Button.clicked.connect(self.calculateButton_clicked)
        self.uiMain.openFolder_Button.clicked.connect(self.openFolderButton_clicked)
        self.uiMain.find_point_Button.clicked.connect(self.findFOSButton_clicked)

        self.show()

    #------------ BUTTON CLICKS ------------ #

    def calculateButton_clicked(self):
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
        
        else: # cannot calculate due to missing data. show relevant error popup.
            self.uiMain.statusbar.showMessage("Calculation failed. Missing input data.")
            self.dialog_bad_source_folder(fail, missing_file)

    def openFolderButton_clicked(self):
        success = self.open_folder()

        if success: 
            self.uiMain.statusbar.showMessage("Open folder success.")
            # TODO: check if required files exist
        else:
            self.uiMain.statusbar.showMessage("Open folder failed/cancelled.")

    def findFOSButton_clicked(self):
        
        print(self.x1, self.x2, self.y1, self.y2)
        x_value = self.uiMain.inputVWC_dbSpinBox.value()
        if x_value <= self.x1:
            y_value = self.y1
        elif x_value >= 0.5:
            y_value = self.y2
        else:
            y_value = self.m * x_value + self.q

        alert_level = self.uiMain.alert_level_dbSpinBox.value()
        if y_value > alert_level:
            self.uiMain.fosResult_label.setText(self.make_bold_blue(str(round(y_value,3))))
        else:
            self.uiMain.fosResult_label.setText(self.make_bold_red(str(round(y_value,3))))
        pass


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    ams = AMS(main_window)
    sys.exit(app.exec_())