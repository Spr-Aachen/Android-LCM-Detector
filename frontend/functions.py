import inspect
from typing import Union, Optional
from PySide6.QtCore import Qt, QObject, Signal, Slot, QThread, QPoint
from PySide6.QtCore import QCoreApplication as QCA
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from components.Components import *
from windows.Windows import *

##############################################################################################################################

# Where to store custom signals
class CustomSignals_Functions(QObject):
    '''
    Set up signals for functions
    '''
    # Run task
    Signal_ExecuteTask = Signal(tuple)


FunctionSignals = CustomSignals_Functions()

##############################################################################################################################

def Function_SetMethodExecutor(
    ParentWindow: Optional[QWidget] = None,
    Method: object = ...,
    Params: Optional[tuple] = None,
    FinishEvent = None
):
    '''
    Function to execute outer class methods
    '''
    QualName = str(Method.__qualname__)
    MethodName = QualName.split('.')[1]

    ClassInstance = inspect.getmodule(Method).__dict__[Method.__qualname__.split('.')[0]]()
    ClassInstance.finished.connect(FinishEvent) if hasattr(ClassInstance, 'finished') else None

    WorkerThread = ClassInstance

    def ExecuteMethod():
        Args = Params

        FunctionSignals = CustomSignals_Functions()
        FunctionSignals.Signal_ExecuteTask.connect(getattr(ClassInstance, MethodName))

        FunctionSignals.Signal_ExecuteTask.emit(Args)

        WorkerThread.start()

    TempButton = QPushButton(ParentWindow)
    TempButton.clicked.connect(ExecuteMethod)
    TempButton.setVisible(False)
    TempButton.click()
    WorkerThread.finished.connect(TempButton.deleteLater)

##############################################################################################################################