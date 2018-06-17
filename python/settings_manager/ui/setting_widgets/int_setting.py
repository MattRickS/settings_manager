from PySide2 import QtCore, QtGui, QtWidgets
from settings_manager.ui.setting_widgets.base_settings_ui import BaseSettingsUI


class IntSetting(QtWidgets.QSpinBox, BaseSettingsUI):
    def __init__(self, setting, parent=None):
        """
        :param Setting setting:
        """
        super(IntSetting, self).__init__(parent)
        BaseSettingsUI.__init__(self, setting)

        minmax = setting.property('minmax')
        if minmax:
            lo, hi = minmax
            self.setMinimum(int(lo))
            self.setMaximum(int(hi))

        # Connection
        self.valueChanged.connect(self.onValueChanged)
