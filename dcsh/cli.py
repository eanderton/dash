#!/usr/bin/env python

import sys
import argparse
from .printer import StylePrinter
from .config import load_settings
from .show import do_show_help
from .show import do_show_script
from .subshell import do_subshell

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
 
    show = commands.add_parser('show', help='outputs details about dcsh config')
    show_subcommands = show.add_subparsers(title='type')

    show_script = show_subcommands.add_parser('script', help='shows the init script')
    show_script.set_defaults(fn=do_show_script)

    show_help = show_subcommands.add_parser('help', help='shows information about configuration')
    show_help.set_defaults(fn=do_show_help)
    
    show_help_cmd = commands.add_parser('help', 
            help='alias for "show help"; shows information about configuration')
    show_help_cmd.set_defaults(fn=do_show_help)

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
    settings = load_settings(args)
    sys.exit(args.fn(printer, settings))


if __name__ == '__main__':
    main()
