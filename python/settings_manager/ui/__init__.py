from .setting_widgets import *
from .viewer_widget import SettingsViewer


def get_default_widget(setting, *args, **kwargs):
    """
    Returns the default widget for a Settings object.
    Default widgets are created from Qt.py

    :param      setting:   Setting object
    :rtype: QtWidgets.QWidget
    """
    data_type = setting.type
    choices = setting.property('choices')
    minmax = setting.property('minmax')
    if choices and minmax:
        return ListChoiceSetting(setting, *args, **kwargs)
    elif choices:
        return ChoiceSetting(setting, *args, **kwargs)
    elif data_type == str:
        return StringSetting(setting, *args, **kwargs)
    elif data_type == int:
        return IntSetting(setting, *args, **kwargs)
    elif data_type == float:
        return FloatSetting(setting, *args, **kwargs)
    elif data_type == bool:
        return BoolSetting(setting, *args, **kwargs)
    elif data_type == list:
        return ListSetting(setting, *args, **kwargs)
    else:
        raise TypeError('Unsupported setting UI type: {}'.format(data_type))


def show_settings(settings, *args, **kwargs):
    """
    Displays the settings UI. If no QApplication instance is available, one is
    initialised.
    Additional arguments are passed directly to the Settings.widget() method.

    :param Settings settings:
    :rtype: QWidget
    """
    from Qt.QtWidgets import QApplication

    app = None if QApplication.instance() else QApplication([])

    widget = settings.widget(*args, **kwargs)

    if app:
        widget.show()
        app.exec_()
        return widget
    else:
        widget.exec_()
        return widget
