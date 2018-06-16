from PySide2 import QtCore, QtGui, QtWidgets
from settings_manager.ui.setting_widgets.base_settings_ui import BaseSettingsUI

"""
WIP

Make the display show the names of selected items (elided).

Example:
  [item 1, item 2, ite...]
    [x] item 1
    [x] item 2
    [x] item 3
    [ ] item 4
    [ ] item 5
"""


class CheckableComboBox(QtWidgets.QComboBox):
    def __init__(self, parent=None):
        super(CheckableComboBox, self).__init__(parent)
        self.view().pressed.connect(self.handleItemPressed)
        self._changed = False

    def checkedItems(self):
        for row in range(self.model().rowCount()):
            item = self.model().item(row, self.modelColumn())
            if item.checkState() == QtCore.Qt.Checked:
                yield item

    def handleItemPressed(self, index):
        item = self.model().itemFromIndex(index)
        state = QtCore.Qt.Unchecked if item.checkState() == QtCore.Qt.Checked else QtCore.Qt.Checked
        item.setCheckState(state)
        self._changed = True

    def hidePopup(self):
        if not self._changed:
            super(CheckableComboBox, self).hidePopup()
        self._changed = False

    def itemChecked(self, index):
        item = self.model().item(index, self.modelColumn())
        return item.checkState() == QtCore.Qt.Checked

    def setItemChecked(self, index, checked=True):
        item = self.model().item(index, self.modelColumn())
        state = QtCore.Qt.Checked if checked else QtCore.Qt.Unchecked
        item.setCheckState(state)


class Window(QtWidgets.QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.combo = CheckableComboBox(self)
        print(self.combo.model())
        for index in range(6):
            self.combo.addItem('Item %d' % index)
            self.combo.setItemChecked(index, False)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.combo)


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)

    widget = Window()
    widget.show()

    app.exec_()

    for item in widget.combo.checkedItems():
        print(item.data(QtCore.Qt.DisplayRole))

    sys.exit()
