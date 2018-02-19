from Qt import QtWidgets, QtCore, QtGui
from functools import partial


class SettingsViewer(QtWidgets.QWidget):
    def __init__(self, settings, parent=None):
        super(SettingsViewer, self).__init__(parent)
        self.settings = settings

        layout = QtWidgets.QGridLayout()

        for row, name in enumerate(sorted(settings)):
            properties = settings.get_properties(name)
            if properties["hidden"]:
                continue
            widget = self._build_setting_widget(name, properties)
            layout.addWidget(QtWidgets.QLabel(properties["label"]), row, 0)
            layout.addWidget(widget, row, 1)

        self.setLayout(layout)

    def _build_setting_widget(self, name, properties):
        if properties["choices"]:
            widget = QtWidgets.QComboBox()
            widget.addItems(map(str, properties["choices"]))
            index = widget.findText(str(properties["default"]))
            widget.setCurrentIndex(index)
            widget.currentIndexChanged.connect(partial(self._on_widget_index_changed, name))
        elif properties["type"] == str:
            widget = QtWidgets.QLineEdit()
            if properties["default"]:
                widget.setText(properties["default"])
            widget.textChanged.connect(partial(self._on_widget_text_changed, name))
        elif properties["type"] == int:
            widget = QtWidgets.QSpinBox()
            widget.setMaximum(1000000)
            widget.setValue(properties["default"])
            widget.valueChanged.connect(partial(self._on_widget_value_changed, name))
        elif properties["type"] == float:
            widget = QtWidgets.QDoubleSpinBox()
            widget.setMaximum(10000)
            widget.setValue(properties["default"])
            widget.valueChanged.connect(partial(self._on_widget_value_changed, name))
        elif properties["type"] == bool:
            widget = QtWidgets.QCheckBox()
            widget.stateChanged.connect(partial(self._on_widget_checked, name))
        else:
            raise TypeError("Unknown setting type: {}".format(properties["type"]))

        return widget

    # ================================== SLOTS ==================================

    def _on_widget_checked(self, name, check_state):
        self.settings[name] = bool(check_state)

    def _on_widget_index_changed(self, name, index):
        # Retrieve value from choices list, not combo box strings.
        data_type = self.settings.get_properties(name)["choices"][index]
        self.settings[name] = data_type

    def _on_widget_text_changed(self, name, value):
        # Ensure the correct formatting is kept
        data_type = self.settings.get_properties(name)["type"]
        self.settings[name] = data_type(value)

    def _on_widget_value_changed(self, name, value):
        self.settings[name] = value
