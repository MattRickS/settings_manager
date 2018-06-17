from PySide2 import QtCore, QtGui, QtWidgets
from settings_manager.ui.setting_widgets.setting_ui import SettingUI


class FloatSetting(QtWidgets.QDoubleSpinBox, SettingUI):
    def __init__(self, setting, parent=None):
        """
        :param Setting setting:
        """
        super(FloatSetting, self).__init__(parent)
        SettingUI.__init__(self, setting)

        minmax = setting.property('minmax')
        if minmax:
            lo, hi = minmax
            self.setMinimum(float(lo))
            self.setMaximum(float(hi))

        self.valueChanged.connect(self.onValueChanged)
