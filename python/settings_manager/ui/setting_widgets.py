from PySide2 import QtWidgets, QtCore, QtGui

__all__ = [
    "BoolSetting",
    "ChoiceSetting",
    "FloatSetting",
    "IntSetting",
    "ListSetting",
    "StringSetting",
]


class EnterItemDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(EnterItemDialog, self).__init__(parent)

        # ----- Widgets -----

        self.line_edit = QtWidgets.QLineEdit()
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.ok_btn = QtWidgets.QPushButton("Ok")
        self.ok_btn.setDefault(True)

        # ----- Layout -----

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.ok_btn)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.line_edit)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        # ----- Connections -----

        self.cancel_btn.clicked.connect(self.reject)
        self.ok_btn.clicked.connect(self.accept)


# ==============================================================
#                       SETTING WIDGETS
# ==============================================================


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


class ListSetting(QtWidgets.QWidget):
    def __init__(self, settings, setting_name):
        """
        :param Settings settings:
        :param str      setting_name:
        """
        super(ListSetting, self).__init__()
        self.settings = settings
        self.setting_name = setting_name

        # ----- Widgets -----

        self.list_widget = QtWidgets.QListWidget()
        self.add_btn = QtWidgets.QPushButton("+")
        self.add_btn.setFixedWidth(self.add_btn.sizeHint().height())
        self.sub_btn = QtWidgets.QPushButton("-")
        self.sub_btn.setFixedWidth(self.sub_btn.sizeHint().height())

        # ----- Layout -----

        btn_layout = QtWidgets.QVBoxLayout()
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.sub_btn)
        btn_layout.addStretch()

        main_layout = QtWidgets.QHBoxLayout()
        main_layout.addWidget(self.list_widget)
        main_layout.addLayout(btn_layout)

        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

        # ----- Initialise -----

        # Set starting value
        value = self.settings.get(self.setting_name)
        if value:
            self.list_widget.addItems([str(x) for x in value])

        # ----- Connections -----

        self.add_btn.clicked.connect(self._on_add_btn_clicked)
        self.sub_btn.clicked.connect(self._on_sub_btn_clicked)
        self.list_widget.itemChanged.connect(self._on_list_widget_item_changed)

    def _on_add_btn_clicked(self):
        enter_item = EnterItemDialog()
        if enter_item.exec_():
            text = enter_item.line_edit.text()
            self.list_widget.addItem(text)
            self._on_list_widget_item_changed()

    def _on_list_widget_item_changed(self, item=None):
        # All items to text
        lst = list()
        for row in range(self.list_widget.count()):
            text = self.list_widget.item(row).text()
            lst.append(text)

        self.settings.set(self.setting_name, lst)

    def _on_sub_btn_clicked(self):
        for item in self.list_widget.selectedItems():
            index = self.list_widget.indexFromItem(item)
            self.list_widget.takeItem(index.row())
        self._on_list_widget_item_changed()


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
