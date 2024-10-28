from pandas import DataFrame
from typing import Union, Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import *
from QEasyWidgets.Components import *

from assets.Sources import *

##############################################################################################################################

class Table_ViewTasks(TableBase):
    caseModuleCol = 0
    caseNameCol = 1
    caseChkTypeCol = 6
    caseCMDCol = 7

    onButtonClicked = Signal(int)

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.setRowCount(0)
        self.setColumnCount(0)
        self.setIndexHeaderVisible(False)
        #self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)

    def addRow(self, ValueRow: list[str]):
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
            Label = LabelBase()
            Label.setText(str(Value))
            ColumnLayout = QHBoxLayout()
            SetColumnLayout(ColumnLayout)
            ColumnLayout.addWidget(Label)
            Layouts += [ColumnLayout]
            ResizeModes += [QHeaderView.ResizeToContents if ValueRow.index(Value) in (self.caseModuleCol, self.caseNameCol, self.caseChkTypeCol) else QHeaderView.Stretch]
            ColumnWidth += [6*RowHeight if ValueRow.index(Value) == self.caseCMDCol else 3*RowHeight]

        Button = ButtonBase()
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

    def setValue(self, Value: Union[DataFrame, dict] = {'ModuleName': [], 'caseName': [], 'SupportedCalulation': [],}):
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
            self.addRow(ValueRow)
        #self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Interactive)

    def getValue(self):
        '''
        Get value of the table, minus the last 1 (checkbox) column
        '''
        ValueDict = {}
        for colCount in range(self.columnCount() - 1): # Remove last 1 (checkbox) column
            ValueList = []
            for row in range(self.rowCount()):
                item = self.cellWidget(row, colCount).findChild(LabelBase)
                if item is None:
                    item = self.cellWidget(row, colCount).findChild(ButtonBase)
                ValueList.append(item.text())
            ValueDict[self.horizontalHeaderItem(colCount).text()] = ValueList
        return ValueDict

    def findRow(self, caseModule, caseName):
        '''
        Assume the combinition of caseModule and caseName is unique
        '''
        for row in range(self.rowCount()):
            if self.cellWidget(row, self.caseModuleCol).findChild(LabelBase).text() == caseModule and self.cellWidget(row, self.caseNameCol).findChild(LabelBase).text() == caseName:
                return row

    def getCaseInfo(self, caseRow: int):
        caseStatusCol = self.columnCount() - 2
        caseCMD = self.cellWidget(caseRow, self.caseCMDCol).findChild(LabelBase).text()
        case = f"[{self.cellWidget(caseRow, self.caseModuleCol).findChild(LabelBase).text()}]{self.cellWidget(caseRow, self.caseNameCol).findChild(LabelBase).text()}"
        caseStatus = self.cellWidget(caseRow, caseStatusCol).findChild(ButtonBase).text()
        return caseCMD, case, caseStatus

    def getCheckedCaseInfos(self):
        CheckBoxCol = self.columnCount() - 1
        checkedCaseInfos = []
        for row in range(self.rowCount()):
            if self.cellWidget(row, CheckBoxCol).findChild(QCheckBox).isChecked():
                caseCMD, case, caseStatus = self.getCaseInfo(row)
                checkedCaseInfos.append([row, caseCMD, case])
        return checkedCaseInfos

    def setCaseStatus(self, caseRow: int, Status: str = ...):
        caseStatusCol = self.columnCount() - 2
        self.cellWidget(caseRow, caseStatusCol).findChild(ButtonBase).setText(Status)

    def getCaseChkTypes(self, caseRow: int):
        return self.cellWidget(caseRow, self.caseChkTypeCol).findChild(LabelBase).text().splitlines()

##############################################################################################################################