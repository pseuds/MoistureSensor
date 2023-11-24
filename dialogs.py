import typing
from PyQt5 import QtCore
from progress_UI import Ui_Dialog
from createSlope_UI import Ui_CreateSlope_Dialog
from PyQt5.QtWidgets import QDialog, QMessageBox

class ProgressDialog(QDialog):
    def __init__(self, parent=None):
        super(ProgressDialog, self).__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

class CreateSlopeDialog(QDialog):
    def __init__(self, parent=None):
        super(CreateSlopeDialog, self).__init__(parent)
        self.ui = Ui_CreateSlope_Dialog()
        self.ui.setupUi(self)

        # remove what's this button
        self.setWindowFlags(self.windowFlags()
                    ^ QtCore.Qt.WindowContextHelpButtonHint)
    
    def dialog_empty(self):
        error_text = f"Empty field(s).\n\nPlease enter slope name and select save directory." 
        error_MsgBox = QMessageBox(self)
        error_MsgBox.setWindowTitle("ERROR: Missing Inputs")
        error_MsgBox.setIcon(QMessageBox.Warning)
        error_MsgBox.setText(error_text)
        error_MsgBox.setStandardButtons(QMessageBox.Ok)
        return_value = error_MsgBox.exec_()
        if return_value == QMessageBox.Ok:
            pass
        pass

    def get_dir(self): return self.ui.dir_label.text()
    def get_slope_name(self): return self.ui.slopeName_lineEdit.text()