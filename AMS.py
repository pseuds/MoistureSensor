import sys, math
from main_Window import MainWindow
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from read_asc import *
from PyQt5.QtGui import QPixmap

#TODO Got some unknown property align whenever running the gui

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

        #get inputs:
        zone = self.uiMain.zoneNo_spinBox.value()
        slopex = self.uiMain.xslope_dbSpinBox.value()
        slopey = self.uiMain.yslope_dbSpinBox.value()
        sensorx = self.uiMain.xsensor_dbSpinbox.value()
        sensory = self.uiMain.ysensor_dbSpinBox.value()
        
        # Running
        self.m, self.q , self.x1, self.x2, self.y1, self.y2, rsquared, vwc = gorun(slopex, slopey, sensorx, sensory)


        # Outputs
        self.uiMain.gradientResult_label.setText(str(self.m))
        self.uiMain.interceptResult_label.setText(str(self.q))
        self.uiMain.r2Result_label.setText(str(rsquared))
        self.uiMain.vwcResult_label.setText(str(vwc))
        

        
        #TODO Make picture size better idk help plsssssss
        self.uiMain.graphResult_label.setPixmap(QPixmap("Z_plot.png").scaled(1200, 375, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

        pass

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

        self.uiMain.fosResult_label.setText(str(y_value))

        pass


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    ams = AMS(main_window)
    sys.exit(app.exec_())