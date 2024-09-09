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

    onButtonClicked = Signal(int)

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.setRowCount(0)
        self.setColumnCount(0)
        #self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)

    def AddRow(self, ValueRow: list[str]):
        TargetRow = self.rowCount()
        ColumnCount = self.columnCount()
        self.insertRow(TargetRow)

        RowHeight = 36
        def SetColumnLayout(ColumnLayout):
            ColumnLayout.setContentsMargins(0, 0, 0, 0)
            ColumnLayout.setSpacing(0)

        Layouts = []
        ResizeModes = []
        ColumnWidth = []

        for Value in ValueRow[:-1]:
            Label = QLabel()
            Label.setText(str(Value))
            ColumnLayout = QHBoxLayout()
            SetColumnLayout(ColumnLayout)
            ColumnLayout.addWidget(Label)
            Layouts += [ColumnLayout]
            ResizeModes += [QHeaderView.ResizeToContents if ValueRow.index(Value) in (self.CaseModuleCol, self.CaseNameCol, self.CaseChkTypeCol) else QHeaderView.Fixed]
            ColumnWidth += [6*RowHeight if ValueRow.index(Value) == self.CaseCMDCol else 3*RowHeight]

        Button = QPushButton()
        Button.setText(ValueRow[-1])
        Button.clicked.connect(lambda: self.onButtonClicked.emit(TargetRow))
        ColumnLayout_Button = QHBoxLayout()
        SetColumnLayout(ColumnLayout_Button)
        ColumnLayout_Button.addWidget(Button)
        Layouts += [ColumnLayout_Button]
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

        for Column in range(ColumnCount):
            self.setCellWidget(TargetRow, Column, QWidget())
            self.cellWidget(TargetRow, Column).setLayout(Layouts[Column])
            self.horizontalHeader().setSectionResizeMode(Column, ResizeModes[Column])
            self.setColumnWidth(Column, ColumnWidth[Column]) if ColumnWidth[Column] is not None else None
        self.setRowHeight(TargetRow, RowHeight) if RowHeight is not None else None

    def SetValue(self, Value: Union[DataFrame, dict] = {'ModuleName': [], 'CaseName': [], 'SupportedCalulation': [],}):
        '''
        Set value of the table, minus the last 1 (checkbox) column
        '''
        if isinstance(Value, DataFrame):
            Headers = Value.columns.tolist() + ["选框"]
            Value = Value.values.tolist()
        if isinstance(Value, dict):
            Headers = list(Value.keys()) + ["选框"]
            Value = [list(x) for x in zip(*Value.values())]
        for ValueRow in Value:
            QApplication.processEvents()
            self.setColumnCount(len(ValueRow) + 1)
            self.setHorizontalHeaderLabels(Headers)
            self.AddRow(ValueRow)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Interactive)

    def GetValue(self):
        '''
        Get value of the table, minus the last 1 (checkbox) column
        '''
        ValueDict = {}
        for colCount in range(self.columnCount() - 1): # Remove last 1 (checkbox) column
            ValueList = []
            for row in range(self.rowCount()):
                item = self.cellWidget(row, colCount).findChild(QLabel)
                if item is None:
                    item = self.cellWidget(row, colCount).findChild(QPushButton)
                ValueList.append(item.text())
            ValueDict[self.horizontalHeaderItem(colCount).text()] = ValueList
        return ValueDict

    def FindRow(self, CaseModule, CaseName):
        '''
        Assume the combinition of CaseModule and CaseName is unique
        '''
        for row in range(self.rowCount()):
            if self.cellWidget(row, self.CaseModuleCol).findChild(QLabel).text() == CaseModule and self.cellWidget(row, self.CaseNameCol).findChild(QLabel).text() == CaseName:
                return row

    def GetCaseInfo(self, CaseRow: int):
        CaseStatusCol = self.columnCount() - 2
        CaseCMD = self.cellWidget(CaseRow, self.CaseCMDCol).findChild(QLabel).text()
        Case = f"[{self.cellWidget(CaseRow, self.CaseModuleCol).findChild(QLabel).text()}]{self.cellWidget(CaseRow, self.CaseNameCol).findChild(QLabel).text()}"
        CaseStatus = self.cellWidget(CaseRow, CaseStatusCol).findChild(QPushButton).text()
        return CaseCMD, Case, CaseStatus

    def GetCheckedCaseInfos(self):
        CheckBoxCol = self.columnCount() - 1
        CheckedCaseInfos = []
        for row in range(self.rowCount()):
            if self.cellWidget(row, CheckBoxCol).findChild(QCheckBox).isChecked():
                CaseCMD, Case, CaseStatus = self.GetCaseInfo(row)
                CheckedCaseInfos.append([row, CaseCMD, Case])
        return CheckedCaseInfos

    def SetCaseStatus(self, CaseRow: int, Status: str = ...):
        CaseStatusCol = self.columnCount() - 2
        self.cellWidget(CaseRow, CaseStatusCol).findChild(QPushButton).setText(Status)

    def GetCaseChkTypes(self, CaseRow: int):
        return self.cellWidget(CaseRow, self.CaseChkTypeCol).findChild(QLabel).text().splitlines()

##############################################################################################################################