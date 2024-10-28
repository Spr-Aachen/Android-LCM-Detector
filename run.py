# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path
from typing import Optional
from subprocess import Popen

##############################################################################################################################

# Get current directory
CurrentDir = Path(sys.argv[0]).parent.as_posix()


IsCompiled = False


def run(
    ModelDir: str,
    ProfileDir: str,
):
    resourceDir = Path(sys._MEIPASS).as_posix() if getattr(sys, 'frozen', None) else CurrentDir
    BackendDir = Path(f'{resourceDir}{os.sep}backend').as_posix()
    backendFile = Path(f'{BackendDir}{os.sep}main.py').as_posix()
    backendCMD = f'python "{backendFile}" --modeldir "{ModelDir}"'
    Popen(backendCMD, shell = True)
    FrontendDir = Path(f'{resourceDir}{os.sep}frontend').as_posix()
    FrontendFile = Path(f'{FrontendDir}{os.sep}main.py').as_posix()
    frontendCMD = f'python "{FrontendFile}" --profile "{ProfileDir}"'
    Popen(frontendCMD, shell = True)

##############################################################################################################################

if __name__ == "__main__":
    run(
        ModelDir = Path(CurrentDir).joinpath('models').as_posix(),
        ProfileDir = Path(CurrentDir).joinpath('profile').as_posix()
    )

##############################################################################################################################