import pytest

from settings_manager.exceptions import SettingsError
from settings_manager.settings_group import SettingsGroup
from settings_manager.setting import Setting


@pytest.fixture(scope='module')
def mock_settings_config_list():
    return [
        {
            'one': 'value'
        },
        {
            'two': {
                'default': 2,
                'label': 'Two'
            }
        },
        {
            'three': {
                'default': ['a'],
                'choices': ['a', 'b', 'c'],
                'minmax': (1, 2)
            }
        }
    ]


@pytest.fixture(scope='module')
def mock_settings_config_dict():
    return {
        'one': 'value',
        'two': {
            'default': 2,
            'label': 'Two'
        },
        'three': {
            'default': ['a'],
            'choices': ['a', 'b', 'c'],
            'minmax': (1, 2)
        },
    }


@pytest.fixture(scope='module')
def mock_settings_config_flat_dict():
    return {
        'one': 'value',
        'two': 2,
        'three': False,
    }


class TestSettingsGroup(object):
    @pytest.mark.parametrize('name, default, properties', (
        ('key', 1, {}),
        ('key', 'value', {'choices': ['value', 'other']}),
    ))
    def test_add(self, name, default, properties):
        # Compare setting added via Settings object to direct instantiation
        s1 = SettingsGroup().add_setting(name, default, **properties)
        s2 = Setting(name, default, **properties)
        assert s1 == s2

    def test_add__unique_names(self):
        s = SettingsGroup()
        s.add_setting('key', 1)
        with pytest.raises(SettingsError):
            s.add_setting('key', 2)

    def test_add_batch_settings(self, mock_settings_config_list, mock_settings_config_dict):
        s = SettingsGroup()
        s.add_batch_settings(mock_settings_config_list)
        # Ensure ordered
        keys = list(s)
        for idx, i in enumerate(mock_settings_config_list):
            name, _ = i.copy().popitem()
            assert keys[idx].name == name

        # New object to avoid duplicates
        s = SettingsGroup()
        s.add_batch_settings(mock_settings_config_dict)

    def test_get(self, mock_settings_config_flat_dict):
        s = SettingsGroup(mock_settings_config_flat_dict)
        for key, val in mock_settings_config_flat_dict.items():
            assert s.get(key) == val

    def test_len(self):
        s = SettingsGroup()
        s.add_setting('one', 1)
        s.add_setting('two', 2)
        assert len(s) == 2

    def test_iter(self, mock_settings_config_list):
        s = SettingsGroup(mock_settings_config_list)
        for idx, i in enumerate(s):
            name, _ = mock_settings_config_list[idx].popitem()
            assert i.name == name
