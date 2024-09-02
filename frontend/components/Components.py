from pandas import DataFrame
from typing import Union, Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import *

from assets.Sources import *

##############################################################################################################################

class Table_ViewTasks(QTableWidget):
    CaseModuleCol = 0
    CaseNameCol = 1
    CaseChkTypeCol = 6
    CaseCMDCol = 7

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.setRowCount(0)
        self.setColumnCount(0)
        #self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    def AddRow(self, ValueRow: list[str]):
        RowHeight = 36
        def SetColumnLayout(ColumnLayout):
            ColumnLayout.setContentsMargins(0, 0, 0, 0)
            ColumnLayout.setSpacing(0)

        Layouts = []
        ResizeModes = []
        ColumnWidth = []

        for Value in ValueRow:
            Label = QLabel()
            Label.setText(str(Value))
            ColumnLayout = QHBoxLayout()
            SetColumnLayout(ColumnLayout)
            ColumnLayout.addWidget(Label)
            Layouts += [ColumnLayout]
            ResizeModes += [QHeaderView.ResizeToContents] if ValueRow.index(Value) != self.CaseCMDCol else [QHeaderView.Stretch]
            ColumnWidth += [None]

        Label = QLabel()
        Label.setText("未执行")
        ColumnLayout_Label = QHBoxLayout()
        SetColumnLayout(ColumnLayout_Label)
        ColumnLayout_Label.addWidget(Label)
        Layouts += [ColumnLayout_Label]
        ResizeModes += [QHeaderView.ResizeToContents]
        ColumnWidth += [None]

        CheckBox = QCheckBox()
        CheckBox.setChecked(False)
        ColumnLayout_CheckBox = QHBoxLayout()
        SetColumnLayout(ColumnLayout_CheckBox)
        ColumnLayout_CheckBox.addWidget(CheckBox)
        ColumnLayout_CheckBox.setAlignment(Qt.AlignCenter)
        Layouts += [ColumnLayout_CheckBox]
        ResizeModes += [QHeaderView.Fixed]
        ColumnWidth += [RowHeight]

        TargetRow = self.currentRow() + 1
        ColumnCount = self.columnCount()
        self.insertRow(TargetRow)
        for Column in range(ColumnCount):
            self.setCellWidget(TargetRow, Column, QWidget())
            self.cellWidget(TargetRow, Column).setLayout(Layouts[Column])
            self.horizontalHeader().setSectionResizeMode(Column, ResizeModes[Column])
            self.setColumnWidth(Column, ColumnWidth[Column]) if ColumnWidth[Column] is not None else None
        self.setRowHeight(TargetRow, RowHeight) if RowHeight is not None else None

    def SetValue(self, Value: Union[DataFrame, dict] = {'ModuleName': [], 'CaseName': [], 'SupportedCalulation': [],}):
        if isinstance(Value, DataFrame):
            Headers = Value.columns.tolist() + ["测试状态", "选框"]
            Value = Value.values.tolist()
        if isinstance(Value, dict):
            Headers = list(Value.keys()) + ["测试状态", "选框"]
            Value = [list(x) for x in zip(*Value.values())]
        for ValueRow in Value:
            QApplication.processEvents()
            self.setColumnCount(len(ValueRow) + 2)
            self.setHorizontalHeaderLabels(Headers)
            self.AddRow(ValueRow)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Interactive)

    def GetValue(self):
        ValueDict = {}
        for colCount in range(self.columnCount() - 2): # Remove last 2 (taskstatus&checkbox) columns
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

    def FindRow(self, CaseModule, CaseName):
        '''
        Assume the combinition of CaseModule and CaseName is unique
        '''
        for row in range(self.rowCount()):
            if self.cellWidget(row, self.CaseModuleCol).findChild(QLabel).text() == CaseModule and self.cellWidget(row, self.CaseNameCol).findChild(QLabel).text() == CaseName:
                return row

    def GetCheckedCaseInfos(self, AllowMultiple: bool = False):
        CheckBoxCol = self.columnCount() - 1
        CheckedCaseInfos = []
        for row in range(self.rowCount()):
            if self.cellWidget(row, CheckBoxCol).findChild(QCheckBox).isChecked():
                CaseCMD = self.cellWidget(row, self.CaseCMDCol).findChild(QLabel).text()
                CaseName = f"[{self.cellWidget(row, self.CaseModuleCol).findChild(QLabel).text()}]{self.cellWidget(row, self.CaseNameCol).findChild(QLabel).text()}"
                CheckedCaseInfos.append([row, CaseCMD, CaseName])
        if not AllowMultiple and len(CheckedCaseInfos) > 1:
            CheckedCaseInfos.append(Exception("Multiple cases selected"))
        return CheckedCaseInfos

    def SetCheckedCaseStatus(self, CaseRow: int, Status: str = ...):
        CheckedCaseCol = self.columnCount() - 2
        self.cellWidget(CaseRow, CheckedCaseCol).findChild(QLabel).setText(Status)

    def GetCaseChkTypes(self, CaseRow: int):
        return self.cellWidget(CaseRow, self.CaseChkTypeCol).findChild(QLabel).text().splitlines()

##############################################################################################################################