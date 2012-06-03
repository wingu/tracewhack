"""
Extract tracebacks.
"""

import re

PY_TRACEBACK_RE = re.compile(
    """.*(Traceback[ ]\(most[ ]recent[ ]call[ ]last\):[ ]*[\n] # traceback line
       ([ ]+[^\n]*[\n])+ # at least one File/code line, start with spaces
       ([^ ]+[^\n]*[\n])? # first error line, if there is one
       ([^\n]+[\n]?)*) # any remaining error lines, to a blank line or eos
    """,
    re.DOTALL | re.MULTILINE | re.VERBOSE)

ALL_RES = [PY_TRACEBACK_RE]


def extract_tracebacks(txt):
    """
    Extract any and all tracebacks from txt.

    We make the simplifying assumption that if there are multiple
    tracebacks, they are separated by at least one blank line.  LATER
    make this smarter.
    """
    txt = _normalize_linebreaks(txt)
    tbs = [extract_traceback(chunk) for chunk in txt.split('\n\n')]
    return [tb for tb in tbs if tb]


def extract_traceback(chunk):
    """
    Attempts to extract a single traceback from a chunk of text,
    returning just the traceback if found, else None.

    Note that if chunk contains multiple tracebacks, this function will
    become violently confused.

    Chunk should have only \n's as line separators, not \r or \r\n.
    """
    for matcher in ALL_RES:
        matched = matcher.match(chunk)
        if matched:
            return matched.group(1)
    return None


def _normalize_linebreaks(txt):
    """
    Make all line breaks \n only.
    """
    return txt.replace('\r\n', '\n').replace('\r', '\n')
