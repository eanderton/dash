"""Utility for building CLI argument sets from dicionary data."""


def boolean(*fmt):
    """Returns formatted literal argument if the data value is true."""

    def fn(v):
        if v:
            return [f.format(v=v) for f in fmt]
        return []
    return fn


def single(*fmt):
    """Passes the data value through, following literal values."""

    def fn(value):
        return [f.format(v=value) for f in fmt]
    return fn


def multi(*fmt):
    """Passes multiple values through formats."""

    def fn(value):
        if isinstance(value, dict):
            return [f.format(v=v,k=v) for f in fmt for k, v in value.items()]
        else:    
            return [f.format(k=v) for f in fmt for v in value]
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
    for name, fn in argmap.items():
        if name in data:
            args += fn(data[name])
    return args
