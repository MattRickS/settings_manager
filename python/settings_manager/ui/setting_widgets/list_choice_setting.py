from PySide2 import QtCore, QtGui, QtWidgets
from settings_manager.ui.setting_widgets.base_settings_ui import BaseSettingsUI
from settings_manager.ui.checkable_combo_box import CheckableComboBox


class ListChoiceSetting(CheckableComboBox, BaseSettingsUI):
    def __init__(self, setting, parent=None):
        super(ListChoiceSetting, self).__init__(parent)
        BaseSettingsUI.__init__(self, setting)

        # Load choices
        choices = setting.property('choices')
        self.addItems(choices)
        for i in range(len(choices)):
            self.setItemChecked(i, False)

        # Set a useful default message
        minmax = setting.property('minmax')
        self.setDefaultText('Select {}-{} items...'.format(*minmax))

        self.itemStateChanged.connect(self.settingChanged.emit)

    def setValue(self, value):
        if not isinstance(value, list):
            value = [value]
        for row in range(self.model().rowCount()):
            self.setItemChecked(row, self.itemText(row) in value)

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

    def onSettingChanged(self, value):
        items = [i.data(QtCore.Qt.DisplayRole) for i in self.checkedItems()]
        self._setting.set(items)


if __name__ == '__main__':
    from settings_manager import Settings

    s = Settings()
    s.add('choice_list', ['mid'], data_type=list, choices=['xlo', 'lo', 'mid', 'hi', 'xhi'], minmax=(1, 5))

    import sys
    app = QtWidgets.QApplication(sys.argv)

    widget = ListChoiceSetting(s.setting('choice_list'))
    widget.show()

    app.exec_()
    print(s.as_dict(values_only=True))

