from Qt import QtCore, QtGui, QtWidgets
import pytest

from settings_manager.setting import Setting
from settings_manager.settings_group import SettingsGroup
from settings_manager.ui.settings_viewer import SettingsViewer
from settings_manager.ui.setting_widgets import (StringSetting,
                                                 BoolSetting,
                                                 IntSetting,
                                                 FloatSetting,
                                                 ListSetting,
                                                 ListChoiceSetting,
                                                 ChoiceSetting,
                                                 get_default_setting_widget)


@pytest.fixture(scope='module')
def qapplication():
    return QtWidgets.QApplication([])


@pytest.mark.parametrize('klass, properties', (
    (StringSetting, {'default': 'abc'}),
    (StringSetting, {'default': 'abc', 'minmax': (1, 10)}),
    (IntSetting, {'default': 1}),
    (IntSetting, {'default': 1, 'minmax': (1, 10)}),
    (FloatSetting, {'default': 1.0}),
    (FloatSetting, {'default': 1.0, 'minmax': (1, 10)}),
    (BoolSetting, {'default': True}),
    (ListSetting, {'default': ['a']}),
    (ListSetting, {'default': ['a'], 'minmax': (1, 10)}),
    # Choices
    (ChoiceSetting, {'default': None, 'choices': ['a', 'b']}),
    (ChoiceSetting, {'default': 'a', 'choices': ['a', 'b']}),
    (ChoiceSetting, {'default': 0, 'choices': [0, 1]}),
    (ChoiceSetting, {'default': 0.0, 'choices': [0.0, 1.0]}),
    # ListChoiceSetting
    (ListChoiceSetting, {'default': [], 'choices': ['a', 'b']}),
    (ListChoiceSetting, {'default': [], 'choices': [0.0, 1.0]}),
    (ListChoiceSetting, {'default': [], 'choices': [0.0, 1.0], 'minmax': (0, 2)}),
    (ListChoiceSetting, {'default': None, 'choices': [0.0, 1.0], 'minmax': (0, 2)}),
))
def test_create_widget(qapplication, klass, properties):
    s = Setting('key', **properties)
    widget_class = get_default_setting_widget(s)
    assert widget_class == klass
    widget = klass(s)
    widget.show()


def test_settings_viewer(qapplication):
    s = SettingsGroup({
        'one': 'abc',
        'two': 1,
        'three': 1.0,
        'four': {
            'default': None,
            'data_type': str
        },
        'five': {
            'default': ['1'],
            'nullable': True
        },
    })
    widget = SettingsViewer(s)
    widget.show()
    widget.set_setting_none('four', False)
    widget.set_setting_none('five', True)
    widget.set_setting_hidden('one', True)
