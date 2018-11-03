#!/usr/bin/env python

import sys
import argparse
from .printer import StylePrinter
from .config import load_settings
from .show import do_show_help
from .show import do_show_script
from .subshell import do_subshell


# https://stackoverflow.com/questions/6365601/default-sub-command-or-handling-no-sub-command-with-argparse
def set_default_subparser(self, name, args=None, positional_args=0):
    """default subparser selection. Call after setup, just before parse_args()
    name: is the name of the subparser to call by default
    args: if set is the argument list handed to parse_args()

    , tested with 2.7, 3.2, 3.3, 3.4
    it works with 2.6 assuming argparse is installed
    """
    subparser_found = False
    existing_default = False # check if default parser previously defined
    for arg in sys.argv[1:]:
        if arg in ['-h', '--help']:  # global help if no subparser
            break
    else:
        for x in self._subparsers._actions:
            if not isinstance(x, argparse._SubParsersAction):
                continue
            for sp_name in x._name_parser_map.keys():
                if sp_name in sys.argv[1:]:
                    subparser_found = True
                if sp_name == name: # check existance of default parser
                    existing_default = True
        if not subparser_found:
            # If the default subparser is not among the existing ones,
            # create a new parser.
            # As this is called just before 'parse_args', the default
            # parser created here will not pollute the help output.

            if not existing_default:
                for x in self._subparsers._actions:
                    if not isinstance(x, argparse._SubParsersAction):
                        continue
                    x.add_parser(name)
                    break # this works OK, but should I check further?

            # insert default in last position before global positional
            # arguments, this implies no global options are specified after
            # first positional argument
            if args is None:
                sys.argv.insert(len(sys.argv) - positional_args, name)
            else:
                args.insert(len(args) - positional_args, name)


argparse.ArgumentParser.set_default_subparser = set_default_subparser


def main():
    """Entry point for CLI.

    Argument parsing, I/O configuration, and subcommmand dispatch are conducted here.
    """

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

    parser.set_default_subparser('launch')

    args = parser.parse_args()
    settings = load_settings(args)
    
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
    sys.exit(args.fn(printer, settings))


if __name__ == '__main__':
    main()
