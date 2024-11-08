# -*- coding: utf-8 -*-

import os
import sys
import argparse
import json
import requests
import polars
from pathlib import Path
from typing import Optional
from PySide6.QtCore import Qt, QObject, Signal, Slot, QThread
from PySide6.QtWidgets import *
from QEasyWidgets import ComponentsSignals, Theme, EasyTheme, IconBase
from QEasyWidgets import QFunctions as QFunc

from windows.Windows import *
from functions import *
from config import CurrentDir, ResourceDir

##############################################################################################################################

# 启动参数解析，启动环境，应用端口由命令行传入
parser = argparse.ArgumentParser()
parser.add_argument("--profiledir", help = "配置目录", type = str, default = Path(CurrentDir).joinpath('Profile').as_posix())
args = parser.parse_args()

ProfileDir = args.profiledir
ConfigDir = Path(ProfileDir).joinpath('Config').as_posix()

##############################################################################################################################

TypeDict = {
    '检查花屏': 'chkHua',
    '检查黑白': 'chkB_ok_W',
    '分屏+检查黑白': 'chkSplit_then_BokW',
    '无bar分屏+检查黑白': 'chkNobarSplit_then_BW',
    '桌面来电底色': 'chkBlackback'
}


def Upload(
    protocol: str = 'http',
    ip: str = 'localhost',
    port: int = 8080,
    filePaths: Union[list, str] = ...,
):
    URL = f"{protocol}://{ip}:{port}/upload"
    files = [{"file": (Path(filePath).name, open(filePath, "rb"), 'application/json')} for filePath in QFunc.ToIterable(filePaths)]
    response = requests.post(
        url = URL,
        files = files
    )
    return json.loads(response.text) if response.status_code == 200 else "文件上传失败", response.status_code


class Thread_Upload(QThread):
    def __init__(self,
        protocol: str = 'http',
        ip: str = 'localhost',
        port: int = 8080,
        filePath: str = ...
    ):
        super().__init__()

        self.protocol = protocol
        self.ip = ip
        self.port = port
        self.filePath = filePath

    def run(self):
        result, statuscode = Upload(
            protocol = self.protocol,
            ip = self.ip,
            port = self.port,
            filePath = self.filePath
        )


def ExecuteAnalyser(
    protocol: str = 'http',
    ip: str = 'localhost',
    port: int = 8080,
    fileName: str = ...,
    types: list[str] = ...,
):
    URL = f"{protocol}://{ip}:{port}/execute_analyser"
    Payload = {
        'fileName': fileName,
        'chkTypes': [TypeDict[type] for type in types],
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


class Thread_ExecuteAnalyser(QThread):
    dictReceived = Signal(dict, bool)

    def __init__(self,
        protocol: str = 'http',
        ip: str = 'localhost',
        port: int = 8080,
        fileName: str = ...,
        types: list[str] = ...,
    ):
        super().__init__()

        self.protocol = protocol
        self.ip = ip
        self.port = port
        self.fileName = fileName
        self.types = types

    def run(self):
        result, statuscode = ExecuteAnalyser(
            protocol = self.protocol,
            ip = self.ip,
            port = self.port,
            fileName = self.fileName,
            types = self.types,
        )
        self.dictReceived.emit(result, True if statuscode == 200 else False)


def Execute(
    protocol: str = 'http',
    ip: str = 'localhost',
    port: int = 8080,
    caseCMD: str = ...,
    types: list[str] = ...,
    outputFolder: str = ...,
):
    URL = f"{protocol}://{ip}:{port}/execute"
    Payload = {
        'caseCMD': caseCMD,
        'chkTypes': [TypeDict[type] for type in types],
        'outputFolder': outputFolder
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


class Thread_Execute(QThread):
    dictReceived = Signal(dict, bool)

    def __init__(self,
        protocol: str = 'http',
        ip: str = 'localhost',
        port: int = 8080,
        caseCMD: str = ...,
        saveDir_PC: str = ...,
        types: list[str] = ...,
        outputFolder: str = ...,
    ):
        super().__init__()

        self.protocol = protocol
        self.ip = ip
        self.port = port
        self.caseCMD = caseCMD
        self.saveDir_PC = saveDir_PC
        self.types = types
        self.outputFolder = outputFolder

    def run(self):
        result, statuscode = Execute(
            protocol = self.protocol,
            ip = self.ip,
            port = self.port,
            caseCMD = self.caseCMD,
            saveDir_PC = self.saveDir_PC,
            types = self.types,
            outputFolder = self.outputFolder
        )
        self.dictReceived.emit(result, True if statuscode == 200 else False)
        # TODO: unpack zipfile to saveDir_PC


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
        return

##############################################################################################################################

class MainWindow(Window_MainWindow):
    caseDict = {}

    resultDict = {}

    Thread = None

    def __init__(self):
        super().__init__()

        self.sqlManager = QFunc.ManageSQL()

    def updateCaseDict(self, caseRow, saveDir_PC):
        self.caseDict[caseRow] = saveDir_PC

    def add_result_to_exceldb(self):
        df = polars.DataFrame(self.ui.Table.getValue())
        # Add result column if value in 'CaseModule'&'CaseName' collumns is in resultDict
        CaseModuleCol = df.get_columns()[0]
        CaseNameCol = df.get_columns()[1]
        Cases = [f"[{CaseModule}]{CaseName}" for CaseModule, CaseName in zip(CaseModuleCol, CaseNameCol)] # The casename in resultdict is the combinition of CaseModule and CaseName
        for case, Result in self.resultDict.items():
            CaseIndex = Cases.index(case)
            df.insert_column(len(df.columns), polars.Series('TestResult', [""] * len(df))) if 'TestResult' not in df.columns else None
            df[CaseIndex, 'TestResult'] = str(Result)
            print(f"TEST: Result added to dataframe:\n", df)
        self.sqlManager.export_data_to_filedb(df, new = False)

    def load_data_from_exceldb(self):
        # 与excel数据库建立连接
        df = self.sqlManager.load_data_from_filedb()
        # check if the table has a 'TestResult' column
        if 'TestResult' in df.columns:
            # get the existing values of the 'TestResult' column & update results in resultDict
            CaseModuleCol = df.get_columns()[0]
            CaseNameCol = df.get_columns()[1]
            Cases = [f"[{CaseModule}]{CaseName}" for CaseModule, CaseName in zip(CaseModuleCol, CaseNameCol)] # The casename in resultdict is the combinition of CaseModule and CaseName
            for case, Result in zip(Cases, df['TestResult'].to_list()):
                if Result == "":
                    continue
                self.resultDict[case] = eval(Result)
            print("TEST: resultDict updated:", self.resultDict)
            # remove the 'TestResult' column
            df = df.drop(['TestResult'])
        return df

    def open_excel_file(self):
        # 弹出文件选择对话框
        filePath, _ = QFileDialog.getOpenFileName(self,
            caption = "打开Excel文件",
            dir = "",
            filter = "Excel Files (*.xlsx *.xls)"
        )
        if len(filePath.strip()) == 0:
            return
        sheetName, ok = QInputDialog.getText(self,
            "子表名称",
            "请输入子表名称，若没有子表则留空",
            text = "场景测试用例"
        )
        self.sqlManager.filePath = filePath
        try:
            # 与历史记录数据库建立连接
            self.sqlManager.create_historydb()
            # 检查哈希值是否存在于数据库中，不在则将[表格哈希值,表格数据库名]写入历史记录数据库
            self.sqlManager.filedb_name = self.sqlManager.chk_historydb()
            if self.sqlManager.filedb_name is None:
                # 使用polars读取Excel文件
                df = polars.read_excel(filePath, sheet_name = sheetName) if ok and len(sheetName) > 0 else polars.read_excel(filePath)
                df.fill_nan("")
                # 在表格末端添加一列，用于存储测试状态
                df.insert_column(len(df.columns), polars.Series('测试状态', ["未测试"] * len(df)))
                # 将DataFrame写入excel数据库
                self.sqlManager.export_data_to_filedb(df, new=True)
                # 将[表格哈希值,表格数据库名]写入历史记录数据库
                self.sqlManager.to_historydb()
            else:
                df = self.load_data_from_exceldb()
        except Exception as e:
            print(f"出错: {e}")
        else:
            # 清空表格
            while self.ui.Table.rowCount() > 0:
                self.ui.Table.removeRow(0)
            # 填充数据
            self.ui.Table.setValue(
                df.to_dict(as_series=False)
            )

    def startAnalyseThread(self, fileName, ChkTypes):
        if QMessageBox.question(self, '提示', '是否开始分析？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.No:
            return
        # Start thread
        if self.Thread is not None and self.Thread.isRunning():
            self.Thread.terminate()
        self.Thread = Thread_ExecuteAnalyser(
            'http',
            'localhost',
            8080,
            fileName,
            ChkTypes,
        )
        self.Thread.dictReceived.connect(
            lambda dict, isSucceeded: (
                self.ui.ProgressBar_Exec.setRange(0, 100),
                self.ui.ProgressBar_Exec.setValue(100),
                self.ui.StackedWidget_ExecAndStop.setCurrentWidget(self.ui.StackedWidget_Page_Exec)
            )
        )
        self.Thread.start()
        self.ui.ProgressBar_Exec.setRange(0, 0)
        self.ui.StackedWidget_ExecAndStop.setCurrentWidget(self.ui.StackedWidget_Page_Stop)

    def upload_file(self):
        # 弹出文件选择对话框
        filePath, _ = QFileDialog.getOpenFileName(self,
            caption = "上传文件",
            dir = "",
            filter = "Video Files (*.mp4 *.avi *.mkv *.flv)"
        )
        if filePath is None:
            return
        if self.Thread is not None and self.Thread.isRunning():
            self.Thread.terminate()
        self.Thread = Thread_Upload(
            'http',
            'localhost',
            8080,
            filePath
        )
        self.Thread.finished.connect(
            lambda: (
                self.startAnalyseThread(Path(filePath).name, list(TypeDict.keys()))
            )
        )
        self.Thread.start()

    def updateResultDict(self, case: str, result: dict):
        '''
        for key, value in result.copy().items():
            result.pop(key) if len(value) == 0 else None
        '''
        self.resultDict[case] = result

    def startThread(self, CheckedCaseInfo):
        caseRow, caseCMD, case = CheckedCaseInfo
        if caseCMD.strip().lower() in ("nan", ""):
            return
        SaveRoot_PC = self.ui.LineEdit_pcSaveLoc.text()
        saveDir_PC = Path(SaveRoot_PC).joinpath(case).as_posix()
        ChkTypes = self.ui.Table.getCaseChkTypes(caseRow)
        outputFolder = saveDir_PC
        # Update caseDict
        self.updateCaseDict(caseRow, saveDir_PC)
        # Start thread
        if self.Thread is not None and self.Thread.isRunning():
            self.Thread.terminate()
        self.Thread = Thread_Execute(
            'http',
            'localhost',
            8080,
            caseCMD,
            saveDir_PC,
            ChkTypes,
            outputFolder,
        )
        self.Thread.dictReceived.connect(
            lambda dict, isSucceeded: (
                self.updateResultDict(case, dict),
                self.ui.Table.setCaseStatus(caseRow, Status = "完成" if isSucceeded else "失败"),
                self.add_result_to_exceldb(),
                self.ui.ProgressBar_Exec.setRange(0, 100),
                self.ui.ProgressBar_Exec.setValue(100),
                self.ui.StackedWidget_ExecAndStop.setCurrentWidget(self.ui.StackedWidget_Page_Exec)
            )
        )
        self.Thread.start()
        self.ui.Table.setCaseStatus(caseRow, Status = "执行中")
        self.ui.ProgressBar_Exec.setRange(0, 0)
        self.ui.StackedWidget_ExecAndStop.setCurrentWidget(self.ui.StackedWidget_Page_Stop)

    def stopThread(self, CheckedCaseInfo):
        caseRow, caseCMD, case = CheckedCaseInfo
        if self.ui.Table.getCaseInfo(caseRow)[2] != "执行中":
            return
        if self.Thread is not None and self.Thread.isRunning():
            self.Thread.terminate()
        self.Thread = Thread_Stop(
            'http',
            'localhost',
            8080,
        )
        self.Thread.finished.connect(
            lambda: (
                self.ui.Table.setCaseStatus(caseRow, Status = "已终止"),
                self.ui.ProgressBar_Exec.setRange(0, 100),
                self.ui.ProgressBar_Exec.setValue(0),
                self.ui.StackedWidget_ExecAndStop.setCurrentWidget(self.ui.StackedWidget_Page_Exec)
            )
        )
        self.Thread.start()

    def Execute(self):
        CheckedCaseInfos = self.ui.Table.getCheckedCaseInfos()
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
        CheckedCaseInfos = self.ui.Table.getCheckedCaseInfos()
        for CheckedCaseInfo in CheckedCaseInfos:
            self.stopThread(CheckedCaseInfo)

    def CheckadbOutput(self):
        CheckedCaseInfos = self.ui.Table.getCheckedCaseInfos()
        if len(CheckedCaseInfos) == 0:
            return
        for CheckedCaseInfo in CheckedCaseInfos:
            caseRow, caseCMD, case = CheckedCaseInfo
            saveDir_PC = self.caseDict[caseRow]
            try:
                os.startfile(saveDir_PC)
            except:
                QMessageBox.critical(self, "错误", f"无法打开目录: {saveDir_PC}")
                return

    def CheckAnalysationOutput(self, caseRow):
        caseCMD, case, caseStatus = self.ui.Table.getCaseInfo(caseRow)
        if caseStatus != "完成":
            return
        imageDict = self.resultDict[case]
        imageWindow = ImageWindow(imageDict)
        imageWindow.show()

    def closeEvent(self, event):
        exitService(
            protocol = 'http',
            ip = 'localhost',
            port = 8080,
        )
        super().closeEvent(event)

    def Main(self):
        # ParamsManager
        configPath = QFunc.NormPath(Path(ConfigDir).joinpath('config.ini'))
        paramsManager = ParamsManager(configPath)

        # Theme toggler
        ComponentsSignals.Signal_SetTheme.connect(
            lambda: self.ui.CheckBox_SwitchTheme.setChecked(
                {Theme.Light: True, Theme.Dark: False}.get(EasyTheme.THEME)
            )
        )
        Function_ConfigureCheckBox(
            CheckBox = self.ui.CheckBox_SwitchTheme,
            CheckedEvents = [
                lambda: paramsManager.Config.editConfig('Settings', 'Theme', Theme.Light),
                lambda: ComponentsSignals.Signal_SetTheme.emit(Theme.Light) if EasyTheme.THEME != Theme.Light else None
            ],
            UncheckedEvents = [
                lambda: paramsManager.Config.editConfig('Settings', 'Theme', Theme.Dark),
                lambda: ComponentsSignals.Signal_SetTheme.emit(Theme.Dark) if EasyTheme.THEME != Theme.Dark else None
            ],
            TakeEffect = False
        )

        # Window controling buttons
        self.ui.Button_Close_Window.clicked.connect(self.close)
        self.ui.Button_Close_Window.setBorderless(True)
        self.ui.Button_Close_Window.setTransparent(True)
        self.ui.Button_Close_Window.setHoverBackgroundColor(QColor(210, 123, 123, 210))
        self.ui.Button_Close_Window.setIcon(IconBase.X)

        self.ui.Button_Maximize_Window.clicked.connect(lambda: self.showNormal() if self.isMaximized() else self.showMaximized())
        self.ui.Button_Maximize_Window.setBorderless(True)
        self.ui.Button_Maximize_Window.setTransparent(True)
        self.ui.Button_Maximize_Window.setHoverBackgroundColor(QColor(123, 123, 123, 123))
        self.ui.Button_Maximize_Window.setIcon(IconBase.FullScreen)

        self.ui.Button_Minimize_Window.clicked.connect(self.showMinimized)
        self.ui.Button_Minimize_Window.setBorderless(True)
        self.ui.Button_Minimize_Window.setTransparent(True)
        self.ui.Button_Minimize_Window.setHoverBackgroundColor(QColor(123, 123, 123, 123))
        self.ui.Button_Minimize_Window.setIcon(IconBase.Dash)

        # Logo
        self.setWindowIcon(QIcon(QFunc.NormPath(Path(CurrentDir).joinpath('assets/images/Logo.ico'))))

        self.setWindowTitle("Excel Data to Table")

        self.ui.Label_pcSaveLoc.setText('输出位置')
        self.ui.LineEdit_pcSaveLoc.setFileDialog(
            Mode = "SelectFolder",
            Directory = Path(CurrentDir).anchor
        )
        paramsManager.SetParam(
            Widget = self.ui.LineEdit_pcSaveLoc,
            Section = 'Input Params',
            Option = 'OutputDir',
            DefaultValue = QFunc.NormPath(Path(Path(CurrentDir).anchor).joinpath('vids'))
        )

        self.ui.Button_LoadData.setText("打开Excel文件")
        self.ui.Button_LoadData.clicked.connect(self.open_excel_file)

        self.ui.Button_UploadFile.setText("上传视频文件")
        self.ui.Button_UploadFile.clicked.connect(self.upload_file)

        self.ui.Button_Exec.setText("执行测试用例")
        self.ui.Button_Exec.clicked.connect(self.Execute)
        self.ui.Button_Stop.setText("停止")
        self.ui.Button_Stop.clicked.connect(self.StopTask)
        self.ui.ProgressBar_Exec.setTextVisible(False)

        #self.ui.Button_ViewOutput.setText("查看输出")
        self.ui.Button_ViewOutput.clicked.connect(self.CheckadbOutput)

        self.ui.Table.onButtonClicked.connect(self.CheckAnalysationOutput)

        # Set theme
        ComponentsSignals.Signal_SetTheme.emit(paramsManager.Config.getValue('Settings', 'Theme', Theme.Auto))

        # Show window
        self.show()

##############################################################################################################################

if __name__ == '__main__':
    App = QApplication(sys.argv)

    window = MainWindow()
    window.Main()

    sys.exit(App.exec())

##############################################################################################################################