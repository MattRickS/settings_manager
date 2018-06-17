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


if __name__ == '__main__':
    from settings_manager import Settings

    s = Settings()
    s.add('string', 'value')

    import sys
    app = QtWidgets.QApplication(sys.argv)

    widget = StringSetting(s.setting('string'))
    widget.show()

    app.exec_()
    print(s.as_dict(values_only=True))

