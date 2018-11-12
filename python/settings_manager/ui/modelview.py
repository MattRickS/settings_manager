from PySide2 import QtCore, QtGui, QtWidgets

from settings_manager.exceptions import SettingsError
from settings_manager.setting import Setting
from settings_manager.ui.setting_widgets import create_setting_widget


class SettingNode(object):
    def __init__(self, name, value=None, parent=None):
        # type: (str, object, SettingNode) -> None
        self._name = name
        self._setting = None
        if value is not None:
            try:
                self._setting = Setting(name, value)
            except SettingsError:
                pass
        self.value = value
        self._parent = None     # type: SettingNode
        self._children = []

        if parent is not None:
            parent.add_child(self)

    def __repr__(self):
        return 'Node({!r}, {!r}, {!r})'.format(
            self._name, self._setting.get(), self._parent
        )

    def __str__(self):
        return self._name

    @property
    def children(self):
        # type: () -> list[SettingNode]
        return self._children[:]

    @property
    def name(self):
        # type: () -> str
        return self._name

    @property
    def parent(self):
        # type: () -> SettingNode
        return self._parent

    @property
    def setting(self):
        # type: () -> Setting
        return self._setting

    def add_child(self, node):
        # type: (SettingNode) -> None
        self._children.append(node)
        node._parent = self

    def child_by_index(self, index):
        # type: (int) -> SettingNode
        return self._children[index]

    def child_by_name(self, name):
        # type: (str) -> SettingNode
        for child in self._children:
            if child.name == name:
                return child

    def child_count(self):
        # type: () -> int
        return len(self._children)

    def clear(self):
        """ Removes all children """
        self._children = []

    def path(self, skip_root=False):
        # type: (bool) -> str
        curr = self
        ancestors = []
        while curr is not None:
            ancestors.append(curr.name)
            curr = curr.parent
        if skip_root:
            ancestors.pop(-1)
        return '.'.join(reversed(ancestors))

    def remove_child(self, node):
        # type: (SettingNode) -> None
        self._children.remove(node)
        node._parent = None

    def row(self):
        # type: () -> int
        return -1 if self._parent is None else self._parent._children.index(self)

    def to_string(self, level=0):
        # type: (int) -> str
        string = '. ' * level + self._name + '\n'
        for child in self._children:
            string += child.to_string(level + 1)
        return string


class SettingModel(QtCore.QAbstractItemModel):
    columns = ('key', 'value')

    def __init__(self, parent=None):
        # type: (QtWidgets.QWidget) -> None
        super(SettingModel, self).__init__(parent)
        self._root = SettingNode('root')

    @property
    def root(self):
        # type: () -> SettingNode
        return self._root

    def set_data(self, data):
        # type: (dict) -> None
        self.beginResetModel()
        self.rebuild_tree(data, self._root)
        self.endResetModel()

    def rebuild_tree(self, data, parent=None):
        # type: (dict, SettingNode) -> None
        for key, val in data.items():
            is_dict = isinstance(val, dict)
            node = SettingNode(str(key), None if is_dict else val, parent)
            if is_dict:
                self.rebuild_tree(val, node)

    # ======================================================================== #
    #                                SUBCLASSED                                #
    # ======================================================================== #

    def columnCount(self, parent=QtCore.QModelIndex()):
        # type: (QtCore.QModelIndex) -> int
        return len(self.columns)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        # type: (QtCore.QModelIndex, int) -> object
        if not index.isValid():
            return
        node = index.internalPointer()
        col = index.column()
        if role == QtCore.Qt.DisplayRole:
            if col == 0:
                return node.name
            elif col == 1:
                if isinstance(node.value, list):
                    return '\n'.join(map(str, node.value)) + '\n'
                return node.value

    def flags(self, index):
        # type: (QtCore.QModelIndex) -> QtCore.Qt.ItemFlags
        flags = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        if index.column() == 1:
            flags |= QtCore.Qt.ItemIsEditable
        return flags

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        # type: (int, QtCore.Qt.Orientation, int) -> str
        if role == QtCore.Qt.DisplayRole:
            if section < len(self.columns):
                return self.columns[section]

    def index(self, row, column, parent=QtCore.QModelIndex()):
        # type: (int, int, QtCore.QModelIndex) -> QtCore.QModelIndex
        parent_node = parent.internalPointer() if parent.isValid() else self._root
        child = parent_node.child_by_index(row)
        return self.createIndex(row, column, child)

    def parent(self, child):
        # type: (QtCore.QModelIndex) -> QtCore.QModelIndex
        node = child.internalPointer() if child.isValid() else self._root
        parent = node.parent
        if parent is not None and parent != self._root:
            return self.createIndex(parent.row(), 0, parent)
        return QtCore.QModelIndex()

    def rowCount(self, parent=QtCore.QModelIndex()):
        # type: (QtCore.QModelIndex) -> int
        node = parent.internalPointer() if parent.isValid() else self._root
        return node.child_count()

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        # type: (QtCore.QModelIndex, object, int) -> bool
        if not index.isValid():
            return False
        node = index.internalPointer()
        if node.setting is not None:
            try:
                node.setting.set(value)
            except SettingsError:
                return False
        if value != node.value:
            node.value = value
            self.dataChanged.emit(index, index)
        return True


class SettingDelegate(QtWidgets.QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        if index.isValid():
            node = index.internalPointer()
            if node.setting is not None:
                widget = create_setting_widget(node.setting, parent)
                widget.setAutoFillBackground(True)
                return widget
        return super(SettingDelegate, self).createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        if index.isValid():
            node = index.internalPointer()
            editor.setValue(node.value)
            return
        super(SettingDelegate, self).setEditorData(editor, index)


class SettingDictionaryView(QtWidgets.QTreeView):
    settingChanged = QtCore.Signal(str, object)  # setting_name, new_value

    def __init__(self, data=None, parent=None):
        # type: (dict, QtWidgets.QWidget) -> None
        super(SettingDictionaryView, self).__init__(parent)
        self.data = data

        self.setModel(SettingModel())
        self.setItemDelegate(SettingDelegate(self))

        self.model().dataChanged.connect(self._on_data_changed)

        if data is not None:
            self.set_data(data)

    def set_data(self, data):
        # type: (dict) -> None
        self.model().set_data(data)

    def _on_data_changed(self, from_index, to_index):
        # type: (QtCore.QModelIndex, QtCore.QModelIndex) -> None
        if not from_index.isValid():
            return
        node = from_index.internalPointer()
        path = node.path(skip_root=True)

        # Walk the path through the dictionary and set the final value
        parts = path.split('.')
        curr = self.data
        for part in parts[:-1]:
            curr = curr[part]
        curr[parts[-1]] = node.value

        self.settingChanged.emit(path, node.value)


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)

    data_dict = {
        'integer': 1,
        'string': 'some text',
        'float': 3.0,
        'list': ['a', 'b'],
        'bool': True,
        'dict': {
            'integer': 10,
            'string': 'more text',
            'subdict': {
                'bool': False
            }
        }
    }

    def print_changes(path, value):
        print(path, value)

    w = SettingDictionaryView(data_dict)
    w.settingChanged.connect(print_changes)
    w.show()

    app.exec_()
    print(w.data)
    sys.exit()
