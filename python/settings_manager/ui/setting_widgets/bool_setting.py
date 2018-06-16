from PySide2 import QtCore, QtGui, QtWidgets
from settings_manager.ui.setting_widgets.base_settings_ui import BaseSettingsUI


class BoolSetting(QtWidgets.QCheckBox, BaseSettingsUI):
    def __init__(self, settings, setting_name, parent=None):
        """
        :param Settings settings:
        :param str      setting_name:
        """
        super(BoolSetting, self).__init__(parent)
        BaseSettingsUI.__init__(self, settings, setting_name)

        # Connection
        self.stateChanged.connect(self.settingChanged.emit)

    # -----------------------------------------------------------------
    #                              SLOTS
    # -----------------------------------------------------------------

    def setValue(self, value):
        if isinstance(value, bool):
            value = QtCore.Qt.Checked if value else QtCore.Qt.Unchecked
        self.setCheckState(value)

    def onSettingChanged(self, value):
        value = True if value == QtCore.Qt.Checked else False
        self._settings.set(self._setting_name, value)


if __name__ == '__main__':
    from settings_manager import Settings

    s = Settings()
    s.add('bool', True)

    import sys
    app = QtWidgets.QApplication(sys.argv)

    widget = BoolSetting(s, 'bool')
    widget.show()

    app.exec_()
    print(s.as_dict())
    print(widget.settings.as_dict())

