from PySide2 import QtCore, QtGui, QtWidgets

from settings_manager.setting import Setting
from settings_manager.ui.setting_widgets.setting_ui import SettingUI


class StringSetting(QtWidgets.QLineEdit, SettingUI):
    def __init__(self, setting=None, parent=None):
        # type: (Setting, QtWidgets.QWidget) -> None
        super(StringSetting, self).__init__(parent)
        SettingUI.__init__(self, setting)
        self.textChanged.connect(self.onValueChanged)

    def setValue(self, value):
        # type: (str) -> None
        self.setText(value)

    def value(self):
        # type: () -> str
        return self.text()

    def onValueChanged(self, value):
        # type: (str) -> None
        # Convert to data type to keep encoding
        super(StringSetting, self).onValueChanged(self._setting.type(value))
