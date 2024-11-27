import os
import re
from pathlib import Path
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from QEasyWidgets import QFunctions as QFunc

from components.components import *
from windows.windows import *

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
        lambda IsChecked: QFunc.runEvents(CheckedEvents if IsChecked else UncheckedEvents)
    )

    QFunc.runEvents(CheckedEvents) if TakeEffect and CheckBox.isChecked() else None
    QFunc.runEvents(UncheckedEvents) if TakeEffect and not CheckBox.isChecked() else None


def Function_SetWidgetValue(
    Widget: QWidget,
    Config: QFunc.configManager,
    Section: str = ...,
    Option: str = ...,
    Value = ...,
    Times: Union[int, float] = 1,
    SetPlaceholderText: bool = False,
    PlaceholderText: Optional[str] = None
):
    if isinstance(Widget, (QLineEdit, QTextEdit, QPlainTextEdit)):
        QFunc.setText(Widget, Value, setPlaceholderText = SetPlaceholderText, placeholderText = PlaceholderText)
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
        configPath: str,
    ):
        self.configPath = configPath
        self.config = QFunc.configManager(configPath)

        self.RegistratedWidgets = {}

    def registrate(self, widget: QWidget, value: tuple):
        self.RegistratedWidgets[widget] = value

    def SetParam(self,
        widget: QWidget,
        section: str = ...,
        option: str = ...,
        defaultValue = None,
        times: Union[int, float] = 1,
        setPlaceholderText: bool = False,
        placeholderText: Optional[str] = None,
        registrate: bool = True
    ):
        value = self.config.getValue(section, option, str(defaultValue))
        Function_SetWidgetValue(widget, self.config, section, option, value, times, setPlaceholderText, placeholderText)
        self.registrate(widget, (section, option, defaultValue, times, setPlaceholderText, placeholderText)) if registrate else None

    def ResetParam(self, widget: QWidget):
        value = self.RegistratedWidgets[widget]
        Function_SetWidgetValue(widget, self.config, *value)

    def ClearSettings(self):
        with open(self.configPath, 'w'):
            pass
        self.config = QFunc.configManager(self.configPath)

    def ResetSettings(self):
        self.ClearSettings()
        for widget in list(self.RegistratedWidgets.keys()):
            self.ResetParam(widget)

    def ImportSettings(self, readPath: str):
        configParser = QFunc.configManager(readPath).parser()
        with open(self.configPath, 'w', encoding = 'utf-8') as config:
            configParser.write(config)
        for widget, value in list(self.RegistratedWidgets.items()):
            self.SetParam(widget, *value)

    def ExportSettings(self, savePath: str):
        with open(savePath, 'w', encoding = 'utf-8') as config:
            self.config.parser().write(config)

##############################################################################################################################