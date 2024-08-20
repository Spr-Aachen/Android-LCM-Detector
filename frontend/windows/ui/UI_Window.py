# -*- coding: utf-8 -*-

from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, QSize
from PySide6.QtWidgets import *

from components.Components import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.Button_LoadData = QPushButton(self.centralwidget)
        self.Button_LoadData.setObjectName(u"Button_LoadData")

        self.gridLayout.addWidget(self.Button_LoadData, 0, 0, 1, 1)

        self.Button_Execute = QPushButton(self.centralwidget)
        self.Button_Execute.setObjectName(u"Button_Execute")

        self.gridLayout.addWidget(self.Button_Execute, 2, 0, 1, 1)

        self.Table = Table_ViewTasks(self.centralwidget)
        self.Table.setObjectName(u"Table")

        self.gridLayout.addWidget(self.Table, 1, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.Button_LoadData.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.Button_Execute.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
    # retranslateUi