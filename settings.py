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
    >>> settings.options
    'None'
    >>> settings["some_value"]
    3

    The SettingsViewer provides a default UI for displaying settings.
    """
    def __init__(self):
        self.__dict__["_data"] = dict()

    def __iter__(self):
        return iter(self._data)

    def __getattr__(self, item):
        return self[item]

    def __getitem__(self, item):
        return self._data[item]["value"]

    def __setattr__(self, key, value):
        self[key] = value

    def __setitem__(self, key, value):
        if key not in self._data:
            raise SettingsError("No setting exists for: {!r}".format(key))
        if type(value) != self._data[key]["type"]:
            raise SettingsError("Invalid value {!r} for setting {!r}".format(value, key))
        self._data[key]["value"] = value

    def add(self, name, default, choices=None, data_type=None, label=None, hidden=False):
        """
        :param str  name:      The name of the setting. Used to get and set the value.
        :param      default:   Default value.
        :param list choices:   A list of fixed values for the setting.
        :param      data_type: The type of the value. Inferred from default if not given.
        :param str  label:     The display name for the setting. Uses name if not given.
        :param bool hidden:    Whether or not the setting should be visible.
        """
        if name in self._data:
            raise SettingsError("Setting already exists: {!r}".format(name))

        if data_type is None and default is None:
            raise SettingsError("Unknown data type for setting {!r}. "
                                "Must specify a data type or valid default value".format(name))

        if data_type and not isinstance(default, data_type):
            raise SettingsError("Default value does not match data type for setting {!r}".format(name))

        data_type = data_type or type(default)

        if choices and not all(isinstance(c, data_type) for c in choices):
            raise SettingsError("Invalid choices for setting {!r}. "
                                "Not all choices match the data type: {}".format(name, data_type))

        if choices and default not in choices:
            raise SettingsError("Default value is not one of the given choices for setting {!r}".format(name))

        self._data[name] = {
            "choices": choices,
            "default": default,
            "hidden": hidden,
            "label": label or name,
            "type": data_type,
            "value": default,
        }

    def get_properties(self, name):
        """

        >>> s = Settings()
        >>> s.add("option", "setting")
        >>> s.get_properties("option")
        {
            'choices': None,
            'default': 'setting',
            'hidden': False,
            'label': 'option',
            'type': <type 'str'>,
            'value': 'setting'
        }

        :param str name: The setting name to return properties for
        :rtype: dict
        """
        return self._data[name]
