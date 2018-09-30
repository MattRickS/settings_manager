import copy

from settings_manager.exceptions import *

import argparse


def required_length(lo, hi):
    class RequiredLength(argparse.Action):
        def __call__(self, parser, args, values, option_string=None):
            if not lo <= len(values) <= hi:
                msg = 'Argument {!r} requires between {} and {} arguments'.format(
                    self.dest, lo, hi
                )
                raise argparse.ArgumentTypeError(msg)
            setattr(args, self.dest, values)

    return RequiredLength


def class_from_string(string):
    """
    Attempts to resolve a class from the global scope.

    :param str  string:
    :rtype: type
    """
    global_dict = globals()
    cls = global_dict['__builtins__'].get(string)
    if cls is None:
        cls = global_dict.get(string)
    if cls is None:
        raise TypeError('Unknown type')
    return cls


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
        :param type       widget:     UI setting. Callable object that returns a
                                      UI widget to use for this setting. If 
                                      None, a default UI will be generated.
        """
        if not isinstance(name, str):
            raise SettingsError(
                'Setting names must be strings: {}'.format(name))

        # When there are multiple choices and a given range, enforce a
        # list data type (ie, value must be a subset of choices). This
        # modifies data type so must be done before normal validation.
        is_multi_choice = minmax is not None and choices is not None
        if is_multi_choice:
            data_type = list

        # Determine data_type
        if isinstance(data_type, str):
            # If data_type was given as a string, eg, via a configuration,
            # get the actual type object.
            try:
                data_type = class_from_string(data_type)
            except TypeError:
                raise SettingsError(
                    'Unknown data_type for setting: {!r}'.format(name))
        if data_type is None and default is None:
            raise SettingsError('Unknown data type for setting {!r}. '
                                'Must specify a data type or valid '
                                'default value'.format(name))
        data_type = data_type or type(default)

        # minmax must be 2 numeric values that define a numeric range,
        # or a length validation for strings.
        if minmax is not None:
            # If minmax is a single value, set it as both the min and max
            # This is only really relevant for a fixed string length
            minmax = minmax if hasattr(minmax, '__iter__') else (minmax, minmax)
            if not len(minmax) == 2 and not all(isinstance(i, (int, float)) for i in minmax):
                raise SettingsError(
                    'Invalid minmax value for setting {!r}: '
                    'Must be tuple of 2 numeric values.'.format(name))
            lo, hi = minmax
            if lo < 0:
                raise SettingsError(
                    'Invalid minmax range for setting {!r}: '
                    'Cannot have negative range')
            if hi < lo:
                raise SettingsError(
                    'Invalid minmax range for setting {!r}: '
                    'Max cannot be lower than min'.format(name)
                )

        # Multi choice is a list of values chosen from choices. The number
        # of choices required are defined by minmax. Only string values are
        # currently supported.
        if is_multi_choice:
            if not all(isinstance(x, str) for x in choices):
                raise SettingsError('Multi choice lists must be strings')
        # Choices by itself requires a single value chosen from the list
        elif choices is not None:
            if not all(isinstance(c, data_type) for c in choices):
                raise SettingsError(
                    "{!r}'s choices do not match "
                    "the data type: {}".format(name, data_type))

        # Fixed properties
        self._name = name
        self._type = data_type
        self._value = None

        # Set known properties and add any user defined properties
        self._properties = {
            'choices': choices,
            'default': default,
            'hidden': hidden,
            'label': label or name.replace('_', ' '),
            'minmax': minmax,
            'nullable': nullable or (default is None),
            'tooltip': tooltip or '',
            'widget': widget
        }
        self._properties.update(kwargs)

        # Setting hierarchy
        self._subsettings = []
        self._parent = None

        # Attempt to set the default value to validate it
        self.set(default)

        # Parent must be assigned after all validation, or the instance won't
        # be garbage collected as it's stored in the parents subsettings.
        if parent is not None:
            if not isinstance(parent, Setting):
                raise SettingsError('Parent must be a Setting object')
            parent.add_subsetting(self)

    def __str__(self):
        return self._name

    @property
    def name(self):
        # type: () -> str
        return self._name

    @property
    def parent(self):
        # type: () -> Setting
        return self._parent

    @property
    def subsettings(self):
        # type: () -> list[Setting]
        return self._subsettings[:]

    @property
    def type(self):
        # type: () -> type
        return self._type

    def add_subsetting(self, setting):
        # type: (Setting) -> None
        self._subsettings.append(setting)
        setting._parent = self

    def as_dict(self):
        # type: () -> dict
        properties = copy.deepcopy(self._properties)
        properties.update({
            'data_type': self._type,
            'name': self._name,
            'parent': self._parent,
            'value': copy.copy(self._value),  # Must be immutable
        })
        return properties

    def as_parser_args(self):
        """
        :rtype: dict
        :return: Dictionary to populate ArgumentParser.add_argument
        """
        default = self._properties['default']
        nullable = self._properties['nullable']
        flag = '--' + self._name

        args = {
            'choices': self._properties['choices'],
            'default': default,
            'help': self._properties['tooltip'],
            'type': self._type,
        }

        if self._type == bool:
            # Can't define choices/default/type for boolean
            args.pop('choices')
            args.pop('default')
            args.pop('type')
            if default:
                flag = '--no-' + self._name
                action = 'store_false'
                args['dest'] = self._name
            else:
                action = 'store_true'
            args['action'] = action
        elif self._type == list and not nullable:
            nargs = '*'
            minmax = self._properties['minmax']
            if minmax:
                lo, hi = minmax
                args['action'] = required_length(lo, hi)
                if lo > 0:
                    nargs = '+'
            args['nargs'] = nargs
            # type for multi value arguments refers to the sub type
            args['type'] = type(default[0]) if default else str
        # In order for an argument to accept no fields, it must use nargs='?'
        # If an argument is then given with no value, it uses const, not default
        elif nullable:
            args['nargs'] = '?'
            args['const'] = default

        args['flag'] = flag

        return args

    def get(self):
        """
        Returns the value. If the key is disabled of has a
        parent whose value is False, returns None.
        """
        # Check if disabled or parent evaluates to False
        if self._parent and not self._parent.get():
            return None
        return self._value

    def has_property(self, name):
        # type: (str) -> bool
        return name in self._properties

    def property(self, name):
        """
        :raise KeyError: if not a valid property
        :param str name:
        :return: Property value
        """
        # Accessor only
        return copy.copy(self._properties[name])

    def set(self, value):
        """
        Sets a setting's value.

        :raise: SettingsError if not a valid value.
        :param value:
        """
        # Only set value if it has no parent, or parent evaluates to True
        if self._parent and not self._parent.get():
            raise SettingsError(
                'Setting {!r} cannot be set, parent {!r} '
                'is not valid'.format(self._name, self._parent.name))

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
        # Multi choice properties require a subset of values from choices.
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
        widget_class = self._properties['widget']
        if widget_class:
            return widget_class(self, *args, **kwargs)

        # Only import UI when required
        from settings_manager.ui import get_default_widget
        return get_default_widget(self, *args, **kwargs)

    def _set(self, value):
        self._value = value
