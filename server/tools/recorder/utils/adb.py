import os
import subprocess
from typing import Optional

##############################################################################################################################

def reboot():
    adbReboot = subprocess.Popen(
        "adb kill-server && adb start-server",
        shell = True
    )
    return adbReboot


def pull(
    savePath_AD: str,
    saveDir_PC: str
):
    adb3 = subprocess.Popen(
        f"adb pull {savePath_AD} {saveDir_PC}",
        shell = True
    )
    return adb3


def record(
    savePath_AD: str = ...,
    recPeriod: int = 180,
    sn: Optional[str] = None
):
    adbRecord = subprocess.Popen(
        f"adb {f'-s {sn}' if sn else ''} shell screenrecord {savePath_AD} --time-limit {recPeriod}",
        shell = True
    )
    return adbRecord

##############################################################################################################################