"""Tests for the printer module."""

import sys
import dcsh.printer as printer
import unittest
from mock import patch
from StringIO import StringIO


class TestBasics(unittest.TestCase):
    def test_create_no_args(self):
        p = printer.StylePrinter()
        self.assertEqual(p._start_newline, True)
        self.assertEqual(p._style_defaults, printer.default_style)
        self.assertEqual(p.ansimode, True)
        self.assertEqual(p.stream, sys.stdout)
        self.assertEqual(p.stylesheet, {})

    def test_create_full_args(self):
        stream = {}
        stylesheet = {}
        style_defaults = {}
        p = printer.StylePrinter(stream, stylesheet, style_defaults)
        self.assertEqual(p._start_newline, True)
        self.assertIs(p._style_defaults, style_defaults)
        self.assertEqual(p.ansimode, True)
        self.assertIs(p.stream, stream)
        self.assertIs(p.stylesheet, stylesheet)

    def test_write(self):
        stream = StringIO()
        p = printer.StylePrinter(stream)
        p.write(None, 'hello world')
        self.assertEqual(stream.getvalue(), 'hello world')

    def test_writeln(self):
        stream = StringIO()
        p = printer.StylePrinter(stream)
        p.writeln(None, 'hello world')
        self.assertEqual(stream.getvalue(), 'hello world\n')

    def test_newline(self):
        stream = StringIO()
        p = printer.StylePrinter(stream)
        p.newline()
        self.assertTrue(p._start_newline)
        self.assertEqual(stream.getvalue(), '\n')
        p.nl()
        self.assertTrue(p._start_newline)
        self.assertEqual(stream.getvalue(), '\n\n')

    def test_get_unknown_style(self):
        stream = StringIO()
        p = printer.StylePrinter(stream)
        self.assertEquals(p._get_style(None), printer.default_style)

    @patch.object(printer.StylePrinter, '_get_style', autospec=True,
                  side_effect=printer.StylePrinter._get_style)
    def test_write_unknown_style(self, mock_get_style):
        stream = StringIO()
        p = printer.StylePrinter(stream)
        p.foobarbaz('hello world')
        self.assertEqual(stream.getvalue(), 'hello world')
        mock_get_style.assert_called_once_with(p, 'foobarbaz')


class TestStyles(unittest.TestCase):
    def setUp(self):
        self.stream = StringIO()
        self.stylesheet = {
            'header': {'display': 'block'},
            'tpad': {'padding-top': 3},
            'bpad': {'padding-bottom': 3},
            'prefix': {'before': '<<<'},
            'suffix': {'after': '>>>'},
            'bold': {'bold': True},
            'underline': {'underline': True},
            'italic': {'italic': True},
            'block': {'display': 'block'},
            'start': {'display': 'start'},
            'end': {'display': 'end'},
            'inline': {'display': 'inline'},
            'hidden': {'display': 'hidden'},
            'red': {'color': 'red'},
            'white': {'background': 'white'},
        }
        self.p = printer.StylePrinter(self.stream, self.stylesheet)

    def test_style_lookup(self):
        with patch.object(printer.StylePrinter, '_get_style', autospec=True,
                          side_effect=printer.StylePrinter._get_style) as mock_get_style:
            self.p.foo('foo text')
            mock_get_style.assert_called_once_with(self.p, 'foo')
        with patch.object(printer.StylePrinter, '_get_style', autospec=True,
                          side_effect=printer.StylePrinter._get_style) as mock_get_style:
            self.p.header('header text')
            mock_get_style.assert_called_once_with(self.p, 'header')
        with patch.object(printer.StylePrinter, '_get_style', autospec=True,
                          side_effect=printer.StylePrinter._get_style) as mock_get_style:
            self.p.bold('bold text')
            mock_get_style.assert_called_once_with(self.p, 'bold')
        self.assertEqual(self.stream.getvalue(), 'foo text\nheader text\n\x1b[1mbold text\x1b[0m')

    def test_padding(self):
        self.p.tpad('one').bpad('two')
        self.assertEqual(self.stream.getvalue(), '\n\n\nonetwo\n\n\n')

    def test_before_after(self):
        self.p.prefix('one').suffix('two')
        self.assertEqual(self.stream.getvalue(), '<<<onetwo>>>')

    def test_typeface(self):
        self.p.bold('one').italic('two').underline('three')
        self.assertEqual(self.stream.getvalue(), '\x1b[1mone\x1b[0m\x1b[3mtwo\x1b[0m\x1b[4mthree\x1b[0m')

    def test_display(self):
        self.p.text('-').block('one').start('two').end('three').hidden('four')
        self.assertEqual(self.stream.getvalue(), '-\none\ntwothree\n')

    def test_color(self):
        self.p.red('error').white('inverted')
        self.assertEqual(self.stream.getvalue(), '\x1b[31merror\x1b[0m\x1b[47minverted\x1b[0m')

    def test_nocolor(self):
        self.p.ansimode = False
        self.p.red('one').white('two').bold('three').italic('four')
        self.assertEqual(self.stream.getvalue(), 'onetwothreefour')

    def test_context(self):
        with self.p.bold as p:
            with p.italic as p2:
                p2.header('hello world')
        self.assertEqual(self.stream.getvalue(), '\x1b[1;3mhello world\x1b[0m\n')
