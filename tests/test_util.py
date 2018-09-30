import pytest

from settings_manager import util
from settings_manager.setting import Setting


@pytest.mark.parametrize('string, expected', (
    ('str', str),
    ('int', int),
    ('float', float),
    ('bool', bool),
    ('list', list),
    ('settings_manager.setting.Setting', Setting),
))
def test_class_from_string(string, expected):
    assert util.class_from_string(string) == expected
