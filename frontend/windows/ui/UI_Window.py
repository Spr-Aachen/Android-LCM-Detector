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
        self.Button_UploadFile = ButtonBase(self.content)
        self.Button_UploadFile.setObjectName(u"Button_UploadFile")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.Button_UploadFile.sizePolicy().hasHeightForWidth())
        self.Button_UploadFile.setSizePolicy(sizePolicy1)
        icon = QIcon()
        icon.addFile(u":/Button_Icon/images/icons/file-earmark-arrow-up.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.Button_UploadFile.setIcon(icon)

        self.horizontalLayout_2.addWidget(self.Button_UploadFile)

        self.horizontalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)


        self.gridLayout.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)

        self.ProgressBar_Exec = ProgressBarBase(self.content)
        self.ProgressBar_Exec.setObjectName(u"ProgressBar_Exec")

        self.gridLayout.addWidget(self.ProgressBar_Exec, 2, 0, 1, 2)

        self.gridLayout_4 = QGridLayout()
        self.gridLayout_4.setSpacing(12)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.LineEdit_pcSaveLoc = LineEditBase(self.content)
        self.LineEdit_pcSaveLoc.setObjectName(u"LineEdit_pcSaveLoc")
        sizePolicy1.setHeightForWidth(self.LineEdit_pcSaveLoc.sizePolicy().hasHeightForWidth())
        self.LineEdit_pcSaveLoc.setSizePolicy(sizePolicy1)
        self.LineEdit_pcSaveLoc.setMinimumSize(QSize(210, 0))

        self.gridLayout_4.addWidget(self.LineEdit_pcSaveLoc, 0, 1, 2, 1)

        self.Button_ViewOutput = ButtonBase(self.content)
        self.Button_ViewOutput.setObjectName(u"Button_ViewOutput")
        self.Button_ViewOutput.setMaximumSize(QSize(30, 30))
        icon1 = QIcon()
        icon1.addFile(u":/Button_Icon/images/icons/OpenedFolder.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.Button_ViewOutput.setIcon(icon1)

        self.gridLayout_4.addWidget(self.Button_ViewOutput, 0, 2, 2, 1)

        self.Label_pcSaveLoc = LabelBase(self.content)
        self.Label_pcSaveLoc.setObjectName(u"Label_pcSaveLoc")

        self.gridLayout_4.addWidget(self.Label_pcSaveLoc, 0, 0, 2, 1)


        self.gridLayout.addLayout(self.gridLayout_4, 0, 1, 1, 1)

        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_2.addItem(self.verticalSpacer, 0, 0, 1, 1)


        self.gridLayout.addLayout(self.gridLayout_2, 1, 0, 1, 2)


        self.gridLayout_5.addWidget(self.content, 1, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.Label_pcSaveLoc.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
    # retranslateUi

