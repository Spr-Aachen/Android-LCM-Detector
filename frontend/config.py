import sys
from pathlib import Path
from QEasyWidgets import QFunctions as QFunc

##############################################################################################################################

# Check whether python file is compiled
_, IsFileCompiled = QFunc.GetFileInfo()

# Get current directory
CurrentDir = QFunc.GetBaseDir(__file__ if IsFileCompiled == False else sys.executable)

# Set profile directory
ProfileDir = Path(CurrentDir).joinpath('Profile').as_posix()

# Set directory to store client config
ConfigDir = Path(ProfileDir).joinpath('Config').as_posix()

##############################################################################################################################