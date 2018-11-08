from collections import OrderedDict
import argparse
import json
import sys

from settings_manager.exceptions import SettingsError
from settings_manager.setting import Setting
from settings_manager import util


class SubSettings(object):
    """
    Container for nested Settings objects.
    """
    def __init__(self, name, settings, enabled=True, nullable=False, widget=None):
        # type: (str, SettingsGroup, bool) -> None
        self._name = name
        self._settings = settings
        self._nullable = nullable
        self._enabled = enabled
        self._widget = widget

    @property
    def name(self):
        # type: () -> str
        return self._name

    @property
    def settings(self):
        # type: () -> SettingsGroup
        return self._settings

    def is_enabled(self):
        # type: () -> bool
        return self._enabled

    def is_nullable(self):
        # type: () -> bool
        return self._nullable

    def set_enabled(self, enabled):
        # type: (bool) -> None
        if not self.is_nullable() and not enabled:
            raise SettingsError('Group {!r} is not nullable'.format(self._name))
        self._enabled = enabled

    def widget(self, *args, **kwargs):
        if self._widget is not None:
            return self._widget(*args, **kwargs)

        return self._settings.widget(*args, **kwargs)


class SettingsGroup(object):
    """
    Convenience class for storing settings with explicit data types.
    Settings are added via Settings.add() and can be get / set as properties, or as keys.

    Settings objects can be nested to provide grouping

    Iteration over a Settings object will yield the Setting objects.

    eg,

    >>> settings = SettingsGroup()
    >>> settings.add_setting('some_value', 3, label='Some Value')
    >>> settings.add_setting('options', 'None', choices=['None', 'yes', 'no', 'maybe'])
    >>> settings.get('options')
    'None'
    >>> settings['some_value']
    3
    """

    @classmethod
    def from_json(cls, path):
        """
        Reads the settings from a json file, preserving the settings order.

        :param str  path:
        :rtype: SettingsGroup
        """
        with open(path, 'r') as f:
            data = json.load(f, object_pairs_hook=OrderedDict)

        # Convert data from unicode to string (python 2 only)
        if sys.version_info[0] < 3:
            data = util.byteify(data)

        def cast_from_string(data, key):
            item = data.get(key)
            if item is not None and isinstance(item, str):
                data[key] = util.class_from_string(item)

        # Types are converted to strings in json, evaluate them back to types
        for setting_data in data.values():
            if isinstance(setting_data, dict):
                cast_from_string(setting_data, 'data_type')
                cast_from_string(setting_data, 'widget')

        return cls(data)

    def __init__(self, settings=None, widget=None):
        """
        :param list|dict    settings:
            Settings can be accepted in multiple forms to allow for ordering:
                * Dictionary of properties; {setting_name: {properties}}
                * Dictionary with single value; {setting_name: value}
                * List of single dicts; {setting_name: {properties}}
                * List of single dicts; {setting_name: value}
                * List of tuples; (setting_name, value)
        :param type         widget:
        """
        self._contents = OrderedDict()
        self._widget_cls = widget

        if settings is not None:
            self.add_batch_settings(settings)

    def __eq__(self, other):
        if isinstance(other, SubSettings):
            other = other.settings
        if not isinstance(other, SettingsGroup):
            return False
        return self.as_dict(ordered=True) == other.as_dict(ordered=True)

    def __getitem__(self, item):
        return self.get(item)

    def __iter__(self):
        return iter(self._contents.values())

    def __len__(self):
        return len(self._contents)

    # Python 2.x
    def __nonzero__(self):
        return len(self) > 0

    # Python 3.x
    def __bool__(self):
        return len(self) > 0

    def add_setting(self, name, default, choices=None, data_type=None,
                    hidden=False, label=None, minmax=None, nullable=False,
                    tooltip='', widget=None, **kwargs):
        """
        :param str          name:       Name of the setting.
        :param object       default:    Value. If None, data_type is required.
                            
        :param list         choices:    List of fixed values for the setting.
        :param              data_type:  Type of the value. Inferred from default 
                                        if not given.
        :param bool         hidden:     Whether or not the setting should be 
                                        visible in UI / argparser.
        :param str          label:      UI setting. Display name for the setting 
                                        (defaults to name).
        :param tuple|int    minmax:     Tuple of minimum and maximum values for 
                                        floats and ints. If provided with
                                        choices, the setting becomes a list 
                                        type, and minmax defines the number of 
                                        choices that can be selected.
        :param bool         nullable:   Whether or not None is a valid value.
        :param bool         tooltip:    Description message for widget tooltip 
                                        and parser help
        :param              widget:     UI setting. Callable object that returns 
                                        a UI widget to use for this setting. If 
                                        None, a default UI will be generated.
        :rtype: Setting
        """
        if name in self._contents:
            raise SettingsError('Setting already exists: {!r}'.format(name))
        setting = Setting(name, default, choices=choices, data_type=data_type,
                          hidden=hidden, label=label, minmax=minmax,
                          nullable=nullable, tooltip=tooltip,
                          widget=widget, **kwargs)
        self._contents[name] = setting
        return setting

    def add_batch_settings(self, settings):
        """
        :param list|dict    settings:
            Settings can be accepted in multiple forms to allow for ordering:
                * Dictionary of properties; {setting_name: {properties}}
                * Dictionary with single value; {setting_name: value}
                * List of single dicts; {setting_name: {properties}}
                * List of single dicts; {setting_name: value}
                * List of tuples; (setting_name, value)
        """
        # Recursive
        if isinstance(settings, dict):
            for setting, data in settings.items():
                # Dictionary of properties {setting_name: {...}}
                if isinstance(data, dict):
                    self.add_setting(setting, **data)
                # Dictionary with single value {setting_name: value}
                else:
                    self.add_setting(setting, data)
        elif isinstance(settings, list):
            for item in settings:
                # List of single dicts, likely from a configuration {setting_name: {...}}
                if isinstance(item, dict):
                    for setting, data in item.items():
                        # List of dicts {setting_name: {properties}}
                        if isinstance(data, dict):
                            self.add_setting(setting, **data)
                        # List of dicts {setting_name: value}
                        else:
                            self.add_setting(setting, data)
                # List of tuples, (setting_name, value)
                else:
                    setting, value = item
                    self.add_setting(setting, value)

    def as_argparser(self, keys=None, hidden=False):
        """
        Create an ArgumentParser for the current settings.

        :param list[str]    keys:   Restricts args to keys if given.
        :param bool         hidden: If true, includes hidden keys
        :return:
        """
        parser = argparse.ArgumentParser()

        for setting in self._contents.values():
            if keys:
                if setting.name not in keys:
                    continue
            elif not hidden and setting.property('hidden'):
                continue

            flag, args = setting.as_parser_args()
            parser.add_argument(flag, **args)

        return parser

    def as_dict(self, ordered=False, values_only=False):
        """
        Returns the settings as a dictionary mapping setting_name to value.

        :param bool ordered:     If True, returns an OrderedDict instead of dict
        :param bool values_only: If True, only writes values instead of full properties
        :rtype: dict
        """
        generator = ((s.name, s.get()) if values_only else (s.name, s.as_dict())
                     for s in self._contents.values())
        data_type = OrderedDict if ordered else dict
        return data_type(generator)

    def get(self, key):
        """
        :raise: KeyError if key is not a valid setting

        :param str key:
        :return: Value for the given setting name.
        """
        return self._contents[key].get()

    def has_visible(self):
        """
        Returns True if any contents have the hidden property disabled.

        :rtype: bool
        """
        return any(not s.property('hidden') for s in self._contents.values())

    def reset(self):
        """
        Restores all settings to their default value

        :return:
        """
        for setting in self._contents.values():
            setting.reset()

    def set(self, key, value):
        """
        Sets a setting's value. Triggers the settingChanged signal to be emitted.

        :raise: KeyError if key is not a valid setting

        :param str key:
        :param object value:
        """
        setting = self._contents[key]
        setting.set(value)

    def setting(self, key):
        """
        :param str  key:
        :rtype: Setting
        """
        return self._contents.get(key)

    def to_json(self, ordered=True, values_only=False):
        """
        Writes the settings to a json object. Unrecognised objects will be
        converted to their __name__ attribute if available, otherwise to __str__

        :param bool ordered:     If True, preserves the settings order
        :param bool values_only: If True, only writes the settings names and values

        """
        data = self.as_dict(ordered=ordered, values_only=values_only)
        return json.dumps(data, default=util.object_to_string)

    def widget(self, *args, **kwargs):
        """
        Retrieves the widget assigned to the settings object, or a default widget.
        The default widget will be connected to settings.set()

        :return: UI Widget object
        """
        if self._widget_cls is not None:
            return self._widget_cls(self, *args, **kwargs)

        # Only import UI when required
        from settings_manager.ui import SettingsViewer
        return SettingsViewer(self, *args, **kwargs)
