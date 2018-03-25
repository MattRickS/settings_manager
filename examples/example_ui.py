from settings_manager import Settings
from Qt import QtCore, QtGui, QtWidgets
import sys

settings = Settings()
settings.add("enable_options", True, label="Enable Options?")
settings.add("number_of_tries", 1, label="Number of Tries", parent="enable_options")
settings.add("options", "down", choices=["up", "down", "left", "right"], parent="enable_options")
settings.add("custom_command", None, data_type=str, label="Custom Command")

app = QtWidgets.QApplication(sys.argv)
widget = settings.widget()
widget.show()
app.exec_()

for setting in settings:
    sys.stdout.write("{} : {}\n".format(setting, settings.get(setting)))

sys.exit()
