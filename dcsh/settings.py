"""Module for program settings and defaults."""

import merge
import argbuilder
from .printer import StylePrinter


default_stylesheet = {
    'text': {},
    'intro': {'display': 'block', 'color': 'green'},
    'title': {'display': 'block', 'color': 'white', 'bold': True, 'underline': True},
    'heading': {'display': 'start', 'padding-top': 1, 'color': 'white', 'bold': True},
    'subheading': {'display': 'start', 'before': '  ', 'after': ' ', 'color': 'yellow'},
    'on': {'color': 'green'},
    'off': {'color': 'red'},
    'error': {'color': 'red'},
    'debug': {'color': 'blue', 'italic': True},
    'prompt': {'color': 'yellow'},
    'debug_prompt': {'color': 'red'},
}


default_settings = {
    'tasks': {},
    'environment': {},
    'debug': False,
    'sudo': False,
    'prompt': '(dcsh)$',
    'debug_prompt': '(dcsh debug mode)$',
    'prompt_style': 'prompt',
    'debug_prompt_style': 'debug_prompt',
    'intro': 'DCSH started. Type "help" for assitance.',
    'dc_path': 'docker-compose',
    'stylesheet': default_stylesheet,
}


merge_settings = merge.Merge(merge.left, merge.discard, {
    'tasks': merge.shallow,
    'environment': merge.shallow,
    'debug': merge.override,
    'sudo': merge.override,
    'prompt': merge.override,
    'debug_prompt': merge.override,
    'prompt_style': merge.override,
    'debug_prompt_style': merge.override,
    'intro': merge.override,
    'dc_path': merge.override,
    'stylesheet': merge.override,
})

run_defaults = {
    'detach': False,
    'name': None,
    'user': None,
    'remove': True,
    'nodeps': False,
    'service-ports': False,
    'disable-tty': False,
    'labels': {},
    'publish': [],
    'volumes': [],
    'environment': {},
    'help': None,
    'service': None,
    'args': [],
}


exec_defaults = {
    'detach': False,
    'privileged': None,
    'user': None,
    'disable-tty': None,
    'index': None,
    'environment': {},
    'help': None,
    'service': None,
    'args': [],
}

merge_task = merge.Merge(merge.left, merge.override)

task_arg_map = {
    'detach': argbuilder.arg('-d'),
    'name': argbuilder.arg('--name {v}'),
    'nodeps': argbuilder.arg('--no-deps'),
    'remove': argbuilder.arg('--rm'),
    'disable-tty': argbuilder.arg('-T'),
    'entrypoint': argbuilder.arg('--entrypoint {v}'),
    'privileged': argbuilder.arg('--privileged'),
    'user': argbuilder.arg('--user {v}'),
    'index': argbuilder.arg('--index {v}'),
    'service-ports': argbuilder.arg('--service-ports'),
    'labels': argbuilder.multi_arg('--label', '{k}={v}'),
    'volume': argbuilder.multi_arg('--volume', '{v}'),
    'publish': argbuilder.multi_arg('--publish', '{v}'),
    'environment': argbuilder.multi_arg('-e', '{k}={v}'),
}


# singleton state for all program settings
settings = dict(default_settings)


# singleton state for output printer
printer = StylePrinter()
