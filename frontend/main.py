# -*- coding: utf-8 -*-

import os
import sys
import json
import requests
import pandas
from pathlib import Path
from typing import Optional
from sqlalchemy import create_engine
from PySide6.QtCore import Qt, QObject, Signal, Slot, QThread
from PySide6.QtGui import QTextCursor, QAction, QStandardItem
from PySide6.QtWidgets import *

from windows.Windows import *
from functions import RenameIfExists
from config import CurrentDir

##############################################################################################################################

def adbRequest(
    protocol: str = 'http',
    ip: str = 'localhost',
    port: int = 8080,
    CaseCMD: str = ...,
    SaveRoot_PC: str = ...,
    SaveName_PC: str = ...
):
    URL = f"{protocol}://{ip}:{port}/execute_adb"
    Payload = {
        'CaseCMD': CaseCMD,
        'SaveRoot_PC': SaveRoot_PC,
        'SaveName_PC': SaveName_PC
    }
    with requests.post(
        url = URL,
        data = json.dumps(Payload)
    ) as response:
        if response.status_code == 200:
            for chunk in response.iter_content(chunk_size = None, decode_unicode = False):
                if chunk:
                    content = chunk.decode('utf-8', errors = 'ignore')
                    try:
                        parsed_content = json.loads(content)
                        result = parsed_content['data']
                        return result, response.status_code
                    except:
                        continue
        else:
            return "Request failed", response.status_code


class adbThread(QThread):
    def __init__(self):
        super().__init__()

    def run(self, *Params):
        print(*Params)
        adbRequest(*Params)

##############################################################################################################################

TypeDict = {
    'chkHua': '检查花屏',
    'chkB_ok_W': '检查黑白',
    'chkSplit_then_BokW': '分屏+检查黑白',
    'chkNobarSplit_then_BW': '无bar分屏+检查黑白',
    'chkBlackback': '桌面来电底色'
}

def analysationRequest(
    protocol: str = 'http',
    ip: str = 'localhost',
    port: int = 8080,
    file: str = ...,
    types: list[str] = ...,
):
    URL = f"{protocol}://{ip}:{port}/analysis_video"
    Payload = {
        'file': file,
        'chkHua': TypeDict['chkHua'] in types,
        'chkB_ok_W': TypeDict['chkB_ok_W'] in types,
        'chkSplit_then_BokW': TypeDict['chkNobarSplit_then_BW'] in types,
        'chkNobarSplit_then_BW': TypeDict['chkNobarSplit_then_BW'] in types,
        'chkBlackback': TypeDict['chkBlackback'] in types
    }
    with requests.post(
        url = URL,
        data = json.dumps(Payload),
    ) as response:
        if response.status_code == 200:
            for chunk in response.iter_content(chunk_size = None, decode_unicode = False):
                if chunk:
                    content = chunk.decode('utf-8', errors = 'ignore')
                    try:
                        parsed_content = json.loads(content)
                        results = dict(parsed_content)
                        for key, value in results.items():
                            results.pop(key) if len(value) == 0 else None
                        return results, response.status_code
                    except:
                        continue
        else:
            return "Request failed", response.status_code


class analysationThread(QThread):
    dictReceived = Signal(dict)

    def __init__(self):
        super().__init__()

    def run(self, *Params):
        results, statuscode = analysationRequest(*Params)
        self.dictReceived.emit(results)

##############################################################################################################################

class MainWindow(Window_MainWindow):

    CaseDict = {}

    def __init__(self):
        super().__init__()

    def import_data_to_table(self, df: pandas.DataFrame):
        # 清空表格
        while self.ui.Table.rowCount() > 0:
            self.ui.Table.removeRow(0)
        # 填充数据
        self.ui.Table.SetValue(
            df.to_dict(orient='list')
        )

    def export_data_to_sqlite(self):
        # 提取表格数据到列表
        data = self.ui.Table.GetValue()
        # 将列表转为DataFrame
        df = pandas.DataFrame(data)
        # 创建SQLite数据库引擎
        dbname = self.ui.LineEdit_dbName.text()
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

    def ExecuteADB(self):
        CheckedCaseInfo = self.ui.Table.GetCheckedCaseInfos(AllowMultiple = False)[0]
        if isinstance(CheckedCaseInfo, Exception):
            QMessageBox.critical(self, "错误", f"{CheckedCaseInfo}")
            return
        CaseRow, CaseCMD, CaseName = CheckedCaseInfo
        if CaseCMD.strip().lower() in ("nan", ""):
            return
        SaveRoot_PC = self.ui.LineEdit_pcSaveLoc.text()
        SaveName_PC = CaseName
        SaveDir_PC = RenameIfExists(Path(SaveRoot_PC).joinpath(SaveName_PC).as_posix())
        self.CaseDict[CaseRow] = SaveDir_PC
        thread = adbThread()
        thread.finished.connect(
            lambda: (
                self.ui.Table.SetCheckedCaseStatus(CaseRow, Status = "完成"),
                self.ui.ProgressBar_adbExec.setRange(0, 100),
                self.ui.ProgressBar_adbExec.setValue(100),
                self.ui.StackedWidget_adbExec.setCurrentWidget(self.ui.Page_adbExecButton)
            )
        )
        thread.run(
            'http',
            'localhost',
            8080,
            CaseCMD,
            SaveRoot_PC,
            SaveName_PC
        )
        self.ui.ProgressBar_adbExec.setRange(0, 0)
        self.ui.StackedWidget_adbExec.setCurrentWidget(self.ui.Page_adbExecProgressBar)

    def ExecuteAnalysation(self):
        CheckedCaseInfo = self.ui.Table.GetCheckedCaseInfos(AllowMultiple = False)[0]
        if isinstance(CheckedCaseInfo, Exception):
            QMessageBox.critical(self, "错误", f"{CheckedCaseInfo}")
            return
        CaseRow, CaseCMD, CaseName = CheckedCaseInfo
        SaveRoot_PC = self.ui.LineEdit_pcSaveLoc.text()
        SaveDir_PC = self.CaseDict[CaseRow]
        SaveName_PC = Path(SaveDir_PC).name
        for DirName in os.listdir(SaveRoot_PC):
            if DirName != SaveName_PC:
                continue
            for FileName in os.listdir(SaveDir_PC):
                if not FileName.endswith(".mp4"):
                    continue
                isLast = FileName == os.listdir(SaveDir_PC)[-1]
                thread = analysationThread()
                thread.dictReceived.connect(
                    lambda dict: 
                )
                thread.finished.connect(
                    lambda: (
                        self.ui.ProgressBar_Analyse.setRange(0, 100),
                        self.ui.ProgressBar_Analyse.setValue(100),
                        self.ui.StackedWidget_Analyse.setCurrentWidget(self.ui.Page_adbExecButton)
                    )
                ) if isLast else None
                thread.run(
                    'http',
                    'localhost',
                    8080,
                    Path(SaveDir_PC).joinpath(FileName).as_posix(),
                    self.ui.Table.GetAnalysationTypes(CaseRow)
                )
            self.ui.ProgressBar_Analyse.setRange(0, 0)
            self.ui.StackedWidget_Analyse.setCurrentWidget(self.ui.Page_adbExecProgressBar)
            break

    def CheckadbOutput(self):
        CheckedCaseInfo = self.ui.Table.GetCheckedCaseInfos(AllowMultiple = False)[0]
        if isinstance(CheckedCaseInfo, Exception):
            QMessageBox.critical(self, "错误", f"{CheckedCaseInfo}")
            return
        CaseRow, CaseCMD, CaseName = CheckedCaseInfo
        SaveDir_PC = self.CaseDict[CaseRow]
        try:
            os.startfile(SaveDir_PC)
        except:
            QMessageBox.critical(self, "错误", f"无法打开目录: {SaveDir_PC}")
            return

    def CheckAnalysationOutput(self):
        CheckedCaseInfo = self.ui.Table.GetCheckedCaseInfos(AllowMultiple = False)[0]
        if isinstance(CheckedCaseInfo, Exception):
            QMessageBox.critical(self, "错误", f"{CheckedCaseInfo}")
            return
        CaseRow, CaseCMD, CaseName = CheckedCaseInfo
        SaveDir_PC = self.CaseDict[CaseRow]
        

    def Main(self):
        self.setWindowTitle("Excel Data to Table")

        self.ui.Label_pcSaveLoc.setText('输出位置')
        self.ui.LineEdit_pcSaveLoc.setText(Path(CurrentDir).parent.joinpath('vids').as_posix())

        self.ui.Label_dbName.setText('数据库名')
        self.ui.LineEdit_dbName.setText("db_1")

        self.ui.Button_LoadData.setText("打开Excel文件")
        self.ui.Button_LoadData.clicked.connect(self.open_excel_file)

        self.ui.Button_adbExec.setText("执行测试")
        self.ui.Button_adbExec.clicked.connect(self.ExecuteADB)
        self.ui.ProgressBar_adbExec.setTextVisible(False)

        self.ui.Button_adbOutput.setText("测试结果")
        self.ui.Button_adbOutput.clicked.connect(self.CheckadbOutput)

        self.ui.Button_Analyse.setText("执行分析")
        self.ui.Button_Analyse.clicked.connect(self.ExecuteAnalysation)
        self.ui.ProgressBar_Analyse.setRange(0, 100)
        self.ui.ProgressBar_Analyse.setTextVisible(False)

        self.ui.Button_AnalysationOutput.setText("分析结果")
        self.ui.Button_AnalysationOutput.clicked.connect(self.CheckAnalysationOutput)

        self.show()

##############################################################################################################################

if __name__ == '__main__':
    App = QApplication(sys.argv)

    window = MainWindow()
    window.Main()

    sys.exit(App.exec())

##############################################################################################################################