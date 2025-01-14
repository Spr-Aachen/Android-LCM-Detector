# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path
from subprocess import Popen

##############################################################################################################################

# Get current directory
currentDir = Path(sys.argv[0]).parent.as_posix()


def run(
    modelDir: str,
    profileDir: str,
):
    resourceDir = Path(sys._MEIPASS).as_posix() if getattr(sys, 'frozen', None) else currentDir
    serverDir = Path(f'{resourceDir}{os.sep}server').as_posix()
    serverFile = Path(f'{serverDir}{os.sep}main.py').as_posix()
    serverCMD = f'python "{serverFile}" --modelDir "{modelDir}"'
    Popen(serverCMD)
    clientDir = Path(f'{resourceDir}{os.sep}client').as_posix()
    clientFile = Path(f'{clientDir}{os.sep}main.py').as_posix()
    clientCMD = f'python "{clientFile}" --profile "{profileDir}"'
    Popen(clientCMD)

##############################################################################################################################

if __name__ == "__main__":
    run(
        modelDir = Path(currentDir).joinpath('models').as_posix(),
        profileDir = Path(currentDir).joinpath('profile').as_posix()
    )

##############################################################################################################################