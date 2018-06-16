from PySide2 import QtCore, QtGui, QtWidgets
from settings_manager.ui.setting_widgets.base_settings_ui import BaseSettingsUI


class ChoiceSetting(QtWidgets.QComboBox, BaseSettingsUI):
    def __init__(self, settings, setting_name, parent=None):
        """
        :param Settings settings:
        :param str      setting_name:
        """
        super(ChoiceSetting, self).__init__(parent)

        # Initialise choices
        properties = settings.properties(setting_name)
        self.addItems(list(map(str, properties["choices"])))

        BaseSettingsUI.__init__(self, settings, setting_name)

        self.currentTextChanged.connect(self.settingChanged.emit)

    def setValue(self, value):
        self.setCurrentText(value)


if __name__ == '__main__':
    from settings_manager import Settings

    s = Settings()
    s.add('choice', 'A', choices=['A', 'B', 'C'])

    import sys
    app = QtWidgets.QApplication(sys.argv)

    widget = ChoiceSetting(s, 'choice')
    widget.show()

    app.exec_()
    print(s.as_dict())
    print(widget.settings.as_dict())
