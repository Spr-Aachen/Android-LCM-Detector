# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path
from typing import Optional
from subprocess import Popen

##############################################################################################################################

# Get current directory
CurrentDir = sys.path[0]


def run(
):
    # 后台启动
    BackendDir = Path(f'{CurrentDir}{os.sep}backend').as_posix()
    backendFileStem = Path(f'{BackendDir}{os.sep}main').as_posix()
    if Path(f'{backendFileStem}.py').exists():
        Popen(
            f'python "{backendFileStem}.py"',
            shell = True
        )
    if Path(f'{backendFileStem}.exe').exists():
        Popen(
            f'"{backendFileStem}.exe"',
            shell = True
        )

    # 前台启动
    FrontendDir = Path(f'{CurrentDir}{os.sep}frontend').as_posix()
    FrontendFileStem = Path(f'{FrontendDir}{os.sep}main').as_posix()
    if Path(f'{FrontendFileStem}.py').exists():
        Popen(
            f'python "{FrontendFileStem}.py"',
            shell = True
        )
    if Path(f'{FrontendFileStem}.exe').exists():
        Popen(
            f'"{FrontendFileStem}.exe"',
            shell = True
        )

##############################################################################################################################

if __name__ == "__main__":
    run(
    )

##############################################################################################################################