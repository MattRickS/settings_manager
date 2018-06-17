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
