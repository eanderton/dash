#!/usr/bin/env python

import os
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

    # parse args and clean up flags
    args = parser.parse_args()
    if os.fstat(0) != os.fstat(1):
        args.no_color = True  # turn off ansi color on redirect

    # load+validate settings, and run command
    try:
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
