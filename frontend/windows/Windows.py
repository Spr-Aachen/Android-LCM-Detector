import os
from pathlib import Path
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QMainWindow

from windows.ui.UI_Window import *

##############################################################################################################################

class Window_MainWindow(QMainWindow):
    ui = Ui_MainWindow()

    def __init__(self, parent = None):
        super().__init__(parent)

        self.ui.setupUi(self)

##############################################################################################################################

class ImageWindow(QWidget):
    def __init__(self, image_paths: dict):
        super().__init__()

        self.image_paths = image_paths

        self.current_index = 0

    def initUI(self):
        self.label = QLabel()
        self.lbl_path = QLabel()

        self.prev_button = QPushButton()
        self.next_button = QPushButton()

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.prev_button)
        button_layout.addWidget(self.next_button)

        vlayout = QVBoxLayout()
        vlayout.addWidget(self.label)
        vlayout.addWidget(self.lbl_path)
        vlayout.addLayout(button_layout)

        container = QWidget(self)
        container.setLayout(vlayout)

    def update_image(self):
        pixmap = QPixmap(self.image_paths[self.current_index])
        self.label.setPixmap(pixmap)
        self.label.setScaledContents(True)
        self.lbl_path.setText(str(self.current_index+1)+'/'+str(len(self.image_paths))+' '+ self.image_paths[self.current_index])

    def show_prev_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_image()

    def show_next_image(self):
        if self.current_index < len(self.image_paths) - 1:
            self.current_index += 1
            self.update_image()

    def show(self):
        self.initUI()

        self.setWindowTitle("Image Viewer")

        self.prev_button.setText("<")
        self.prev_button.clicked.connect(self.show_prev_image)

        self.next_button.setText(">")
        self.next_button.clicked.connect(self.show_next_image)

        self.update_image()

        super().show()

##############################################################################################################################