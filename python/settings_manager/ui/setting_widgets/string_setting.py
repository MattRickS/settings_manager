from PySide2 import QtCore, QtGui, QtWidgets

from settings_manager.setting import Setting
from settings_manager.ui.setting_widgets.setting_ui import SettingUI


class LengthValidator(QtGui.QValidator):
    def __init__(self, minmax, parent=None):
        # type: (tuple[int, int], QtWidgets.QWidget) -> None
        super(LengthValidator, self).__init__(parent)
        self.lo, self.hi = minmax
        self._last_valid = None

    @property
    def last_valid(self):
        # type: () -> str
        return self._last_valid

    def fixup(self, text):
        # type: (str) -> None
        # PySide bug does not actually use this behaviour
        return self._last_valid

    def validate(self, text, pos):
        # type: (str, int) -> int
        length = len(text)
        if length > self.hi:
            return QtGui.QValidator.Invalid
        elif length < self.lo:
            return QtGui.QValidator.Intermediate
        else:
            self._last_valid = text
            return QtGui.QValidator.Acceptable


class StringSetting(QtWidgets.QLineEdit, SettingUI):
    def __init__(self, setting=None, parent=None):
        # type: (Setting, QtWidgets.QWidget) -> None
        super(StringSetting, self).__init__(parent)
        SettingUI.__init__(self, setting)
        self.editingFinished.connect(self.onValueChanged)

    def setSetting(self, setting):
        # type: (Setting) -> None
        super(StringSetting, self).setSetting(setting)
        minmax = setting.property('minmax')
        validator = LengthValidator(minmax, self) if minmax else None
        self.setValidator(validator)

    def setValue(self, value):
        # type: (str) -> None
        self.setText(value)

    def value(self):
        # type: () -> str
        return self.text()

    def onValueChanged(self, value=None):
        # type: (str) -> None
        # Unlike most onValueChanged signals, this is connected to
        # editingFinished (in case of validation) which sends no value.
        # Note: value may be empty string, check None explicitly
        if value is None:
            value = self.value()
        # Convert to data type to keep encoding
        super(StringSetting, self).onValueChanged(self._setting.type(value))

    # ======================================================================== #
    #                               TEXT VALIDATION                            #
    # ======================================================================== #

    def focusOutEvent(self, event):
        super(StringSetting, self).focusOutEvent(event)
        self._fix_text()

    def keyPressEvent(self, event):
        super(StringSetting, self).keyPressEvent(event)
        if event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
            self._fix_text()

    def _fix_text(self):
        validator = self.validator()
        if validator and validator.validate(self.text(), 0) != validator.Acceptable:
            self.setText(validator.last_valid)
            self.onValueChanged()
