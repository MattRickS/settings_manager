from settings_manager import SettingsGroup
from settings_manager.ui import show_settings
from Qt import QtCore, QtGui, QtWidgets


# Define custom widget as class
class MultiLineSettings(QtWidgets.QPlainTextEdit):
    def __init__(self, settings, setting_name):
        super(MultiLineSettings, self).__init__()
        self.settings = settings
        self.setting_name = setting_name

        # Better to use the property directly in case value is disabled
        value = settings.properties(setting_name)["value"]
        if value:
            self.setPlainText(str(value))

        self.textChanged.connect(self._on_plain_text_changed)

    def _on_plain_text_changed(self):
        self.settings.set(self.setting_name, self.toPlainText())


# Define custom widget as function
def plain_text_edit(settings, setting_name):
    editor = QtWidgets.QPlainTextEdit()

    # Better to use the property directly in case value is disabled
    value = settings.properties(setting_name)["value"]
    if value:
        editor.setPlainText(str(value))

    def _on_plain_text_changed():
        settings.set(setting_name, editor.toPlainText())

    editor.textChanged.connect(_on_plain_text_changed)
    return editor


if __name__ == '__main__':
    # Check and see -- they both work the same
    s = SettingsGroup()
    s.add("enable_options", True, label="Enable Options?")
    s.add("multi_line_class", 'Line 1\nLine 2', label="Multi Line Class",
          nullable=True, parent="enable_options", widget=MultiLineSettings)
    s.add("multi_line_method", 'Line 1\nLine 2', label="Multi Line Method",
          nullable=True, parent="enable_options", widget=plain_text_edit)
    show_settings(s)
