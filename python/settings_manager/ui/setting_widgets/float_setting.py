from PySide2 import QtCore, QtGui, QtWidgets
from settings_manager.ui.setting_widgets.base_settings_ui import BaseSettingsUI


class FloatSetting(QtWidgets.QDoubleSpinBox, BaseSettingsUI):
    def __init__(self, setting, parent=None):
        """
        :param Setting setting:
        """
        super(FloatSetting, self).__init__(parent)
        BaseSettingsUI.__init__(self, setting)

        minmax = setting.property('minmax')
        if minmax:
            lo, hi = minmax
            self.setMinimum(float(lo))
            self.setMaximum(float(hi))

        self.valueChanged.connect(self.settingChanged.emit)


if __name__ == '__main__':
    from settings_manager import Settings

    s = Settings()
    s.add('float', 10.0)

    import sys
    app = QtWidgets.QApplication(sys.argv)

    widget = FloatSetting(s.setting('float'))
    widget.show()

    app.exec_()
    print(s.as_dict(values_only=True))
