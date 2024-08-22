# -*- coding: utf-8 -*-

import os
import sys
import json
import socket
import struct
import pandas
import subprocess
import threading
from pathlib import Path
from typing import Optional
from sqlalchemy import create_engine
from PySide6.QtCore import Qt, QObject, Signal, Slot, QThread
from PySide6.QtGui import QTextCursor, QAction, QStandardItem
from PySide6.QtWidgets import *

from windows.Windows import *
from functions import Function_SetMethodExecutor
from config import CurrentDir

##############################################################################################################################

def Reboot():
    adbReboot = subprocess.Popen(
        "adb kill-server && adb start-server",
        shell = True
    )
    return adbReboot


def Pull(
    SavePath_AD: str,
    SaveDir_PC: str
):
    adb3 = subprocess.Popen(
        f"adb pull {SavePath_AD} {SaveDir_PC}",
        shell = True
    )
    return adb3


adbRecord = None
StopEvent = None
def RecordAndPull(
    SavePath_AD: str,
    SaveDir_PC: str,
    RecPeriod: int = 180,
):
    global adbRecord
    global StopEvent
    i = 0
    while not StopEvent.is_set():
        adbRecord = subprocess.Popen(
            f"adb shell screenrecord {SavePath_AD} --time-limit {RecPeriod}",
            shell = True
        )
        adbRecord.wait()
        adbPull = Pull(SavePath_AD, SaveDir_PC)
        adbPull.wait()
        i += 1
        OldName = Path(SaveDir_PC).joinpath(Path(SavePath_AD).name).as_posix()
        NewName = Path(SaveDir_PC).joinpath(f"{i}.{Path(SavePath_AD).suffix}").as_posix()
        os.rename(OldName, NewName)


def adbExec(
    TaskCMD: str = "adb shell am instrument -w -r -e debug false -e class",
    SaveRoot_PC: str = "D:/",
    SaveName_PC: str = "用例名",
    RecPeriod: int = 180,
):
    global adbRecord
    global StopEvent

    # Set the save location
    SavePath_AD = "/sdcard/testcase.mp4"
    SaveDir_PC = Path(SaveRoot_PC).joinpath(SaveName_PC).as_posix()
    Path(SaveDir_PC).mkdir(parents = True) if not Path(SaveDir_PC).exists() else None

    # Reboot server
    adbReboot = Reboot()
    adbReboot.wait()

    # Event to signal the recording thread to stop
    StopEvent = threading.Event()

    # Start the screen recording thread
    recordingThread = threading.Thread(
        target = RecordAndPull,
        args = (SavePath_AD, SaveDir_PC, RecPeriod,)
    )
    recordingThread.start()

    # Execute the main task
    adbTask = subprocess.Popen(
        TaskCMD,
        shell = True
    )
    adbTask.wait()

    # Signal the recording thread to stop and wait for it to finish
    StopEvent.set()
    if adbRecord is not None:
        adbRecord.terminate()
    recordingThread.join()


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
        SaveRoot_PC = Path(CurrentDir).parent.as_posix() #SaveRoot_PC = self.ui.LineEdit_SaveRootPC.text()
        SaveName_PC = CaseName
        Function_SetMethodExecutor(self,
            Method = adbThread.Execute,
            Params = (CaseCMD, SaveRoot_PC, SaveName_PC),
            FinishEvent = lambda: self.ui.Table.SetCheckedCaseStatus(CaseRow, Status = "完成")
        )

    def ExecuteADB(self):
        CheckedCaseInfos = self.ui.Table.GetCheckedCaseInfos()
        if isinstance(CheckedCaseInfos, Exception):
            QMessageBox.critical(self, "错误", f"{CheckedCaseInfos}")
            return
        for CaseInfo in CheckedCaseInfos:
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