import os
import re
from pathlib import Path
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from QEasyWidgets import QFunctions as QFunc

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

def Function_ConfigureCheckBox(
    CheckBox: QCheckBox,
    CheckedText: Optional[str] = None,
    CheckedEvents: list = [],
    UncheckedText: Optional[str] = None,
    UncheckedEvents: list = [],
    TakeEffect: bool = False
):
    if CheckedText is not None:
        CheckedEvents.append(lambda: CheckBox.setText(CheckedText))
    if UncheckedText is not None:
        UncheckedEvents.append(lambda: CheckBox.setText(UncheckedText))

    CheckBox.toggled.connect(
        lambda IsChecked: QFunc.RunEvents(CheckedEvents if IsChecked else UncheckedEvents)
    )

    QFunc.RunEvents(CheckedEvents) if TakeEffect and CheckBox.isChecked() else None
    QFunc.RunEvents(UncheckedEvents) if TakeEffect and not CheckBox.isChecked() else None


def Function_SetWidgetValue(
    Widget: QWidget,
    Config: QFunc.ManageConfig,
    Section: str = ...,
    Option: str = ...,
    Value = ...,
    Times: Union[int, float] = 1,
    SetPlaceholderText: bool = False,
    PlaceholderText: Optional[str] = None
):
    if isinstance(Widget, (QLineEdit, QTextEdit, QPlainTextEdit)):
        QFunc.Function_SetText(Widget, Value, SetPlaceholderText = SetPlaceholderText, PlaceholderText = PlaceholderText)
        def EditConfig(Value):
            Config.editConfig(Section, Option, str(Value))
        if Config is not None:
            Widget.textChanged.connect(lambda: EditConfig(Widget.text() if isinstance(Widget, (QLineEdit)) else Widget.toPlainText()))
            EditConfig(Value)

    if isinstance(Widget, (QComboBox)):
        itemTexts = []
        for index in range(Widget.count()):
            itemTexts.append(Widget.itemText(index))
        Widget.setCurrentText(str(Value)) if str(Value) in itemTexts else None
        def EditConfig(Value):
            Config.editConfig(Section, Option, str(Value))
        if Config is not None:
            Widget.currentTextChanged.connect(EditConfig)
            EditConfig(Value) if str(Value) in itemTexts else None

    if isinstance(Widget, (QSlider, QSpinBox)):
        Widget.setValue(int(eval(str(Value)) * Times))
        def EditConfig(Value):
            Config.editConfig(Section, Option, str(eval(str(Value)) / Times))
        if Config is not None:
            Widget.valueChanged.connect(EditConfig)
            EditConfig(Value)

    if isinstance(Widget, (QDoubleSpinBox)):
        Widget.setValue(float(eval(str(Value)) * Times))
        def EditConfig(Value):
            Config.editConfig(Section, Option, str(eval(str(Value)) / Times))
        if Config is not None:
            Widget.valueChanged.connect(EditConfig)
            EditConfig(Value)

    if isinstance(Widget, (QCheckBox, QRadioButton)):
        Widget.setChecked(eval(str(Value)))
        def EditConfig(Value):
            Config.editConfig(Section, Option, str(Value))
        if Config is not None:
            Widget.toggled.connect(EditConfig)
            EditConfig(Value)


class ParamsManager:
    def __init__(self,
        ConfigPath: str,
    ):
        self.ConfigPath = ConfigPath
        self.Config = QFunc.ManageConfig(ConfigPath)

        self.RegistratedWidgets = {}

    def Registrate(self, Widget: QWidget, value: tuple):
        self.RegistratedWidgets[Widget] = value

    def SetParam(self,
        Widget: QWidget,
        Section: str = ...,
        Option: str = ...,
        DefaultValue = None,
        Times: Union[int, float] = 1,
        SetPlaceholderText: bool = False,
        PlaceholderText: Optional[str] = None,
        Registrate: bool = True
    ):
        Value = self.Config.getValue(Section, Option, str(DefaultValue))
        Function_SetWidgetValue(Widget, self.Config, Section, Option, Value, Times, SetPlaceholderText, PlaceholderText)
        self.Registrate(Widget, (Section, Option, DefaultValue, Times, SetPlaceholderText, PlaceholderText)) if Registrate else None

    def ResetParam(self, Widget: QWidget):
        value = self.RegistratedWidgets[Widget]
        Function_SetWidgetValue(Widget, self.Config, *value)

    def ClearSettings(self):
        with open(self.ConfigPath, 'w'):
            pass
        self.Config = QFunc.ManageConfig(self.ConfigPath)

    def ResetSettings(self):
        self.ClearSettings()
        for Widget in list(self.RegistratedWidgets.keys()):
            self.ResetParam(Widget)

    def ImportSettings(self, ReadPath: str):
        ConfigParser = QFunc.ManageConfig(ReadPath).parser()
        with open(self.ConfigPath, 'w', encoding = 'utf-8') as Config:
            ConfigParser.write(Config)
        for Widget, value in list(self.RegistratedWidgets.items()):
            self.SetParam(Widget, *value)

    def ExportSettings(self, SavePath: str):
        with open(SavePath, 'w', encoding = 'utf-8') as Config:
            self.Config.parser().write(Config)

##############################################################################################################################