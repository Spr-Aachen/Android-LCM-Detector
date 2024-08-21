# -*- coding: utf-8 -*-

import os
import sys
import json
import socket
import struct
import pandas
from pathlib import Path
from subprocess import Popen
from typing import Optional
from sqlalchemy import create_engine
from PySide6.QtCore import Qt, QObject, Signal, Slot, QThread
from PySide6.QtGui import QTextCursor, QAction, QStandardItem
from PySide6.QtWidgets import *

from windows.Windows import *
from functions import Function_SetMethodExecutor
from config import CurrentDir, ConfigDir

##############################################################################################################################

def adbExec(
    TaskCMD: str = "adb shell am instrument -w -r -e debug false -e class",
    SaveName: str = "lcm",
    SaveLoc_PC: str = "D:/"
):
    adbreboot = Popen(
        "adb kill-server && adb start-server",
        shell = True
    )
    adbreboot.wait()
    SaveLoc_AD = f"/sdcard/{SaveName}.mp4"
    adb1 = Popen(
        f"adb shell screenrecord {SaveLoc_AD} --time-limit 360",
        shell = True
    )
    adb2 = Popen(
        TaskCMD,
        shell = True
    )
    adb2.wait()
    adb1.kill()
    adb3 = Popen(
        f"adb pull {SaveLoc_AD} {SaveLoc_PC}",
    )
    adb3.wait()


class adbThread(QThread):
    def __init__(self):
        super().__init__()

    @Slot(tuple)
    def Execute(self, Params: tuple):
        adbExec(*Params)

##############################################################################################################################

class MainWindow(Window_MainWindow):
    def __init__(self):
        super().__init__()

    def import_data_to_table(self, df: pandas.DataFrame):
        # 清空表格
        '''
        self.ui.Table.clearContents()
        '''
        while self.ui.Table.rowCount() > 0:
            self.ui.Table.removeRow(0)
        '''
        # 设置行列数
        self.ui.Table.setRowCount(len(df))
        self.ui.Table.setColumnCount(len(df.columns) + 1)
        '''
        # 填充数据
        '''
        for row_idx in range(len(df)):
            for col_idx in range(len(df.columns)):
                item = QTableWidgetItem(str(df.iloc[row_idx][col_idx]))
                self.ui.Table.setItem(row_idx, col_idx, item)
        '''
        self.ui.Table.SetValue(
            df.to_dict(orient='list')
        )

    def export_data_to_sqlite(self):
        # 提取表格数据到列表
        '''
        data = []
        for row in range(self.ui.Table.rowCount()):
            row_data = []
            for column in range(self.ui.Table.columnCount()):
                item = self.ui.Table.item(row, column)
                if item is not None:
                    row_data.append(item.text())
                else:
                    row_data.append('')  # 或者你喜欢的其他默认值
            data.append(row_data)
        '''
        data = self.ui.Table.GetValue()
        # 将列表转为DataFrame
        df = pandas.DataFrame(data)
        # 创建SQLite数据库引擎
        dbname = "db_1"
        engine = create_engine(f'sqlite:///{dbname}.db')
        # 将DataFrame写入SQLite数据库
        df.to_sql(
            name = dbname,
            con = engine,
            if_exists = 'replace',
            index = False
        )
        QMessageBox.information(self, "完成", "数据已成功写入SQLite数据库。")

    def open_excel_file(self):
        # 弹出文件选择对话框
        file_path, _ = QFileDialog.getOpenFileName(self,
            caption = "打开Excel文件",
            dir = "",
            filter = "Excel Files (*.xlsx *.xls)"
        )
        sheet_name, ok = QInputDialog.getText(self,
            "子表名称",
            "请输入子表名称，若没有子表则留空",
            text = "场景测试用例"
        )
        if file_path:
            try:
                # 使用pandas读取Excel文件
                df = pandas.read_excel(file_path, sheet_name = sheet_name) if ok and len(sheet_name) > 0 else pandas.read_excel(file_path)
            except Exception as e:
                print(f"读取Excel文件时出错: {e}")
            else:
                # 导入Excel数据到表格
                self.import_data_to_table(df)
                self.export_data_to_sqlite()

    def startThread(self, CaseCMD: str, CaseRow: str, CaseName: str):
        if CaseCMD.strip().lower() in ("nan", ""):
            return
        SaveName = CaseName
        SaveLoc_PC = 'D:/' #SaveLoc_PC = self.ui.LineEdit_SaveLoc_PC.text()
        Function_SetMethodExecutor(self,
            Method = adbThread.Execute,
            Params = (CaseCMD, SaveName, SaveLoc_PC),
            FinishEvent = lambda: self.ui.Table.SetCheckedCaseStatus(CaseRow, Status = "完成")
        )

    def ExecuteADB(self):
        for CaseInfo in self.ui.Table.GetCheckedCaseInfos():
            CaseRow, CaseCMD, CaseName = CaseInfo
            self.startThread(CaseCMD, CaseRow, CaseName)

    def Main(self):
        self.setWindowTitle("Excel Data to Table")

        self.ui.Button_LoadData.setText("打开Excel文件")
        self.ui.Button_LoadData.clicked.connect(self.open_excel_file)

        self.ui.Button_Execute.setText("执行选中项")
        self.ui.Button_Execute.clicked.connect(self.ExecuteADB)

        self.show()

##############################################################################################################################

if __name__ == '__main__':
    App = QApplication(sys.argv)

    window = MainWindow()
    window.Main()

    sys.exit(App.exec())

##############################################################################################################################