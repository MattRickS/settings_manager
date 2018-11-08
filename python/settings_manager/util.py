from collections import OrderedDict
import argparse
import inspect
import sys


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


def class_from_string(string):
    """
    Attempts to resolve a class from the global scope. If the string is not
    a python builtin, it will assume the string is a full path to the module
    and class to use

    :param str  string:
    :rtype: type
    """
    global_dict = globals()
    # Check for built in type
    cls = global_dict['__builtins__'].get(string)
    # Check for module scope class
    if cls is None:
        cls = global_dict.get(string)
    # Check for full module path to object definition
    if cls is None:
        parts = string.rsplit('.', 1)
        # If not dot separated, would have been retrieved from globals
        if len(parts) == 2:
            mod_name, cls_name = parts
            mod = sys.modules.get(mod_name)
            if mod is not None:
                cls = getattr(mod, cls_name, None)
                # Make sure the object is a class, not an instance
                if not inspect.isclass(cls):
                    cls = None
    return cls


def object_to_string(value):
    # type: (object) -> str
    """ Converts unknown objects to strings """
    try:
        return value.__name__  # types / classes / functions
    except AttributeError:
        return str(value)


def multi_choice(lo, hi, choices):
    class MultiChoice(argparse.Action):
        def __call__(self, parser, args, values, option_string=None):
            if not lo <= len(values) <= hi:
                msg = 'Argument {!r} requires between {} and {} arguments'.format(
                    self.dest, lo, hi
                )
                raise argparse.ArgumentTypeError(msg)
            setattr(args, self.dest, values)

    return MultiChoice


def required_length(lo, hi):
    # type: (int|float, int|float) -> RequiredLength
    """ Provides a range Action for argparse """
    class RequiredLength(argparse.Action):
        def __call__(self, parser, args, values, option_string=None):
            if not lo <= len(values) <= hi:
                msg = 'Argument {!r} requires between {} and {} arguments'.format(
                    self.dest, lo, hi
                )
                raise argparse.ArgumentTypeError(msg)
            setattr(args, self.dest, values)

    return RequiredLength
