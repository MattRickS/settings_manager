from PySide2 import QtCore, QtGui, QtWidgets


class SettingUI(object):
    """
    Provides a common interface for settings widgets.
    Must be initialised after the parent widget for the signal to work.

    To subclass:
        Connect the widget's normal 'valueChanged' signal to self.onValueChanged
        Implement setValue() to either call onValueChanged or emit the
        'valueChanged' signal
        Implement value to return the widget value

    """
    settingChanged = QtCore.Signal(object)  # Setting

    def __init__(self, setting):
        self._setting = setting
        self._last_value = None
        if setting:
            self.setSetting(setting)

    @property
    def setting(self):
        """
        :rtype: Setting
        """
        return self._setting

    def setSetting(self, setting):
        """
        :param Setting  setting:
        """
        self._setting = setting

        # Set starting value -- nullable settings would be blank if using get(),
        # use value property directly and let it be disabled
        value = self._setting.property('value')
        if value:
            self.setValue(value)

    def setValue(self, value):
        """ For setting the widget value should trigger onValueChanged """
        if value is None:
            self.setNone()
        else:
            self._last_value = value

    def value(self):
        """ Should return UI setting value, eg, Qt.Checked """
        raise NotImplementedError

    def onValueChanged(self, value):
        """ Sets the setting and emits the settingChanged signal """
        self._setting.set(value)
        self.settingChanged.emit(self._setting)

    def setNone(self):
        self._setting.set(None)
        self.setEnabled(False)

    def restoreLastValue(self):
        self.setValue(self._last_value)
        self.setEnabled(True)
