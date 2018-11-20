"""Ansi-enhanced output printer library."""

import sys
from colors import color


default_style = {
    'display': 'inline',
    'padding-top': 0,
    'padding-bottom': 0,
    'before': '',
    'after': '',
    'bold': False,
    'italic': False,
    'underline': False,
}


class StylePrinter(object):
    """Styled printer for generating ANSI decorated text."""

    def __init__(self, stream=None, stylesheet=None, style_defaults=None):
        """Constructs an ansi-capable printer around a stream and stylesheet.

        The optional stream argument defaults to stdout if none is applied.

        The optional stylesheet argument is a dict of style names to
        a dict of style settings.  These settings are forwarded to the
        ansicolor `color` function as kwargs.  Please see the ansicolor
        module for more information.

        The optional style_defaults argument specifies the baseline for all
        styles in use by the printer.

        All public methods return self, such that chained calls are possible.

        This class provides a __getattr__ override that behaves like a proxy for
        write(style_name, ...).  This has a side-effect of allowing almost anything as
        a valid method name. As a result, invalid styles will still proxy to write()
        with no style applied.
        """

        self._start_newline = True
        self.ansimode = True
        self._style_defaults = style_defaults or default_style
        self.stream = stream if stream else sys.stdout
        self.stylesheet = stylesheet or {}

    def _get_style(self, style_name):
        """Gets the style for name, populated with defaults."""
        return dict(self._style_defaults, **self.stylesheet.get(style_name, {}))

    def write(self, style_name, text, *args, **kwargs):
        """Writes formatted text to the configured stream, in a specified style.

        If no args or kwargs are supplied, the `text` argument is applied literally. Otherwise,
        the *args and **kwargs arguments are applied against text using str.format.

        If the indicated style is not in the stylesheet, no style formatting is applied.
        """
        style = self._get_style(style_name)

        # handle display conditions for hidden, block, and start
        display = style['display']
        if display == 'hidden':
            return  # do nothing
        elif display in ['block', 'start'] and not self._start_newline:
            self.stream.write('\n')

        # emit the formatted text with padding and before/after style
        formatted_text = text.format(*args, **kwargs) if args or kwargs else text
        text = ('\n' * style['padding-top']) + style['before'] + formatted_text + \
            style['after'] + ('\n' * style['padding-bottom'])

        # configure ansi formatting
        ansicolor = {}
        if self.ansimode:
            ansi_style = '+'.join([k for k in ['bold', 'underline', 'italic'] if style[k]])
            if ansi_style:
                ansicolor['style'] = ansi_style
            if 'color' in style:
                ansicolor['fg'] = style['color']

        # emit to stream
        if ansicolor:
            self.stream.write(color(text, **ansicolor))
        else:
            self.stream.write(text)

        # handle block condition and newline boolean
        if display in ['block', 'end']:
            self.stream.write('\n')
            self._start_newline = True
        else:
            self._start_newline = text.endswith('\n')
        return self

    def writeln(self, style_name, text, *args, **kwargs):
        """Identical to write(), except a newline is written afterwards."""
        self.write(style_name, text, *args, **kwargs)
        self.newline()
        return self

    def newline(self):
        """Writes a newline to the configured stream."""
        self.stream.write('\n')
        return self

    def nl(self):
        """Writes a newline to the configured stream."""
        self.stream.write('\n')
        return self

    def __getattr__(self, name):
        """Returns write wrapper for the style indicated by the attribute name."""

        def fn(*args, **kwargs):
            return self.write(name, *args, **kwargs)
        return fn
