from Qt import QtWidgets, QtCore, QtGui
from functools import partial


class SettingsViewer(QtWidgets.QDialog):
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

    def __init__(self, settings_obj, parent=None, prefix="", skip=None):
        """
        :param Settings             settings_obj:   Settings object to build for
        :param QtWidgets.QWidget    parent:         Parent widget
        :param str                  prefix:         Name to prefix all setting with (Default blank)
        :param list[str]            skip:           List of setting names to ignore
        """
        super(SettingsViewer, self).__init__(parent)
        self.prefix = prefix
        self._settings = settings_obj
        layout = self._build_default_layout(settings_obj, skip=skip)
        self.setLayout(layout)

    @property
    def settings(self):
        return self._settings

    def get_widget(self, setting):
        """
        Retrieves the widget for the given setting name.

        :param str setting:
        :rtype: QtWidgets.QWidget
        """
        name = self._settings.setting(setting).property("label")
        for label, widget, checkbox in self.iter_widgets():
            if label == name:
                return widget

    def iter_widgets(self):
        """
        Iterates through (setting_label, widget, checkbox/None) tuples
        """
        prefix_len = len(self.prefix)
        for i in range(self.layout().rowCount()):
            label_item = self.layout().itemAtPosition(i, 0)
            widget_item = self.layout().itemAtPosition(i, 1)
            checkbox_item = self.layout().itemAtPosition(i, 2)

            checkbox_widget = checkbox_item.widget() if checkbox_item else None
            setting_label = label_item.widget().text()[prefix_len:]

            yield setting_label, widget_item.widget(), checkbox_widget

    # -----------------------------------------------------------------
    #                            PROTECTED
    # -----------------------------------------------------------------

    def _build_default_layout(self, settings_obj, skip=None):
        """
        Builds a default grid layout for the UI.

        :param Settings settings_obj:
        :rtype: QtWidgets.QGridLayout
        """
        skip = skip or list()
        layout = QtWidgets.QGridLayout()

        # Count ourselves instead of enumerate to avoid invalid rows when skipping
        row = 0
        for name in self._settings:
            setting = self._settings.setting(name)

            hidden = setting.property('hidden')
            data_type = setting.property('data_type')

            # Get the widget if required
            if hidden or data_type == object or name in skip:
                continue

            # Setup a separate label for the widget
            label = setting.property('label')
            label = QtWidgets.QLabel(self.prefix + label)

            # Get the widget defined by the setting - may be user defined
            widget = setting.widget()
            parent = setting.property('parent')
            if parent and not parent.get():
                widget.setEnabled(False)

            # Add to Layout
            layout.addWidget(label, row, 0, alignment=QtCore.Qt.AlignTop)
            layout.addWidget(widget, row, 1)

            # If nullable, add a checkbox to disable the value
            if setting.property('nullable'):
                null_checkbox = QtWidgets.QCheckBox("None")

                # Initial state
                if settings_obj.get(name) is None:
                    null_checkbox.setCheckState(QtCore.Qt.Checked)
                    widget.setEnabled(False)

                null_checkbox.stateChanged.connect(partial(self._on_none_checkbox_checked, name))
                layout.addWidget(null_checkbox, row, 2)

            row += 1

        # This would be so much easier if children were edited when parent changed
        self.settings.settingChanged.connect(self.onSettingChanged)

        layout.setColumnStretch(1, 1)

        return layout

    # -----------------------------------------------------------------
    #                              SLOTS
    # -----------------------------------------------------------------

    def _on_none_checkbox_checked(self, setting, state):
        widget = self.get_widget(setting)
        value = state != QtCore.Qt.Checked
        widget.setEnabled(value)
        self.onSettingChanged(setting, value)

    def onSettingChanged(self, setting, enabled):
        """
        Recursively update the enabled state of all dependent settings

        :param str      setting:
        :param object   enabled:
        """
        enabled = bool(enabled)
        self._settings.properties(setting)["enabled"] = enabled
        dependencies = self.settings.dependents(setting)
        for dependency in dependencies:
            # Widget might be hidden / not valid - continue recursing but only set valid widgets
            widget = self.get_widget(dependency)
            if widget:
                widget.setEnabled(enabled)
            # Recursively update grandchildren
            self.onSettingChanged(dependency, enabled)
