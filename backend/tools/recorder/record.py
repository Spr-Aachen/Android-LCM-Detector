from pathlib import Path

from .utils import *

##############################################################################################################################

adbRecord = None
def videoRecord(
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

##############################################################################################################################