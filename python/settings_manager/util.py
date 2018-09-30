from collections import OrderedDict
import argparse


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
