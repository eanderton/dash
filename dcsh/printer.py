"""Ansi-enhanced output printer library."""

import sys
from colors import color

class StylePrinter(object):
    """Styled printer for generating ANSI decorated text."""
    
    def __init__(self, stream=None, stylesheet=None):
        """Constructs a new stylesheet capable printer around a stream and stylesheet.

        The optional stream argument defaults to stdout if none is applied.
        
        The optional stylesheet argument is a dict of style names to
        a dict of style settings.  These settings are forwarded to the
        ansicolor `color` function as kwargs.  Please see the ansicolor
        module for more information.
        """
        self.stream = stream if stream else sys.stdout
        self.stylesheet = dict(stylesheet) if stylesheet else {}

    def style(self, name, **kwargs):
        """Configures a single style for the printer.

        The kwargs provided are forwarded to the ansicolor `color` function
        on styled formatting calls.  Please see the ansicolor module for more
        information.
        """
        self.stylesheet[name] = kwargs

    def block(self, style=None, indent=None, justify=None):
        pass

    def endblock(self):
        pass

    def write(self, style, text, *args, **kwargs):
        """Writes formatted text to the configured stream, in a specified style.

        If no args or kwargs are supplied, the `text` argument is applied literally. Otherwise,
        the *args and **kwargs arguments are applied against text using str.format.
        
        If the indicated style is not in the stylesheet, no style formatting is applied.
        """
        formatted_text = text.format(*args, **kwargs) if args or kwargs else text
        self.stream.write(color(formatted_text, **self.stylesheet.get(style,{})))
    
    def writeln(self, style, text, *args, **kwargs):
        """Identical to write(), except a newline is written afterwards."""
        self.write(style, text, *args, **kwargs)
        self.newline()

    def newline(self):
        """Writes a newline to the configured stream."""
        self.stream.write('\n')
