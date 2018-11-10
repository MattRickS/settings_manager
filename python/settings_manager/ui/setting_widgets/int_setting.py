from Qt import QtCore, QtGui, QtWidgets

from settings_manager.setting import Setting
from settings_manager.ui.setting_widgets.setting_ui import SettingUI


class IntSetting(QtWidgets.QSpinBox, SettingUI):
    def __init__(self, setting=None, parent=None):
        # type: (Setting, QtWidgets.QWidget) -> None
        super(IntSetting, self).__init__(parent)
        SettingUI.__init__(self, setting)
        self.valueChanged.connect(self.onValueChanged)

    def setSetting(self, setting):
        # type: (Setting) -> None
        super(IntSetting, self).setSetting(setting)
        minmax = setting.property('minmax')
        if minmax:
            lo, hi = minmax
            self.setMinimum(int(lo))
            self.setMaximum(int(hi))
