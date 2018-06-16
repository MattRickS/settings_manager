from PySide2 import QtCore, QtGui, QtWidgets


class CheckableComboBox(QtWidgets.QComboBox):
    itemStateChanged = QtCore.Signal(QtGui.QStandardItem)

    def __init__(self, parent=None):
        super(CheckableComboBox, self).__init__(parent)
        self.view().pressed.connect(self.onItemPressed)
        self._changed = False
        self._default_string = 'Select Items...'
        self._selected_string = self._default_string

    def checkedItems(self):
        for row in range(self.model().rowCount()):
            item = self.model().item(row, self.modelColumn())
            if item.checkState() == QtCore.Qt.Checked:
                yield item

    def hidePopup(self):
        if not self._changed:
            super(CheckableComboBox, self).hidePopup()
        self._changed = False

    def itemChecked(self, index):
        item = self.model().item(index, self.modelColumn())
        return item.checkState() == QtCore.Qt.Checked

    def paintEvent(self, event):
        painter = QtWidgets.QStylePainter(self)
        painter.setPen(self.palette().color(QtGui.QPalette.Text))
        opt = QtWidgets.QStyleOptionComboBox()
        self.initStyleOption(opt)
        opt.currentText = self._selected_string
        painter.drawComplexControl(QtWidgets.QStyle.CC_ComboBox, opt)
        painter.drawControl(QtWidgets.QStyle.CE_ComboBoxLabel, opt)

    def setDefaultText(self, text):
        self._default_string = text
        self._set_selection_string()

    def setItemChecked(self, index, checked=True):
        item = self.model().item(index, self.modelColumn())
        state = QtCore.Qt.Checked if checked else QtCore.Qt.Unchecked
        item.setCheckState(state)

    def _set_selection_string(self):
        selected = [i.data(QtCore.Qt.DisplayRole) for i in self.checkedItems()]
        self._selected_string = ', '.join(selected) if selected else self._default_string

    # ======================================================================== #
    #                               CONNECTIONS                                #
    # ======================================================================== #

    def onItemPressed(self, index):
        item = self.model().itemFromIndex(index)
        state = QtCore.Qt.Unchecked if item.checkState() == QtCore.Qt.Checked else QtCore.Qt.Checked
        item.setCheckState(state)
        self.itemStateChanged.emit(item)
        self._changed = True
        self._set_selection_string()


if __name__ == '__main__':
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

    import sys

    app = QtWidgets.QApplication(sys.argv)

    widget = Window()
    widget.show()

    app.exec_()

    for item in widget.combo.checkedItems():
        print(item.data(QtCore.Qt.DisplayRole))

    sys.exit()
