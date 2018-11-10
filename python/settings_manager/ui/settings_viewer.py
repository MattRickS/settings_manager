from functools import partial
from collections import namedtuple

from Qt import QtWidgets, QtCore, QtGui

from settings_manager.setting import Setting
from settings_manager.settings_group import SettingsGroup
from settings_manager.ui.setting_widgets import create_setting_widget


Row = namedtuple('Row', 'label widget null')


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
    settingChanged = QtCore.Signal(object)  # Setting

    @classmethod
    def launch(cls, settings, parent=None):
        # type: (SettingsGroup, QtWidgets.QWidget) -> cls
        """
        Initialises and shows the viewer. If no QApplication instance is
        available, one is initialised.
        """
        app = None if QtWidgets.QApplication.instance() else QtWidgets.QApplication([])
        widget = cls(settings, parent=parent)
        if app:
            widget.show()
            app.exec_()
        else:
            widget.exec_()
        return widget

    def __init__(self, settings=None, parent=None):
        # type: (SettingsGroup, QtWidgets.QWidget) -> None
        super(SettingsViewer, self).__init__(parent)
        self._rows = {}
        self._settings = settings
        layout = QtWidgets.QGridLayout()

        # Stretch the widgets rather than the labels
        layout.setColumnStretch(1, 1)
        self.setLayout(layout)

        if self._settings is not None:
            self.rebuild_layout(self._settings)

    @property
    def settings(self):
        # type: () -> SettingsGroup
        return self._settings

    def clear(self):
        layout = self.layout()
        while self._rows:
            name, row = self._rows.popitem()
            for widget in row:
                if widget:
                    layout.removeWidget(widget)

    def get_row(self, setting):
        # type: (Setting|str) -> Row
        if isinstance(setting, Setting):
            setting = setting.name
        return self._rows[setting]

    def rebuild_layout(self, settings, build_settings=None):
        # type: (SettingsGroup, list[str]) -> None
        """ Builds the widgets for the settings, optionally only using build_settings """
        self.clear()

        build_settings = build_settings or tuple(settings)
        layout = self.layout()
        self._settings = settings

        # Count instead of enumerate to avoid invalid rows when skipping
        row = 0
        for name in build_settings:
            setting = settings.setting(name)
            if setting.property('hidden'):
                continue

            # Get the widget defined by the setting - may be user defined
            label = QtWidgets.QLabel(setting.property('label'))
            widget = create_setting_widget(setting)
            widget.settingChanged.connect(self.settingChanged)

            layout.addWidget(label, row, 0, alignment=QtCore.Qt.AlignTop)
            layout.addWidget(widget, row, 1)

            # If nullable, add a checkbox to disable the value
            null_checkbox = None
            if setting.property('nullable'):
                null_checkbox = QtWidgets.QCheckBox('None')

                # Initial state
                if setting.get() is None:
                    null_checkbox.setCheckState(QtCore.Qt.Checked)
                    label.setEnabled(False)
                    widget.setEnabled(False)

                null_checkbox.stateChanged.connect(
                    partial(self._on_none_checkbox_checked, setting)
                )
                layout.addWidget(null_checkbox, row, 2)

            self._rows[name] = Row(label, widget, null_checkbox)
            row += 1

    def set_setting_hidden(self, setting, hidden):
        # type: (Setting|str, bool) -> None
        # Get the row and hide/show each widget
        row = self.get_row(setting)
        method = 'hide' if hidden else 'show'
        for widget in row:
            if widget:
                getattr(widget, method)()

    def set_setting_none(self, setting, is_none):
        # type: (Setting|str, bool) -> bool
        row = self.get_row(setting)
        if not row.null:
            return False
        state = QtCore.Qt.Checked if is_none else QtCore.Qt.Unchecked
        row.null.setCheckState(state)
        return True

    # ======================================================================== #
    #                                  SLOTS                                   #
    # ======================================================================== #

    def _on_none_checkbox_checked(self, setting, state):
        # type:(Setting, QtCore.Qt.CheckState) -> None
        row = self._rows[setting]
        is_none = state == QtCore.Qt.Checked
        row.widget.setNone(is_none)
        row.label.setEnabled(not is_none)
        self.settingChanged.emit(setting)
