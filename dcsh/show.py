"""Help subcommand module."""

from .config import get_docker_compose_commands


def do_show(printer, settings):
    """Renders user-friendly help describing the current configuration."""

    printer.nl().title('DCSH Configuration').nl()
    printer.heading('Flags').nl()

    printer.subheading('  Debug mode: ')
    if settings['debug']:
        printer.on('Enabled').nl()
    else:
        printer.off('Disabled').nl()

    printer.subheading('  Sudo mode: ')
    if settings['sudo']:
        printer.on('Enabled - Calls to `dc` will use `sudo`.').nl()
    else:
        printer.off('Disabled').nl()

    if settings['environment']:
        printer.nl()
        printer.heading('Task environment').nl()
        for name, value in settings['environment'].items():
            printer.subheading('  {}: ', name)
            printer.text(value).nl()
    else:
        printer.text('No task environment vars are configured.').nl()
    printer.nl()


def do_help(printer, settings):
    """Renders user-friendly help describing commands and user-defined tasks."""

    printer.nl().title('DCSH Shell Commands').nl()
   
    printer.nl().heading('Basic DCSH commands').nl()
    printer.subheading('  help: ').text('This help screen').nl()
    printer.subheading('  show: ').text('Displays DCSH configuration details').nl()
    printer.subheading('  exit: ').text('Exits the shell').nl()
    printer.subheading('  dc: ').text('Runs docker-compose').nl()

    if settings['tasks']:
        printer.nl().heading('User defined tasks').nl()
        for name, value in settings['tasks'].items():
            printer.subheading('  {}', name)
            if value['help']:
                printer.text(': {}', value['help']).nl()
            else:
                printer.nl()
    else:
        printer.text('No tasks are configured.').nl()
    printer.nl()
    
    printer.heading('Docker-compose commands')
    for name, helptext in get_docker_compose_commands().items():
        printer.subheading('  {}', name).text(': {}', helptext).nl()
    printer.nl()
