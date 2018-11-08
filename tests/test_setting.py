import argparse

import pytest

from settings_manager import Setting
from settings_manager.exceptions import SettingsError


class TestProperties(object):
    @pytest.mark.parametrize('value, choices, invalid', (
        (1, [1, 2], [0, 3]),
        (1.0, [1.0, 2.0], [0.0, 3.0]),
        ('a', ['a', 'b'], ['c', 'd']),
    ))
    def test_choices(self, value, choices, invalid):
        s = Setting('key', value, choices=choices)
        for i in choices:
            s.set(i)
        for i in invalid:
            with pytest.raises(SettingsError):
                s.set(i)

    @pytest.mark.parametrize('default, alternate', (
        (1, 2),
        (1.0, 2.0),
        ('a', 'b'),
        (True, False),
        ([1, 2, 3], [4, 5, 6])
    ))
    def test_default(self, default, alternate):
        s = Setting('key', default)
        assert s.property('default') == default
        s.set(alternate)
        assert s.property('default') == default

    def test_hidden(self):
        assert Setting('key', 0).property('hidden') is False
        assert Setting('key', 0, hidden=True).property('hidden') is True

    def test_label(self):
        assert Setting('custom_key', 0).property('label') == 'custom key'
        assert Setting('key', 0, label='Label').property('label') == 'Label'

    @pytest.mark.parametrize('value, minmax, expected, valid, invalid', (
        (1, (1, 10), (1, 10), (1, 2, 3), (-1, 0, 11)),
        (1.0, (1.0, 10.0), (1.0, 10.0), (1.0, 2.0, 3.0), (-1.0, 0.0, 11.0)),
        (10, 10, (10, 10), (10, ), (9, 11)),
    ))
    def test_minmax(self, value, minmax, expected, valid, invalid):
        s = Setting('key', value, minmax=minmax)
        assert s.property('minmax') == expected
        for i in valid:
            s.set(i)
        for i in invalid:
            with pytest.raises(SettingsError):
                s.set(i)

    @pytest.mark.parametrize('value, choices, minmax', (
        (['a', 'b'], ['a', 'b', 'c'], (1, 3)),
        (['a'], ['a', 'b', 'c'], (1, 2)),
        ([], ['a', 'b', 'c'], (0, 2)),
    ))
    def test_multi_choice(self, value, choices, minmax):
        Setting('key', value, choices=choices, minmax=minmax)

    @pytest.mark.parametrize('value, choices, minmax', (
        (['a'], ['a', 'b', 'c'], (1, 5)),    # minmax range is greater than amount of choices
        (['a'], ['a', 'b', 'c'], (10, 20)),  # minmax range is greater than amount of choices
        (['a'], ['a', 'b', 'c'], (2, 3)),    # Default value does not meet min from minmax
    ))
    def test_multi_choice_invalid(self, value, choices, minmax):
        with pytest.raises(SettingsError):
            Setting('key', value, choices=choices, minmax=minmax)

    @pytest.mark.parametrize('value, properties, nullable', (
        (None, {'data_type': int}, True),
        (0, {}, False),
        (False, {}, False),
        (0, {'nullable': True}, True),
    ))
    def test_nullable(self, value, properties, nullable):
        assert Setting('key', value, **properties).property('nullable') is nullable

    def test_nullable_invalid(self):
        with pytest.raises(SettingsError):
            Setting('key', None)


def _get_single_arg_parser(name, value, **setting_kwargs):
    s = Setting(name, value, **setting_kwargs)
    flag, args = s.as_parser_args()
    parser = argparse.ArgumentParser()
    parser.add_argument(flag, **args)
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

        # Nullable const value
        parser = _get_single_arg_parser('key', value, nullable=True)
        parsed = parser.parse_args(['--key'])
        # For boolean actions, const is set to the value to store, eg
        # for value=False, we get action='store_true' which results in const=True
        value = not value if isinstance(value, bool) else None
        assert getattr(parsed, 'key') is value

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

    def test_as_parser_args__multi_choice(self):
        parser = _get_single_arg_parser('key', ['a', 'b'], choices=['a', 'b', 'c', 'd'], minmax=2)
        # Default value
        parsed = parser.parse_args([])
        assert getattr(parsed, 'key') == ['a', 'b']
        # Given value
        parsed = parser.parse_args('--key c d'.split())
        assert getattr(parsed, 'key') == ['c', 'd']

    @pytest.mark.parametrize('value, alt_value', (
            ('a', 'b'),
            (1, 2),
            (1.0, 2.0),
            (True, False),
            ([1, 2, 3], [4, 5, 6]),
    ))
    def test_get(self, value, alt_value):
        s = Setting('key', value)
        assert s.get() == value
        s.set(alt_value)
        assert s.get() == alt_value

    def test_has_property(self):
        s = Setting('key', 0, custom=1)
        assert s.has_property('custom') is True
        assert s.has_property('unknown') is False

    @pytest.mark.parametrize('value, alt_value, modified', (
            (1, 2, True),
            (1, 1, False),
            (1.0, 2.0, True),
            (1.0, 1.0, False),
            ('a', 'b', True),
            ('a', 'a', False),
    ))
    def test_is_modified(self, value, alt_value, modified):
        s = Setting('key', value)
        assert s.is_modified() is False
        s.set(alt_value)
        assert s.is_modified() is modified

    def test_name(self):
        assert Setting('key', 0).name == 'key'

    def test_property(self):
        s = Setting('key', 0, custom=1)
        assert s.property('choices') is None
        assert s.property('custom') == 1
        assert s.property('default') == 0

        with pytest.raises(KeyError):
            s.property('unknown')

    @pytest.mark.parametrize('value, alt_value', (
            ('a', 'b'),
            (1, 2),
            (1.0, 2.0),
            (True, False),
            ([1, 2, 3], [4, 5, 6]),
    ))
    def test_reset(self, value, alt_value):
        s = Setting('key', value)
        s.set(alt_value)
        assert s.get() == alt_value
        s.reset()
        assert s.get() == value


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
