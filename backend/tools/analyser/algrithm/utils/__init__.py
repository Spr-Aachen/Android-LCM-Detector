import threading
from typing import Optional

from .torchvision import *
from .cv import *

##############################################################################################################################

def getFiles(dir, extensions):
    matchedFiles = []
    for extension in extensions:
        matchedFiles.extend(Path(dir).glob(f'*{extension}'))
    return matchedFiles


def updateDict(Dict1, Dict2):
    for key, value in Dict2.items():
        if key in Dict1:
            Dict1[key] += value
        else:
            Dict1[key] = value
    return Dict1


def stopSignal(stopEvent: Optional[threading.Event] = None):
    return isinstance(stopEvent, threading.Event) and stopEvent.is_set()

##############################################################################################################################