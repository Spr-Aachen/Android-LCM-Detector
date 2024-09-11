# -*- coding: utf-8 -*-

import os
import sys
import re
import json
import hashlib
import requests
import pandas
import sqlalchemy
import redis
from pathlib import Path
from typing import Optional
from datetime import datetime
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
    dictReceived = Signal(dict, bool)

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
        self.dictReceived.emit(result, True if statuscode == 200 else False)


def stopTask(
    protocol: str = 'http',
    ip: str = 'localhost',
    port: Optional[int] = None
):
    with requests.post(
        url = f"{protocol}://{ip}:{port}/stop"
    ) as response:
        return json.loads(response.text) if response.status_code == 200 else "任务未能停止", response.status_code


class Thread_Stop(QThread):
    def __init__(self,
        protocol: str = 'http',
        ip: str = 'localhost',
        port: int = 8080,
    ):
        super().__init__()

        self.protocol = protocol
        self.ip = ip
        self.port = port

    def run(self):
        result, statuscode = stopTask(
            protocol = self.protocol,
            ip = self.ip,
            port = self.port,
        )


def exitService(
    protocol: str = 'http',
    ip: str = 'localhost',
    port: Optional[int] = None
):
    with requests.post(
        url = f"{protocol}://{ip}:{port}/actuator/shutdown"
    ) as response:
        return json.loads(response.text) if response.status_code == 200 else "服务未能关闭", response.status_code

##############################################################################################################################

class MainWindow(Window_MainWindow):
    historydbName = "history"

    excel_path = None
    exceldb_name = None

    CaseDict = {}

    ResultDict = {}

    Thread = None

    def __init__(self):
        super().__init__()

    def updateCaseDict(self, CaseRow, SaveDir_PC):
        self.CaseDict[CaseRow] = SaveDir_PC

    def export_data_to_exceldb(self, df, new = True):
        # 创建excel数据库引擎
        if new:
            self.exceldb_name = f"DB_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        exceldb_engine = sqlalchemy.create_engine(f'sqlite:///{self.exceldb_name}.db')
        # 将DataFrame写入excel数据库
        df.to_sql(
            name = self.exceldb_name,
            con = exceldb_engine,
            if_exists = 'replace',
            index = False
        )

    def add_result_to_exceldb(self):
        df = pandas.DataFrame(self.ui.Table.GetValue())
        # Add result column if value in 'CaseModule'&'CaseName' collumns is in ResultDict
        CaseModuleCol = df.iloc[:, 0]
        CaseNameCol = df.iloc[:, 1]
        Cases = [f"[{CaseModule}]{CaseName}" for CaseModule, CaseName in zip(CaseModuleCol.values, CaseNameCol.values)] # The casename in resultdict is the combinition of CaseModule and CaseName
        CaseCol = pandas.Series(Cases)
        for Case, Result in self.ResultDict.items():
            CaseIndex = CaseCol[CaseCol == Case].index
            df.loc[CaseIndex, 'TestResult'] = str(Result)
            print(f"TEST: Result added to dataframe:\n", df)
        self.export_data_to_exceldb(df, new = False)

    def load_data_from_exceldb(self):
        # 与excel数据库建立连接
        exceldb_engine = sqlalchemy.create_engine(f'sqlite:///{self.exceldb_name}.db')
        df = pandas.read_sql_query(
            f"SELECT * FROM {self.exceldb_name}",
            con = exceldb_engine
        )
        df.fillna("", inplace=True)
        # check if the table has a 'TestResult' column
        if 'TestResult' in df.columns:
            # get the existing values of the 'TestResult' column & update results in ResultDict
            CaseModuleCol = df.iloc[:, 0]
            CaseNameCol = df.iloc[:, 1]
            Cases = [f"[{CaseModule}]{CaseName}" for CaseModule, CaseName in zip(CaseModuleCol.values, CaseNameCol.values)] # The casename in resultdict is the combinition of CaseModule and CaseName
            for Case, Result in zip(Cases, df['TestResult'].values):
                if Result == "":
                    continue
                self.ResultDict[Case] = eval(Result)
            print("TEST: ResultDict updated:", self.ResultDict)
            # remove the 'TestResult' column
            df = df.drop(columns=['TestResult'])
        return df

    def create_historydb(self):
        self.historyEngine = sqlalchemy.create_engine(f'sqlite:///{self.historydbName}.db')
        # 创建table
        if not sqlalchemy.inspect(self.historyEngine).has_table(self.historydbName):
            df = pandas.DataFrame({
                "excel_hash": [],
                "exceldb_name": []
            })
            df.to_sql(
                name = self.historydbName,
                con = self.historyEngine,
                if_exists = 'replace',
                index = False
            )

    def to_historydb(self):
        # 将[表格哈希值,表格数据库名]写入历史记录数据库
        excel_hash = hashlib.md5(open(self.excel_path, 'rb').read()).hexdigest()
        df = pandas.DataFrame({
            "excel_hash": [excel_hash],
            "exceldb_name": [self.exceldb_name]
        })
        df.to_sql(
            name = self.historydbName,
            con = self.historyEngine,
            if_exists = 'append',
            index = False
        )
        # TODO 通过redis建立旁路缓存模式

    def chk_historydb(self):
        # 检查哈希值在数据库中的对应值
        excel_hash = hashlib.md5(open(self.excel_path, 'rb').read()).hexdigest()
        print(f'checking hash {excel_hash} in {self.historydbName}.db')
        df = pandas.read_sql_query(
            f"SELECT * FROM {self.historydbName} WHERE excel_hash = '{excel_hash}'",
            con = self.historyEngine
        )
        exceldb_name = df.iloc[0]["exceldb_name"] if len(df) > 0 else None
        print(f'exceldb name found: {exceldb_name}')
        return exceldb_name

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
            self.excel_path = file_path
            try:
                # 与历史记录数据库建立连接
                self.create_historydb()
                # 检查哈希值是否存在于数据库中，不在则将[表格哈希值,表格数据库名]写入历史记录数据库
                self.exceldb_name = self.chk_historydb()
                if self.exceldb_name is None:
                    # 使用pandas读取Excel文件
                    df = pandas.read_excel(file_path, sheet_name = sheet_name) if ok and len(sheet_name) > 0 else pandas.read_excel(file_path)
                    df.fillna("", inplace=True)
                    # 在表格末端添加一列，用于存储测试状态
                    df['测试状态'] = "未测试"
                    # 将DataFrame写入excel数据库
                    self.export_data_to_exceldb(df, new=True)
                    # 将[表格哈希值,表格数据库名]写入历史记录数据库
                    self.to_historydb()
                else:
                    df = self.load_data_from_exceldb()
            except Exception as e:
                print(f"出错: {e}")
            else:
                # 清空表格
                while self.ui.Table.rowCount() > 0:
                    self.ui.Table.removeRow(0)
                # 填充数据
                self.ui.Table.SetValue(
                    df.to_dict(orient='list')
                )

    def updateResultDict(self, Case: str, result: dict):
        '''
        for key, value in result.copy().items():
            result.pop(key) if len(value) == 0 else None
        '''
        self.ResultDict[Case] = result

    def startThread(self, CheckedCaseInfo):
        CaseRow, CaseCMD, Case = CheckedCaseInfo
        if CaseCMD.strip().lower() in ("nan", ""):
            return
        SaveRoot_PC = self.ui.LineEdit_pcSaveLoc.text()
        SaveDir_PC = Path(SaveRoot_PC).joinpath(Case).as_posix()
        ChkTypes = self.ui.Table.GetCaseChkTypes(CaseRow)
        output_folder = SaveDir_PC
        # Update CaseDict
        self.updateCaseDict(CaseRow, SaveDir_PC)
        # Start thread
        if self.Thread is not None and self.Thread.isRunning():
            self.Thread.terminate()
        self.Thread = Thread(
            'http',
            'localhost',
            8080,
            CaseCMD,
            SaveDir_PC,
            ChkTypes,
            output_folder,
        )
        self.Thread.dictReceived.connect(
            lambda dict, isSucceeded: (
                self.updateResultDict(Case, dict),
                self.ui.Table.SetCaseStatus(CaseRow, Status = "完成" if isSucceeded else "失败"),
                self.add_result_to_exceldb(),
                self.ui.ProgressBar_Exec.setRange(0, 100),
                self.ui.ProgressBar_Exec.setValue(100),
                self.ui.StackedWidget_ExecAndStop.setCurrentWidget(self.ui.StackedWidget_Page_Exec)
            )
        )
        self.Thread.start()
        self.ui.ProgressBar_Exec.setRange(0, 0)
        self.ui.StackedWidget_ExecAndStop.setCurrentWidget(self.ui.StackedWidget_Page_Stop)

    def Execute(self):
        CheckedCaseInfos = self.ui.Table.GetCheckedCaseInfos()
        if len(CheckedCaseInfos) == 0:
            return
        self.CheckedCaseIndex = 0
        self.startThread(CheckedCaseInfos[self.CheckedCaseIndex])
        def startNextThread():
            self.CheckedCaseIndex += 1
            if self.CheckedCaseIndex > len(CheckedCaseInfos)-1:
                return
            self.startThread(CheckedCaseInfos[self.CheckedCaseIndex])
        self.Thread.finished.connect(startNextThread)

    def StopTask(self):
        if self.Thread is not None and self.Thread.isRunning():
            self.Thread.terminate()
            self.Thread.wait()
        self.Thread = Thread_Stop(
            'http',
            'localhost',
            8080,
        )
        self.Thread.finished.connect(
            lambda: (
                self.ui.ProgressBar_Exec.setRange(0, 100),
                self.ui.ProgressBar_Exec.setValue(0),
                self.ui.StackedWidget_ExecAndStop.setCurrentWidget(self.ui.StackedWidget_Page_Exec)
            )
        )
        self.Thread.start()

    def CheckadbOutput(self):
        CheckedCaseInfos = self.ui.Table.GetCheckedCaseInfos()
        if len(CheckedCaseInfos) == 0:
            return
        for CheckedCaseInfo in CheckedCaseInfos:
            CaseRow, CaseCMD, Case = CheckedCaseInfo
            SaveDir_PC = self.CaseDict[CaseRow]
            try:
                os.startfile(SaveDir_PC)
            except:
                QMessageBox.critical(self, "错误", f"无法打开目录: {SaveDir_PC}")
                return

    def CheckAnalysationOutput(self, CaseRow):
        CaseCMD, Case, CaseStatus = self.ui.Table.GetCaseInfo(CaseRow)
        if CaseStatus != "完成":
            return
        imageDict = self.ResultDict[Case]
        imageWindow = ImageWindow(imageDict)
        imageWindow.show()

    def closeEvent(self, event):
        exitService(
            protocol = 'http',
            ip = 'localhost',
            port = 8080,
        )
        event.accept()

    def Main(self):
        self.setWindowTitle("Excel Data to Table")

        self.ui.Label_pcSaveLoc.setText('输出位置')
        self.ui.LineEdit_pcSaveLoc.setText(Path(CurrentDir).parent.joinpath('vids').as_posix())

        self.ui.Button_LoadData.setText("打开Excel文件")
        self.ui.Button_LoadData.clicked.connect(self.open_excel_file)

        self.ui.Button_Exec.setText("执行测试用例")
        self.ui.Button_Exec.clicked.connect(self.Execute)
        self.ui.Button_Stop.setText("停止")
        self.ui.Button_Stop.clicked.connect(self.StopTask)
        self.ui.ProgressBar_Exec.setTextVisible(False)

        #self.ui.Button_ViewOutput.setText("查看输出")
        self.ui.Button_ViewOutput.clicked.connect(self.CheckadbOutput)

        self.ui.Table.onButtonClicked.connect(self.CheckAnalysationOutput)

        self.show()

##############################################################################################################################

if __name__ == '__main__':
    App = QApplication(sys.argv)

    window = MainWindow()
    window.Main()

    sys.exit(App.exec())

##############################################################################################################################