import subprocess
import threading
from pathlib import Path

from utils.adb import *

##############################################################################################################################

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
        adbRecord = Record(SavePath_AD, RecPeriod)
        adbRecord.wait()
        adbPull = Pull(SavePath_AD, SaveDir_PC)
        adbPull.wait()
        i += 1
        OldName = Path(SaveDir_PC).joinpath(Path(SavePath_AD).name).as_posix()
        NewName = Path(SaveDir_PC).joinpath(f"{i}{Path(SavePath_AD).suffix}").as_posix()
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

##############################################################################################################################