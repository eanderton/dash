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
}


default_settings = {
    'tasks': {},
    'environment': {},
    'debug': False,
    'sudo': False,
    'prompt': None,
    'intro': 'DCSH started. Type "help" for assitance.',
    'dc_path': 'docker-compose',
}


merge_settings = merge.Merge(merge.left, merge.discard, {
    'tasks': merge.shallow,
    'environment': merge.shallow,
    'debug': merge.override,
    'sudo': merge.override,
    'prompt': merge.override,
    'intro': merge.override,
    'dc_path': merge.override,
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
    'detach': argbuilder.boolean('-d'),
    'name': argbuilder.single('--name'),
    'nodeps': argbuilder.boolean('--no-deps'),
    'remove': argbuilder.boolean('--rm'),
    'disable-tty': argbuilder.boolean('-T'),
    'entrypoint': argbuilder.single('--entrypoint'),
    'privileged': argbuilder.boolean('--privileged'),
    'user': argbuilder.single('--user'),
    'index': argbuilder.single('--index'),
    'service-ports': argbuilder.boolean('--service-ports'),
    'labels': argbuilder.multi('--label', '{k}={v}'),
    'volume': argbuilder.multi('--volume', '{v}'),
    'publish': argbuilder.multi('--publish', '{v}'),
    'environment': argbuilder.multi('-e', '{k}={v}'),
}


# singleton state for all program settings
settings = dict(default_settings)


# singleton state for output printer
printer = StylePrinter(stylesheet=default_stylesheet)
