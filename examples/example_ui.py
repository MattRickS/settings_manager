from settings_manager import Settings
from Qt import QtCore, QtGui, QtWidgets
import sys


class MultiLineSettings(QtWidgets.QPlainTextEdit):
    def __init__(self, settings, setting_name):
        super(MultiLineSettings, self).__init__()
        self.settings = settings
        self.setting_name = setting_name

        value = self.settings.get(setting_name)
        if value:
            self.setPlainText(str(value))

        self.textChanged.connect(self._on_plain_text_changed)

    def _on_plain_text_changed(self):
        self.settings.set(self.setting_name, self.toPlainText())


settings = Settings()
settings.add("enable_options", True, label="Enable Options?")
settings.add("number_of_tries", 1, label="Number of Tries", parent="enable_options")
settings.add("options", "down", choices=["up", "down", "left", "right"], parent="enable_options")
settings.add("custom_command", None, data_type=str,
             label="Custom Command", widget=MultiLineSettings)

app = QtWidgets.QApplication(sys.argv)
widget = settings.widget()
widget.show()
app.exec_()

for setting in settings:
    sys.stdout.write("{} : {}\n".format(setting, settings.get(setting)))

sys.exit()
