from PySide2 import QtCore, QtGui, QtWidgets
from settings_manager.ui.setting_widgets.setting_ui import SettingUI


class ChoiceSetting(QtWidgets.QComboBox, SettingUI):
    def __init__(self, setting, parent=None):
        """
        :param Setting setting:
        """
        super(ChoiceSetting, self).__init__(parent)

        # Initialise choices
        choices = setting.property('choices')
        self.addItems(list(map(str, choices)))

        SettingUI.__init__(self, setting)

        self.currentTextChanged.connect(self.onValueChanged)

    def setValue(self, value):
        self.setCurrentText(value)
        self.currentTextChanged.emit(value)

    def value(self):
        return self.currentText()


if __name__ == '__main__':
    from settings_manager import Settings

    s = Settings()
    s.add('choice', 'A', choices=['A', 'B', 'C'])

    import sys
    app = QtWidgets.QApplication(sys.argv)

    widget = ChoiceSetting(s.setting('choice'))
    widget.show()

    app.exec_()
    print(s.as_dict(values_only=True))
