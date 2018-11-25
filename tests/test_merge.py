"""Tests for the merge module."""

import dcsh.merge as merge
import unittest


class TestMergeStrategies(unittest.TestCase):
    def test_discard(self):
        left = {'a': 555}
        right = {'a': 1, 'b': 2}
        self.assertEqual(merge.discard(left, right, 'a', None), merge.no_value)

    def test_override(self):
        """Values must move from src to dst."""
        left = {'a': 555}
        right = {'a': 1, 'b': 2}
        self.assertEqual(merge.override(left, right, 'a', None), 1)
        self.assertEqual(merge.override(left, right, 'b', None), 2)
        self.assertEqual(merge.override(left, right, 'c', None), None)

    def test_shallow_dict(self):
        """Dest dict values are updated from src."""
        left = {'a': {'b': 555}}
        right = {'a': {'b': 2, 'c': 3}}
        self.assertEqual(merge.shallow(left, right, 'a', None), right['a'])

    def test_shallow_dict_missing(self):
        """Dest value is provided from source if non existent."""
        left = {}
        right = {'a': {'b': 2, 'c': 3}}
        self.assertEqual(merge.shallow(left, right, 'a', None), right['a'])
        self.assertEqual(merge.shallow(left, right, 'b', None), None)

    def test_shallow_dict_mismatch(self):
        """Dest value is overridden from source if either src or dst is not a dict."""
        left = {'a': 'foobarbaz'}
        right = {'a': {'b': 2, 'c': 3}}
        self.assertEqual(merge.shallow(left, right, 'a', None), right['a'])


class TestKeys(unittest.TestCase):
    def test_inner(self):
        self.assertEqual(merge.inner({'a': 1, 'b': 2, 'c': 3}, {'c': 3, 'd': 4}), set('c'))

    def test_full(self):
        self.assertEqual(merge.full({'a': 1, 'b': 2, 'c': 3}, {'c': 3, 'd': 4}), set(['a', 'b', 'c', 'd']))

    def test_outermost(self):
        self.assertEqual(merge.outermost({'a': 1, 'b': 2, 'c': 3}, {'c': 3, 'd': 4}), set(['a', 'b', 'd']))

    def test_left(self):
        self.assertEqual(merge.left({'a': 1, 'b': 2, 'c': 3}, {'c': 3, 'd': 4}), set(['a', 'b', 'c']))

    def test_leftmost(self):
        self.assertEqual(merge.leftmost({'a': 1, 'b': 2, 'c': 3}, {'c': 3, 'd': 4}), set(['a', 'b']))

    def test_right(self):
        self.assertEqual(merge.right({'a': 1, 'b': 2, 'c': 3}, {'c': 3, 'd': 4}), set(['c', 'd']))

    def test_rightmost(self):
        self.assertEqual(merge.rightmost({'a': 1, 'b': 2, 'c': 3}, {'c': 3, 'd': 4}), set(['d']))


class TestMerge(unittest.TestCase):
    def test_merge(self):
        """All specified keys merge from left to right."""
        left = {'a': 1}
        right = {'b': 2}
        self.assertEqual(merge.Merge(['a'], merge.override)(left, right), left)
        self.assertEqual(merge.Merge(['b'], merge.override)(left, right), right)
        self.assertEqual(merge.Merge(['a'], merge.override)(left, right), left)
        self.assertEqual(merge.Merge(['a', 'b', 'c'], merge.override)(left, right),
                         {'a': 1, 'b': 2, 'c': None})
        self.assertEqual(merge.Merge(['a', 'b', 'c'], merge.override)(left, right, 9000),
                         {'a': 1, 'b': 2, 'c': 9000})

    def test_inner(self):
        """Merge for the subset of left and right keys."""
        left = {'a': 1, 'b': 2}
        right = {'b': 222, 'c': 333}
        self.assertEqual(merge.Merge(merge.inner, merge.override)(left, right), {'b': 222})

    def test_full(self):
        """Merge for the union of left and right keys."""
        left = {'a': 1, 'b': 2}
        right = {'b': 222, 'c': 333}
        self.assertEqual(merge.Merge(merge.full, merge.override)(left, right),
                         {'a': 1, 'b': 222, 'c': 333})

    def test_outermost(self):
        """Merge for keys exclusive to left and right. """
        left = {'a': 1, 'b': 2}
        right = {'b': 222, 'c': 333}
        self.assertEqual(merge.Merge(merge.outermost, merge.override)(left, right),
                         {'a': 1, 'c': 333})

    def test_left(self):
        """Merge for keys in left."""
        left = {'a': 1, 'b': 2}
        right = {'b': 222, 'c': 333}
        self.assertEqual(merge.Merge(merge.left, merge.override)(left, right),
                         {'a': 1, 'b': 222})

    def test_leftmost(self):
        """Merge for keys exclusive to left."""
        left = {'a': 1, 'b': 2}
        right = {'b': 222, 'c': 333}
        self.assertEqual(merge.Merge(merge.left, merge.override)(left, right),
                         {'a': 1, 'b': 222})

    def test_right(self):
        """Merge for keys in right."""
        left = {'a': 1, 'b': 2}
        right = {'b': 222, 'c': 333}
        self.assertEqual(merge.Merge(merge.right, merge.override)(left, right),
                         {'b': 222, 'c': 333})

    def test_rightmost(self):
        """Merge for keys exclusive to right."""
        left = {'a': 1, 'b': 2}
        right = {'b': 222, 'c': 333}
        self.assertEqual(merge.Merge(merge.rightmost, merge.override)(left, right),
                         {'c': 333})
