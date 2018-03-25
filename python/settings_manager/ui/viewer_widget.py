from PySide2 import QtWidgets, QtCore, QtGui
from functools import partial


class SettingsViewer(QtWidgets.QWidget):
    """
    Default widget for the settings object.

    Uses a GridLayout, with the following columns:
        0: Label using the setting name plus any prefix supplied to the widget.
        1: Widget. This is requested from the setting, so can be the default or user supplied.
        2: [Optional] Null checkbox. If the value is nullable, a checkbox is added labelled "None".
            Checking this will disable the widget, and any child widgets.

    Settings are added in sorted order unless the "parent" property is set, in which case it is
    added directly after the parent. SettingsViewer will respect the "parent" property of settings,
    and recursively enable / disable dependent setting widgets whenever a value is changed.

    WARNING:
        Settings.settingChanged is connected to the UI updates. Attempting to connect a UI signal
        to the settingChanged signal will cause infinite recursion. If you need to do this, only
        update the setting if the value has changed, eg:

            >>> def _on_ui_setting_changed(self, setting, value):
            >>>     if value != self.settings.get(setting):
            >>>         self.settings.set(setting, value)
    """

    def __init__(self, settings_obj, parent=None, prefix=""):
        super(SettingsViewer, self).__init__(parent)
        self.prefix = prefix
        self.settings = settings_obj
        layout = self._build_default_layout(settings_obj)
        self.setLayout(layout)

    def get_widget(self, setting):
        """
        Retrieves the widget for the given setting name.

        :param str setting:
        :rtype: QtWidgets.QWidget
        """
        name = self.prefix + self.settings.properties(setting)["label"]
        for label_item, widget_item in self.iter_widgets():
            if label_item.widget().text() == name:
                return widget_item.widget()

    def iter_widgets(self):
        """
        Iterates through (label, widget) pairs. Note, label will be prefix + setting.
        """
        for i in range(self.layout().rowCount()):
            yield self.layout().itemAtPosition(i, 0), self.layout().itemAtPosition(i, 1)

    # -----------------------------------------------------------------
    #                            PROTECTED
    # -----------------------------------------------------------------

    def _build_default_layout(self, settings_obj):
        """
        Builds a default grid layout for the UI.

        :param Settings settings_obj:
        :rtype: QtWidgets.QGridLayout
        """
        layout = QtWidgets.QGridLayout()

        # Order so that children are after their parents
        ordered = list()
        for setting in sorted(settings_obj):
            parent = self.settings.properties(setting)["parent"]
            if parent and parent not in ordered:
                ordered.append(parent)
            if setting not in ordered:
                ordered.append(setting)

        for row, name in enumerate(ordered):
            properties = self.settings.properties(name)

            # Get the widget if required
            if properties["hidden"] or properties["data_type"] == object:
                continue

            # Setup a separate label for the widget
            label = QtWidgets.QLabel(self.prefix + properties["label"])

            # Get the widget defined by the setting - may be user defined
            widget = settings_obj.setting_widget(name)
            parent = properties["parent"]
            if parent and not self.settings.get(parent):
                widget.setEnabled(False)

            # Add to Layout
            layout.addWidget(label, row, 0, alignment=QtCore.Qt.AlignTop)
            layout.addWidget(widget, row, 1)

            # If nullable, add a checkbox to disable the value
            if properties["nullable"]:
                null_checkbox = QtWidgets.QCheckBox("None")

                # Initial state
                if settings_obj.get(name) is None:
                    null_checkbox.setCheckState(QtCore.Qt.Checked)
                    widget.setEnabled(False)

                null_checkbox.stateChanged.connect(partial(self._on_none_checkbox_checked, name))
                layout.addWidget(null_checkbox, row, 2)

        # This would be so much easier if children were edited when parent changed
        self.settings.settingChanged.connect(self._on_setting_changed)

        layout.setColumnStretch(1, 1)

        return layout

    # -----------------------------------------------------------------
    #                              SLOTS
    # -----------------------------------------------------------------

    def _on_none_checkbox_checked(self, setting, state):
        widget = self.get_widget(setting)
        if state == QtCore.Qt.Checked:
            widget.setEnabled(False)
            self._on_setting_changed(setting, False)
        else:
            widget.setEnabled(True)
            self._on_setting_changed(setting, True)

    def _on_setting_changed(self, setting, enabled):
        """
        Recursively update the enabled state of all dependent settings

        :param str      setting:
        :param object   enabled:
        """
        enabled = bool(enabled)
        dependencies = self.settings.dependencies(setting)
        for dependency in dependencies:
            widget = self.get_widget(dependency)
            widget.setEnabled(enabled)
            # Recursively update grandchildren
            self._on_setting_changed(dependency, enabled)
