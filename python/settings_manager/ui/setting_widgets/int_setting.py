from PySide2 import QtCore, QtGui, QtWidgets
from settings_manager.ui.setting_widgets.base_settings_ui import BaseSettingsUI


class IntSetting(QtWidgets.QSpinBox, BaseSettingsUI):
    def __init__(self, settings, setting_name, parent=None):
        """
        :param Settings settings:
        :param str      setting_name:
        """
        super(IntSetting, self).__init__(parent)
        BaseSettingsUI.__init__(self, settings, setting_name)

        properties = self.settings.properties(setting_name)
        minmax = properties["minmax"]
        if minmax:
            lo, hi = minmax
            self.setMinimum(int(lo))
            self.setMaximum(int(hi))

        # Connection
        self.valueChanged.connect(self.settingChanged.emit)
