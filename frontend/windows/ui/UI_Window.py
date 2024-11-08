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
        self.gridLayout_5 = QGridLayout(self.centralwidget)
        self.gridLayout_5.setSpacing(0)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.gridLayout_5.setContentsMargins(0, 0, 0, 0)
        self.titleBar = QFrame(self.centralwidget)
        self.titleBar.setObjectName(u"titleBar")
        self.titleBar.setMinimumSize(QSize(0, 30))
        self.titleBar.setMaximumSize(QSize(16777215, 30))
        self.horizontalLayout_30 = QHBoxLayout(self.titleBar)
        self.horizontalLayout_30.setSpacing(0)
        self.horizontalLayout_30.setObjectName(u"horizontalLayout_30")
        self.horizontalLayout_30.setContentsMargins(0, 0, 0, 0)
        self.Frame_Top = QFrame(self.titleBar)
        self.Frame_Top.setObjectName(u"Frame_Top")
        self.horizontalLayout_11 = QHBoxLayout(self.Frame_Top)
        self.horizontalLayout_11.setSpacing(21)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.horizontalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.HorizontalSpacer_Right_Top = QSpacerItem(587, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_11.addItem(self.HorizontalSpacer_Right_Top)

        self.CheckBox_SwitchTheme = QCheckBox(self.Frame_Top)
        self.CheckBox_SwitchTheme.setObjectName(u"CheckBox_SwitchTheme")
        self.CheckBox_SwitchTheme.setStyleSheet(u"QCheckBox {\n"
"	font-size: 12px;\n"
"	spacing: 12.3px;\n"
"	background-color: transparent;\n"
"	padding: 0px;\n"
"	border-width: 0px;\n"
"	border-radius: 6px;\n"
"	border-style: solid;\n"
"}\n"
"QCheckBox:hover {\n"
"}\n"
"\n"
"QCheckBox::indicator {\n"
"	width: 16.8px;\n"
"	height: 16.8px;\n"
"    background-color: transparent;\n"
"	padding: 0px;\n"
"	border-width: 0px;\n"
"	border-radius: 6px;\n"
"	border-style: solid;\n"
"}\n"
"QCheckBox::indicator:hover {\n"
"	background-color: rgba(255, 255, 255, 24);\n"
"}\n"
"QCheckBox::indicator:unchecked {\n"
"	border-image: url(:/CheckBox_Icon/images/icons/Moon.png);\n"
"}\n"
"QCheckBox::indicator:checked {\n"
"	border-image: url(:/CheckBox_Icon/images/icons/Sun.png);\n"
"}")

        self.horizontalLayout_11.addWidget(self.CheckBox_SwitchTheme)

        self.Frame_Top_Control_Window = QFrame(self.Frame_Top)
        self.Frame_Top_Control_Window.setObjectName(u"Frame_Top_Control_Window")
        self.Frame_Top_Control_Window.setMinimumSize(QSize(144, 0))
        self.Frame_Top_Control_Window.setMaximumSize(QSize(144, 16777215))
        self.horizontalLayout_12 = QHBoxLayout(self.Frame_Top_Control_Window)
        self.horizontalLayout_12.setSpacing(0)
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.horizontalLayout_12.setContentsMargins(0, 0, 0, 0)
        self.Button_Minimize_Window = ButtonBase(self.Frame_Top_Control_Window)
        self.Button_Minimize_Window.setObjectName(u"Button_Minimize_Window")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Button_Minimize_Window.sizePolicy().hasHeightForWidth())
        self.Button_Minimize_Window.setSizePolicy(sizePolicy)

        self.horizontalLayout_12.addWidget(self.Button_Minimize_Window)

        self.Button_Maximize_Window = ButtonBase(self.Frame_Top_Control_Window)
        self.Button_Maximize_Window.setObjectName(u"Button_Maximize_Window")
        sizePolicy.setHeightForWidth(self.Button_Maximize_Window.sizePolicy().hasHeightForWidth())
        self.Button_Maximize_Window.setSizePolicy(sizePolicy)

        self.horizontalLayout_12.addWidget(self.Button_Maximize_Window)

        self.Button_Close_Window = ButtonBase(self.Frame_Top_Control_Window)
        self.Button_Close_Window.setObjectName(u"Button_Close_Window")
        sizePolicy.setHeightForWidth(self.Button_Close_Window.sizePolicy().hasHeightForWidth())
        self.Button_Close_Window.setSizePolicy(sizePolicy)

        self.horizontalLayout_12.addWidget(self.Button_Close_Window)


        self.horizontalLayout_11.addWidget(self.Frame_Top_Control_Window)


        self.horizontalLayout_30.addWidget(self.Frame_Top)


        self.gridLayout_5.addWidget(self.titleBar, 0, 0, 1, 1)

        self.content = QWidget(self.centralwidget)
        self.content.setObjectName(u"content")
        self.gridLayout = QGridLayout(self.content)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setHorizontalSpacing(21)
        self.gridLayout.setVerticalSpacing(12)
        self.gridLayout.setContentsMargins(21, 12, 21, 12)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setSpacing(21)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.Button_LoadData = ButtonBase(self.content)
        self.Button_LoadData.setObjectName(u"Button_LoadData")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.Button_LoadData.sizePolicy().hasHeightForWidth())
        self.Button_LoadData.setSizePolicy(sizePolicy1)
        self.Button_LoadData.setMaximumSize(QSize(210, 30))
        icon = QIcon()
        icon.addFile(u":/Button_Icon/images/icons/Plus.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.Button_LoadData.setIcon(icon)

        self.horizontalLayout_2.addWidget(self.Button_LoadData)

        self.Button_UploadFile = ButtonBase(self.content)
        self.Button_UploadFile.setObjectName(u"Button_UploadFile")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Ignored)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.Button_UploadFile.sizePolicy().hasHeightForWidth())
        self.Button_UploadFile.setSizePolicy(sizePolicy2)
        icon1 = QIcon()
        icon1.addFile(u":/Button_Icon/images/icons/file-earmark-arrow-up.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.Button_UploadFile.setIcon(icon1)

        self.horizontalLayout_2.addWidget(self.Button_UploadFile)

        self.StackedWidget_ExecAndStop = QStackedWidget(self.content)
        self.StackedWidget_ExecAndStop.setObjectName(u"StackedWidget_ExecAndStop")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.StackedWidget_ExecAndStop.sizePolicy().hasHeightForWidth())
        self.StackedWidget_ExecAndStop.setSizePolicy(sizePolicy3)
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
        self.Button_Exec = ButtonBase(self.StackedWidget_Page_Exec)
        self.Button_Exec.setObjectName(u"Button_Exec")
        sizePolicy1.setHeightForWidth(self.Button_Exec.sizePolicy().hasHeightForWidth())
        self.Button_Exec.setSizePolicy(sizePolicy1)
        self.Button_Exec.setMaximumSize(QSize(210, 30))
        icon2 = QIcon()
        icon2.addFile(u":/CheckBox_Icon/images/icons/CheckedSquare.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.Button_Exec.setIcon(icon2)

        self.gridLayout_3.addWidget(self.Button_Exec, 0, 0, 1, 1)

        self.StackedWidget_ExecAndStop.addWidget(self.StackedWidget_Page_Exec)
        self.StackedWidget_Page_Stop = QWidget()
        self.StackedWidget_Page_Stop.setObjectName(u"StackedWidget_Page_Stop")
        self.gridLayout_2 = QGridLayout(self.StackedWidget_Page_Stop)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.Button_Stop = ButtonBase(self.StackedWidget_Page_Stop)
        self.Button_Stop.setObjectName(u"Button_Stop")
        sizePolicy1.setHeightForWidth(self.Button_Stop.sizePolicy().hasHeightForWidth())
        self.Button_Stop.setSizePolicy(sizePolicy1)
        self.Button_Stop.setMaximumSize(QSize(210, 30))
        icon3 = QIcon()
        icon3.addFile(u":/Button_Icon/images/icons/X.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.Button_Stop.setIcon(icon3)

        self.gridLayout_2.addWidget(self.Button_Stop, 0, 0, 1, 1)

        self.StackedWidget_ExecAndStop.addWidget(self.StackedWidget_Page_Stop)

        self.horizontalLayout_2.addWidget(self.StackedWidget_ExecAndStop)

        self.horizontalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)


        self.gridLayout.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)

        self.gridLayout_4 = QGridLayout()
        self.gridLayout_4.setSpacing(12)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.LineEdit_pcSaveLoc = LineEditBase(self.content)
        self.LineEdit_pcSaveLoc.setObjectName(u"LineEdit_pcSaveLoc")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.LineEdit_pcSaveLoc.sizePolicy().hasHeightForWidth())
        self.LineEdit_pcSaveLoc.setSizePolicy(sizePolicy4)
        self.LineEdit_pcSaveLoc.setMinimumSize(QSize(210, 0))

        self.gridLayout_4.addWidget(self.LineEdit_pcSaveLoc, 0, 1, 2, 1)

        self.Button_ViewOutput = ButtonBase(self.content)
        self.Button_ViewOutput.setObjectName(u"Button_ViewOutput")
        self.Button_ViewOutput.setMaximumSize(QSize(30, 30))
        icon4 = QIcon()
        icon4.addFile(u":/Button_Icon/images/icons/OpenedFolder.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.Button_ViewOutput.setIcon(icon4)

        self.gridLayout_4.addWidget(self.Button_ViewOutput, 0, 2, 2, 1)

        self.Label_pcSaveLoc = LabelBase(self.content)
        self.Label_pcSaveLoc.setObjectName(u"Label_pcSaveLoc")

        self.gridLayout_4.addWidget(self.Label_pcSaveLoc, 0, 0, 2, 1)


        self.gridLayout.addLayout(self.gridLayout_4, 0, 1, 1, 1)

        self.Table = Table_ViewTasks(self.content)
        self.Table.setObjectName(u"Table")

        self.gridLayout.addWidget(self.Table, 1, 0, 1, 2)

        self.ProgressBar_Exec = ProgressBarBase(self.content)
        self.ProgressBar_Exec.setObjectName(u"ProgressBar_Exec")

        self.gridLayout.addWidget(self.ProgressBar_Exec, 2, 0, 1, 2)


        self.gridLayout_5.addWidget(self.content, 1, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.StackedWidget_ExecAndStop.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.Label_pcSaveLoc.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
    # retranslateUi