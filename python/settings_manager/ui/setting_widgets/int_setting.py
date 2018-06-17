from PySide2 import QtCore, QtGui, QtWidgets
from settings_manager.ui.setting_widgets.setting_ui import SettingUI


class IntSetting(QtWidgets.QSpinBox, SettingUI):
    def __init__(self, setting, parent=None):
        """
        :param Setting setting:
        """
        super(IntSetting, self).__init__(parent)
        SettingUI.__init__(self, setting)

        minmax = setting.property('minmax')
        if minmax:
            lo, hi = minmax
            self.setMinimum(int(lo))
            self.setMaximum(int(hi))

        # Connection
        self.valueChanged.connect(self.onValueChanged)
