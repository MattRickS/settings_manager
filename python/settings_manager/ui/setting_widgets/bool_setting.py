from PySide2 import QtCore, QtGui, QtWidgets
from settings_manager.ui.setting_widgets.setting_ui import SettingUI


class BoolSetting(QtWidgets.QCheckBox, SettingUI):
    def __init__(self, setting, parent=None):
        """
        :param Setting setting:
        """
        super(BoolSetting, self).__init__(parent)
        SettingUI.__init__(self, setting)

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
