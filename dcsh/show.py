"""Help subcommand module."""

from .config import get_rc_script

def get_script_comments(script):
    """Parses out comments from a script block.

    Returns the first set of '#' prefixed lines from `script`, if available.

    If no such comments are at the start of `script`, the first line is
    returned instead.
    """

    script_lines = script.split('\n')
    comment = []
    for line in script_lines:
        if line.startswith('#'):
            comment.append(line.replace('#', '', 1).strip())
        else:
            break
    if len(comment) == 0:
        comment = script_lines[:1]
    return comment


def do_show_help(printer, settings):
    """Renders user-friendly help describing the current configuration."""

    printer.writeln('title', 'DCSH Configuration')
    printer.newline()
    printer.writeln('heading', 'Flags')

    printer.write('subheading', '  Debug mode: ')
    if settings['debug']:
        printer.writeln('on', 'Enabled')
    else:
        printer.writeln('off', 'Disabled')

    printer.write('subheading', '  Sudo mode: ')
    if settings['sudo']:
        printer.writeln('on', 'Enabled - Calls to `dc` will use `sudo`.')
    else:
        printer.writeln('off', 'Disabled')
    
    if settings['scripts']:
        printer.newline()
        printer.writeln('heading', 'Scripts')
        for name, value in settings['scripts'].items():
            if settings['debug']:
                comment = value.split('\n')
            else:
                comment = get_script_comments(value)
            printer.write('subheading', '  {}: ', name)
            printer.writeln('text', '\n    '.join(comment))
    else:
        printer.writeln(None, 'No scripts are configured.')

    if settings['environment']:
        printer.newline()
        printer.writeln('heading', 'Environment')
        for name, value in settings['environment'].items():
            printer.write('subheading', '  {}: ', name)
            printer.writeln('text', value)
    else:
        printer.writeln(None, 'No environment are configured.')


def do_show_script(printer, settings):
    """Renders the init script without ANSI formatting."""
    printer.writeln(None, '\n'.join(get_rc_script(settings)))


