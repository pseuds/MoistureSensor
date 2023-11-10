import sys, math
from main_Window import MainWindow
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from read_asc import *
from PyQt5.QtGui import QPixmap

#TODO Got some unknown property align whenever running the gui
# ignoring it until theres visible error in the GUI.

class AMS(MainWindow):
    def __init__(self, parent):
        super(AMS, self).__init__(parent)

        # connect buttons
        self.uiMain.calculate_Button.clicked.connect(self.calculateButton_clicked)
        self.uiMain.openFolder_Button.clicked.connect(self.openFolderButton_clicked)
        self.uiMain.find_point_Button.clicked.connect(self.findFOSButton_clicked)

        self.show()

    #------------ BUTTON CLICKS ------------ #

    def calculateButton_clicked(self):
        self.uiMain.calculate_Button.setEnabled(False) # disable button to prevent spamming
        self.uiMain.find_point_Button.setEnabled(False)
        self.uiMain.statusbar.showMessage("Calculating...")

        # Check if source folder has required data
        fail, missing_file = self.check_folder()

        if not fail:

            fail_calc = self.calculate_and_display()
            
            if fail_calc:
                self.uiMain.statusbar.showMessage("Calculation failed. See console log for details.")
                self.dialog_failed_calc()

            else: # calculation is successful
                self.uiMain.statusbar.showMessage("Calculation success.")
                self.uiMain.graphResult_label.setPixmap(QPixmap("assets/Z_plot.png").scaled(1200, 400, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
                self.enable_findFromGraph()

        else: # cannot calculate due to missing data. show relevant error popup.
            self.uiMain.statusbar.showMessage("Calculation failed. Missing input data.")
            self.dialog_bad_source_folder(fail, missing_file)

        self.uiMain.calculate_Button.setEnabled(True) # reenable button when done
        self.uiMain.find_point_Button.setEnabled(True) 

    def openFolderButton_clicked(self):
        success = self.open_folder()

        if success: 
            self.uiMain.statusbar.showMessage("Open folder success.")
            # TODO: check if required files exist
        else:
            self.uiMain.statusbar.showMessage("Open folder failed/cancelled.")

    def findFOSButton_clicked(self):
        #Laze change name fa
        print(self.x1, self.x2, self.y1, self.y2)
        x_value = self.uiMain.inputVWC_dbSpinBox.value()
        if x_value <= self.x1:
            y_value = self.y1
        elif x_value >= 0.5:
            y_value = self.y2
        else:
            y_value = self.m * x_value + self.q

        self.uiMain.fosResult_label.setText(self.make_bold_blue(str(round(y_value,3))))

        pass


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    ams = AMS(main_window)
    sys.exit(app.exec_())