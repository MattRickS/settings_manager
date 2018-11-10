from Qt import QtCore, QtGui, QtWidgets

from settings_manager.setting import Setting
from settings_manager.ui.setting_widgets.setting_ui import SettingUI


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


class ListSetting(QtWidgets.QWidget, SettingUI):
    def __init__(self, setting=None, parent=None):
        # type: (Setting, QtWidgets.QWidget) -> None
        super(ListSetting, self).__init__(parent)

        # ----- Widgets -----

        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.setAcceptDrops(True)
        self.list_widget.setDragEnabled(True)
        self.list_widget.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.list_widget.setDropIndicatorShown(True)

        self.add_btn = QtWidgets.QPushButton('+')
        self.add_btn.setFixedWidth(self.add_btn.sizeHint().height())
        self.add_btn.setEnabled(False)

        self.sub_btn = QtWidgets.QPushButton('-')
        self.sub_btn.setFixedWidth(self.sub_btn.sizeHint().height())
        self.sub_btn.setEnabled(False)

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

        # ----- Connections -----

        self.add_btn.clicked.connect(self._on_add_btn_clicked)
        self.sub_btn.clicked.connect(self._on_sub_btn_clicked)
        self.list_widget.itemChanged.connect(self.onValueChanged)
        self.list_widget.model().rowsMoved.connect(self._on_rows_moved)
        self.list_widget.selectionModel().selectionChanged.connect(self._on_selection_changed)

        # ----- Initialise -----

        SettingUI.__init__(self, setting)

    def onValueChanged(self, value):
        # Use self.value() as it uses a list of strings, whereas the
        # valueChanged uses a single QtWidgets.ListWidgetItem or None
        value = self.value()
        super(ListSetting, self).onValueChanged(value)
        self._enable_buttons()

    def setSetting(self, setting):
        # type: (Setting) -> None
        super(ListSetting, self).setSetting(setting)
        self._enable_buttons()

    def setValue(self, value):
        # type: (list) -> None
        self.list_widget.clear()
        for x in value:
            self._add_item(str(x))

    def sizeHint(self):
        return QtCore.QSize(100, 80)

    def value(self):
        # type: () -> list[str]
        num_items = self.list_widget.count()
        lst = [self.list_widget.item(row).text() for row in range(num_items)]
        return lst

    # ======================================================================== #
    #                                PROTECTED                                 #
    # ======================================================================== #

    def _add_item(self, text):
        # type: (str) -> QtWidgets.QListWidgetItem
        item = QtWidgets.QListWidgetItem(text, self.list_widget)
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
        return item

    def _enable_buttons(self):
        if self._setting is None:
            self.add_btn.setEnabled(False)
            self.sub_btn.setEnabled(False)
            return

        has_selection = bool(self.list_widget.selectedIndexes())
        value = self._setting.get()
        minmax = self._setting.property('minmax')
        if minmax:
            lo, hi = minmax
            self.add_btn.setEnabled(hi > len(value))
            self.sub_btn.setEnabled(has_selection and lo < len(value))
        else:
            self.add_btn.setEnabled(True)
            self.sub_btn.setEnabled(has_selection)

    # ======================================================================== #
    #                                  SLOTS                                   #
    # ======================================================================== #

    def _on_add_btn_clicked(self):
        enter_item = EnterItemDialog()
        if enter_item.exec_():
            text = enter_item.line_edit.text()
            self._add_item(text)

    def _on_rows_moved(self, parent, start, end, destination, row):
        # Force the setting to update
        self.onValueChanged(None)

    def _on_selection_changed(self, selected, deselected):
        self._enable_buttons()

    def _on_sub_btn_clicked(self):
        for item in self.list_widget.selectedItems():
            index = self.list_widget.indexFromItem(item)
            self.list_widget.takeItem(index.row())
            self.list_widget.itemChanged.emit(item)
