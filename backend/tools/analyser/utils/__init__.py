from .cv import *


def UpdateDict(Dict1, Dict2):
    for key, value in Dict2.items():
        if key in Dict1:
            Dict1[key] += value
        else:
            Dict1[key] = value
    return Dict1