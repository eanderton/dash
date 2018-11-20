#!/usr/bin/env python

import sys
import argparse
from .config import load_settings
from .settings import printer
from .shell import DcShell


def main():
    """Entry point for CLI.

    Argument parsing, I/O configuration, and subcommmand dispatch are conducted here.
    """
    # configure parser
    parser = argparse.ArgumentParser('Shell wrapper for docker-compose')
    parser.add_argument('--no-color', default=False, action='store_true', help='turns off ANSI colors')
    parser.add_argument('-s', '--sudo', default=False, action='store_true', help='run docker-compose using sudo')
    parser.add_argument('-d', '--debug', default=False, action='store_true', help='enable debug output')
    parser.add_argument('-c', '--command', default=None, help='executes a command and exits')

    # parse arguments, load+validate settings, and run command
    try:
        args = parser.parse_args()
        load_settings(**vars(args))
        sh = DcShell()
        if args.command:
            return sh.onecmd(args.command)
        else:
            return sh.cmdloop()
    except Exception as e:
        if args.debug:
            raise
        printer.error('Error: {}', str(e)).newline()
        sys.exit(1)


if __name__ == '__main__':
    main()
