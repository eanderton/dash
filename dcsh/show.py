"""Help subcommand module."""

from .settings import settings
from .settings import printer


def do_show():
    """Renders user-friendly help describing the current configuration."""
    printer.title('DCSH Configuration')

    printer.heading('Settings')
    printer.subheading('dc_path:').text(settings['dc_path'])
    printer.subheading('Debug mode:')
    if settings['debug']:
        printer.on('Enabled')
    else:
        printer.off('Disabled')

    printer.subheading('Sudo mode:')
    if settings['sudo']:
        printer.on('Enabled - All docker-compose commands will use "sudo".')
    else:
        printer.off('Disabled')

    printer.heading('Task environment')
    if settings['environment']:
        for name, value in settings['environment'].items():
            printer.subheading('{}:', name).text(value)
    else:
        printer.newline().text('No task environment vars are configured.')
    printer.newline()


def do_help():
    """Renders user-friendly help describing commands and user-defined tasks."""
    printer.title('DCSH Shell Commands')

    printer.heading('Docker-compose commands')
    for name, helptext in settings['dc_commands'].items():
        printer.subheading('{}:', name).text(helptext)

    printer.heading('Built-in DCSH commands')
    printer.subheading('help:').text('This help screen')
    printer.subheading('show:').text('Displays DCSH configuration details')
    printer.subheading('exit:').text('Exits the shell')
    printer.subheading('dc:').text('Runs docker-compose')

    if settings['tasks']:
        printer.heading('User defined tasks')
        for name, value in settings['tasks'].items():
            if value['help']:
                printer.subheading('{}:', name).text(value['help'])
            else:
                printer.subheading(name)
    else:
        printer.text('No tasks are configured.')
    printer.newline()
