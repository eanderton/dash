"""Configuration loading module."""

import os
import sys
import yaml
import functools
import merge
import argbuilder
import shlex
from colors import color as ansicolor


default_settings = {
    'tasks': {},
    'scripts': {},
    'environment': {},
    'debug': False,
    'sudo': False,
    'prompt': None,
}

merge_settings = functools.partial(merge.with_strategy, {
    'tasks': merge.shallow,
    'scripts': merge.shallow,
    'environment': merge.shallow,
    'services': merge.shallow,
    'debug': merge.override,
    'sudo': merge.override,
    'prompt': merge.override,
})

run_defaults = {
    'detach': False,
    'help': None,
    'service': None,
    'remove': True,
    'nodeps': False,
    'disable-tty': False,
    'service-ports': False,
    'labels': {},
    'environment': {},
    'volumes': [],
    'args': [],
}

exec_defaults = {
    'detach': False,
    'help': None,
    'service': None,
    'privileged': None,
    'user': None,
    'disable-tty': None,
    'index': None,
    'environment': {},
    'args': [],
}

task_arg_map = {
    'detach': argbuilder.boolean('-d'),
    'name': argbuilder.single('--name'),
    'nodeps': argbuilder.boolean('--no-deps'),
    'remove': argbuilder.boolean('--rm'),
    'disable-tty': argbuilder.boolean('--disable-tty'),
    'entrypoint': argbuilder.single('--entrypoint'),
    'privileged': argbuilder.boolean('--privileged'),
    'user': argbuilder.single('--user'),
    'index': argbuilder.single('--index'),
    'labels': argbuilder.multi('--label','{k}={v}'),
    'volume': argbuilder.multi('--volume','{v}'),
    'publish': argbuilder.multi('--publish','{v}'),
    'environment': argbuilder.multi('-e','{k}={v}'),
}


def load_yaml(file_path):
    """Attempts to load and parse a given YAML file path; returns empty dict on failure."""

    if os.path.exists(file_path):
        with open(file_path) as f:
            return yaml.load(f.read())
    return {}


def load_settings(args):
    """Loads settings, merging all available configration sources."""

    settings = dict(default_settings)
    merge_settings(settings, load_yaml('/etc/dcsh.yml'))
    if 'HOME' in os.environ:
        merge_settings(settings, load_yaml(os.environ['HOME'] + '/.dcsh.yml'))
    merge_settings(settings, load_yaml('.dcsh.yml'))
    
    dc_config = load_yaml('./docker-compose.yml')
    settings['services'] = dc_config.get('services', {})
    merge_settings(settings, dc_config.get('x-dcsh', {}))
    
    if args.debug:
        settings['debug'] = True
    if args.sudo:
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
        taskdef = merge.left(taskdef, value)
        if isinstance(taskdef['args'], str):
            taskdef['args'] = shlex.split(taskdef['args'])
        taskdef['compiled_args'] += \
                argbuilder.build(task_arg_map, taskdef) + \
                [taskdef['service']] + \
                taskdef['args']
        print '\n'
        print value
        print taskdef['compiled_args']
        settings['tasks'][name] = taskdef

    # default prompt depends on debug and no_color settings
    if not settings['prompt']:
        style={}
        if not args.no_color:
            style['fg'] = 'red' if settings['debug'] else 'yellow'
        prompt = '(dcsh debug mode)$' if settings['debug'] else '(dcsh)$'
        settings['prompt'] = ansicolor(prompt, **style)

    return settings


def validate_settings(settings):
    # TODO: use some schema validation to enforce task.args as str or list
    pass


