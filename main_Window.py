import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QFileDialog, QMessageBox, QTableWidgetItem
from PIL import Image
from main_UI import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.uiMain = Ui_MainWindow()
        self.uiMain.setupUi(self)
        self.resize(1400, 800)
        self.centerOnScreen()
        self.setMaximumSize(1600, 800)

        self.initialise()

        self.source_folder = ""    # root folder that the user chose to read from

    def centerOnScreen (self):
        resolution = QDesktopWidget().screenGeometry()
        self.move((resolution.width() // 2) - (self.frameSize().width() // 2),
                  (resolution.height() // 2) - int(round(self.frameSize().height() / 1.67, 0)))

    def check_folder(self, folder_path):
        if folder_path != "": 
            root_contents = os.listdir(folder_path)
            if "fos" in root_contents and "vwc" in root_contents:
                fos_contents = os.listdir(f"{folder_path}/fos")
                vwc_contents = os.listdir(f"{folder_path}/vwc")
                
                # check that both folders are not empty
                if len(fos_contents) == 0 or len(vwc_contents) == 0:
                    return 1

                # check that both folders contain only .asc files
                for fos in fos_contents:
                    if not fos.endswith(".asc"):
                        return 2
                    
                for vwc in vwc_contents:
                    if not vwc.endswith(".asc"):
                        return 2
                    
                return 0
            else:
                return 3
        
    def dialog_bad_source_folder(self, code):
        if code == 1:
            error_text = "Empty 'fos' and/or 'vwc' folder(s).\n\nPlease make sure they contain relevant .asc files."
        elif code == 2:
            error_text = "Invalid file format in 'fos' or 'vwc' folder.\n\nPlease make sure they only contain relevant .asc files."
        elif code == 3:
            error_text = "'fos' or 'vwc' folder not found.\n\nPlease make sure the folder you choose contains both 'fos' and 'vwc' folders."
        error_MsgBox = QMessageBox(self)
        error_MsgBox.setWindowTitle("ERROR: Missing Paths")
        error_MsgBox.setIcon(QMessageBox.Warning)
        error_MsgBox.setText(error_text)
        error_MsgBox.setStandardButtons(QMessageBox.Ok)
        return_value = error_MsgBox.exec_()
        if return_value == QMessageBox.Ok:
            pass
        pass

    def initialise(self):
        pass

    # to display aligned version of the text
    def make_align(self, text, align=None):
        if align in ['left', 'right', 'center']:
            return f"<html><head/><body><p align=\"{align}\"><span>" + text + "</span></p></body></html>"

    def open_folder(self):
        source_path = QFileDialog.getExistingDirectory(self, 'Open Folder', '/home')

        if source_path == '':
            print("Load cancelled.")
            self.uiMain.sourceFolder_display.setText(self.make_align(source_path, 'right'))
            return False
        
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
        