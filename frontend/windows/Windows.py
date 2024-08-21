import os
from pathlib import Path
from PySide6.QtWidgets import QMainWindow

from windows.ui.UI_Window import *

##############################################################################################################################

class Window_MainWindow(QMainWindow):
    ui = Ui_MainWindow()

    def __init__(self, parent = None):
        super().__init__(parent)

        self.ui.setupUi(self)

##############################################################################################################################