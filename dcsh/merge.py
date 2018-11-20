"""Utility for configurable dictionary merges."""


class NoValue(object):
    """ Placeholder for a no-value type. """
    pass


# singleton for NoValue
no_value = NoValue()


def discard(dst, src, key, default):
    """Does nothing, effectively discarding the merged value."""
    return no_value


def override(left, right, key, default):
    """Returns right[key] if exists, else left[key]."""
    return right.get(key, left.get(key, default))


def shallow(left, right, key, default):
    """Updates fields from src at key, into key at dst. """
    left_v = left.get(key, default)
    if key in right:
        right_v = right[key]
        if key in left:
            if isinstance(left_v, dict) and isinstance(right_v, dict):
                return dict(left_v, **right_v)
        return right_v
    return left_v


# TODO: deep merge


class Merge(object):
    def __init__(self, key_fn, default_fn, *args, **kwargs):
        """Creates a merge strategy for the provided dictionaries and/or keys."""
        self._key_fn = key_fn
        if isinstance(key_fn, list):
            self._key_fn = lambda l, r: key_fn
        self._default_fn = default_fn
        self._strategy = dict(*args, **kwargs)

    def __call__(self, left, right, default=None):
        """Returns the merge of right to left for all keys in keys.

        If no such key exists in left or right, default is used as the value.
        """
        keys = self._key_fn(left, right)
        result = {}
        for key in keys:
            value = self._strategy.get(key, self._default_fn)(left, right, key, default)
            if value != no_value:
                result[key] = value
        return result


def inner(left, right):
    """Returns keys from right to left for all keys that exist in both."""
    return set(left.keys()) & set(right.keys())


def full(left, right):
    """Returns keys from right to left for all keys that exist in either."""
    return set(left.keys()) | set(right.keys())


def outermost(left, right):
    """Returns keys from right to left for all keys exclusive to both left and right."""
    return set(left.keys()) ^ set(right.keys())


def left(left, right):
    """Returns keys from right to left for all keys in left."""
    return set(left.keys())


def leftmost(left, right):
    """Returns keys from right to left for keys that exist only in left."""
    return set(left.keys()) - set(right.keys())


def right(left, right):
    """Returns keys from right to left for all keys in right."""
    return set(right.keys())


def rightmost(left, right):
    """Returns keys from right to left for keys that exist only in right."""
    return set(right.keys()) - set(left.keys())
