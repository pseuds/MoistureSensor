import typing
from PyQt5 import QtCore
from progress_UI import Ui_Dialog
from createSlope_UI import Ui_CreateSlope
from PyQt5.QtWidgets import QDialog, QWidget

class ProgressDialog(QDialog):
    def __init__(self, parent=None):
        super(ProgressDialog, self).__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

class CreateSlopeDialog(QDialog):
    def __init__(self, parent=None):
        super(CreateSlopeDialog, self).__init__(parent)
        self.ui = Ui_CreateSlope()
        self.ui.setupUi(self)