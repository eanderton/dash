"""Utility for configurable dictionary merges."""


def override(dst, src, key):
    """Sets key field from src in dstc."""
    dst[key] = src[key]


def shallow(dst, src, key):
    """Updates fields from src at key, into key at dst. """
    dst[key].update(src[key])


def with_strategy(strategy, dst, src):
    """Merges src into dst destructively, using the provided strategy

    If a key is found in src that is not in the strategy, its value is ignored.
    """
    for key in src:
        strategy.get(key, lambda d,s,k: None)(dst, src, key)


def merge(keys, left, right, default=None):
    """Performs a merge for a provided set of keys, preferring left over right for values.

    Returns the merge of right to left for all keys in keys.

    If no such key exists in left or right, default is used as the value.
    """

    result = {}
    for k in keys:
        result[k] = right[k] if k in right else left.get(k, default)
    return result


def inner(left, right):
    """Returns a merge of right to left for all keys that exist in both."""
    return merge(set(left.keys()) & set(right.keys()), left, right)


def outer(left, right):
    """Returns a merge of right to left for all keys() that exist in either."""
    return merge(set(left.keys()) + set(right.keys()), left, right)


def left(left, right):
    """Returns a merge of right to left for keys that exist only in left."""
    return merge(left.keys(), left, right)


def right(left, right):
    """Returns a merge of right to left for keys that exist only in right."""
    return merge(right.keys(), left, right)
