from PySide2 import QtCore, QtGui, QtWidgets

from settings_manager.setting import Setting
from settings_manager.exceptions import SettingsError


class SettingUI(object):
    """
    Provides a common interface for settings widgets.
    Must be initialised after the parent widget.

    To subclass:
        Subclass onValueChanged to:
        * Cast the UI values to python values, eg, QtCore.Qt.Checked -> True
        Connect the widget's normal 'valueChanged' signal to self.onValueChanged
        Implement setValue() to update the widget (should trigger the signal
        that triggers onValueChanged)
        Implement value() to return the widget value
        Add any setup data to setSetting() after calling the superclass method

    """
    settingChanged = QtCore.Signal(object)  # Setting

    def __init__(self, setting=None):
        # type: (Setting) -> None
        self._setting = None
        self._ignore_value_changed = False
        if setting is not None:
            self.setSetting(setting)

    @property
    def setting(self):
        """
        :rtype: Setting
        """
        return self._setting

    def setSetting(self, setting):
        """
        Sets the Setting to display. This calls setValue using the current
        Setting value

        :param Setting  setting:
        """
        self._setting = setting
        value = self._setting.get()
        # Disable any signals triggering while initialising the value
        self._ignore_value_changed = True
        self.setValue(value)
        self._ignore_value_changed = False

        tooltip = self._setting.property('tooltip')
        if tooltip:
            self.setToolTip(tooltip)

    def setValue(self, value):
        """
        Must be subclassed to set the UI widget and the Setting value

        Note:
            Method should take the UI value, eg, QtCore.Qt.Checked -> True
        """
        raise NotImplementedError

    def value(self):
        """ Should return UI setting value, eg, Qt.Checked """
        raise NotImplementedError

    # ======================================================================== #
    #                                   SLOTS                                  #
    # ======================================================================== #

    def onValueChanged(self, value):
        """
        Sets the Setting and emits the settingChanged signal. This must be
        connected in the subclass

        Note:
            This method assumes the value is the pure python representation,
            but the method should be subclassed to take the UI value

        Example:
            def onValueChanged(self, value):
                py_value = True if value == QtCore.Qt.Checked else False
                super(SettingUI, self).onValueChanged(py_value)
        """
        if self._ignore_value_changed:
            return
        try:
            self._setting.set(value)
            self.settingChanged.emit(self._setting)
        except SettingsError:
            pass
