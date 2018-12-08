"""Tests for the dcsh shell module."""

import dcsh.printer as printer
import dcsh.shell as shell
import unittest
from mock import patch
from StringIO import StringIO


class TestDCShell(unittest.TestCase):
    def setUp(self):
        self.settings = {
            'sudo': False,
            'debug': False,
            'prompt': 'foo',
            'prompt_style': 'prompt',
            'debug_prompt': 'debug foo',
            'debug_prompt_style': 'debug_prompt',
            'intro': 'baz',
            'dc_commands': {
                'cmd1': {'help': 'cmd1 help'},
            },
            'tasks': {
                'task1': {
                    'help': 'task1 help',
                    'compiled_args': ['gorf'],
                },
            },
            'dc_path': '/usr/bin/docker-compose',
            'environment': {},
            'stylesheet': {
                'prompt': {'color': 'yellow'},
                'debug_prompt': {'color': 'red'},
            }
        }
        self.stream = StringIO()
        p = printer.StylePrinter(self.stream)
        self._shell_printer = patch('dcsh.shell.printer', p).start()
        self._show_printer = patch('dcsh.show.printer', p).start()


    def tearDown(self):  # noqa: E303
        patch.stopall()

    def test_prompt(self):
        sh = shell.DcShell(self.settings)
        self.assertEquals(sh.prompt, '\x1b[33mfoo\x1b[0m ')
        self.assertEquals(sh.intro, 'baz')

    def test_debug_prompt(self):
        self.settings['debug'] = True
        sh = shell.DcShell(self.settings)
        self.assertEquals(sh.prompt, '\x1b[31mdebug foo\x1b[0m ')
        self.assertEquals(sh.intro, 'baz')

    def test_run_command(self):
        sh = shell.DcShell(self.settings)
        with patch('dcsh.shell.run_compose', return_value=None) as fn:
            self.assertIsNone(sh.onecmd('cmd1 foo bar baz'))
            fn.assert_called_once_with('cmd1', 'foo', 'bar', 'baz')

    def test_run_task(self):
        sh = shell.DcShell(self.settings)
        with patch('dcsh.shell.run_compose', return_value=None) as fn:
            self.assertIsNone(sh.onecmd('task1 foo bar baz'))
            fn.assert_called_once_with('gorf', 'foo', 'bar', 'baz')

    def test_pipe(self):
        with patch('stat.S_ISFIFO', return_value=True):
            sh = shell.DcShell(self.settings)
        self.assertEquals(sh.prompt, '')
        self.assertEquals(sh.intro, '')

    def test_exit(self):
        sh = shell.DcShell(self.settings)
        self.assertRaises(shell.ShellExit, sh.onecmd, 'exit')
        self.assertEqual(self.stream.getvalue(), 'Exiting DCSH\n')

    def test_debug_exit(self):
        self.settings['debug'] = True
        sh = shell.DcShell(self.settings)
        self.assertRaises(shell.ShellExit, sh.onecmd, 'exit')
        self.assertEqual(self.stream.getvalue(), '')

    def test_get_names(self):
        sh = shell.DcShell(self.settings)
        self.assertEqual(sh.get_names(), dir(sh))

    def test_emptyline(self):
        sh = shell.DcShell(self.settings)
        self.assertIsNone(sh.emptyline())

    def test_do_dc(self):
        sh = shell.DcShell(self.settings)
        with patch('dcsh.shell.run_compose', return_value=None) as fn:
            self.assertIsNone(sh.do_dc('foo bar baz'))
            fn.assert_called_once_with('foo', 'bar', 'baz')

    def test_do_show(self):
        sh = shell.DcShell(self.settings)
        with patch('dcsh.shell.do_show') as fn:
            self.assertIsNone(sh.do_show('foo bar baz'))
            fn.assert_called_once_with()

    def test_do_help(self):
        sh = shell.DcShell(self.settings)
        with patch('dcsh.shell.do_help') as fn:
            self.assertIsNone(sh.do_help('foo bar baz'))
            fn.assert_called_once_with()

    def test_do_build(self):
        sh = shell.DcShell(self.settings)
        with patch('dcsh.shell.run_compose', return_value=None) as fn:
            self.assertIsNone(sh.do_build('foo bar baz'))
            fn.assert_called_once_with('build', 'foo', 'bar', 'baz')

    def test_do_EOF(self):
        sh = shell.DcShell(self.settings)
        self.assertTrue(sh.do_EOF(None))

    def test_cmdloop(self):
        sh = shell.DcShell(self.settings)

        def do_ctrl_c(cmdargs):
            raise KeyboardInterrupt()

        sh.do_ctrl_c = do_ctrl_c
        sh.cmdqueue = [
            'ctrl_c',
            'exit'
        ]
        sh.cmdloop()
        self.assertEqual(self.stream.getvalue(),
                         'bazKeyboardInterrupt\n' +
                         'Exiting DCSH\n')
