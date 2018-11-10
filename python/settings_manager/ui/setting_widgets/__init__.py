from PySide2 import QtCore, QtGui, QtWidgets

from settings_manager.setting import Setting
from settings_manager.ui.setting_widgets.setting_ui import SettingUI
from settings_manager.ui.setting_widgets.bool_setting import BoolSetting
from settings_manager.ui.setting_widgets.choice_setting import ChoiceSetting
from settings_manager.ui.setting_widgets.float_setting import FloatSetting
from settings_manager.ui.setting_widgets.int_setting import IntSetting
from settings_manager.ui.setting_widgets.list_setting import ListSetting
from settings_manager.ui.setting_widgets.list_choice_setting import ListChoiceSetting
from settings_manager.ui.setting_widgets.string_setting import StringSetting


def create_setting_widget(setting, parent=None):
    # type: (Setting, QtWidgets.QWidget) -> SettingUI|QtWidgets.QWidget
    """ Initialises the setting widget or a default widget """
    cls = setting.property('widget') or get_default_setting_widget(setting)
    if cls is None:
        raise ValueError('No widget defined for setting: {}'.format(setting))
    return cls(setting, parent=parent)


def get_default_setting_widget(setting):
    """
    Returns the default widget for a Settings object.
    Default widgets are created using Qt.py

    :param Setting              setting:
    :rtype: type[QtWidgets.QWidget]
    """
    data_type = setting.type
    choices = setting.property('choices')
    minmax = setting.property('minmax')
    if choices and minmax:
        return ListChoiceSetting
    elif choices:
        return ChoiceSetting
    elif data_type == str:
        return StringSetting
    elif data_type == int:
        return IntSetting
    elif data_type == float:
        return FloatSetting
    elif data_type == bool:
        return BoolSetting
    elif data_type == list:
        return ListSetting
