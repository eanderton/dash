"""Utility for building CLI argument sets from dicionary data."""


def arg(*fmt):
    """Returns all provided formats for value, if value is truthy."""

    def fn(value):
        if value:
            return [f.format(v=value) for f in fmt]
        return []
    return fn


def dict_arg(*fmt):
    """Returns all provided formats for value.

    Value must be dict, or a type that supports .items().
    """

    def fn(value):
        return [f.format(v=v, k=k) for k, v in value.items() for f in fmt]
    return fn


def iter_arg(*fmt):
    """Returns all provided formats for value.

    Value must be an iterable type.
    """

    def fn(value):
        return [f.format(v=v) for v in value for f in fmt]
    return fn


def multi_arg(*fmt):
    """Returns all provided formats for value, based on value's type.

    Value is mapped to a formatter based on the following rules:
    - dict-like object: dict_arg
    - iterables (non-string): iter_arg
    - strings and all other types: arg
    """

    def fn(value):
        if isinstance(value, str):
            return arg(*fmt)(value)
        try:
            return dict_arg(*fmt)(value)
        except AttributeError:
            try:
                return iter_arg(*fmt)(value)
            except TypeError:
                return arg(*fmt)(value)
    return fn


def build(argmap, data):
    """Builds an array of arguments from the provided map and data.

    The argmap must consist of a mapping of keys to argbuilder functions.

    keys in the argmap are indexed into data, and if they are present, the
    corresponding values are passed to the corresponding argmap function. The
    argmap function returns with one or more array elements to be added to
    the returned array.
    """

    args = []
    for name, fn in argmap.iteritems():
        if name in data:
            args += fn(data[name])
    return args
