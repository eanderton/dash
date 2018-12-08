"""Tests for the dcsh argbuilder module."""

import dcsh.argbuilder as argbuilder
import unittest
from collections import OrderedDict


class TestArgbuilder(unittest.TestCase):
    def test_arg(self, arg_fn=argbuilder.arg):
        fn = arg_fn('--one "{v}"', '--two \'{v}\'', '--three')
        self.assertEqual(fn('value'), ['--one "value"', '--two \'value\'', '--three'])
        self.assertEqual(fn(None), [])
        self.assertEqual(fn(False), [])

    def test_dict_arg(self, arg_fn=argbuilder.dict_arg):
        fn = arg_fn('-v {v}', '-k {k}', '--{k}={v}')
        self.assertEqual(fn(OrderedDict((('one', 'two'), ('three', 'four')))), [
                '-v two', '-k one', '--one=two',
                '-v four', '-k three', '--three=four',
            ])

    def test_iter_arg(self, arg_fn=argbuilder.iter_arg):
        fn = arg_fn('-v {v}', '--value {v}')
        self.assertEqual(fn(['one', 'two']), [
                '-v one', '--value one',
                '-v two', '--value two',
            ])
        fn = argbuilder.iter_arg('-v {v}', '--value {v}')
        self.assertEqual(fn(('one', 'two')), [
                '-v one', '--value one',
                '-v two', '--value two',
            ])
        fn = argbuilder.iter_arg('-v {v}', '--value {v}')
        self.assertEqual(fn({'one', 'two'}), [
                '-v two', '--value two',
                '-v one', '--value one',
            ])

    def test_multi_arg(self):
        self.test_arg(argbuilder.multi_arg)
        self.test_dict_arg(argbuilder.multi_arg)
        self.test_iter_arg(argbuilder.multi_arg)

    def test_build(self):
        self.assertEqual(argbuilder.build(OrderedDict((
                ('foo', argbuilder.arg('--foo {v}')),
                ('bar', argbuilder.dict_arg('--bar {k}={v}')),
                ('baz', argbuilder.iter_arg('--baz {v}')),
            )), {
                'foo': 'one',
                'bar': OrderedDict((('two', 'three'), ('four', 'five'))),
                'baz': ['six', 'seven'],
            }), [
                '--foo one',
                '--bar two=three', '--bar four=five',
                '--baz six', '--baz seven',
            ])
