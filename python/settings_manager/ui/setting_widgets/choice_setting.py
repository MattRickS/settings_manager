from PySide2 import QtCore, QtGui, QtWidgets

from settings_manager.setting import Setting
from settings_manager.ui.setting_widgets.setting_ui import SettingUI


class ChoiceSetting(QtWidgets.QComboBox, SettingUI):
    def __init__(self, setting=None, parent=None):
        # type: (Setting, QtWidgets.QWidget) -> None
        super(ChoiceSetting, self).__init__(parent)
        SettingUI.__init__(self, setting)
        self.currentTextChanged.connect(self.onValueChanged)

    def setSetting(self, setting):
        # type: (Setting) -> None
        super(ChoiceSetting, self).setSetting(setting)
        choices = setting.property('choices')
        self.clear()
        self.addItems(list(map(str, choices)))

    def setValue(self, value):
        # type: (str) -> None
        self.setCurrentText(value)

    def value(self):
        # type: () -> str
        return self.currentText()
