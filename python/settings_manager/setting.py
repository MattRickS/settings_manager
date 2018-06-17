from settings_manager.exceptions import *


class Setting(object):
    def __init__(self, name, default, choices=None, data_type=None,
                 hidden=False, label=None, minmax=None, nullable=False,
                 parent=None, tooltip=None, widget=None, **kwargs):
        """
        :param str        name:       Name of the setting.
        :param object     default:    Value. If None, data_type is required.

        :param list       choices:    List of fixed values for the setting.
        :param            data_type:  Type of the value. Inferred from default 
                                      if not given.
        :param bool       hidden:     Whether or not the setting should be 
                                      visible in UI / argparser.
        :param str        label:      UI setting. Display name for the setting 
                                      (defaults to name).
        :param tuple|int  minmax:     Tuple of minimum and maximum values for 
                                      floats and ints. If provided with choices, 
                                      the setting becomes a list type, and 
                                      minmax defines the number of choices that 
                                      can be selected.
        :param bool       nullable:   Whether or not None is a valid value.
        :param Setting    parent:     Another setting who's value must evaluate 
                                      True for this setting to be get/set. 
                                      Calling get() on a setting whose parent
                                      does not evaluate True will return None.
        :param bool       tooltip:    Description message for widget tooltip and 
                                      parser help
        :param            widget:     UI setting. Callable object that returns a 
                                      UI widget to use for this setting. If 
                                      None, a default UI will be generated.
        """
        if not isinstance(name, str):
            raise SettingsError(
                'Setting names must be strings: {}'.format(name))

        has_value = default is not None
        # Special case modifies data_type before validation
        is_multi_choice = minmax is not None and choices is not None
        if is_multi_choice:
            data_type = list
            # Explicit use case type validation, to avoid confusion
            if has_value and not isinstance(default, list):
                raise SettingsError(
                    'Setting {!r} must be a list when '
                    'combining minmax and choices'.format(name))

        # Determine data_type
        if isinstance(data_type, str):
            # If data_type was given as a string, eg, via a configuration, get the object
            try:
                data_type = __builtins__.get(data_type)
            except KeyError:
                raise SettingsError(
                    'Unknown data_type for setting: {!r}'.format(name))
        if data_type is None and default is None:
            raise SettingsError('Unknown data type for setting {!r}. '
                                'Must specify a data type or valid '
                                'default value'.format(name))
        if data_type and has_value and not isinstance(default, data_type):
            raise SettingsError(
                'Default value does not match data '
                'type for setting {!r}'.format(name))
        data_type = data_type or type(default)

        # Special properties
        if is_multi_choice:
            if has_value:
                lo, hi = minmax
                if lo > len(default) > hi:
                    raise SettingsError(
                        'Invalid number of choices '
                        'for setting: {!r}'.format(name))
                if not set(default).issubset(set(choices)):
                    raise SettingsError(
                        'Invalid choices for setting: {!r}'.format(name))
            # TODO: Add sub_type key for converting values to from strings,
            # remove this error
            if not all(isinstance(x, str) for x in choices):
                raise SettingsError('Multi choice lists must be strings')
        elif choices is not None:
            if not all(isinstance(c, data_type) for c in choices):
                raise SettingsError(
                    "{!r}'s choices do not match "
                    "the data type: {}".format(name, data_type))
            if default not in choices:
                raise SettingsError(
                    '{} is not a valid choice for '
                    'setting {!r}'.format(default, name))

        # TODO: look at allowing minmax to control another setting's list
        # length... maybe by passing a Setting instance's method as the keyword
        # it links it? eg, minmax=setting.get
        elif minmax is not None and has_value:
            minmax = minmax if hasattr(minmax, '__iter__') else (minmax, minmax)
            size = default if data_type in (float, int) else len(default)
            try:
                lo, hi = minmax
                if not lo <= size <= hi:
                    raise SettingsError(
                        'Setting {!r} value is not in '
                        'minmax range: {}'.format(name, minmax))
            except (ValueError, TypeError):
                raise SettingsError(
                    'minmax property is not a valid value. '
                    'Must be tuple of 2 numeric values.')

        # Store properties as dict so that additional properties can be added
        self._properties = {
            'choices': choices,
            'default': default,
            'hidden': hidden,
            'label': label or name.replace('_', ' '),
            'minmax': minmax,
            'nullable': nullable or (default is None),
            'tooltip': tooltip or '',
            'value': default,
        }
        self._properties.update(kwargs)

        self._name = name
        self._subsettings = []
        self._type = data_type
        self._widget = widget

        # Must be appended after all validation, or an invalid Setting could be
        # stored
        self.parent = None
        if parent is not None:
            if not isinstance(parent, Setting):
                raise SettingsError('Parent must be a Setting object')
            parent.add_subsetting(self)

    def __str__(self):
        return self._name

    @property
    def name(self):
        """
        :rtype: str
        """
        return self._name

    @property
    def subsettings(self):
        return self._subsettings[:]

    @property
    def type(self):
        return self._type

    def add_subsetting(self, setting):
        """
        :param Setting setting:
        """
        self._subsettings.append(setting)
        setting.parent = self

    def as_dict(self):
        """
        :rtype: dict
        """
        properties = self._properties.copy()
        properties.update({
            'data_type': self._type,
            'name': self._name,
            'parent': self.parent,
            'widget': self._widget,
        })
        return properties

    def as_parser_args(self):
        """
        :rtype: dict
        :return: Dictionary to populate ArgumentParser.add_argument
        """
        default = self._properties['default']
        choices = self._properties['choices']
        tooltip = self._properties['tooltip']

        # TODO: minmax / nargs for multi choice

        args = {'help': tooltip}
        if self._type == bool:
            args['action'] = 'store_false' if default else 'store_true'
        elif self._type == list:
            args['nargs'] = '*'
        elif self._type != str:
            args['type'] = self._type

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
        # Check if disabled or parent evaluates to False
        if self.parent and not self.parent.get():
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
        Sets a setting's value.

        :raise: SettingsError if not a valid value.
        :param value:
        """
        # Only set value if it has no parent, or parent evaluates to True
        if self.parent and not self.parent.get():
            raise SettingsError(
                'Setting {!r} cannot be set, parent {!r} '
                'is not valid'.format(self._name, self.parent.name))

        # Nullable can set without further validation
        nullable = self._properties['nullable']
        if value is None and nullable:
            self._set(value)
            return

        # Ensure type is valid
        if not isinstance(value, self._type):
            raise SettingsError(
                'Invalid value type {!r} for '
                'setting {!r}'.format(value, self._name))

        # Special properties
        choices = self._properties['choices']
        minmax = self._properties['minmax']
        if choices is not None and minmax is not None:
            lo, hi = minmax
            if not lo <= len(value) <= hi:
                raise SettingsError(
                    'Invalid number of choices for '
                    'setting: {!r}'.format(self._name))
            if not set(value).issubset(set(choices)):
                raise SettingsError(
                    'Invalid choices for setting: {!r}'.format(self._name))
        elif choices is not None:
            if value not in choices:
                raise SettingsError(
                    'Invalid choice {!r} for setting: '
                    '{!r}'.format(value, self._name))
        elif minmax is not None:
            size = value if isinstance(value, (float, int)) else len(value)
            lo, hi = minmax
            if not lo <= size <= hi:
                raise SettingsError(
                    'Value does not fit in range {} for setting: '
                    '{!r}'.format(minmax, self._name))

        self._set(value)

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

    def _set(self, value):
        self._properties['value'] = value
