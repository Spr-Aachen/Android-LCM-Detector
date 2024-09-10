import os
from pathlib import Path
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import *

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
        self.tabs = {}
        self.initUI()

    def initUI(self):
        self.tab_widget = QTabWidget()

        for name, paths in self.image_paths.items():
            label = QLabel()
            lbl_path = QLabel()

            prev_button = QPushButton("<")
            prev_button.clicked.connect(lambda checked, n=name: self.show_prev_image(n))
            next_button = QPushButton(">")
            next_button.clicked.connect(lambda checked, n=name: self.show_next_image(n))

            button_layout = QHBoxLayout()
            button_layout.addWidget(prev_button)
            button_layout.addWidget(next_button)

            tab_layout = QVBoxLayout()
            tab_layout.addWidget(label)
            tab_layout.addWidget(lbl_path)
            tab_layout.addLayout(button_layout)

            tab = QWidget()
            tab.setLayout(tab_layout)

            self.tab_widget.addTab(tab, name)

            self.tabs[name] = {
                'label': label,
                'lbl_path': lbl_path,
                'tab': tab
            }

            self.update_image(name)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.tab_widget)

    def update_image(self, name):
        current_index = self.current_indices[name]
        if len(self.image_paths[name]) == 0:
            return
        pixmap = QPixmap(self.image_paths[name][current_index])

        tab_components = self.tabs[name]
        label = tab_components['label']
        lbl_path = tab_components['lbl_path']

        label.setPixmap(pixmap)
        label.setScaledContents(True)
        lbl_path.setText(f"{current_index + 1}/{len(self.image_paths[name])}: {self.image_paths[name][current_index]}")

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