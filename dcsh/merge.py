"""Utility for configurable dictionary merges."""


def override(dst, src, key):
    """Sets key field from src in dstc."""
    dst[key] = src[key]


def shallow(dst, src, key):
    """Updates fields from src at key, into key at dst. """
    dst[key].update(src[key])


def merge(strategy, dst, src):
    """Merges src into dst destructively, using the provided strategy

    If a key is found in src that is not in the strategy, its value is ignored.
    """
    for key in src:
        strategy.get(key, lambda d,s,k: None)(dst, src, key)


