"""Interactive shell implementation"""

import os
import cmd
import stat
import sys
import functools
import shlex
from .printer import printer_fmt
from .show import do_help
from .show import do_show
from .settings import settings as global_settings
from .settings import printer
from .compose import run_compose


class ShellExit(Exception):
    """Used to signal a clean exit from the shell."""
    pass


class DcShell(cmd.Cmd):
    def __init__(self, settings=None, stdin=None):
        settings = settings or global_settings
        self.debug = settings['debug']

        # do not display any prompts on redirect/pipe mode
        mode = os.fstat(sys.stdin.fileno()).st_mode
        if stat.S_ISFIFO(mode) or stat.S_ISREG(mode):
            self.intro = ''
            self.prompt = ''
        else:
            self.intro = settings['intro']

            # prompt text varies based on debug mode
            if self.debug:
                prompt_text = settings['debug_prompt']
                style = settings['debug_prompt_style']
            else:
                prompt_text = settings['prompt']
                style = settings['prompt_style']
            ss = settings['stylesheet']
            self.prompt = printer_fmt(ss, style, prompt_text) + ' '

        # create cmd.Cmd compatible proxy methods for commands
        for name, help_text in settings['dc_commands'].items():
            fn = functools.partial(self._run_command, name)
            setattr(self, 'do_' + name, fn)
            setattr(fn, '__doc__', help_text)
        for name, task in settings['tasks'].items():
            fn = functools.partial(self._run_task, task)
            setattr(self, 'do_' + name, fn)
            if task['help']:
                setattr(fn, '__doc__', task['help'])

        cmd.Cmd.__init__(self, stdin=stdin)  # , stdout=printer.stream)

    def _run_command(self, name, cmdargs):
        """Runs a specified docker-compose command with optional args."""
        run_compose(name, *shlex.split(cmdargs))

    def _run_task(self, task, cmdargs):
        """Runs a specified task definition with optional args."""
        run_compose(*(task['compiled_args'] + shlex.split(cmdargs)))

    def get_names(self):
        """Cmd override to provide sane name support for cmd.Cmd."""
        return dir(self)

    def emptyline(self):
        """Cmd override that does nothing on empty input."""
        pass

    def do_exit(self, cmdargs):
        """Ends the shell session."""
        if not self.debug:
            printer.text('Exiting DCSH').newline()
        raise ShellExit()

    def do_dc(self, cmdargs):
        """Passthrough to docker-compose."""
        run_compose(*shlex.split(cmdargs))

    def do_show(self, cmdargs):
        """Shows current configuration."""
        do_show()

    def do_help(self, cmdargs):
        """Shows help text."""
        do_help()

    def do_build(self, cmdargs):
        """Builds all services or specified services."""
        run_compose('build', *shlex.split(cmdargs))

    def do_EOF(self, cmdargs):
        """Undocumented command shim to allow cmd.Cmd to function on a pipe."""
        return True

    def cmdloop(self, intro=None):
        """Cmd override that handles CTRL+C gracefully."""
        intro_text = intro or self.intro
        if intro_text:
            printer.intro(intro_text)
        while True:
            try:
                cmd.Cmd.cmdloop(self, intro='')  # start loop but suppress intro
            except KeyboardInterrupt:
                printer.text('KeyboardInterrupt').newline()
            except ShellExit:
                break
