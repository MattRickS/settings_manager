from PySide2 import QtCore, QtGui, QtWidgets

from settings_manager.setting import Setting
from settings_manager.ui.setting_widgets.setting_ui import SettingUI


class BoolSetting(QtWidgets.QCheckBox, SettingUI):
    def __init__(self, setting=None, parent=None):
        # type: (Setting, QtWidgets.QWidget) -> None
        super(BoolSetting, self).__init__(parent)
        SettingUI.__init__(self, setting)
        self.stateChanged.connect(self.onValueChanged)

    # -----------------------------------------------------------------
    #                              SLOTS
    # -----------------------------------------------------------------

    def setValue(self, value):
        # type: (QtCore.Qt.CheckState|bool) -> None
        if isinstance(value, bool):
            value = QtCore.Qt.Checked if value else QtCore.Qt.Unchecked
        self.setCheckState(value)

    def value(self):
        # type: () -> QtCore.Qt.CheckState
        return self.checkState()

    def onValueChanged(self, value):
        # type: (QtCore.Qt.CheckState) -> None
        value = True if value == QtCore.Qt.Checked else False
        super(BoolSetting, self).onValueChanged(value)
