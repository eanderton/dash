"""Configuration loading module."""

import os
import sys
import yaml
from colors import color as ansicolor


def merge_settings(dst, src):
    """Merges fields from src to dst, with consideration to the field type."""

    # override fields if present in src
    for k in ['debug', 'sudo', 'prompt']:
        if k in src:
            dst[k] = src[k]

    # shallow merge for dict fields
    for k in ['scripts', 'environment']:
        dst[k].update(src.get(k, {}))


def load_yaml(file_path):
    """Attempts to load and parse a given YAML file path; returns empty dict on failure."""

    try:
        with open(file_path) as f:
            return yaml.load(f.read())
    except:
        pass
    return {}


def load_settings(args):
    settings = {
        'scripts': {},
        'environment': {},
        'services': {},
        'debug': False,
        'sudo': False,
        'prompt': None,
    }

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

    if not settings['prompt']:
        style={}
        if not args.no_color:
            style['fg'] = 'red' if settings['debug'] else 'yellow'
        prompt = '(dcsh debug mode)' if settings['debug'] else '(dcsh)'
        settings['prompt'] = ansicolor(prompt, **style)

    settings['prompt'] = settings['prompt'] + os.environ.get('PS1', '')
    return settings


def get_rc_script(settings):
    """Generates an rc script suitable for configuring a subshell."""
    
    dcsh_cmd = os.path.abspath(sys.argv[0])
    compose_cmd = 'docker-compose'

    # build stock commands
    if settings['debug']:
        dcsh_cmd += ' --debug'
    if settings['sudo']:
        dcsh_cmd += ' --sudo'
        compose_cmd = 'sudo ' + compose_cmd

    # compose the core script
    init_script = [
        'if [ -f /etc/bash.bashrc ]; then source /etc/bash.bashrc; fi',
        'if [ -f $HOME/.bashrc ]; then source $HOME/.bashrc; fi',
        'PS1="{}"'.format(settings['prompt']),
        'alias help="{} help"'.format(dcsh_cmd),
        'alias dc="{}"'.format(compose_cmd),
        'alias build="dc build"',
        'alias up="dc up"',
        'alias down="dc down"',
    ]
    if settings['debug']:
        init_script = ['set -x'] + init_script + ['set +x']

    # build run aliases from docker compose services, and add custom scripts
    for service in settings['services'].keys():
        init_script.append('alias {0}="dc run --rm {0}"'.format(service)) 
    for name, func in settings['scripts'].items():
        init_script.append('function {} {{\n{}\n}}'.format(name, func))
    
    return init_script
