from PySide2 import QtCore, QtGui, QtWidgets
from settings_manager.ui.setting_widgets.base_settings_ui import BaseSettingsUI


class BoolSetting(QtWidgets.QCheckBox, BaseSettingsUI):
    def __init__(self, setting, parent=None):
        """
        :param Setting setting:
        """
        super(BoolSetting, self).__init__(parent)
        BaseSettingsUI.__init__(self, setting)

        # Connection
        self.stateChanged.connect(self.onValueChanged)

    # -----------------------------------------------------------------
    #                              SLOTS
    # -----------------------------------------------------------------

    def setValue(self, value):
        self.setCheckState(value)
        self.stateChanged.emit(value)

    def value(self):
        return True if self.checkState() == QtCore.Qt.Checked else False
        # return self.checkState()

    def onValueChanged(self, value):
        value = True if value == QtCore.Qt.Checked else False
        super(BoolSetting, self).onValueChanged(value)


if __name__ == '__main__':
    from settings_manager import Settings

    s = Settings()
    s.add('bool', True)

    import sys
    app = QtWidgets.QApplication(sys.argv)

    widget = BoolSetting(s.setting('bool'))
    widget.show()

    app.exec_()
    print(s.as_dict(values_only=True))

