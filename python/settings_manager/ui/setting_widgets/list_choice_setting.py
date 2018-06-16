from PySide2 import QtCore, QtGui, QtWidgets
from settings_manager.ui.setting_widgets.base_settings_ui import BaseSettingsUI
from settings_manager.ui.checkable_combo_box import CheckableComboBox


class ListChoiceSetting(CheckableComboBox, BaseSettingsUI):
    def __init__(self, setting, parent=None):
        super(ListChoiceSetting, self).__init__(parent)
        self.addItems(['a', 'b', 'c'])
        BaseSettingsUI.__init__(self, setting)

        self.itemStateChanged.connect(self.settingChanged.emit)

    def setValue(self, value):
        if not isinstance(value, list):
            value = [value]
        for row in range(self.model().rowCount()):
            self.setItemChecked(row, self.itemText(row) in value)

    def onSettingChanged(self, value):
        items = [i.data(QtCore.Qt.DisplayRole) for i in self.checkedItems()]
        self._setting.set(items)


if __name__ == '__main__':
    from settings_manager import Settings

    s = Settings()
    s.add('choice_list', ['a'])

    import sys
    app = QtWidgets.QApplication(sys.argv)

    widget = ListChoiceSetting(s.setting('choice_list'))
    widget.show()

    app.exec_()
    print(s.as_dict(values_only=True))

