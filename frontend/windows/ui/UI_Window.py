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
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.Label_pcSaveLoc = QLabel(self.centralwidget)
        self.Label_pcSaveLoc.setObjectName(u"Label_pcSaveLoc")

        self.horizontalLayout.addWidget(self.Label_pcSaveLoc)

        self.LineEdit_pcSaveLoc = QLineEdit(self.centralwidget)
        self.LineEdit_pcSaveLoc.setObjectName(u"LineEdit_pcSaveLoc")

        self.horizontalLayout.addWidget(self.LineEdit_pcSaveLoc)


        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)

        self.Button_LoadData = QPushButton(self.centralwidget)
        self.Button_LoadData.setObjectName(u"Button_LoadData")

        self.gridLayout.addWidget(self.Button_LoadData, 3, 0, 1, 2)

        self.Table = Table_ViewTasks(self.centralwidget)
        self.Table.setObjectName(u"Table")

        self.gridLayout.addWidget(self.Table, 4, 0, 1, 2)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.Label_dbName = QLabel(self.centralwidget)
        self.Label_dbName.setObjectName(u"Label_dbName")

        self.horizontalLayout_2.addWidget(self.Label_dbName)

        self.LineEdit_dbName = QLineEdit(self.centralwidget)
        self.LineEdit_dbName.setObjectName(u"LineEdit_dbName")

        self.horizontalLayout_2.addWidget(self.LineEdit_dbName)


        self.gridLayout.addLayout(self.horizontalLayout_2, 1, 1, 1, 1)

        self.StackedWidget_adbExec = QStackedWidget(self.centralwidget)
        self.StackedWidget_adbExec.setObjectName(u"StackedWidget_adbExec")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.StackedWidget_adbExec.sizePolicy().hasHeightForWidth())
        self.StackedWidget_adbExec.setSizePolicy(sizePolicy)
        self.Page_adbExecButton = QWidget()
        self.Page_adbExecButton.setObjectName(u"Page_adbExecButton")
        self.gridLayout_2 = QGridLayout(self.Page_adbExecButton)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.Button_adbExec = QPushButton(self.Page_adbExecButton)
        self.Button_adbExec.setObjectName(u"Button_adbExec")

        self.gridLayout_2.addWidget(self.Button_adbExec, 0, 0, 1, 1)

        self.StackedWidget_adbExec.addWidget(self.Page_adbExecButton)
        self.Page_adbExecProgressBar = QWidget()
        self.Page_adbExecProgressBar.setObjectName(u"Page_adbExecProgressBar")
        self.gridLayout_3 = QGridLayout(self.Page_adbExecProgressBar)
        self.gridLayout_3.setSpacing(0)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.ProgressBar_adbExec = QProgressBar(self.Page_adbExecProgressBar)
        self.ProgressBar_adbExec.setObjectName(u"ProgressBar_adbExec")
        self.ProgressBar_adbExec.setValue(24)

        self.gridLayout_3.addWidget(self.ProgressBar_adbExec, 0, 0, 1, 1)

        self.StackedWidget_adbExec.addWidget(self.Page_adbExecProgressBar)

        self.gridLayout.addWidget(self.StackedWidget_adbExec, 5, 0, 1, 1)

        self.StackedWidget_Analyse = QStackedWidget(self.centralwidget)
        self.StackedWidget_Analyse.setObjectName(u"StackedWidget_Analyse")
        sizePolicy.setHeightForWidth(self.StackedWidget_Analyse.sizePolicy().hasHeightForWidth())
        self.StackedWidget_Analyse.setSizePolicy(sizePolicy)
        self.Page_AnalyseButton = QWidget()
        self.Page_AnalyseButton.setObjectName(u"Page_AnalyseButton")
        self.gridLayout_5 = QGridLayout(self.Page_AnalyseButton)
        self.gridLayout_5.setSpacing(0)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.gridLayout_5.setContentsMargins(0, 0, 0, 0)
        self.Button_Analyse = QPushButton(self.Page_AnalyseButton)
        self.Button_Analyse.setObjectName(u"Button_Analyse")

        self.gridLayout_5.addWidget(self.Button_Analyse, 0, 0, 1, 1)

        self.StackedWidget_Analyse.addWidget(self.Page_AnalyseButton)
        self.page_AnalyseProgressBar = QWidget()
        self.page_AnalyseProgressBar.setObjectName(u"page_AnalyseProgressBar")
        self.gridLayout_4 = QGridLayout(self.page_AnalyseProgressBar)
        self.gridLayout_4.setSpacing(0)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_4.setContentsMargins(0, 0, 0, 0)
        self.ProgressBar_Analyse = QProgressBar(self.page_AnalyseProgressBar)
        self.ProgressBar_Analyse.setObjectName(u"ProgressBar_Analyse")
        self.ProgressBar_Analyse.setValue(24)

        self.gridLayout_4.addWidget(self.ProgressBar_Analyse, 0, 0, 1, 1)

        self.StackedWidget_Analyse.addWidget(self.page_AnalyseProgressBar)

        self.gridLayout.addWidget(self.StackedWidget_Analyse, 8, 0, 1, 1)

        self.Button_adbOutput = QPushButton(self.centralwidget)
        self.Button_adbOutput.setObjectName(u"Button_adbOutput")

        self.gridLayout.addWidget(self.Button_adbOutput, 5, 1, 1, 1)

        self.Button_AnalysationOutput = QPushButton(self.centralwidget)
        self.Button_AnalysationOutput.setObjectName(u"Button_AnalysationOutput")

        self.gridLayout.addWidget(self.Button_AnalysationOutput, 8, 1, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.StackedWidget_adbExec.setCurrentIndex(0)
        self.StackedWidget_Analyse.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.Label_pcSaveLoc.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.Button_LoadData.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.Label_dbName.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.Button_adbExec.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.Button_Analyse.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.Button_adbOutput.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.Button_AnalysationOutput.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
    # retranslateUi