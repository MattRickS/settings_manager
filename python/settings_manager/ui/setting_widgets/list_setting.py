from PySide2 import QtCore, QtGui, QtWidgets
from settings_manager.ui.setting_widgets.base_settings_ui import BaseSettingsUI


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


class ListSetting(QtWidgets.QWidget, BaseSettingsUI):
    def __init__(self, settings, setting_name):
        """
        :param Settings settings:
        :param str      setting_name:
        """
        super(ListSetting, self).__init__()
        self.list_widget = QtWidgets.QListWidget()
        BaseSettingsUI.__init__(self, settings, setting_name)

        # ----- Widgets -----

        self.add_btn = QtWidgets.QPushButton("+")
        self.add_btn.setFixedWidth(self.add_btn.sizeHint().height())
        self.sub_btn = QtWidgets.QPushButton("-")
        self.sub_btn.setFixedWidth(self.sub_btn.sizeHint().height())
        # TODO: add up/down arrows

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
        self.list_widget.itemChanged.connect(self.settingChanged.emit)

    def setValue(self, value):
        self.list_widget.clear()
        self.list_widget.addItems([str(x) for x in value])

    def onSettingChanged(self, value=None):
        # All items to text
        lst = list()
        for row in range(self.list_widget.count()):
            text = self.list_widget.item(row).text()
            lst.append(text)

        self._settings.set(self._setting_name, lst)

    def _on_add_btn_clicked(self):
        enter_item = EnterItemDialog()
        if enter_item.exec_():
            text = enter_item.line_edit.text()
            item = self.list_widget.addItem(text)
            self.settingChanged.emit(item)

    def _on_sub_btn_clicked(self):
        for item in self.list_widget.selectedItems():
            index = self.list_widget.indexFromItem(item)
            self.list_widget.takeItem(index.row())
        self.settingChanged.emit(None)


if __name__ == '__main__':
    from settings_manager import Settings

    s = Settings()
    s.add('list', ['A', 'B', 'D'])

    import sys
    app = QtWidgets.QApplication(sys.argv)

    widget = ListSetting(s, 'list')
    widget.show()

    app.exec_()
    print(s.as_dict())
    print(widget.settings.as_dict())

