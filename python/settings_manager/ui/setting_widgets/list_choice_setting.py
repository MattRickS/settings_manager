from PySide2 import QtCore, QtGui, QtWidgets

from settings_manager.setting import Setting
from settings_manager.ui.setting_widgets.setting_ui import SettingUI
from settings_manager.ui.checkable_combo_box import CheckableComboBox


class ListChoiceSetting(CheckableComboBox, SettingUI):
    def __init__(self, setting=None, parent=None):
        # type: (Setting, QtWidgets.QWidget) -> None
        super(ListChoiceSetting, self).__init__(parent)
        SettingUI.__init__(self, setting)
        self.itemStateChanged.connect(self.onValueChanged)

    def setSetting(self, setting):
        # type: (Setting) -> None
        super(ListChoiceSetting, self).setSetting(setting)
        # Load choices
        choices = setting.property('choices')
        current_values = setting.get()
        self.addItems(list(map(str, choices)))
        for idx, value in enumerate(choices):
            self.setItemChecked(idx, value in current_values)

        # Set a useful default message
        minmax = setting.property('minmax')
        self.setDefaultText('Select {}-{} items...'.format(*minmax))

    def setValue(self, value):
        # type: (str|list[str]) -> None
        if not isinstance(value, list):
            value = [value]
        value = list(map(str, value))
        for row in range(self.model().rowCount()):
            self.setItemChecked(row, self.itemText(row) in value)
        self.itemStateChanged.emit(None)

    def value(self):
        # type: () -> list[str]
        return [self._setting.subtype(i.data(QtCore.Qt.DisplayRole))
                for i in self.checkedItems()]

    def onItemPressed(self, index):
        # type: (QtCore.QModelIndex) -> None
        # Checked items are not updated yet, so get the current number of
        # checked items and check whether checking the item enables or disables
        # it, modifying the number accordingly and only allowing it if the new
        # value is within the given range
        num_selected = len(list(self.checkedItems()))
        num_selected += -1 if self.itemChecked(index.row()) else 1
        lo, hi = self._setting.property('minmax')
        if lo <= num_selected <= hi:
            super(ListChoiceSetting, self).onItemPressed(index)

    def onValueChanged(self, value):
        # type: (QtGui.QStandardItem) -> None
        # Use the value which preserves the choice's type
        super(ListChoiceSetting, self).onValueChanged(self.value())
