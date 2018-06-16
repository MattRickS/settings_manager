from settings_manager.exceptions import *
from settings_manager.custom_signal import Signal


class Setting(object):
    settingChanged = Signal(str, object)  # name, value

    def __init__(self, name, default, choices=None, data_type=None,
                 enabled=True, hidden=False, label=None, minmax=None,
                 nullable=False, parent=None, tooltip='', widget=None, **kwargs):
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
        :param Setting  parent:     Another setting who's value must evaluate True for this
                                    setting to be get/set. Calling get() on a setting whose parent
                                    does not evaluate True will return None.
        :param bool     tooltip:    Description message for widget tooltip and parser help
        :param          widget:     UI setting. A callable object that can return a UI widget to use
                                    for this setting. If omitted, a default UI will be generated.
        """
        if not isinstance(name, str):
            raise SettingsError("Setting names must be strings: {}".format(name))

        if data_type is None and default is None:
            raise SettingsError("Unknown data type for setting {!r}. "
                                "Must specify a data type or valid default value".format(name))

        if data_type and default is not None and not isinstance(default, data_type):
            raise SettingsError(
                "Default value does not match data type for setting {!r}".format(name))

        data_type = data_type or type(default)

        # TODO: Clean up multi choice results
        # TODO: Consider allowing MultiChoice int/float for large number of choices,
        # ie, they can only cycle through numbers
        is_multi_choice = data_type is list and minmax and choices
        if is_multi_choice:
            if default is not None:
                value = default if isinstance(default, list) else [default]
                if not set(value).issubset(set(choices)):
                    raise SettingsError('BLAH')
        else:
            if choices and not all(isinstance(c, data_type) for c in choices):
                raise SettingsError(
                    "Invalid choices for setting {!r}. "
                    "Not all choices match the data type: {}".format(name, data_type))

            if choices and default not in choices:
                raise SettingsError(
                    "Default value is not one of the given choices for setting {!r}".format(name))

        if parent and not isinstance(parent, Setting):
            raise SettingsError("Parent must be a Setting object")

        if minmax is not None:
            size = default if data_type in (float, int) else (0 if default is None else len(default))
            try:
                lo, hi = minmax
                if not lo <= size <= hi:
                    raise SettingsError(
                        "Setting {!r} value is not in minmax range: {}".format(name, minmax))
            except (ValueError, TypeError):
                raise SettingsError(
                    "minmax property is not a valid value. Must be tuple of 2 numeric values.")

        # Store properties as dict so that additional properties can be added
        self._properties = {
            "choices": choices or list(),
            "data_type": data_type,
            "default": default,
            "enabled": enabled,
            "hidden": hidden,
            "label": label or name.replace('_', ' '),
            "minmax": minmax,
            "nullable": nullable or (default is None),
            "parent": parent,
            "tooltip": tooltip,
            "value": default,
        }
        self._properties.update(kwargs)
        self._name = name
        self._widget = widget

    @property
    def name(self):
        """
        :rtype: str
        """
        return self._name

    def as_dict(self):
        """
        :rtype: dict
        """
        properties = self._properties.copy()
        properties.update({
            'name': self._name,
            'widget': self._widget,
        })
        return properties

    def as_parser_args(self):
        """
        :rtype: dict
        :return: Dictionary to populate ArgumentParser.add_argument
        """
        default = self._properties['default']
        data_type = self._properties['data_type']
        choices = self._properties['choices']
        tooltip = self._properties['tooltip']

        # TODO: minmax / nargs for multi choice

        args = {'help': tooltip}
        if data_type == bool:
            args['action'] = 'store_false' if default else 'store_true'
        elif data_type == list:
            args['nargs'] = '*'
        elif data_type != str:
            args['type'] = data_type

        if default is not None:
            args['default'] = default

        if choices:
            args['choices'] = choices

        return args

    def get(self):
        """
        Returns the value. If the key is disabled of has a
        parent whose value is False, returns None.
        """
        # Check if disabled
        # Check if parent evaluates to False
        parent = self._properties['parent']
        enabled = self._properties['enabled']
        if not enabled or (parent and not parent.get()):
            return None
        return self._properties['value']

    def property(self, name):
        """
        :param str name:
        :return: Property value
        """
        return self._properties.get(name)

    def set(self, value):
        """
        Sets a setting's value. Triggers the settingChanged signal to be emitted.

        :raises: SettingsError if not a valid value.

        :param object value:
        """
        # Ensure type is valid
        data_type = self._properties['data_type']
        nullable = self._properties['nullable']
        if not isinstance(value, data_type) and not (value is None and nullable):
            raise SettingsError(
                "Invalid value type {!r} for setting {!r}".format(value, self._name))

        # Only return value if it has no parent, or parent evaluates to True
        parent = self._properties['parent']
        if parent and not parent.get():
            raise SettingsError(
                "Setting {!r} cannot be set, parent {!r} is not valid".format(self._name, parent))

        # Ensure value is a valid option
        # TODO: Clean up multi choice results
        # Should have a 'validate value' method
        choices = self._properties['choices']
        minmax = self._properties['minmax']
        if data_type is list and choices and minmax:
            # multi choice list
            if isinstance(value, list):
                print('choices: {}, value: {}'.format(choices, value))
                if not set(value).issubset(set(choices)):
                    raise SettingsError('BLAH')
            else:
                if value not in choices:
                    raise SettingsError('BLAH')
        elif choices and value not in choices and not (value is None and nullable):
            raise SettingsError(
                "Value {!r} is not a valid choice for setting {!r}".format(value, self._name))

        if minmax is not None:
            size = value if data_type in (float, int) else (0 if value is None else len(value))
            lo, hi = minmax
            if not lo <= size <= hi:
                raise SettingsError(
                    "Value does not fit in range {} for setting: {!r}".format(minmax, self._name))

        self._properties['value'] = value
        self.settingChanged.emit(self._name, value)

    def widget(self, *args, **kwargs):
        """
        Retrieves the assigned widget, or a default widget.
        The default widget will be connected to settings.set()

        :return: UI Widget object
        """
        if self._widget:
            return self._widget(self, *args, **kwargs)

        # Only import UI when required
        from settings_manager.ui import get_default_widget
        return get_default_widget(self)
