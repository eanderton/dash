#!/usr/bin/env python

from __future__ import print_function
import os
import subprocess
import yaml
import sys
import tempfile
import argparse
from .printer import StylePrinter
from .config import load_settings
from .config import load_settings, get_rc_script
from .help_command import do_help


def do_subshell(printer, args):
    """Launches a subshell, according to the current configuration.

    A subshell is started with a custom prefix, and is configured with functions
    as provided by the configuration.  

    Duplicate nested subshells are explicitly disallowed.
    """
    
    if os.environ.get('__dcsh__', None):
        printer.writeln('error', 'DCSH already started; use "reload" to refresh environment. Exiting.')
        sys.exit(1) 

    # run the subshell
    settings = load_settings(args)
    with tempfile.NamedTemporaryFile() as init_file:
        init_file.write('\n'.join(get_rc_script(settings)))
        init_file.flush()
        env = dict(os.environ)
        env.update(settings['environment'])
        env['__dcsh__'] = 'true'
        shell = os.environ.get('SHELL', os.environ.get('DCSH_SHELL', '/bin/bash'))
        sh = subprocess.Popen([shell, '--init-file', init_file.name, '-i'], env=env)
        sh.communicate()
        sys.exit(sh.returncode)


def do_show_script(printer, args):
    """Renders the init script without ANSI formatting."""
    printer.writeln(None, '\n'.join(get_rc_script(load_settings(args))))


def main():
    """Entry point for CLI.

    Argument parsing, I/O configuration, and subcommmand dispatch are conducted here.
    """

    # set default subcommand for argparse by providing arguments
    if len(sys.argv) == 1:
        sys.argv.append('launch')
    
    # configure parser 
    parser = argparse.ArgumentParser('Shell wrapper for docker-compose')
    parser.add_argument('--no-color', action='store_true', help='turns off ANSI colors')
    parser.add_argument('-s', '--sudo', action='store_true', help='run docker-compose using sudo')
    parser.add_argument('-d', '--debug', action='store_true', help='enable debug output')
    parser.set_defaults(no_color=False, sudo=False, debug=False)
    commands = parser.add_subparsers(title='subcommands')
 
    launch = commands.add_parser('launch', help='launches configured subshell (default)')
    launch.set_defaults(fn=do_subshell)
 
    init_script = commands.add_parser('show-script', help='outputs the rendered shell init script')
    init_script.set_defaults(fn=do_show_script)

    show_help = commands.add_parser('help', help='shows information about configuration')
    show_help.set_defaults(fn=do_help)

    args = parser.parse_args()
    
    # configure printer and run command
    printer = StylePrinter()
    if not args.no_color:
        printer.style('text')
        printer.style('title', fg='white', style='bold+underline')
        printer.style('heading', fg='white', style='bold')
        printer.style('subheading', fg='yellow')
        printer.style('on', fg='green')
        printer.style('off', fg='red')
        printer.style('error', fg='red')
    args.fn(printer, args)


if __name__ == '__main__':
    main()
