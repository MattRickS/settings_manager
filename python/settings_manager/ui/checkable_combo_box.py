from Qt import QtCore, QtGui, QtWidgets


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
        # type: (int) -> bool
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
        # type: (str) -> None
        self._default_string = text
        self._set_selection_string()

    def setItemChecked(self, index, checked=True):
        # type: (int, bool) -> None
        item = self.model().item(index, self.modelColumn())
        state = QtCore.Qt.Checked if checked else QtCore.Qt.Unchecked
        item.setCheckState(state)
        self.itemStateChanged.emit(item)
        self._set_selection_string()

    def _set_selection_string(self):
        selected = [i.data(QtCore.Qt.DisplayRole) for i in self.checkedItems()]
        if selected:
            self._selected_string = '({}) {}'.format(
                len(selected), ', '.join(selected))
        else:
            self._selected_string = self._default_string

    # ======================================================================== #
    #                               CONNECTIONS                                #
    # ======================================================================== #

    def onItemPressed(self, index):
        # type: (QtCore.Qt.QModelIndex) -> None
        item = self.model().itemFromIndex(index)
        checked = item.checkState() == QtCore.Qt.Unchecked
        self.setItemChecked(index.row(), checked=checked)
        self._changed = True
