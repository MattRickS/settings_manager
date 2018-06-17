from Qt import QtWidgets, QtCore, QtGui
from functools import partial


# TODO: Look at moving all widgets to a Model View system
# EditorWidgets (persistent optional) are the SettingWidgets


class SettingsViewer(QtWidgets.QDialog):
    """
    Default widget for the settings object.

    Uses a GridLayout, with the following columns:
        0: Label using the setting name plus any prefix supplied to the widget.
        1: Widget. This is requested from the setting, so can be the default or
           user defined.
        2: [Optional] Null checkbox. If the value is nullable, a checkbox is
           added labelled 'None'. Checking this will disable the widget, and any
           child widgets.

    Settings are added in sorted order. SettingsViewer will respect the 'parent'
    property of settings, and recursively enable / disable dependent setting
    widgets whenever a value is changed.
    """

    def __init__(self, settings, parent=None, prefix='', skip=None):
        """
        :param Settings             settings:   Settings object to build for
        :param QtWidgets.QWidget    parent:     Parent widget
        :param str                  prefix:     Name to prefix all setting with
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
        """
        :rtype: Settings
        """
        return self._settings

    def get_row(self, setting):
        """
        :param Setting setting:
        :rtype: tuple(QtWidgets.QLabel, QtWidgets.QWidget, QtWidgets.QCheckbox)
        """
        return self._rows[setting]

    def get_widget(self, setting):
        """
        Retrieves the widget for the given setting name.

        :param Setting setting:
        :rtype: QtWidgets.QWidget
        """
        return self._rows[setting][1]

    def _build_default_layout(self, skip=None):
        """
        Builds a default grid layout for the UI.

        :rtype: QtWidgets.QGridLayout
        """
        skip = skip or list()
        layout = QtWidgets.QGridLayout()

        # Count instead of enumerate to avoid invalid rows when skipping
        row = 0
        for name in self._settings:
            setting = self._settings.setting(name)

            # Get the widget if required
            hidden = setting.property('hidden')
            if hidden or name in skip:
                continue

            # Setup a separate label for the widget
            label = setting.property('label')
            label = QtWidgets.QLabel(self.prefix + label)

            # Get the widget defined by the setting - may be user defined
            widget = setting.widget()
            if setting.parent and not setting.parent.get():
                widget.setEnabled(False)
            widget.settingChanged.connect(
                partial(self.onSettingChanged, setting))

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
                    null_checkbox.setEnabled(False)
                    label.setEnabled(False)
                    widget.setEnabled(False)

                null_checkbox.stateChanged.connect(
                    partial(self._on_none_checkbox_checked, setting))
                layout.addWidget(null_checkbox, row, 2)

            self._rows[setting] = (label, widget, null_checkbox)

            row += 1

        layout.setColumnStretch(1, 1)

        return layout

    # ======================================================================== #
    #                                  SLOTS                                   #
    # ======================================================================== #

    def _on_none_checkbox_checked(self, setting, state):
        """
        :param Setting              setting:
        :param QtCore.Qt.ChedkState state:
        """
        label, widget, checkbox = self._rows[setting]
        is_not_none = state != QtCore.Qt.Checked
        # The previous value is still in the disabled widget, set it back
        value = widget.value() if is_not_none else None
        setting.set(value)
        label.setEnabled(is_not_none)
        widget.setEnabled(is_not_none)
        self.onSettingChanged(setting)

    def onSettingChanged(self, setting, *args, **kwargs):
        """
        Recursively update the enabled state of all dependent settings

        :param Setting  setting:
        """
        value = bool(setting.get())
        for subsetting in setting.subsettings:
            # Setting might not be in the viewer (hidden, skipped, etc...)
            widgets = self._rows.get(subsetting)
            if widgets is None:
                continue

            # If any ancestors are None, disable all
            # If self is None, disable all but the None box
            label, widget, checkbox = widgets
            curr_value = value & (subsetting.property('value') is not None)
            label.setEnabled(curr_value)
            widget.setEnabled(curr_value)
            if checkbox:
                checkbox.setEnabled(value)
            self.onSettingChanged(subsetting)
