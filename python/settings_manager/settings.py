import json
import sys

from .custom_signal import Signal
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
    settingChanged = Signal(str, object)  # name, value

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
        self._data = OrderedDict()
        self._widget = None
        self.add_settings(settings)

    def __getitem__(self, item):
        return self.get(item)

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __setitem__(self, key, value):
        self.set(key, value)

    # Python 2.x
    def __nonzero__(self):
        return len(self) > 0

    # Python 3.x
    def __bool__(self):
        return len(self) > 0

    def add(self, name, default, choices=None, data_type=None, enabled=True, hidden=False,
            label=None, minmax=None, nullable=False, parent=None, widget=None, **kwargs):
        """
        :param str      name:      The name of the setting. Used to get and set the value.
        :param object   default:   Default value. If None, data_type is required.

        :param list     choices:    A list of fixed values for the setting.
        :param          data_type:  The type of the value. Inferred from default if not given.
        :param bool     enabled:    UI setting. If nullable is True, this determines whether the
                                    setting should be disabled/enabled.
        :param bool     hidden:     Whether or not the setting should be visible.
        :param str      label:      UI setting. The display name for the setting (defaults to name).
        :param tuple    minmax:     Tuple of minimum and maximum values for floats or ints.
        :param bool     nullable:   Whether or not None is a valid value.
        :param str      parent:     Another setting name who's value must evaluate True for this
                                    setting to be get/set. Calling get() on a setting whose parent
                                    does not evaluate True will return None.
        :param          widget:     UI setting. A callable object that can return a UI widget to use
                                    for this setting. If omitted, a default UI will be generated.
        """
        if name in self._data:
            raise SettingsError("Setting already exists: {!r}".format(name))

        if not isinstance(name, str):
            raise SettingsError("Setting keys must be strings: {}".format(name))

        if data_type is None and default is None:
            raise SettingsError("Unknown data type for setting {!r}. "
                                "Must specify a data type or valid default value".format(name))

        if data_type and default is not None and not isinstance(default, data_type):
            raise SettingsError(
                "Default value does not match data type for setting {!r}".format(name))

        data_type = data_type or type(default)

        if choices and not all(isinstance(c, data_type) for c in choices):
            raise SettingsError(
                "Invalid choices for setting {!r}. "
                "Not all choices match the data type: {}".format(name, data_type))

        if choices and default not in choices:
            raise SettingsError(
                "Default value is not one of the given choices for setting {!r}".format(name))

        if parent is not None and parent not in self._data:
            raise SettingsError(
                "Parent {!r} does not exist when adding setting: {!r}".format(parent, name))

        if minmax is not None:
            try:
                lo, hi = minmax
                if not lo <= default <= hi:
                    raise SettingsError(
                        "Setting {!r} value is not in minmax range: {}".format(name, minmax))
            except (ValueError, TypeError):
                raise SettingsError(
                    "minmax property is not a valid value. Must be tuple of 2 numeric values.")

        self._data[name] = {
            "choices": choices or list(),
            "default": default,
            "enabled": enabled,
            "hidden": hidden,
            "label": label or name.replace('_', ' '),
            "minmax": minmax,
            "nullable": nullable or (default is None),
            "parent": parent,
            "data_type": data_type,
            "value": default,
            "widget": widget,
        }
        self._data[name].update(kwargs)

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

    def as_dict(self, ordered=False, properties=False):
        """
        Returns the settings as a dictionary mapping setting_name to value.

        :param bool ordered:     If True, returns an OrderedDict instead of dict
        :param bool properties:  If True, write full properties instead of just value
        :rtype: dict
        """
        if ordered:
            if properties:
                return self._data.copy()
            return OrderedDict(((s, props["value"]) for s, props in self._data.items()))
        else:
            if properties:
                return dict(self._data)
            return {setting: properties["value"] for setting, properties in self._data.items()}

    def dependents(self, key):
        """
        Yields all settings whose parent property is the given setting name.
        This is not recursive, only lists first generation dependencies.

        :param str key:
        :rtype: str
        """
        for setting in self._data:
            if self.properties(setting)["parent"] == key:
                yield setting

    def get(self, key):
        """
        Returns the value for the given setting name.
        If the key is disabled of has a parent whose value is False, returns None.

        :raises: KeyError if key is not a valid setting

        :param str key:
        """
        # Check if disabled
        if not self._data[key]["enabled"]:
            return None

        # Check if parent evaluates to False
        parent = self._data[key]["parent"]
        if parent:
            if not self.get(parent):
                return None

        return self._data[key]["value"]

    def has_visible(self):
        """
        Returns True if any settings are visible to the UI.

        :rtype: bool
        """
        return any(not self.properties(s)["hidden"] for s in self._data)

    def properties(self, key):
        """
        Returns the setting properties for the given key

        >>> s = Settings()
        >>> s.add("option", "setting")
        >>> s.properties("option")
        {
            'choices': None,
            'default': 'setting',
            'hidden': False,
            'label': 'option',
            'minmax' : (None, None),
            'nullable': False,
            'parent': None,
            'type': <type 'str'>,
            'value': 'setting',
            'widget': None,
        }

        :raises: KeyError if key is not a valid setting

        :param str key: The setting name to return properties for
        :rtype: dict
        """
        return self._data[key]

    def reset(self):
        """
        Restores all settings to their default value

        :return:
        """
        for key in self._data:
            properties = self.properties(key)
            self.set(key, properties["default"])

    def set(self, key, value):
        """
        Sets a setting's value. Triggers the settingChanged signal to be emitted.

        :raises: SettingsError if not a valid key, value pair.

        :param str key:
        :param object value:
        """
        # Ensure the setting exists
        if key not in self._data:
            raise SettingsError("No setting exists for: {!r}".format(key))

        properties = self.properties(key)

        # Ensure type is valid
        data_type = properties["data_type"]
        nullable = properties["nullable"]
        if not isinstance(value, data_type) and not (value is None and nullable):
            raise SettingsError("Invalid value type {!r} for setting {!r}".format(value, key))

        # Ensure value is a valid option
        choices = properties["choices"]
        if choices and value not in choices and not (value is None and nullable):
            raise SettingsError(
                "Value {!r} is not a valid choice for setting {!r}".format(value, key))

        # Only return value if it has no parent, or parent evaluates to True
        parent = properties["parent"]
        if parent:
            if not self.get(parent):
                raise SettingsError(
                    "Setting {!r} cannot be set, parent {!r} is not valid".format(key, parent))

        minmax = properties["minmax"]
        if data_type in (float, int) and minmax is not None:
            lo, hi = minmax
            if not lo <= value <= hi:
                raise SettingsError(
                    "Value does not fit in range {} for setting: {!r}".format(minmax, key))

        self._data[key]["value"] = value
        self.settingChanged.emit(key, value)

    def set_widget(self, widget_callable):
        """
        Sets the widget to use for the settings object. Note, the given item must be callable,
        and return a an instance of the required widget. This can be a function instead of the
        widget class to avoid importing UI modules into active code modules.

        :param widget_callable:
        """
        self._widget = widget_callable

    def setting_widget(self, key, *args, **kwargs):
        """
        Retrieves the widget assigned to the given setting, or a default widget.
        The default widget will be connected to settings.set()

        :param str key:
        :return: UI Widget object
        """
        widget = self.properties(key)["widget"]
        if widget:
            return widget(self, key, *args, **kwargs)

        # Only import UI when required
        from settings_manager.ui import get_default_widget
        return get_default_widget(self, key)

    def to_json(self, path, values_only=False):
        """
        Writes the settings to a json file, preserving the settings order.
        data_type and widget fields will store the name of their values.

        :param str  path:
        :param bool values_only: If True, only writes the settings names and values

        """

        if values_only:
            data = OrderedDict(((k, v["value"]) for k, v in self._data.items()))
        else:
            data = self._data

        def default(value):
            """Converts unknown types to strings"""
            try:
                return value.__name__  # types / classes / functions
            except AttributeError:
                return str(value)

        with open(path, "w") as f:
            json.dump(data, f, default=default)

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
