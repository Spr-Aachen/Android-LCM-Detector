# -*- coding: utf-8 -*-

from PySide6.QtGui import QIcon
from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, QSize
from PySide6.QtWidgets import *

from components.Components import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        MainWindow.setStyleSheet(u"QWidget#centralwidget {\n"
"	/*background-color: rgba(234, 234, 234, 234);*/\n"
"}")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setHorizontalSpacing(21)
        self.gridLayout.setVerticalSpacing(12)
        self.gridLayout.setContentsMargins(21, 12, 21, 12)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setSpacing(21)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.Button_LoadData = QPushButton(self.centralwidget)
        self.Button_LoadData.setObjectName(u"Button_LoadData")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Button_LoadData.sizePolicy().hasHeightForWidth())
        self.Button_LoadData.setSizePolicy(sizePolicy)
        self.Button_LoadData.setMaximumSize(QSize(210, 30))
        self.Button_LoadData.setStyleSheet(u"QPushButton {\n"
"    color: black;\n"
"    background: rgba(255, 255, 255, 150);\n"
"    border: 1px solid rgba(0, 0, 0, 12);\n"
"    border-bottom: 1px solid rgba(0, 0, 0, 48);\n"
"    border-radius: 3px;\n"
"    padding: 5px 12px 6px 12px;\n"
"    outline: none;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background: rgba(246, 246, 246, 0.5);\n"
"}\n"
"\n"
"QPushButton:pressed, QPushButton:checked {\n"
"    color: rgba(0, 0, 0, 123);\n"
"    background: rgba(246, 246, 246, 75);\n"
"    border-bottom: 1px solid rgba(0, 0, 0, 15);\n"
"}")
        icon = QIcon()
        icon.addFile(u":/Button_Icon/images/icons/Plus.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.Button_LoadData.setIcon(icon)

        self.horizontalLayout_2.addWidget(self.Button_LoadData)

        self.StackedWidget_ExecAndStop = QStackedWidget(self.centralwidget)
        self.StackedWidget_ExecAndStop.setObjectName(u"StackedWidget_ExecAndStop")
        self.StackedWidget_ExecAndStop.setStyleSheet(u"QStackedWidget {\n"
"	background-color: transparent;\n"
"}")
        self.StackedWidget_Page_Exec = QWidget()
        self.StackedWidget_Page_Exec.setObjectName(u"StackedWidget_Page_Exec")
        self.StackedWidget_Page_Exec.setStyleSheet(u"")
        self.gridLayout_3 = QGridLayout(self.StackedWidget_Page_Exec)
        self.gridLayout_3.setSpacing(0)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.Button_Exec = QPushButton(self.StackedWidget_Page_Exec)
        self.Button_Exec.setObjectName(u"Button_Exec")
        sizePolicy.setHeightForWidth(self.Button_Exec.sizePolicy().hasHeightForWidth())
        self.Button_Exec.setSizePolicy(sizePolicy)
        self.Button_Exec.setMaximumSize(QSize(210, 30))
        self.Button_Exec.setStyleSheet(u"QPushButton {\n"
"    color: black;\n"
"    background: rgba(255, 255, 255, 150);\n"
"    border: 1px solid rgba(0, 0, 0, 12);\n"
"    border-bottom: 1px solid rgba(0, 0, 0, 48);\n"
"    border-radius: 3px;\n"
"    padding: 5px 12px 6px 12px;\n"
"    outline: none;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background: rgba(246, 246, 246, 0.5);\n"
"}\n"
"\n"
"QPushButton:pressed, QPushButton:checked {\n"
"    color: rgba(0, 0, 0, 123);\n"
"    background: rgba(246, 246, 246, 75);\n"
"    border-bottom: 1px solid rgba(0, 0, 0, 15);\n"
"}")
        icon1 = QIcon()
        icon1.addFile(u":/CheckBox_Icon/images/icons/CheckedSquare.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.Button_Exec.setIcon(icon1)

        self.gridLayout_3.addWidget(self.Button_Exec, 0, 0, 1, 1)

        self.StackedWidget_ExecAndStop.addWidget(self.StackedWidget_Page_Exec)
        self.StackedWidget_Page_Stop = QWidget()
        self.StackedWidget_Page_Stop.setObjectName(u"StackedWidget_Page_Stop")
        self.gridLayout_2 = QGridLayout(self.StackedWidget_Page_Stop)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.Button_Stop = QPushButton(self.StackedWidget_Page_Stop)
        self.Button_Stop.setObjectName(u"Button_Stop")
        sizePolicy.setHeightForWidth(self.Button_Stop.sizePolicy().hasHeightForWidth())
        self.Button_Stop.setSizePolicy(sizePolicy)
        self.Button_Stop.setMaximumSize(QSize(210, 30))
        self.Button_Stop.setStyleSheet(u"QPushButton {\n"
"    color: black;\n"
"    background: rgba(255, 255, 255, 150);\n"
"    border: 1px solid rgba(0, 0, 0, 12);\n"
"    border-bottom: 1px solid rgba(0, 0, 0, 48);\n"
"    border-radius: 3px;\n"
"    padding: 5px 12px 6px 12px;\n"
"    outline: none;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background: rgba(246, 246, 246, 0.5);\n"
"}\n"
"\n"
"QPushButton:pressed, QPushButton:checked {\n"
"    color: rgba(0, 0, 0, 123);\n"
"    background: rgba(246, 246, 246, 75);\n"
"    border-bottom: 1px solid rgba(0, 0, 0, 15);\n"
"}")
        icon2 = QIcon()
        icon2.addFile(u":/Button_Icon/images/icons/X.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.Button_Stop.setIcon(icon2)

        self.gridLayout_2.addWidget(self.Button_Stop, 0, 0, 1, 1)

        self.StackedWidget_ExecAndStop.addWidget(self.StackedWidget_Page_Stop)

        self.horizontalLayout_2.addWidget(self.StackedWidget_ExecAndStop)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)


        self.gridLayout.addLayout(self.horizontalLayout_2, 0, 0, 4, 2)

        self.ProgressBar_Exec = QProgressBar(self.centralwidget)
        self.ProgressBar_Exec.setObjectName(u"ProgressBar_Exec")
        self.ProgressBar_Exec.setStyleSheet(u"QProgressBar {\n"
"	text-align: center;\n"
"    color: black;\n"
"    background-color: rgba(210, 210, 210, 150);\n"
"    border: none;\n"
"    border-radius: 5px;\n"
"}\n"
"  \n"
"QProgressBar::chunk {\n"
"	background-color: rgba(55, 110, 165, 150);\n"
"}")

        self.gridLayout.addWidget(self.ProgressBar_Exec, 5, 0, 1, 4)

        self.Table = Table_ViewTasks(self.centralwidget)
        self.Table.setObjectName(u"Table")
        self.Table.setStyleSheet(u"QTableView {\n"
"    background: rgba(255, 255, 255, 150);\n"
"    selection-background-color: transparent;\n"
"    alternate-background-color: transparent;\n"
"    border: none;\n"
"    border-radius: 3px;\n"
"    outline: none;\n"
"}\n"
"\n"
"QTableView::item {\n"
"    height: 33px;\n"
"    padding: 3px 6px;\n"
"    background: transparent;\n"
"    border: 0px;\n"
"}\n"
"\n"
"\n"
"QTableView::indicator {\n"
"    width: 18px;\n"
"    height: 18px;\n"
"    background-color: transparent;\n"
"    border: none;\n"
"    border-radius: 3px;\n"
"}\n"
"\n"
"\n"
"QHeaderView {\n"
"    background: transparent;\n"
"}\n"
"\n"
"QHeaderView::section {\n"
"    color: rgb(96, 96, 96);\n"
"    padding: 2.4px 4.8px;\n"
"    background-color: transparent;\n"
"    border: 1px solid rgba(0, 0, 0, 15);\n"
"}\n"
"\n"
"QHeaderView::section:horizontal {\n"
"    height: 33px;\n"
"    border-left: none;\n"
"}\n"
"\n"
"QHeaderView::section:horizontal:last {\n"
"    border-right: none;\n"
"}\n"
"\n"
"QHeaderView::section:vertical {\n"
" "
                        "   border-top: none;\n"
"}\n"
"\n"
"QHeaderView::section:checked {\n"
"    background-color: transparent;\n"
"}")

        self.gridLayout.addWidget(self.Table, 4, 0, 1, 4)

        self.gridLayout_4 = QGridLayout()
        self.gridLayout_4.setSpacing(12)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.LineEdit_pcSaveLoc = QLineEdit(self.centralwidget)
        self.LineEdit_pcSaveLoc.setObjectName(u"LineEdit_pcSaveLoc")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.LineEdit_pcSaveLoc.sizePolicy().hasHeightForWidth())
        self.LineEdit_pcSaveLoc.setSizePolicy(sizePolicy1)
        self.LineEdit_pcSaveLoc.setMinimumSize(QSize(210, 0))
        self.LineEdit_pcSaveLoc.setStyleSheet(u"QLineEdit {\n"
"    color: black;\n"
"    background-color: rgba(255, 255, 255, 150);\n"
"    border: 1px solid rgba(0, 0, 0, 12);\n"
"    border-bottom: 1px solid rgba(0, 0, 0, 100);\n"
"    border-radius: 3px;\n"
"    padding: 5px 10px 6px 10px;\n"
"}\n"
"\n"
"QLineEdit:hover {\n"
"    background-color: rgba(249, 249, 249, 123);\n"
"    border: 1px solid rgba(0, 0, 0, 12);\n"
"    border-bottom: 1px solid rgba(0, 0, 0, 100);\n"
"}\n"
"\n"
"LineEdit:focus {\n"
"    border-bottom: 1px solid rgba(0, 0, 0, 12);\n"
"    background-color: white;\n"
"}")

        self.gridLayout_4.addWidget(self.LineEdit_pcSaveLoc, 0, 1, 2, 1)

        self.Button_ViewOutput = QPushButton(self.centralwidget)
        self.Button_ViewOutput.setObjectName(u"Button_ViewOutput")
        self.Button_ViewOutput.setMaximumSize(QSize(30, 30))
        self.Button_ViewOutput.setStyleSheet(u"QPushButton {\n"
"    color: black;\n"
"    background: rgba(255, 255, 255, 150);\n"
"    border: 1px solid rgba(0, 0, 0, 12);\n"
"    border-bottom: 1px solid rgba(0, 0, 0, 48);\n"
"    border-radius: 3px;\n"
"    padding: 5px 12px 6px 12px;\n"
"    outline: none;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background: rgba(246, 246, 246, 0.5);\n"
"}\n"
"\n"
"QPushButton:pressed, QPushButton:checked {\n"
"    color: rgba(0, 0, 0, 123);\n"
"    background: rgba(246, 246, 246, 75);\n"
"    border-bottom: 1px solid rgba(0, 0, 0, 15);\n"
"}")
        icon3 = QIcon()
        icon3.addFile(u":/Button_Icon/images/icons/OpenedFolder.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.Button_ViewOutput.setIcon(icon3)

        self.gridLayout_4.addWidget(self.Button_ViewOutput, 0, 2, 2, 1)

        self.Label_pcSaveLoc = QLabel(self.centralwidget)
        self.Label_pcSaveLoc.setObjectName(u"Label_pcSaveLoc")
        self.Label_pcSaveLoc.setStyleSheet(u"QLabel {\n"
"	/*qproperty-alignment: AlignCenter;*/\n"
"}")

        self.gridLayout_4.addWidget(self.Label_pcSaveLoc, 0, 0, 2, 1)


        self.gridLayout.addLayout(self.gridLayout_4, 0, 2, 4, 2)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.StackedWidget_ExecAndStop.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.Label_pcSaveLoc.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
    # retranslateUi