from PySide2 import QtCore, QtGui, QtWidgets
from settings_manager.ui.setting_widgets.setting_ui import SettingUI


class StringSetting(QtWidgets.QLineEdit, SettingUI):
    def __init__(self, setting):
        """
        :param Setting setting:
        """
        super(StringSetting, self).__init__()
        SettingUI.__init__(self, setting)

        self.textChanged.connect(self.onValueChanged)

    def setValue(self, value):
        self.setText(value)
        self.textChanged.emit(value)

    def value(self):
        return self.text()

    def onValueChanged(self, value):
        # Convert to data type to keep encoding
        super(StringSetting, self).onValueChanged(self._setting.type(value))
