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
        self.current_indices = {key: 0 for key in image_paths.keys()}

        self.initUI()

    def initUI(self):
        self.tab_widget = QTabWidget()

        for name, paths in self.image_paths.items():
            tab = QWidget()
            tab_layout = QVBoxLayout()

            label = QLabel()
            lbl_path = QLabel()

            prev_button = QPushButton("<")
            next_button = QPushButton(">")

            button_layout = QHBoxLayout()
            button_layout.addWidget(prev_button)
            button_layout.addWidget(next_button)

            tab_layout.addWidget(label)
            tab_layout.addWidget(lbl_path)
            tab_layout.addLayout(button_layout)

            tab.setLayout(tab_layout)
            
            self.tab_widget.addTab(tab, name)

            prev_button.clicked.connect(lambda _, n=name: self.show_prev_image(n))
            next_button.clicked.connect(lambda _, n=name: self.show_next_image(n))

            self.update_image(name)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)

    def update_image(self, name):
        current_index = self.current_indices[name]
        pixmap = QPixmap(self.image_paths[name][current_index])
        tab_idx = self.tab_widget.indexOf(self.tab_widget.findChild(QWidget, name))

        tab = self.tab_widget.widget(tab_idx)
        label = tab.findChild(QLabel)
        lbl_path = tab.findChildren(QLabel)[1]

        label.setPixmap(pixmap)
        label.setScaledContents(True)
        lbl_path.setText(str(len(self.image_paths[name])) + ': ' + self.image_paths[name][current_index])

    def show_prev_image(self, name):
        if self.current_indices[name] > 0:
            self.current_indices[name] -= 1
            self.update_image(name)

    def show_next_image(self, name):
        if self.current_indices[name] < len(self.image_paths[name]) - 1:
            self.current_indices[name] += 1
            self.update_image(name)

    def show(self):
        self.setWindowTitle("Image Viewer")
        super().show()

##############################################################################################################################