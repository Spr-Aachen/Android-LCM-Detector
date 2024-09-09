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
        self.gridLayout.setSpacing(12)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(21, 12, 21, 12)
        self.Table = Table_ViewTasks(self.centralwidget)
        self.Table.setObjectName(u"Table")

        self.gridLayout.addWidget(self.Table, 2, 0, 1, 4)

        self.ProgressBar_adbExec = QProgressBar(self.centralwidget)
        self.ProgressBar_adbExec.setObjectName(u"ProgressBar_adbExec")

        self.gridLayout.addWidget(self.ProgressBar_adbExec, 3, 0, 1, 4)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(12)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.Label_pcSaveLoc = QLabel(self.centralwidget)
        self.Label_pcSaveLoc.setObjectName(u"Label_pcSaveLoc")

        self.horizontalLayout.addWidget(self.Label_pcSaveLoc)

        self.LineEdit_pcSaveLoc = QLineEdit(self.centralwidget)
        self.LineEdit_pcSaveLoc.setObjectName(u"LineEdit_pcSaveLoc")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LineEdit_pcSaveLoc.sizePolicy().hasHeightForWidth())
        self.LineEdit_pcSaveLoc.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.LineEdit_pcSaveLoc)


        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 2)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.Button_LoadData = QPushButton(self.centralwidget)
        self.Button_LoadData.setObjectName(u"Button_LoadData")

        self.horizontalLayout_2.addWidget(self.Button_LoadData)

        self.Button_Exec = QPushButton(self.centralwidget)
        self.Button_Exec.setObjectName(u"Button_Exec")

        self.horizontalLayout_2.addWidget(self.Button_Exec)

        self.Button_ViewOutput = QPushButton(self.centralwidget)
        self.Button_ViewOutput.setObjectName(u"Button_ViewOutput")

        self.horizontalLayout_2.addWidget(self.Button_ViewOutput)


        self.gridLayout.addLayout(self.horizontalLayout_2, 1, 0, 1, 2)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.Label_pcSaveLoc.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.Button_LoadData.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.Button_Exec.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.Button_ViewOutput.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
    # retranslateUi