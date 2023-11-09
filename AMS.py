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

        self.show()

    #------------ BUTTON CLICKS ------------ #

    def calculateButton_clicked(self):

        gorun()
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


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    ams = AMS(main_window)
    sys.exit(app.exec_())