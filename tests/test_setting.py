import argparse

import pytest

from settings_manager import Setting
from settings_manager.exceptions import SettingsError


class TestProperties(object):
    def test_choices(self):
        s = Setting('key', 'value', choices=['value', 'other'])
        assert s.property('choices') == ['value', 'other']

        Setting('key', 1, choices=[1, 2])
        Setting('key', 5.0, choices=[5.0, 10.0])
        # Technically valid but useless
        Setting('key', True, choices=[True, False])
        # Nested lists (unusual - default UI will cast each item to string)
        Setting('key', ['a', 'b'], choices=[['a', 'b'], ['c', 'd']])
        # Not in choices
        with pytest.raises(SettingsError):
            Setting('key', 0, choices=['a', 'b'])
        # Mismatched type
        with pytest.raises(SettingsError):
            Setting('key', '0', choices=[0, 1])
        # Subset requires minmax
        with pytest.raises(SettingsError):
            Setting('key', ['a', 'b'], choices=['a', 'b', 'c'])

    def test_default(self):
        s = Setting('key', 0)
        assert s.property('default') == 0
        s.set(5)
        assert s.property('default') == 0

    def test_hidden(self):
        assert Setting('key', 0).property('hidden') is False
        assert Setting('key', 0, hidden=True).property('hidden') is True

    def test_label(self):
        assert Setting('custom_key', 0).property('label') == 'custom key'
        assert Setting('key', 0, label='Label').property('label') == 'Label'

    def test_minmax(self):
        s = Setting('key', 'value', minmax=5)
        assert s.property('minmax') == (5, 5)
        assert Setting('key', 'value', minmax=(1, 10))
        assert Setting('key', 3, minmax=(1, 10))

        # Out of range
        with pytest.raises(SettingsError):
            Setting('key', 0, minmax=(1, 5))
        # No negative range
        with pytest.raises(SettingsError):
            Setting('key', 0, minmax=(-1, 5))
        # Min must be lower than Max
        with pytest.raises(SettingsError):
            Setting('key', 2, minmax=(3, 1))

    def test_multi_choice(self):
        Setting('key', ['a', 'b'], choices=['a', 'b', 'c'], minmax=(1, 3))
        Setting('key', ['a'], choices=['a', 'b', 'c'], minmax=(1, 2))
        Setting('key', [], choices=['a', 'b', 'c'], minmax=(0, 2))
        # minmax range is greater than amount of choices
        with pytest.raises(SettingsError):
            Setting('key', ['a'], choices=['a', 'b', 'c'], minmax=(1, 5))
        # minmax range is greater than amount of choices
        with pytest.raises(SettingsError):
            Setting('key', ['a'], choices=['a', 'b', 'c'], minmax=(10, 20))
        # Default value does not meet min from minmax
        with pytest.raises(SettingsError):
            Setting('key', ['a'], choices=['a', 'b', 'c'], minmax=(2, 3))

    def test_nullable(self):
        assert Setting('key', None, data_type=int).property('nullable') is True
        assert Setting('key', 0).property('nullable') is False
        assert Setting('key', False).property('nullable') is False
        assert Setting('key', 0, nullable=True).property('nullable') is True
        # Unknown data type
        with pytest.raises(SettingsError):
            Setting('key', None)


def _get_single_arg_parser(name, value, **setting_kwargs):
    s = Setting(name, value, **setting_kwargs)
    args = s.as_parser_args()
    parser = argparse.ArgumentParser()
    parser.add_argument(args.pop('flag'), **args)
    return parser


class TestSetting(object):
    @pytest.mark.parametrize('value, alt_string, alt_result', (
        ('value', 'other', 'other'),
        (1, '3', 3),
        (3.0, '5.0', 5.0),
        (['a', 'b'], 'c d', ['c', 'd']),
        ([1, 2], '3 4', [3, 4]),
        (False, '', True),  # See test_as_parser_args__bool for inverse
    ))
    def test_as_parser_args__basic(self, value, alt_string, alt_result):
        parser = _get_single_arg_parser('key', value)
        # Default value
        parsed = parser.parse_args([])
        assert getattr(parsed, 'key') == value
        # Given value
        parsed = parser.parse_args(('--key ' + alt_string).split())
        assert getattr(parsed, 'key') == alt_result

        # Const value
        parser = _get_single_arg_parser('key', value, nullable=True)
        parsed = parser.parse_args(['--key'])
        # For boolean actions, const is set to the value to store, eg
        # for value=False, we get action='store_true' which results in const=True
        value = not value if isinstance(value, bool) else value
        assert getattr(parsed, 'key') == value

    def test_as_parser_args__bool(self):
        # Because the action becomes 'store_false', we modify the flag name
        # to prepend '--no-', requiring separate testing from parametrize
        parser = _get_single_arg_parser('key', True)
        # Default value
        parsed = parser.parse_args([])
        assert getattr(parsed, 'key') is True
        # Given value
        parsed = parser.parse_args(['--no-key'])
        assert getattr(parsed, 'key') is False

    def test_get(self):
        s = Setting('key', 0)
        assert s.get() == 0

    def test_has_property(self):
        s = Setting('key', 0, custom=1)
        assert s.has_property('custom') is True
        assert s.has_property('unknown') is False

    def test_name(self):
        assert Setting('key', 0).name == 'key'

    def test_property(self):
        s = Setting('key', 0, custom=1)
        assert s.property('choices') is None
        assert s.property('custom') == 1
        assert s.property('default') == 0

        with pytest.raises(KeyError):
            s.property('unknown')

    def test_reset(self):
        s = Setting('key', 1)
        s.set(5)
        assert s.get() == 5
        s.reset()
        assert s.get() == 1


def test_string_setting():
    s = Setting('key', 'value')
    assert s.get() == 'value'
    assert s.type == str
    # Invalid type
    with pytest.raises(SettingsError):
        assert Setting('key', 'value', data_type=int)

    # Property combinations
    assert Setting('key', 'value', minmax=5)
    assert Setting('key', 'value', choices=['value'])
    assert Setting('key', 'value', choices=['value', 'other'])
    # Length of default is wrong
    with pytest.raises(SettingsError):
        Setting('key', 'value', minmax=3)


def test_int_setting():
    s = Setting('key', 1)
    assert s.get() == 1
    assert s.type == int
    assert Setting('key', 1, minmax=(0, 5))
    # Out of range
    with pytest.raises(SettingsError):
        Setting('key', 8, minmax=(0, 5))


def test_float_setting():
    s = Setting('key', 1.0)
    assert s.get() == 1.0
    assert s.type == float
    assert Setting('key', 1.0, minmax=(0, 5))
    # Out of range
    with pytest.raises(SettingsError):
        Setting('key', 8.0, minmax=(0, 5))


def test_bool_setting():
    s = Setting('key', True)
    assert s.get() is True
    assert s.type == bool


def test_list_setting():
    s = Setting('key', ['a', 'b', 'c'])
    assert s.get() == ['a', 'b', 'c']
    assert s.type == list
