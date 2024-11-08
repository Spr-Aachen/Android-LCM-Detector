import threading
from pathlib import Path

from .utils import *
from ..analyser.Analyser import *

##############################################################################################################################

adbRecord = None
def Record(
    savePath_AD: str,
    saveDir_PC: str,
    recPeriod: int = 180,
    sn: Optional[str] = None,
):
    global adbRecord
    adbRecord = record(savePath_AD, recPeriod, sn)
    adbRecord.wait()
    adbPull = pull(savePath_AD, saveDir_PC)
    adbPull.wait()


stopRecordEvent = threading.Event()
stopAllEvent = threading.Event()
def RecordAndPull(
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
            Record(savePath_AD, saveDir_PC, recPeriod, sn)
            i += 1
            OldName = Path(saveDir_PC).joinpath(Path(savePath_AD).name).as_posix()
            NewName = Path(saveDir_PC).joinpath(f"{i}{Path(savePath_AD).suffix}").as_posix()
            if Path(OldName).exists():
                if Path(NewName).exists():
                    os.remove(NewName)
                os.rename(OldName, NewName)
        except Exception as e:
            print(f"RecordAndPull error: {e}")
        finally:
            if not Path(NewName).exists():
                continue
            analysingThread = threading.Thread(
                target = videoAnalyser,
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

##############################################################################################################################