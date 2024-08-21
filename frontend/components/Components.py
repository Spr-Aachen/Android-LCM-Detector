from pandas import DataFrame
from typing import Union, Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import *

from assets.Sources import *

##############################################################################################################################

class Table_ViewTasks(QTableWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.setRowCount(0)
        self.setColumnCount(0)

    def AddRow(self, ValueRow: list[str]):
        RowHeight = 36
        def SetColumnLayout(ColumnLayout):
            ColumnLayout.setContentsMargins(0, 0, 0, 0)
            ColumnLayout.setSpacing(0)

        Layouts = []
        ColumnWidth = []

        for Value in ValueRow:
            Label = QLabel()
            Label.setText(str(Value))
            ColumnLayout = QHBoxLayout()
            SetColumnLayout(ColumnLayout)
            ColumnLayout.addWidget(Label)
            Layouts += [ColumnLayout]
            ColumnWidth += [None]

        Label = QLabel()
        Label.setText("未执行")
        ColumnLayout_Label = QHBoxLayout()
        SetColumnLayout(ColumnLayout_Label)
        ColumnLayout_Label.addWidget(Label)
        Layouts += [ColumnLayout_Label]
        ColumnWidth += [None]

        CheckBox = QCheckBox()
        CheckBox.setChecked(False)
        ColumnLayout_CheckBox = QHBoxLayout()
        SetColumnLayout(ColumnLayout_CheckBox)
        ColumnLayout_CheckBox.addWidget(CheckBox)
        ColumnLayout_CheckBox.setAlignment(Qt.AlignCenter)
        Layouts += [ColumnLayout_CheckBox]
        ColumnWidth += [RowHeight]

        TargetRow = self.currentRow() + 1
        ColumnCount = self.columnCount()
        self.insertRow(TargetRow)
        for ColumnCount in range(ColumnCount):
            self.setCellWidget(TargetRow, ColumnCount, QWidget())
            self.cellWidget(TargetRow, ColumnCount).setLayout(Layouts[ColumnCount])
            self.setColumnWidth(ColumnCount, ColumnWidth[ColumnCount]) if ColumnWidth[ColumnCount] is not None else None
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

    def GetValue(self):
        ValueDict = {}
        for colCount in range(self.columnCount() - 2): # Remve last 2 (taskstatus&checkbox) columns
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

    def GetCheckedCaseInfos(self):
        CheckedCaseInfos = []
        CheckBoxCol = self.columnCount() - 1
        CaseCMDCol = self.columnCount() - 3
        CaseNameCol = 1
        for row in range(self.rowCount()):
            if self.cellWidget(row, CheckBoxCol).findChild(QCheckBox).isChecked():
                CheckedCaseInfos.append([row, self.cellWidget(row, CaseCMDCol).findChild(QLabel).text(), self.cellWidget(row, CaseNameCol).findChild(QLabel).text()])
        return CheckedCaseInfos

    def SetCheckedCaseStatus(self, CaseRow: int, Status: str = ...):
        CheckedCaseCol= self.columnCount() - 2
        self.cellWidget(CaseRow, CheckedCaseCol).findChild(QLabel).setText(Status)

##############################################################################################################################