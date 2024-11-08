import os, sys
import subprocess
import threading

from pathlib import Path
current_dir = Path(__file__).absolute().parent.as_posix()
sys.path.insert(0, f"{current_dir}")
os.chdir(current_dir)

from .recorder.Recorder import *
from .analyser.Analyser import *

##############################################################################################################################

def Exec(
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
    global adbRecord
    global stopRecordEvent
    global stopAllEvent
    global result

    # Set the save location
    SavePath_AD = "/sdcard/testcase.mp4"
    Path(saveDir_PC).mkdir(parents = True) if not Path(saveDir_PC).exists() else None

    # Reboot server
    adbReboot = reboot()
    adbReboot.wait()

    # Start the screen recording thread
    recordingThread = threading.Thread(
        target = RecordAndPull,
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
    if adbRecord is not None:
        adbRecord.terminate()
    recordingThread.join()

    return result

##############################################################################################################################