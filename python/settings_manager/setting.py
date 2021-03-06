import copy

from settings_manager.exceptions import SettingsError
from settings_manager import util


class Setting(object):
    def __init__(self, name, default, choices=None, data_type=None,
                 hidden=False, label=None, minmax=None, nullable=False,
                 subtype=None, tooltip=None, widget=None, **kwargs):
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
        :param type       subtype:    If datatype is list, subtype is the
                                      content type.
        :param bool       tooltip:    Description message for widget tooltip and
                                      parser help
        :param type       widget:     UI setting. Callable object that returns a
                                      UI widget to use for this setting. If 
                                      None, a default UI will be generated.
        """
        # Fixed properties
        self._name = self._validate_name(name)
        self._type = self._validate_data_type(data_type, default, choices, minmax)
        self._subtype = self._validate_subtype(subtype, default, choices)
        self._value = None

        # Validate optional properties
        if minmax is not None:
            minmax = self._validate_minmax(minmax)
        # Type is forced to list by validate_data_type if minmax and choices are given
        if self._type is list and choices is not None:
            minmax = self._validate_multi_choice(choices, minmax)
        # Only validate choices separately if multi choice hasn't validated
        elif choices is not None:
            choices = self._validate_choices(choices)

        # Set optional and user defined properties
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

        # Attempt to set the default value to validate it
        self.set(default)

    def __eq__(self, other):
        if isinstance(other, str):
            return other == self._name
        if isinstance(other, Setting):
            return self.as_dict() == other.as_dict()
        return False

    def __hash__(self):
        return hash(self._name)

    def __repr__(self):
        properties = self._properties.copy()
        properties['data_type'] = self._type
        default = properties.pop('default')
        kwargs = ['{}={!r}'.format(k, v) for k, v in sorted(properties.items())]
        return 'Setting({!r}, {}, {})'.format(self._name, default, ', '.join(kwargs))

    def __str__(self):
        return 'Setting({})'.format(self._name)

    @property
    def name(self):
        # type: () -> str
        return self._name

    @property
    def subtype(self):
        # type: () -> type
        return self._subtype

    @property
    def type(self):
        # type: () -> type
        return self._type

    def as_dict(self):
        # type: () -> dict
        properties = copy.deepcopy(self._properties)
        properties.update({
            'data_type': self._type,
            'name': self._name,
            'value': copy.copy(self._value),  # Must be immutable
        })
        return properties

    def as_parser_args(self):
        """
        :rtype: tuple[str, dict]
        :return: Tuple of (flag, arguments) to populate ArgumentParser.add_argument
        """
        default = self._properties['default']
        nullable = self._properties['nullable']
        flag = '--' + self._name

        args = {
            'default': default,
            'type': self._type,
        }

        tooltip = self._properties['tooltip']
        if tooltip:
            args['help'] = tooltip

        choices = self._properties['choices']
        if choices:
            args['choices'] = choices

        minmax = self._properties['minmax']
        if minmax:
            lo, hi = minmax
            args['action'] = util.required_length(lo, hi)

        if self._type == bool:
            # Can't define choices/default/type for boolean
            args.pop('choices', None)
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
            if minmax:
                lo, hi = minmax
                args['action'] = util.required_length(lo, hi)
                if lo > 0:
                    nargs = '+'
            args['nargs'] = nargs
            args['type'] = self.subtype
        # In order for an argument to accept no fields, it must use nargs='?'
        # If a flag is then given with no value, it uses const, not default
        elif nullable:
            args['nargs'] = '?'
            args['const'] = None

        return flag, args

    def get(self):
        """
        Returns the value. If the key is disabled of has a
        parent whose value is False, returns None.
        """
        # Accessor only
        return copy.copy(self._value)

    def has_property(self, name):
        """
        :param str  name:
        :rtype: bool
        """
        return name in self._properties

    def is_modified(self):
        """
        Returns True if the value doesn't match the default

        :rtype: bool
        """
        return self._properties['default'] != self._value

    def property(self, name):
        """
        :raise KeyError: if not a valid property
        :param str name:
        :return: Property value
        """
        # Accessor only
        return copy.copy(self._properties[name])

    def reset(self):
        """
        Resets a setting to it's initial value

        Warning:
            Does not alter properties
        """
        self.set(self.property('default'))

    def set(self, value):
        """
        Sets a setting's value.

        :raise: SettingsError if not a valid value.
        :param value:
        """
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

    def set_property(self, name, value):
        """
        Sets a property value.

        Warning:
            This does not validate the current value against the new property.
            It is advised to call Setting.set(Setting.get()) after making all
            required modifications to ensure the current value is valid.

        :param str  name:
        :param      value:
        """
        if name == 'choices':
            value = self._validate_choices(value)
            minmax = self._properties['minmax']
            self._validate_multi_choice(value, minmax)
        elif name == 'minmax':
            value = self._validate_minmax(value)
            choices = self._properties['choices']
            self._validate_multi_choice(choices, value)
        self._properties[name] = value

    def _set(self, value):
        self._value = value

    def _validate_choices(self, choices):
        # type: (list) -> list
        if not all(isinstance(c, self._type) for c in choices):
            raise SettingsError(
                "{!r}'s choices do not match "
                "the data type: {}".format(self._name, self._type))
        return choices

    def _validate_data_type(self, data_type, default, choices=None, minmax=None):
        # When there are multiple choices and a given range, enforce a
        # list data type (ie, value must be a subset of choices). This
        # modifies data type so must be done before normal validation.
        if choices is not None and minmax is not None:
            data_type = list

        # Determine data_type
        if isinstance(data_type, str):
            # If data_type was given as a string, get the actual type object.
            cls = util.class_from_string(data_type)
            if cls is None:
                raise SettingsError(
                    'Unknown string for data_type {!r} for setting: {!r}'.format(
                        data_type, self._name))
            data_type = cls
        if data_type is None and default is None:
            if not choices:
                raise SettingsError('Unknown data type for setting {!r}. '
                                    'Must specify a data type or valid '
                                    'default value'.format(self._name))
            data_type = type(choices[0])
        data_type = data_type or type(default)
        if data_type == dict:
            raise SettingsError(
                'Unsupported data type for setting {!r}: {}'.format(
                    self._name, data_type))
        return data_type

    def _validate_minmax(self, minmax):
        # type: (tuple) -> tuple[int|float, int|float]
        # minmax must be 2 numeric values that define a numeric range,
        # or a length validation for strings.
        # If minmax is a single value, set it as both the min and max
        # This is only really relevant for a fixed string length
        minmax = tuple(minmax) if hasattr(minmax, '__iter__') else (minmax, minmax)
        if len(minmax) != 2 or any(not isinstance(i, int) for i in minmax):
            raise SettingsError(
                'Invalid minmax value for setting {!r}: '
                'Must be tuple of 2 numeric values.'.format(self._name))
        lo, hi = minmax
        if self._type in (list, str) and lo < 0:
            raise SettingsError(
                'Invalid minmax range for setting {!r}: Cannot '
                'have negative range for types (list, str)'.format(self._name))
        if hi < lo:
            raise SettingsError(
                'Invalid minmax range for setting {!r}: '
                'Max cannot be lower than min'.format(self._name)
            )
        return minmax

    @staticmethod
    def _validate_multi_choice(choices, minmax):
        # type: (list, tuple) -> tuple[int, int]
        # Multi choice is a list of values chosen from choices. The number
        # of choices required are defined by minmax.
        # If type is list and choices are given without minmax, minmax must
        # be the full range of choices.
        minmax = minmax or (0, len(choices))
        lo, hi = minmax
        num_choices = len(choices)
        if num_choices < lo or num_choices < hi:
            raise SettingsError(
                'Insufficient choices ({}) to meet minmax '
                'requirement: {}'.format(num_choices, minmax)
            )

        return minmax

    @staticmethod
    def _validate_name(name):
        # type: (str) -> str
        if not isinstance(name, str):
            raise SettingsError(
                'Setting names must be strings: {}'.format(name))
        if any(char.isspace() for char in name):
            raise SettingsError(
                'Setting names cannot have whitespace. '
                'Use label for display names'
            )
        return name

    def _validate_subtype(self, subtype, default, choices):
        # type: (type, object, list) -> type|None
        # Only required for list type
        if self._type is not list:
            return
        # All possible options should be present in default and choices
        # either of which may be None or empty.
        options = (default or []) + (choices or [])
        if subtype is None:
            if not options:
                raise SettingsError(
                    'Unknown subtype for setting: {}'.format(self._name)
                )
            subtype = type(options[0]) if options else str
        if not all(isinstance(i, subtype) for i in options):
            raise SettingsError('Subtype does not match the given default/'
                                'choices for setting: {}'.format(self._name))
        return subtype
