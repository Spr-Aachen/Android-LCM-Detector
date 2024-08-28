import re
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from components.Components import *
from windows.Windows import *

##############################################################################################################################

def RenameIfExists(FilePath: str):
    Directory, FileName = os.path.split(FilePath)
    while Path(FilePath).exists():
        pattern = r'(\d+)\)'
        match = re.search(pattern, FileName)
        if match is None:
            FileName += '(0)'
        else:
            CurrentNumber = int(match.group(1))
            FileName = FileName[:match.start(1)] + f'({CurrentNumber + 1})'
        FilePath = Path(Directory).joinpath(FileName).as_posix()
    return FilePath

##############################################################################################################################