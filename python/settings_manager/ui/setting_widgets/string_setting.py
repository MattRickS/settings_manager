from PySide2 import QtCore, QtGui, QtWidgets
from settings_manager.ui.setting_widgets.base_settings_ui import BaseSettingsUI


class StringSetting(QtWidgets.QLineEdit, BaseSettingsUI):
    def __init__(self, settings, setting_name):
        """
        :param Settings settings:
        :param str      setting_name:
        """
        super(StringSetting, self).__init__()
        BaseSettingsUI.__init__(self, settings, setting_name)

        self.textChanged.connect(self.settingChanged.emit)

    def setValue(self, value):
        self.setText(value)

    def onSettingChanged(self, value):
        # Convert to data type to keep encoding
        data_type = self._settings.properties(self._setting_name)["data_type"]
        self._settings.set(self._setting_name, data_type(value))


if __name__ == '__main__':
    from settings_manager import Settings

    s = Settings()
    s.add('string', 'value')

    import sys
    app = QtWidgets.QApplication(sys.argv)

    widget = StringSetting(s, 'string')
    widget.show()

    app.exec_()
    print(s.as_dict())
    print(widget.settings.as_dict())

