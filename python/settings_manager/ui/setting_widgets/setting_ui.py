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

        # Set starting value -- nullable settings would be blank if using get(),
        # use value property directly and let it be disabled
        value = self._setting.property('value')
        if value:
            self.setValue(value)

    @property
    def setting(self):
        return self._setting

    def setValue(self, value):
        """ For setting the widget value should trigger onValueChanged """
        raise NotImplementedError

    def value(self):
        """ Should return UI setting value, eg, Qt.Checked """
        raise NotImplementedError

    def onValueChanged(self, value):
        """ Sets the setting and emits the settingChanged signal """
        self._setting.set(value)
        self.settingChanged.emit(self._setting)
