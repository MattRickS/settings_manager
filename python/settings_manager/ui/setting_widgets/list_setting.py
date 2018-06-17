from PySide2 import QtCore, QtGui, QtWidgets
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
    def __init__(self, setting):
        """
        :param Setting setting:
        """
        super(ListSetting, self).__init__()
        self.list_widget = QtWidgets.QListWidget()

        # ----- Widgets -----

        self.add_btn = QtWidgets.QPushButton('+')
        self.add_btn.setFixedWidth(self.add_btn.sizeHint().height())
        self.sub_btn = QtWidgets.QPushButton('-')
        self.sub_btn.setFixedWidth(self.sub_btn.sizeHint().height())
        # TODO: add up/down arrows
        # TODO: add edit button (eg, fixed size list)

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

        # ----- Initialise -----

        SettingUI.__init__(self, setting)
        self._enable_buttons()

    def setValue(self, value):
        self.list_widget.clear()
        self.list_widget.addItems([str(x) for x in value])
        self.onValueChanged(None)

    def value(self):
        # All items to text
        lst = list()
        for row in range(self.list_widget.count()):
            text = self.list_widget.item(row).text()
            lst.append(text)
        return lst

    def onValueChanged(self, value):
        value = self.value()
        super(ListSetting, self).onValueChanged(value)
        self._enable_buttons()

    def _enable_buttons(self):
        value = self._setting.property('value')
        minmax = self._setting.property('minmax')
        if minmax:
            lo, hi = minmax
            self.add_btn.setEnabled(hi > len(value))
            self.sub_btn.setEnabled(lo < len(value))

    def _on_add_btn_clicked(self):
        enter_item = EnterItemDialog()
        if enter_item.exec_():
            text = enter_item.line_edit.text()
            item = self.list_widget.addItem(text)
            self.list_widget.itemChanged.emit(item)

    def _on_sub_btn_clicked(self):
        for item in self.list_widget.selectedItems():
            index = self.list_widget.indexFromItem(item)
            self.list_widget.takeItem(index.row())
            self.list_widget.itemChanged.emit(item)
