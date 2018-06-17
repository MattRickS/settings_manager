from PySide2 import QtCore, QtGui, QtWidgets
from settings_manager.ui.setting_widgets.setting_ui import SettingUI
from settings_manager.ui.checkable_combo_box import CheckableComboBox


class ListChoiceSetting(CheckableComboBox, SettingUI):
    def __init__(self, setting, parent=None):
        super(ListChoiceSetting, self).__init__(parent)
        SettingUI.__init__(self, setting)

        # Load choices
        choices = setting.property('choices')
        self.addItems(choices)
        for i in range(len(choices)):
            self.setItemChecked(i, False)

        # Set a useful default message
        minmax = setting.property('minmax')
        self.setDefaultText('Select {}-{} items...'.format(*minmax))

        self.itemStateChanged.connect(self.onValueChanged)

    def setValue(self, value):
        if not isinstance(value, list):
            value = [value]
        for row in range(self.model().rowCount()):
            self.setItemChecked(row, self.itemText(row) in value)
        self.itemStateChanged.emit(None)
        # self.onValueChanged(value)

    def value(self):
        return [i.data(QtCore.Qt.DisplayRole) for i in self.checkedItems()]

    def onItemPressed(self, index):
        num_selected = len(list(self.checkedItems()))
        num_selected += -1 if self.itemChecked(index.row()) else 1
        lo, hi = self._setting.property('minmax')
        if lo <= num_selected <= hi:
            super(ListChoiceSetting, self).onItemPressed(index)
        else:
            # Flash red...?
            pass
        self._changed = True

    def onValueChanged(self, value):
        items = [i.data(QtCore.Qt.DisplayRole) for i in self.checkedItems()]
        super(ListChoiceSetting, self).onValueChanged(items)
