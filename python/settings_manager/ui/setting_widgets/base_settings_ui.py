from PySide2 import QtCore, QtGui, QtWidgets


class BaseSettingsUI(object):
    """
    Provides a common interface for settings widgets.
    Must be initialised after the parent widget for the signal to work.
    """
    settingChanged = QtCore.Signal(object)  # Setting

    def __init__(self, setting):
        self._setting = setting

        # Set starting value -- nullable settings would be blank if using get(),
        # use value property directly and let it be disabled
        value = self._setting.property('value')
        if value:
            self.setValue(value)

        # Connection
        self.settingChanged.connect(self.onSettingChanged)

    @property
    def setting(self):
        return self._setting

    def setValue(self, value):
        raise NotImplementedError

    def onSettingChanged(self, value):
        self._setting.set(value)
