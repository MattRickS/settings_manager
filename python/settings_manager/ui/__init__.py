from .setting_widgets import *
from .viewer_widget import SettingsViewer


def get_default_widget(settings, key):
    """
    Returns the default widget for a Settings object.
    Default widgets are created from Qt.py

    :param      settings:   Settings object
    :param str  key:        Name of the setting to build a widget for
    :rtype: QtWidgets.QWidget
    """
    properties = settings.properties(key)
    data_type = properties["data_type"]
    if properties["choices"]:
        return ChoiceSetting(settings, key)
    elif data_type == str:
        return StringSetting(settings, key)
    elif data_type == int:
        return IntSetting(settings, key)
    elif data_type == float:
        return FloatSetting(settings, key)
    elif data_type == bool:
        return BoolSetting(settings, key)
    elif data_type == list:
        return ListSetting(settings, key)
    else:
        raise TypeError("Unsupported setting UI type: {}".format(data_type))
