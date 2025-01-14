import threading
from typing import Optional

from .load import *
from .io import *
from .inference import *
from .calc import *

##############################################################################################################################

def updateDict(dict1: dict, dict2: dict) -> dict:
    for key, value in dict2.items():
        if key in dict1:
            dict1[key] += value
        else:
            dict1[key] = value
    return dict1


def stopSignal(stopEvent: Optional[threading.Event] = None):
    return isinstance(stopEvent, threading.Event) and stopEvent.is_set()

##############################################################################################################################