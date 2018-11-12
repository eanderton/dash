"""Module for running docker-compose related commands."""

import re
import subprocess
from .settings import settings
from .settings import printer

dc_cmd_expr = re.compile(r'\s*(\w+)\s*(.+)$')


def get_docker_compose_commands():
    """Scrapes docker-compose help output to get command names and help text."""

    commands = {}
    sh = subprocess.Popen(settings['dc_path'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    _, text = sh.communicate()

    lines = text.splitlines()
    for ii in range(len(lines)):
        if lines[ii] == 'Commands:':
            break
    for jj in range(ii + 1, len(lines)):
        result = dc_cmd_expr.match(lines[jj])
        if result:
            commands[result.group(1)] = result.group(2)
    return commands


def run_compose(*args):
    """Runs docker-compose with the specified args."""

    cmd = ['docker-compose'] + list(args)
    if settings['sudo']:
        cmd = ['sudo'] + cmd
    if settings['debug']:
        printer.writeln('debug', 'Running: {}', cmd)
    sh = subprocess.Popen(' '.join(cmd), shell=True)
    sh.communicate()
