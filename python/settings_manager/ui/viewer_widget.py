from Qt import QtWidgets, QtCore, QtGui
from functools import partial


# TODO: Look at moving all widgets to a Model View system
# EditorWidgets (persistent optional) are the SettingWidgets


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

    def __init__(self, settings, parent=None, prefix="", skip=None):
        """
        :param Settings             settings:   Settings object to build for
        :param QtWidgets.QWidget    parent:     Parent widget
        :param str                  prefix:     Name to prefix all setting with (Default blank)
        :param list[str]            skip:       List of setting names to ignore
        """
        super(SettingsViewer, self).__init__(parent)
        self.prefix = prefix
        self._settings = settings
        self._rows = {}
        layout = self._build_default_layout(skip=skip)
        self.setLayout(layout)

    @property
    def settings(self):
        return self._settings

    def get_widget(self, setting):
        """
        Retrieves the widget for the given setting name.

        :param Setting setting:
        :rtype: QtWidgets.QWidget
        """
        return self._rows[setting][1]

    # -----------------------------------------------------------------
    #                            PROTECTED
    # -----------------------------------------------------------------

    def _build_default_layout(self, skip=None):
        """
        Builds a default grid layout for the UI.

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
            if setting.parent and not setting.parent.get():
                widget.setEnabled(False)
            widget.settingChanged.connect(partial(self.onSettingChanged, setting))

            # Add to Layout
            layout.addWidget(label, row, 0, alignment=QtCore.Qt.AlignTop)
            layout.addWidget(widget, row, 1)

            # If nullable, add a checkbox to disable the value
            null_checkbox = None
            if setting.property('nullable'):
                null_checkbox = QtWidgets.QCheckBox('None')

                # Initial state
                if setting.property('value') is None:
                    null_checkbox.setCheckState(QtCore.Qt.Checked)
                    label.setEnabled(False)
                    widget.setEnabled(False)
                elif setting.get() is None:
                    label.setEnabled(False)
                    null_checkbox.setEnabled(False)
                    widget.setEnabled(False)

                null_checkbox.stateChanged.connect(partial(self._on_none_checkbox_checked, setting))
                layout.addWidget(null_checkbox, row, 2)

            self._rows[setting] = (label, widget, null_checkbox)

            row += 1

        layout.setColumnStretch(1, 1)

        return layout

    # -----------------------------------------------------------------
    #                              SLOTS
    # -----------------------------------------------------------------

    def _on_none_checkbox_checked(self, setting, state):
        label, widget, checkbox = self._rows[setting]
        if state == QtCore.Qt.Checked:
            setting.set(None)
        else:
            # The previous value is still in the disabled widget, set it back
            setting.set(widget.value())
        value = state != QtCore.Qt.Checked
        label.setEnabled(value)
        widget.setEnabled(value)
        self.onSettingChanged(setting)

    def onSettingChanged(self, setting, *args, **kwargs):
        """
        Recursively update the enabled state of all dependent settings

        :param Setting  setting:
        """
        value = bool(setting.property('value'))
        for subsetting in setting.subsettings:
            # Setting might not be in the viewer (hidden, skipped, etc...)
            widgets = self._rows.get(subsetting)
            if widgets is None:
                continue

            # If parent has no valid value, disable all
            # If self is None, disable all but the None box
            label, widget, checkbox = widgets
            curr_value = value & subsetting.property('value') is not None
            label.setEnabled(curr_value)
            widget.setEnabled(curr_value)
            if checkbox:
                checkbox.setEnabled(value)
            self.onSettingChanged(subsetting)
