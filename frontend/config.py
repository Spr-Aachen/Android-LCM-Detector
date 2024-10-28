import sys
from pathlib import Path
from QEasyWidgets import QFunctions as QFunc

##############################################################################################################################

# Check whether python file is compiled
_, IsFileCompiled = QFunc.GetFileInfo()

# Get current directory
CurrentDir = QFunc.GetBaseDir(__file__ if IsFileCompiled == False else sys.executable)

# Set directory to load static dependencies
ResourceDir = CurrentDir if QFunc.GetBaseDir(SearchMEIPASS = True) is None else QFunc.GetBaseDir(SearchMEIPASS = True)

##############################################################################################################################