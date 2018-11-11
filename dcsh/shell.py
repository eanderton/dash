"""Interactive shell implementation"""

import cmd
import functools
import shlex
import subprocess
from .show import do_show


class ShellExit(Exception):
    """Used to signal a clean exit from the shell."""
    pass


class DcShell(cmd.Cmd):
    def __init__(self, printer, settings):
        self.printer = printer
        self.settings = settings
        self.prompt = settings['prompt'] + ' '
        self.intro = 'DCSH started.  Type "help" for assistance.'
        for name, task in settings['tasks'].items():
            fn = functools.partial(self._run_task, task)
            setattr(self, 'do_' + name, fn)
            if task['help']:
                setattr(fn, '__doc__', task['help'])

        # TODO: patch in all other docker-compose commands
        cmd.Cmd.__init__(self)

    def _run_compose(self, *args):
        """Runs docker-compose with the specified args."""
        cmd = ['docker-compose'] + list(args)
        if self.settings['sudo']:
            cmd = ['sudo'] + cmd
        if self.settings['debug']:
            self.printer.writeln('debug', 'Running: {}', cmd)
        sh = subprocess.Popen(cmd)
        sh.communicate()
    
    def _run_task(self, task, cmdargs):
        """Runs a specified task definition with optional args."""
        self._run_compose(*(task['compiled_args'] + shlex.split(cmdargs)))

    def get_names(self):
        """Cmd override to provide sane name support for cmd.Cmd."""
        return dir(self)

    def emptyline(self):
        """Cmd override that does nothing on empty input."""
        pass

    def do_exit(self, cmdargs):
        """Ends the shell session."""
        raise ShellExit() 

    # TODO: move to help?
    def do_show(self, cmdargs):
        """Shows current configuration."""
        do_show(self.printer, self.settings)

    def do_build(self, cmdargs):
        """Builds all services or specified services."""
        self._run_compose('build', *shlex.split(cmdargs))

    def cmdloop(self, intro=None):
        """Cmd override that handles CTRL+C gracefully."""
        self.printer.writeln('text', intro or self.intro)
        while True:
            try:
                cmd.Cmd.cmdloop(self, intro='')  # start loop but suppress intro
                break
            except KeyboardInterrupt:
                self.printer.writeln('KeyboardInterrupt')
	    except ShellExit:
                self.printer.writeln('text', 'Exiting DCSH')
                break


def do_shell(printer, settings):
    """Runs a shell with the provided printer and seetings."""
    DcShell(printer, settings).cmdloop()
    return 0
