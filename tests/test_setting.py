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

    @pytest.mark.parametrize('value, minmax, valid, invalid', (
        (1, (-10, 10), (-5, 2, 10), (-11, 11)),
        (1.0, (1, 10), (1.0, 2.0, 3.0), (-1.0, 0.0, 11.0)),
        (10, 10, (10, ), (9, 11)),
        ('abc', (2, 4), ('ab', 'abcd'), ('a', 'abcde')),
    ))
    def test_minmax(self, value, minmax, valid, invalid):
        s = Setting('key', value, minmax=minmax)
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


class TestSetting(object):
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

    def test_equals(self):
        assert Setting('key', 1) == 'key'

    def test_hash(self):
        assert hash(Setting('key', 1)) == hash('key')


@pytest.mark.parametrize('properties', (
    # Standard dict (truthy)
    ({'default': 'string'}),
    ({'default': 1}),
    ({'default': 1.0}),
    ({'default': True}),
    ({'default': ['a']}),
    # Standard dict (non-truthy)
    ({'default': ''}),
    ({'default': 0}),
    ({'default': 0.0}),
    ({'default': False}),
    ({'default': [], 'subtype': int}),
    # Null values with a type
    ({'default': None, 'data_type': str}),
    ({'default': None, 'data_type': int}),
    ({'default': None, 'data_type': float}),
    ({'default': None, 'data_type': bool}),
    ({'default': None, 'data_type': list, 'subtype': str}),
    # Choices
    ({'default': None, 'choices': ['a', 'b', 'c']}),
    ({'default': ['a'], 'choices': ['a', 'b', 'c']}),
    ({'default': [1], 'choices': [0, 1, 2]}),
    ({'default': [1.0], 'choices': [0.0, 1.0, 2.0]}),
    ({'default': [True], 'choices': [True, False]}),  # Note, terrible idea
    # Minmax
    ({'default': 'abc', 'minmax': (0, 3)}),
    ({'default': 1, 'minmax': (0, 3)}),
    ({'default': 1.0, 'minmax': (0, 3)}),
    ({'default': ['a'], 'minmax': (0, 3)}),
    # MultiChoice
    ({'default': 'abc', 'minmax': (1, 3)}),
    ({'default': 1, 'minmax': (1, 3)}),
    ({'default': 1.0, 'minmax': (1, 3)}),
    ({'default': ['a'], 'minmax': (1, 3)}),
))
def test_create_setting(properties):
    Setting('key', **properties)


@pytest.mark.parametrize('properties', (
    ({'default': 11, 'minmax': (5, 10)}),     # Value greater than maximum
    ({'default': 4, 'minmax': (5, 10)}),      # Value lower than minimum
    ({'default': 4, 'data_type': str}),       # Invalid datatype
    ({'default': ['a'], 'choices': [0, 1]}),  # Invalid datatype
    ({'default': None, 'data_type': dict}),   # Invalid datatype
    ({'default': None}),                      # No data type
    ({'default': 2, 'choices': [0, 1]}),      # Default not in choices
    ({'default': 2, 'minmax': (0.0, 5.0)}),   # minmax must be int
))
def test_create_setting_error(properties):
    with pytest.raises(SettingsError):
        Setting('key', **properties)


@pytest.mark.parametrize('name, properties, input_string, parsed', (
    # Standard data types (provided)
    ('key', {'default': 'a'}, '--key b', 'b'),
    ('key', {'default': True}, '--no-key', False),
    ('key', {'default': 1}, '--key 2', 2),
    ('key', {'default': 1.0}, '--key 2', 2.0),
    ('key', {'default': [], 'subtype': str}, '--key a b', ['a', 'b']),
    # Standard data types (default)
    ('key', {'default': 'a'}, '', 'a'),
    ('key', {'default': True}, '', True),
    ('key', {'default': 1}, '', 1),
    ('key', {'default': 1.0}, '', 1.0),
    ('key', {'default': [], 'subtype': str}, '', []),
    # Nullable settings
    ('key', {'default': None, 'data_type': str}, '', None),
    ('key', {'default': None, 'data_type': str}, '--key', None),
    ('key', {'default': 'a', 'nullable': True}, '', 'a'),
    ('key', {'default': 'a', 'nullable': True}, '--key', None),
    # Choices
    ('key', {'default': 'a', 'choices': 'a b c'.split()}, '', 'a'),
    ('key', {'default': 'a', 'choices': 'a b c'.split()}, '--key b', 'b'),
    ('key', {'default': [], 'choices': 'a b c'.split()}, '--key b', ['b']),
    ('key', {'default': [], 'choices': 'a b c'.split()}, '', []),
    # Choices and minmax
    ('key', {'default': ['a'], 'choices': 'a b c'.split(), 'minmax': (1, 3)}, '', ['a']),
    ('key', {'default': [1], 'choices': [0, 1, 2], 'minmax': (1, 3)}, '--key 1 2', [1, 2]),
    # Choices and nullable
    ('key', {'default': None, 'choices': 'a b c'.split()}, '--key', None),
    ('key', {'default': None, 'choices': 'a b c'.split()}, '--key b', 'b'),
))
def test_argparse(name, properties, input_string, parsed):
    s = Setting(name, **properties)
    flag, args = s.as_parser_args()
    parser = argparse.ArgumentParser()
    parser.add_argument(flag, **args)
    p_args = parser.parse_args(input_string.split())
    assert getattr(p_args, name) == parsed
