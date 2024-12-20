import threading
from typing import Optional

from .inference import *
from .extract import *
from .cv import *

##############################################################################################################################

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