from PySide2 import QtCore, QtGui, QtWidgets


class BaseSettingsUI(object):
    """
    Provides a common interface for settings widgets.
    Must be initialised after the parent widget for the signal to work.
    """
    settingChanged = QtCore.Signal(object)

    def __init__(self, settings, setting_name):
        self._settings = settings
        self._setting_name = setting_name

        # Set starting value -- nullable settings would be blank if using get(),
        # use value property directly and let it be disabled
        value = self.settings.properties(self._setting_name)["value"]
        if value:
            self.setValue(value)

        # Connection
        self.settingChanged.connect(self.onSettingChanged)

    @property
    def settings(self):
        return self._settings

    @property
    def settingName(self):
        return self._setting_name

    def setValue(self, value):
        raise NotImplementedError

    def onSettingChanged(self, value):
        self.settings.set(self._setting_name, value)
