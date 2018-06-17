import json
import sys

from settings_manager.setting import Setting
from collections import OrderedDict


def byteify(data):
    """
    *** Python 2 only ***
    Recursively converts all unicode elements in a dict back to string objects.

    :param dict data:
    :rtype: OrderedDict
    """
    if isinstance(data, dict):
        return OrderedDict(((byteify(key), byteify(value)) for key, value in data.items()))
    elif isinstance(data, list):
        return [byteify(element) for element in data]
    elif isinstance(data, unicode):
        return data.encode('utf-8')
    else:
        return data


class SettingsError(Exception):
    pass


class Settings(object):
    """
    Convenience class for storing settings with explicit data types.
    Settings are added via Settings.add() and can be get / set as properties, or as keys.

    eg,

    >>> settings = Settings()
    >>> settings.add("some_value", 3, label="Some Value")
    >>> settings.add("options", "None", choices=["None", "yes", "no", "maybe"])
    >>> settings.get("options")
    'None'
    >>> settings["some_value"]
    3

    The SettingsViewer provides a default UI for displaying settings.
    """
    def __init__(self, settings=None):
        """
        :param list|dict    settings:
            Settings can be accepted in multiple forms to allow for ordering:
                * Dictionary of properties; {setting_name: {properties}}
                * Dictionary with single value; {setting_name: value}
                * List of single dicts; {setting_name: {properties}}
                * List of single dicts; {setting_name: value}
                * List of tuples; (setting_name, value)
        """
        self._settings = OrderedDict()
        self._widget = None
        self.add_settings(settings)

    def __getitem__(self, item):
        return self.get(item)

    def __iter__(self):
        return iter(self._settings)

    def __len__(self):
        return len(self._settings)

    def __setitem__(self, key, value):
        self.set(key, value)

    # Python 2.x
    def __nonzero__(self):
        return len(self) > 0

    # Python 3.x
    def __bool__(self):
        return len(self) > 0

    def add(self, name, default, choices=None, data_type=None,
            hidden=False, label=None, minmax=None, nullable=False,
            parent=None, tooltip='', widget=None, **kwargs):
        """
        :param str          name:       Name of the setting. Used to get and set the value.
        :param object       default:    Default value. If None, data_type is required.

        :param list         choices:    List of fixed values for the setting.
        :param              data_type:  Type of the value. Inferred from default if not given.
        :param bool         hidden:     Whether or not the setting should be visible.
        :param str          label:      UI setting. Display name for the setting (defaults to name).
        :param tuple        minmax:     Tuple of minimum and maximum values for floats and ints.
                                        If provided with choices, the setting becomes a list type,
                                        and minmax defines the number of choices that can be selected.
        :param bool         nullable:   Whether or not None is a valid value.
        :param Setting|str  parent:     Another Setting who's value must evaluate True for this
                                        setting to be get/set. Calling get() on a setting whose
                                        parent does not evaluate True will return None.
        :param bool         tooltip:    Description message for widget tooltip and parser help
        :param              widget:     UI setting. Callable object that returns a UI widget to use
                                        for this setting. If None, a default UI will be generated.
        :rtype: Setting
        """
        if name in self._settings:
            raise SettingsError("Setting already exists: {!r}".format(name))
        if isinstance(parent, str):
            parent = self.setting(parent)
        setting = Setting(name, default, choices=choices, data_type=data_type,
                          hidden=hidden, label=label, minmax=minmax,
                          nullable=nullable, parent=parent, tooltip=tooltip,
                          widget=widget, **kwargs)
        self._settings[name] = setting
        return setting

    def add_settings(self, settings):
        """
        :param list|dict    settings:
            Settings can be accepted in multiple forms to allow for ordering:
                * Dictionary of properties; {setting_name: {properties}}
                * Dictionary with single value; {setting_name: value}
                * List of single dicts; {setting_name: {properties}}
                * List of single dicts; {setting_name: value}
                * List of tuples; (setting_name, value)
        """
        if isinstance(settings, dict):
            for setting, data in settings.items():
                # Dictionary of properties {setting_name: {...}}
                if isinstance(data, dict):
                    self.add(setting, **data)
                # Dictionary with single value {setting_name: value}
                else:
                    self.add(setting, data)
        elif isinstance(settings, list):
            for item in settings:
                # List of single dicts, likely from a configuration {setting_name: {...}}
                if isinstance(item, dict):
                    for setting, data in item.items():
                        # List of dicts {setting_name: {properties}}
                        if isinstance(data, dict):
                            self.add(setting, **data)
                        # List of dicts {setting_name: value}
                        else:
                            self.add(setting, data)
                # List of tuples, (setting_name, value)
                else:
                    setting, value = item
                    self.add(setting, value)

    def as_argparser(self, keys=None, hidden=False):
        """
        Create an ArgumentParser for the current settings.

        :param list[str]    keys:   Restricts args to keys if given.
        :param bool         hidden: If true, includes hidden keys
        :return:
        """
        # Uses for argparse in normal runtime are extremely limited, import only
        # when required
        import argparse
        parser = argparse.ArgumentParser()

        for setting in self._settings.values():
            if keys:
                if setting.name not in keys:
                    continue
            elif not hidden and setting.property('hidden'):
                continue

            args = setting.as_parser_args()
            parser.add_argument('--' + setting.name, **args)

        return parser

    def as_dict(self, ordered=False, values_only=False):
        """
        Returns the settings as a dictionary mapping setting_name to value.

        :param bool ordered:     If True, returns an OrderedDict instead of dict
        :param bool values_only: If True, only writes values instead of full properties
        :rtype: dict
        """
        items = ((s.name, s.get()) if values_only else (s.name, s.as_dict()) for s in self._settings.values())
        data_type = OrderedDict if ordered else dict
        return data_type(items)

    def dependents(self, key):
        """
        Yields all settings whose parent property is the given setting name.
        This is not recursive, only lists first generation dependencies.

        :param str key:
        :rtype: str
        """
        for setting in self._settings.values():
            if setting.property('parent') == key:
                yield setting

    def get(self, key):
        """
        Returns the value for the given setting name.
        If the key is disabled of has a parent whose value is False, returns None.

        :raises: KeyError if key is not a valid setting

        :param str key:
        """
        return self._settings[key].get()

    def has_visible(self):
        """
        Returns True if any settings are visible to the UI.

        :rtype: bool
        """
        return any(not s.property('hidden') for s in self._settings.values())

    def properties(self, key):
        """
        Returns the setting properties for the given key

        :raises: KeyError if key is not a valid setting

        :param str key: Name of setting to return properties for
        :rtype: dict
        """
        return self._settings[key].as_dict()

    def reset(self):
        """
        Restores all settings to their default value

        :return:
        """
        for setting in self._settings.values():
            setting.set(setting.property('default'))

    def set(self, key, value):
        """
        Sets a setting's value. Triggers the settingChanged signal to be emitted.

        :raises: SettingsError if not a valid key, value pair.

        :param str key:
        :param object value:
        """
        # Ensure the setting exists
        setting = self._settings.get(key)
        if setting is None:
            raise SettingsError("No setting exists for: {!r}".format(key))

        setting.set(value)

    def set_widget(self, widget_callable):
        """
        Sets the widget to use for the settings object. Note, the given item must be callable,
        and return a an instance of the required widget. This can be a function instead of the
        widget class to avoid importing UI modules into active code modules.

        :param widget_callable:
        """
        self._widget = widget_callable

    def setting(self, key):
        """
        :param str  key:
        :rtype: Setting
        """
        return self._settings.get(key)

    def setting_widget(self, key, *args, **kwargs):
        """
        Retrieves the widget assigned to the given setting, or a default widget.
        The default widget will be connected to settings.set()

        :param str key:
        :return: UI Widget object
        """
        return self._settings.get(key).widget(*args, **kwargs)

    def to_json(self, ordered=True, values_only=False):
        """
        Writes the settings to a json object. Unrecognised objects will be
        converted to their __name__ attribute if available, otherwise to __str__

        :param bool ordered:     If True, preserves the settings order
        :param bool values_only: If True, only writes the settings names and values

        """
        data = self.as_dict(ordered=ordered, values_only=values_only)

        def default(value):
            """Converts unknown types to strings"""
            try:
                return value.__name__  # types / classes / functions
            except AttributeError:
                return str(value)

        return json.dumps(data, default=default)

    def widget(self, *args, **kwargs):
        """
        Retrieves the widget assigned to the settings object, or a default widget.
        The default widget will be connected to settings.set()

        :return: UI Widget object
        """
        if self._widget:
            return self._widget(self, *args, **kwargs)

        # Only import UI when required
        from settings_manager.ui import SettingsViewer
        return SettingsViewer(self, *args, **kwargs)

    @classmethod
    def from_json(cls, path, scope=None):
        """
        Reads the settings from a json file, preserving the settings order.

        WARNING: This uses eval() to retrieve callable methods / classes from
        the data_type and widget properties. Be sure the data is safe before
        loading.

        :param str  path:
        :param dict scope:  The scope to use when evaluating data_type and widget.
        :rtype: Settings
        """
        with open(path, "r") as f:
            data = json.load(f, object_pairs_hook=OrderedDict)

        # Convert data from unicode to string (python 2 only)
        if sys.version_info[0] < 3:
            data = byteify(data)

        # Types are converted to strings in json, evaluate them back to types
        for setting_data in data.values():
            if isinstance(setting_data, dict):
                setting_data["data_type"] = eval(setting_data["data_type"], scope)

                widget = setting_data["widget"]
                if widget:
                    setting_data["widget"] = eval(widget, scope)

        return cls(data)
