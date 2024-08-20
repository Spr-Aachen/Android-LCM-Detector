from typing import Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import *

from assets.Sources import *

##############################################################################################################################

class Table_ViewTasks(QTableWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.setRowCount(0)
        self.setColumnCount(6)

    def setStyleSheet(self, StyleSheet: str):
        super().setStyleSheet(StyleSheet +  '''
            QHeaderView::section, QTableView, QTableView::item {
                gridline-color:rgba(201, 210, 222, 123);
                border-radius:0px;
                border-color:rgba(201, 210, 222, 123);
            }
        '''
        )

    def AddRow(self, Param: tuple):
        CaseName, DazzlingCheck, MonochromeCheck, UndertoneCheck, TaskStatus = Param

        RowHeight = 36
        LabelStyle = '''
        QLabel {
            background-color: transparent;
            padding: 6px;
            border-width: 1px;
            border-style: solid;
            border-color: rgba(201, 210, 222, 123);
        }
        '''
        def SetColumnLayout(ColumnLayout):
            ColumnLayout.setContentsMargins(0, 0, 0, 0)
            ColumnLayout.setSpacing(0)

        Label_CaseName = QLabel()
        Label_CaseName.setStyleSheet(LabelStyle)
        Label_CaseName.setText(CaseName)
        ColumnLayout_CaseName = QHBoxLayout()
        SetColumnLayout(ColumnLayout_CaseName)
        ColumnLayout_CaseName.addWidget(Label_CaseName)

        Label_DazzlingCheck = QLabel()
        Label_DazzlingCheck.setStyleSheet(LabelStyle)
        Label_DazzlingCheck.setText(DazzlingCheck)
        ColumnLayout_DazzlingCheck = QHBoxLayout()
        SetColumnLayout(ColumnLayout_DazzlingCheck)
        ColumnLayout_DazzlingCheck.addWidget(Label_DazzlingCheck)

        Label_MonochromeCheck = QLabel()
        Label_MonochromeCheck.setStyleSheet(LabelStyle)
        Label_MonochromeCheck.setText(MonochromeCheck)
        ColumnLayout_MonochromeCheck = QHBoxLayout()
        SetColumnLayout(ColumnLayout_MonochromeCheck)
        ColumnLayout_MonochromeCheck.addWidget(Label_MonochromeCheck)

        Label_UndertoneCheck = QLabel()
        Label_UndertoneCheck.setStyleSheet(LabelStyle)
        Label_UndertoneCheck.setText(UndertoneCheck)
        ColumnLayout_UndertoneCheck = QHBoxLayout()
        SetColumnLayout(ColumnLayout_UndertoneCheck)
        ColumnLayout_UndertoneCheck.addWidget(Label_UndertoneCheck)

        Label_TaskStatus = QLabel()
        Label_TaskStatus.setStyleSheet(LabelStyle)
        Label_TaskStatus.setText(TaskStatus)
        ColumnLayout_TaskStatus = QHBoxLayout()
        SetColumnLayout(ColumnLayout_TaskStatus)
        ColumnLayout_TaskStatus.addWidget(Label_TaskStatus)

        CheckBox = QCheckBox()
        #CheckBox.setStyleSheet(CheckBoxStyle)
        CheckBox.setChecked(False)
        ColumnLayout_CheckBox = QHBoxLayout()
        SetColumnLayout(ColumnLayout_CheckBox)
        ColumnLayout_CheckBox.addWidget(CheckBox)

        Layouts = [ColumnLayout_CaseName, ColumnLayout_DazzlingCheck, ColumnLayout_MonochromeCheck, ColumnLayout_UndertoneCheck, ColumnLayout_TaskStatus, ColumnLayout_CheckBox]
        ColumnWidth = [None, None, None, None, None, RowHeight]

        TargetRow = self.currentRow() + 1
        ColumnCount = self.columnCount()
        self.insertRow(TargetRow)
        for ColumnCount in range(ColumnCount):
            self.setCellWidget(TargetRow, ColumnCount, QWidget())
            self.cellWidget(TargetRow, ColumnCount).setLayout(Layouts[ColumnCount])
            self.setColumnWidth(ColumnCount, ColumnWidth[ColumnCount]) if ColumnWidth[ColumnCount] is not None else None
        self.setRowHeight(TargetRow, RowHeight) if RowHeight is not None else None

    def SetValue(self, Params: list[list] = [['CaseName', 'DazzlingCheck', 'MonochromeCheck', 'UndertoneCheck', 'TaskStatus'], ]):
        for Param in Params:
            QApplication.processEvents()
            self.AddRow(Param)

    def GetValue(self):
        ValueDict = {}
        for colCount in range(self.columnCount() - 1):
            ValueList = []
            for row in range(self.rowCount()):
                try:
                    item = self.cellWidget(row, colCount).findChild(QLabel)
                except:
                    pass
                else:
                    ValueList.append(item.text()) if item is not None else None
            ValueDict[self.horizontalHeaderItem(colCount).text()] = ValueList
        return ValueDict

##############################################################################################################################