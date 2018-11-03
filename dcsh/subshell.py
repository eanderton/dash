"""Provides support for configuring and launching a subshell."""

import os
import subprocess
import tempfile
from .config import get_rc_script


def do_subshell(printer, settings):
    """Launches a subshell child process, according to the current configuration.

    A subshell is started with a custom prefix, and is configured with functions
    as provided by the configuration.  The return code from the subshell is returned.

    Duplicate nested subshells are explicitly disallowed.
    """
    
    if os.environ.get('__dcsh__', None):
        printer.writeln('error', 'DCSH already started. Exiting.')
        return 1

    # run the subshell
    with tempfile.NamedTemporaryFile() as init_file:
        init_file.write('\n'.join(get_rc_script(settings)))
        init_file.flush()
        env = dict(os.environ)
        env.update(settings['environment'])
        env['__dcsh__'] = 'true'
        shell = os.environ.get('SHELL', os.environ.get('DCSH_SHELL', '/bin/bash'))
        sh = subprocess.Popen([shell, '--init-file', init_file.name, '-i'], env=env)
        sh.communicate()
    return sh.returncode


