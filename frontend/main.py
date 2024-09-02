# -*- coding: utf-8 -*-

import os
import sys
import re
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
from config import CurrentDir

##############################################################################################################################

TypeDict = {
    'chkHua': '检查花屏',
    'chkB_ok_W': '检查黑白',
    'chkSplit_then_BokW': '分屏+检查黑白',
    'chkNobarSplit_then_BW': '无bar分屏+检查黑白',
    'chkBlackback': '桌面来电底色'
}


def Request(
    protocol: str = 'http',
    ip: str = 'localhost',
    port: int = 8080,
    CaseCMD: str = ...,
    SaveDir_PC: str = ...,
    types: list[str] = ...,
    output_folder: str = ...,
):
    URL = f"{protocol}://{ip}:{port}/execute"
    Payload = {
        'CaseCMD': CaseCMD,
        'SaveDir_PC': SaveDir_PC,
        'chkHua': TypeDict['chkHua'] in types,
        'chkB_ok_W': TypeDict['chkB_ok_W'] in types,
        'chkSplit_then_BokW': TypeDict['chkNobarSplit_then_BW'] in types,
        'chkNobarSplit_then_BW': TypeDict['chkNobarSplit_then_BW'] in types,
        'chkBlackback': TypeDict['chkBlackback'] in types,
        'output_folder': output_folder
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
                        result = parsed_content['message']
                        return result, response.status_code
                    except:
                        continue
        else:
            return "Request failed", response.status_code


class Thread(QThread):
    dictReceived = Signal(dict)
    def __init__(self,
        protocol: str = 'http',
        ip: str = 'localhost',
        port: int = 8080,
        CaseCMD: str = ...,
        SaveDir_PC: str = ...,
        types: list[str] = ...,
        output_folder: str = ...,
    ):
        super().__init__()

        self.protocol = protocol
        self.ip = ip
        self.port = port
        self.CaseCMD = CaseCMD
        self.SaveDir_PC = SaveDir_PC
        self.types = types
        self.output_folder = output_folder

    def run(self):
        result, statuscode = Request(
            protocol = self.protocol,
            ip = self.ip,
            port = self.port,
            CaseCMD = self.CaseCMD,
            SaveDir_PC = self.SaveDir_PC,
            types = self.types,
            output_folder = self.output_folder
        )
        self.dictReceived.emit(result)

##############################################################################################################################

class MainWindow(Window_MainWindow):

    CaseDict = {}

    ResultDict = {}

    def __init__(self):
        super().__init__()

    def updateCaseDict(self, CaseRow, SaveDir_PC):
        self.CaseDict[CaseRow] = SaveDir_PC

    def loadCaseDict(self):
        SaveRoot_PC = self.ui.LineEdit_pcSaveLoc.text()
        for DirName in os.listdir(SaveRoot_PC):
            match = re.match(r'\[.*\]', DirName)
            if match is None:
                continue
            CaseModule, CaseName = match.group(0).strip('[').strip(']'), DirName.replace(match.group(0), "")
            CaseRow = self.ui.Table.FindRow(CaseModule, CaseName)
            if CaseRow is None:
                continue
            self.updateCaseDict(CaseRow, Path(SaveRoot_PC).joinpath(DirName).as_posix())

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
                df.fillna("", inplace=True)
            except Exception as e:
                print(f"读取Excel文件时出错: {e}")
            else:
                # 导入Excel数据到表格
                self.import_data_to_table(df)
                self.export_data_to_sqlite()
                # 加载CaseDict
                self.loadCaseDict()

    def getCheckedCaseInfo(self):
        CheckedCaseInfo = self.ui.Table.GetCheckedCaseInfos(AllowMultiple = False)[0]
        if isinstance(CheckedCaseInfo, Exception):
            QMessageBox.critical(self, "错误", f"{CheckedCaseInfo}")
            return
        CaseRow, CaseCMD, CaseName = CheckedCaseInfo
        return CaseRow, CaseCMD, CaseName

    def Execute(self):
        CheckedCaseInfo = self.getCheckedCaseInfo()
        if CheckedCaseInfo is None:
            return
        CaseRow, CaseCMD, CaseName = CheckedCaseInfo
        if CaseCMD.strip().lower() in ("nan", ""):
            return
        SaveRoot_PC = self.ui.LineEdit_pcSaveLoc.text()
        SaveDir_PC = Path(SaveRoot_PC).joinpath(CaseName).as_posix()
        ChkTypes = self.ui.Table.GetCaseChkTypes(CaseRow)
        output_folder = SaveDir_PC
        # Update CaseDict
        self.updateCaseDict(CaseRow, SaveDir_PC)
        # Start thread
        self.Thread = Thread(
            'http',
            'localhost',
            8080,
            CaseCMD,
            SaveDir_PC,
            ChkTypes,
            output_folder,
        )
        self.Thread.finished.connect(
            lambda: (
                self.ui.Table.SetCheckedCaseStatus(CaseRow, Status = "完成"),
                self.ui.ProgressBar_adbExec.setRange(0, 100),
                self.ui.ProgressBar_adbExec.setValue(100),
            )
        )
        self.Thread.dictReceived.connect(
            lambda dict: (
                self.updateResultDict(CaseName, dict),
                self.CheckAnalysationOutput()
            )
        )
        self.Thread.start()
        self.ui.ProgressBar_adbExec.setRange(0, 0)

    def updateResultDict(self, CaseName: str, result: dict):
        for key, value in result.copy().items():
            result.pop(key) if len(value) == 0 else None
        self.ResultDict[CaseName] = result

    def CheckadbOutput(self):
        CheckedCaseInfo = self.getCheckedCaseInfo()
        if CheckedCaseInfo is None:
            return
        CaseRow, CaseCMD, CaseName = CheckedCaseInfo
        SaveDir_PC = self.CaseDict[CaseRow]
        try:
            os.startfile(SaveDir_PC)
        except:
            QMessageBox.critical(self, "错误", f"无法打开目录: {SaveDir_PC}")
            return

    def CheckAnalysationOutput(self):
        CheckedCaseInfo = self.getCheckedCaseInfo()
        if CheckedCaseInfo is None:
            return
        CaseRow, CaseCMD, CaseName = CheckedCaseInfo
        imageDict = self.ResultDict[CaseName]
        '''
        imageWindow = ImageWindow(imageDict)
        imageWindow.show()
        '''
        print(imageDict)

    def Main(self):
        self.setWindowTitle("Excel Data to Table")

        self.ui.Label_pcSaveLoc.setText('输出位置')
        self.ui.LineEdit_pcSaveLoc.setText(Path(CurrentDir).parent.joinpath('vids').as_posix())

        self.ui.Label_dbName.setText('数据库名')
        self.ui.LineEdit_dbName.setText("db_1")

        self.ui.Button_LoadData.setText("打开Excel文件")
        self.ui.Button_LoadData.clicked.connect(self.open_excel_file)

        self.ui.Button_Exec.setText("执行测试")
        self.ui.Button_Exec.clicked.connect(self.Execute)
        self.ui.ProgressBar_adbExec.setTextVisible(False)

        self.ui.Button_ViewOutput.setText("查看输出")
        self.ui.Button_ViewOutput.clicked.connect(self.CheckadbOutput)

        self.ui.Button_ViewResult.setText("查看结果")
        self.ui.Button_ViewResult.clicked.connect(self.CheckAnalysationOutput)

        self.show()

##############################################################################################################################

if __name__ == '__main__':
    App = QApplication(sys.argv)

    window = MainWindow()
    window.Main()

    sys.exit(App.exec())

##############################################################################################################################