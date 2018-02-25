class SettingsError(Exception):
    pass


class Setting(object):
    def __init__(self, default, choices=None, data_type=None, label=None, hidden=False):
        if data_type is None and default is None:
            raise SettingsError("Unknown data type for setting. "
                                "Must specify a data type or valid default value")

        if data_type and not isinstance(default, data_type):
            raise SettingsError("Default value does not match data type for setting")

        data_type = data_type or type(default)

        if choices and not all(isinstance(c, data_type) for c in choices):
            raise SettingsError("Invalid choices for setting. "
                                "Not all choices match the data type: {}".format(data_type))

        if choices and default not in choices:
            raise SettingsError("Default value is not one of the given choices for setting")

        self.name = None
        self.choices = choices
        self.default = default
        self.hidden = hidden
        self.data_type = data_type
        self._label = label

    def __repr__(self):
        return "Setting({!r}, choices={!r}, data_type={}, label={!r}, hidden={!r})".format(
            self.default, self.choices, self.data_type.__name__, self._label, self.hidden)

    def __get__(self, instance, owner):
        if self.name is None:
            self._get_name(owner)
        if instance:
            value = instance.__dict__.get(self.name)
            if value is not None:
                return value
            instance.__dict__[self.name] = self.default
            return self.default
        return self

    def __set__(self, instance, value):
        if not self.name:
            self._get_name(instance.__class__)
        if type(value) != self.data_type:
            raise SettingsError("Invalid value for setting {!r}\n"
                                "Expected: {}\n"
                                "Got: {}".format(self.name, self.data_type, type(value)))
        instance.__dict__[self.name] = value

    def _get_name(self, owner):
        for name, attr in owner.__dict__.items():
            if attr == self:
                self.name = name
                return

    @property
    def label(self):
        if self._label:
            return self._label
        parts = self.name.split('_')
        return ' '.join(s.capitalize() for s in parts)


class Settings(object):
    def __get__(self, instance, owner):
        # Use getattr to force the loading of name
        if instance:
            return {k: getattr(instance, k) for k, v in instance.__class__.__dict__.items() if isinstance(v, Setting)}
        return {k: getattr(owner, k) for k, v in owner.__dict__.items() if isinstance(v, Setting)}


class A(object):
    settings = Settings()

    words = Setting("Important string of words")
    check = Setting(True)
    tester = Setting(None, data_type=object)


if __name__ == '__main__':
    a = A()
    print A.check
    print a.words
    a.words = "other"
    print a.words
    a.check = False
    print a.check
    print a.settings
    print A.settings
    print {k: v.default for k, v in A.settings.items()}
