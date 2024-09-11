# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path
from typing import Optional
from subprocess import Popen

##############################################################################################################################

# Get current directory
CurrentDir = sys.path[0]


IsCompiled = False


def run(
    ModelDir: str,
):
    if not IsCompiled:
        BackendDir = Path(f'{CurrentDir}{os.sep}backend').as_posix()
        backendFile = Path(f'{BackendDir}{os.sep}main.py').as_posix()
        Popen(
            f'python "{backendFile}" --modeldir "{ModelDir}"',
            shell = True
        )
        FrontendDir = Path(f'{CurrentDir}{os.sep}frontend').as_posix()
        FrontendFile = Path(f'{FrontendDir}{os.sep}main.py').as_posix()
        Popen(
            f'python "{FrontendFile}"',
            shell = True
        )
    else:
        BackendDir = Path(f'{CurrentDir}{os.sep}backend').as_posix()
        backendFile = Path(f'{BackendDir}{os.sep}main.exe').as_posix()
        Popen(
            f'"{backendFile}"'
        )
        FrontendDir = Path(f'{CurrentDir}{os.sep}frontend').as_posix()
        FrontendFile = Path(f'{FrontendDir}{os.sep}main.exe').as_posix()
        Popen(
            f'"{FrontendFile}"'
        )

##############################################################################################################################

if __name__ == "__main__":
    run(
        ModelDir = f'{CurrentDir}{os.sep}models'
    )

##############################################################################################################################