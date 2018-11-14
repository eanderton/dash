"""Configuration loading module."""

import os
import yaml
import argbuilder
import shlex
from colors import color as ansicolor
from .compose import get_docker_compose_commands
from .settings import default_stylesheet
from .settings import default_settings
from .settings import merge_settings
from .settings import run_defaults
from .settings import exec_defaults
from .settings import merge_task
from .settings import task_arg_map
from .settings import settings
from .settings import printer


def load_yaml(file_path):
    """Attempts to load and parse a given YAML file path; returns empty dict on failure."""

    if os.path.exists(file_path):
        with open(file_path) as f:
            return yaml.load(f.read())
    return {}


def load_settings(sudo, debug, no_color):
    """Loads settings, merging all available configration sources."""

    data = merge_settings(default_settings, load_yaml('/etc/dcsh.yml'))
    if 'HOME' in os.environ:
        data = merge_settings(data, load_yaml(os.environ['HOME'] + '/.dcsh.yml'))
    data = merge_settings(data, load_yaml('.dcsh.yml'))
    dc_config = load_yaml('./docker-compose.yml')
    data = merge_settings(data, dc_config.get('x-dcsh', {}))

    # TODO: use some schema validation here
    settings.clear()
    settings.update(data)

    if debug:
        settings['debug'] = True
    if sudo:
        settings['sudo'] = True

    # normalize task definitions
    for name, value in settings['tasks'].items():
        if value.setdefault('exec', False):
            taskdef = dict(exec_defaults)
            taskdef['compiled_args'] = ['exec']
        else:
            taskdef = dict(run_defaults)
            taskdef['compiled_args'] = ['run']
        taskdef['environment'] = settings['environment']
        taskdef = merge_task(taskdef, value)
        if isinstance(taskdef['args'], str):
            taskdef['args'] = shlex.split(taskdef['args'])
        taskdef['compiled_args'] += \
            argbuilder.build(task_arg_map, taskdef) + \
            [taskdef['service']] + \
            taskdef['args']
        settings['tasks'][name] = taskdef

    # default prompt depends on debug and no_color settings
    if not settings['prompt']:
        style = {}
        if not no_color:
            style['fg'] = 'red' if settings['debug'] else 'yellow'
        prompt = '(dcsh debug mode)$' if settings['debug'] else '(dcsh)$'
        settings['prompt'] = ansicolor(prompt, **style)

    # supplement config with docker command set
    commands = get_docker_compose_commands()
    if 'help' in commands:
        del commands['help']  # 'help' is already provided elsewhere
    settings['dc_commands'] = commands

    # configure printer and run command
    printer.ansimode = not no_color
