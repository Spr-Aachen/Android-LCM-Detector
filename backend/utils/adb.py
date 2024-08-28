import os
import subprocess
from pathlib import Path

##############################################################################################################################

def Reboot():
    adbReboot = subprocess.Popen(
        "adb kill-server && adb start-server",
        shell = True
    )
    return adbReboot


def Pull(
    SavePath_AD: str,
    SaveDir_PC: str
):
    adb3 = subprocess.Popen(
        f"adb pull {SavePath_AD} {SaveDir_PC}",
        shell = True
    )
    return adb3


def Record(
    SavePath_AD: str,
    RecPeriod: int = 180
):
    adbRecord = subprocess.Popen(
        f"adb shell screenrecord {SavePath_AD} --time-limit {RecPeriod}",
        shell = True
    )
    return adbRecord

##############################################################################################################################