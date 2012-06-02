"""
Logging utilities.
"""

# LATER Right now these are just dumb placeholders.


def warn(msg):
    """
    Log a warning.
    """
    print msg


def verbose(msg, options):
    """
    Log only if verbose mode
    """
    if options and options.get('verbose', False):
        print msg


def error(msg):
    """
    Log an error.
    """
    print msg
