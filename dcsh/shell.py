"""Interactive shell implementation"""

import cmd
import functools
import shlex
import subprocess
from .config import get_docker_compose_commands
from .show import do_help
from .show import do_show


class ShellExit(Exception):
    """Used to signal a clean exit from the shell."""
    pass


class DcShell(cmd.Cmd):
    def __init__(self, printer, settings):
        self.printer = printer
        self.settings = settings
        self.prompt = settings['prompt'] + ' '
        self.intro = settings['intro']
        
        for name, help_text in get_docker_compose_commands().items():
            fn = functools.partial(self._run_command, name)
            setattr(self, 'do_' + name, fn)
            setattr(fn, '__doc__', help_text)
        
        for name, task in settings['tasks'].items():
            fn = functools.partial(self._run_task, task)
            setattr(self, 'do_' + name, fn)
            if task['help']:
                setattr(fn, '__doc__', task['help'])
        
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
   
    def _run_command(self, name, cmdargs):
        """Runs a specified docker-compose command with optional args."""
        self._run_compose(name, *shlex.split(cmdargs))

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

    def do_dc(self, cmdargs):
        """Passthrough to docker-compose."""
        self._run_compose(*shlex.split(cmdargs))

    def do_show(self, cmdargs):
        """Shows current configuration."""
        do_show(self.printer, self.settings)

    def do_help(self, cmdargs):
        """Shows help text."""
        do_help(self.printer, self.settings)

    def do_build(self, cmdargs):
        """Builds all services or specified services."""
        self._run_compose('build', *shlex.split(cmdargs))

    def cmdloop(self, intro=None):
        """Cmd override that handles CTRL+C gracefully."""
        self.printer.writeln('intro', intro or self.intro)
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
