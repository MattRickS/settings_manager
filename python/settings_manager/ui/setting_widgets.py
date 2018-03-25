from Qt import QtWidgets, QtCore, QtGui

__all__ = [
    "BoolSetting",
    "ChoiceSetting",
    "FloatSetting",
    "IntSetting",
    "StringSetting",
]


class BoolSetting(QtWidgets.QCheckBox):
    def __init__(self, settings, setting_name):
        """
        :param Settings settings:
        :param str      setting_name:
        """
        super(BoolSetting, self).__init__()
        self.settings = settings
        self.setting_name = setting_name

        # Set starting value
        value = self.settings.get(setting_name)
        if value:
            self.setCheckState(QtCore.Qt.Checked)

        # Connection
        self.stateChanged.connect(self._on_checkbox_checked)

    # -----------------------------------------------------------------
    #                              SLOTS
    # -----------------------------------------------------------------

    def _on_checkbox_checked(self, state):
        if state == QtCore.Qt.Checked:
            self.settings.set(self.setting_name, True)
        else:
            self.settings.set(self.setting_name, False)


class ChoiceSetting(QtWidgets.QComboBox):
    def __init__(self, settings, setting_name):
        """
        :param Settings settings:
        :param str      setting_name:
        """
        super(ChoiceSetting, self).__init__()
        self.settings = settings
        self.setting_name = setting_name

        # Initialise choices
        properties = self.settings.properties(self.setting_name)
        self.addItems(list(map(str, properties["choices"])))

        # Set starting value
        value = self.settings.get(self.setting_name)
        if value:
            index = self.findText(str(value))
            self.setCurrentIndex(index)

        # Connection
        self.currentIndexChanged.connect(self._on_combo_index_changed)

    # -----------------------------------------------------------------
    #                              SLOTS
    # -----------------------------------------------------------------

    def _on_combo_index_changed(self, index):
        choice = self.settings.properties(self.setting_name)["choices"][index]
        self.settings.set(self.setting_name, choice)


class FloatSetting(QtWidgets.QDoubleSpinBox):
    def __init__(self, settings, setting_name):
        """
        :param Settings settings:
        :param str      setting_name:
        """
        super(FloatSetting, self).__init__()
        self.settings = settings
        self.setting_name = setting_name

        # Set starting value
        value = self.settings.get(setting_name)
        if value:
            self.setValue(value)

        # Connection
        self.valueChanged.connect(self._on_value_changed)

    # -----------------------------------------------------------------
    #                              SLOTS
    # -----------------------------------------------------------------

    def _on_value_changed(self, value):
        self.settings.set(self.setting_name, value)


class IntSetting(QtWidgets.QSpinBox):
    def __init__(self, settings, setting_name):
        """
        :param Settings settings:
        :param str      setting_name:
        """
        super(IntSetting, self).__init__()
        self.settings = settings
        self.setting_name = setting_name

        # Set starting value
        value = self.settings.get(setting_name)
        if value:
            self.setValue(value)

        # Connection
        self.valueChanged.connect(self._on_value_changed)

    # -----------------------------------------------------------------
    #                              SLOTS
    # -----------------------------------------------------------------

    def _on_value_changed(self, value):
        self.settings.set(self.setting_name, value)


class StringSetting(QtWidgets.QLineEdit):
    def __init__(self, settings, setting_name):
        """
        :param Settings settings:
        :param str      setting_name:
        """
        super(StringSetting, self).__init__()
        self.settings = settings
        self.setting_name = setting_name

        # Set starting value
        value = self.settings.get(setting_name)
        if value:
            self.setText(value)

        # Connection
        self.textChanged.connect(self._on_line_text_changed)

    # -----------------------------------------------------------------
    #                              SLOTS
    # -----------------------------------------------------------------

    def _on_line_text_changed(self, text):
        # Convert to data type to keep encoding
        data_type = self.settings.properties(self.setting_name)["data_type"]
        self.settings.set(self.setting_name, data_type(text))
