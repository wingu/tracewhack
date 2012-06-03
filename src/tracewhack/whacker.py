"""
Facade for internal functions.
"""

from collections import defaultdict
import difflib
import os
from textwrap import dedent

from tracewhack import log
from tracewhack.config import TRACEWHACK_DATA_DIR
from tracewhack.bugs import db
from tracewhack.tb import extract_tracebacks


def whack(traceback_txt, config, options):
    """
    Extract any traceback from traceback_txt and attempt to match it
    to a bug.
    """
    _ensure_tracewhack_data_dir()

    tbs = extract_tracebacks(traceback_txt)
    if not tbs:
        err = "Could not extract a traceback"
        log.error(err)
        raise ValueError(err)

    bugs_with_tbs = _bugs_with_tbs(config, options)
    bug_and_scores = _score_bugs(tbs, bugs_with_tbs)
    print "Displaying best matches:"

    for (match_i, (bug, score)) in enumerate(bug_and_scores):
        if match_i >= options['num_results']:
            break
        print _fmt_bug(bug, score)


def _fmt_bug(bug, score):
    """
    Format a bug for display.
    """
    fmted = dedent("""
                   {title}
                   Url: {url}
                   Score: [{score}/1.0]""").format(title=bug['title'],
                                                   url=bug['url'],
                                                   score=score)
    return fmted


def _score_bugs(tbs, bugs_with_tbs):
    """
    Score bugs by how closely their tracebacks match any tracebacks
    we've pulled from the input.  In the case of multiple tbs per
    input / bug, we use the highest score.

    Return the bugs sorted by score.
    """
    bugs_by_id = {}
    score_by_id = defaultdict(lambda: 0.0)

    for (bug, bug_tbs) in bugs_with_tbs:
        bugs_by_id[bug['global_id']] = bug

    for traceback in tbs:
        for (bug, bug_tbs) in bugs_with_tbs:
            for bug_tb in bug_tbs:
                bug_id = bug['global_id']
                score = _score(traceback, bug_tb)
                score_by_id[bug_id] = max(score_by_id[bug_id], score)

    score_and_ids = [(score, bug_id)
                     for (bug_id, score)
                     in score_by_id.items()]
    score_and_ids.sort()
    score_and_ids.reverse()
    return [(bugs_by_id[bug_id], score) for (score, bug_id) in score_and_ids]


def _score(tba, tbb):
    """
    Score how closely the two tracebacks match, returning a score
    between 0.0 and 1.0, lesser meaning a worse match.
    """
    return difflib.SequenceMatcher(a=tba, b=tbb).ratio()


def _bugs_with_tbs(config, options):
    """
    Return (bug, tbs) for only those bugs having tbs.
    """
    bugs_with_tbs = []

    with db.init(config['profile'],
                 config['bugdbs'],
                 options=options) as bugsdb:
        for bug in bugsdb.bugs():
            tbs = extract_tracebacks(bug['text'])
            if tbs:
                bugs_with_tbs.append((bug, tbs))

    return bugs_with_tbs


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
