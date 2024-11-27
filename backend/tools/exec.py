import os, sys
import subprocess
import threading
from typing import Optional

from pathlib import Path
current_dir = Path(__file__).absolute().parent.as_posix()
sys.path.insert(0, f"{current_dir}")
os.chdir(current_dir)

from . import recorder
from . import analyser

##############################################################################################################################

stopRecordEvent = threading.Event()
stopAllEvent = threading.Event()
def recordAndPull(
    savePath_AD: str,
    saveDir_PC: str,
    chkTypes: list,
    outputFolder: str,
    modelDir: str,
    toOnnx: bool = False,
    recPeriod: int = 180,
    sn: Optional[str] = None,
):
    global stopRecordEvent
    global stopAllEvent
    i = 0
    analysingThreads = []
    while not (stopRecordEvent.is_set() or stopAllEvent.is_set()):
        try:
            recorder.record(savePath_AD, saveDir_PC, recPeriod, sn)
            i += 1
            OldName = Path(saveDir_PC).joinpath(Path(savePath_AD).name).as_posix()
            NewName = Path(saveDir_PC).joinpath(f"{i}{Path(savePath_AD).suffix}").as_posix()
            if Path(OldName).exists():
                if Path(NewName).exists():
                    os.remove(NewName)
                os.rename(OldName, NewName)
        except Exception as e:
            print(f"recordAndPull error: {e}")
        finally:
            if not Path(NewName).exists():
                continue
            analysingThread = threading.Thread(
                target = analyser.videoAnalyse,
                args = (NewName, chkTypes, outputFolder, modelDir, toOnnx, stopAllEvent)
            )
            analysingThreads.append(analysingThread)
            analysingThread.start()
    else:
        if not stopAllEvent.is_set():
            for analysingThread in analysingThreads:
                try:
                    analysingThread.join()
                except:
                    pass


def exec(
    taskCMD: str,
    saveDir_PC: str,
    chkTypes: list,
    outputFolder: str,
    modelDir: str,
    toOnnx: bool = False,
    recPeriod: int = 180,
    sn: Optional[str] = None,
):
    """
    执行测试用例并记录屏幕录像（以recPeriod为周期进行录像检测）
    Args:
        taskCMD (str): 测试用例命令
        saveDir_PC (str): 录屏保存路径
        chkTypes (list): 检测类型
        outputFolder (str): 结果输出路径
        modelDir (str): 模型路径
        toOnnx (bool): 是否转换为onnx格式
        recPeriod (int): 录屏周期（秒）
        sn (str): 设备序列号
    Returns:
        result (dict): 检测结果
    """
    global stopRecordEvent
    global stopAllEvent

    # Set the save location
    SavePath_AD = "/sdcard/testcase.mp4"
    Path(saveDir_PC).mkdir(parents = True) if not Path(saveDir_PC).exists() else None

    # Reboot server
    adbReboot = recorder.reboot()
    adbReboot.wait()

    # Start the screen recording thread
    recordingThread = threading.Thread(
        target = recordAndPull,
        args = (SavePath_AD, saveDir_PC, chkTypes, outputFolder, modelDir, toOnnx, recPeriod, sn)
    )
    recordingThread.start()

    # Execute the main task
    adbTask = subprocess.Popen(
        taskCMD,
        shell = True
    )
    # Wait for the task to finish or for the stop event to be set
    while not stopAllEvent.is_set():
        if adbTask.poll() is not None:
            break
    else:
        adbTask.terminate()

    # Signal the recording thread to stop and wait for it to finish
    stopRecordEvent.set()
    if recorder.adbRecord is not None:
        recorder.adbRecord.terminate()
    recordingThread.join()

    return analyser.result

##############################################################################################################################