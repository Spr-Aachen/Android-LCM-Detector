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
    resultDict = {}

    Thread = None

    def __init__(self):
        super().__init__()

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
                MessageBoxBase.pop(self, WindowTitle = 'Tip', Text = '执行成功' if isSucceeded else '执行失败', DetailedText = str(dict)),
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
        if len(filePath.strip()) == 0:
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

    def stopThread(self):
        if self.Thread is not None and self.Thread.isRunning():
            self.Thread.terminate()
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

        self.setWindowTitle("Analyser")

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

        self.ui.Button_UploadFile.setText("上传视频文件")
        self.ui.Button_UploadFile.clicked.connect(self.upload_file)

        self.ui.ProgressBar_Exec.setTextVisible(False)

        #self.ui.Button_ViewOutput.clicked.connect(self.checkOutput)

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