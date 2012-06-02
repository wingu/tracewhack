"""
Facade for internal functions.
"""

import os

from tracewhack.config import TRACEWHACK_DATA_DIR
from tracewhack.bugs import db


def whack(traceback_txt, config, options):
    """
    Extract any traceback from traceback_txt and attempt to match it
    to a bug.
    """
    _ensure_tracewhack_data_dir()
    # shut up, pylint, we're in progress here.
    traceback_txt = traceback_txt

    with db.init(config['profile'],
                 config['bugdbs'],
                 options=options) as bugsdb:
        bugsdb.dump()


def _ensure_tracewhack_data_dir():
    """
    If TRACEWHACK_DATA_DIR doesn't exist, create it, and error out if
    we can't.
    """
    try:
        os.makedirs(TRACEWHACK_DATA_DIR)
    except OSError:
        # if this just happened b/c the directory already existed, no
        # big deal.
        if not os.path.isdir(TRACEWHACK_DATA_DIR):
            raise
