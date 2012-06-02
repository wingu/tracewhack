#!/usr/bin/env python

"""
Main driver script for tracewhack.
"""

import json
from optparse import OptionParser
import sys
from textwrap import dedent

from tracewhack import whacker


def _extract_options(optparse_options):
    """
    Get the options from optparse into our globally recognized format.
    """
    return {'verbose': optparse_options.verbose,
            'refresh': optparse_options.refresh}


def main():
    """
    Main driver routine.
    """

    usage = dedent("""
                   Searches bug databases for tracebacks similar to a
                   target traceback.

                   Invoke as: %prog [options] config_file
                   """).strip()
    parser = OptionParser(usage=usage)
    parser.add_option("-f", "--file", dest="traceback_fname",
                      help=dedent("""File containing the target traceback.
                                     (Defaults to stdin)."""))
    parser.add_option("-r", "--refresh", dest="refresh",
                      default='partial',
                      help=dedent("""
                                  How to refresh the bug cache.  Valid
                                  options are: 'partial' (default):
                                  pull changes since last run; 'full'
                                  (expensive): do a full refresh from
                                  the bug repos; 'none': just use
                                  cache.
                                  """).strip())
    parser.add_option("-v", "--verbose", dest="verbose",
                      default=False, action="store_true",
                      help="Print a lot of extra information.")

    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.error("You must supply a config file.")
    legal_refresh = ['partial', 'full', 'none']
    if options.refresh not in legal_refresh:
        parser.error("refresh param must be one of %s" % legal_refresh)

    config_fname = args[0]
    config = None

    with open(config_fname, 'rb') as config_file:
        config = json.loads(config_file.read())

    traceback_txt = None

    if options.traceback_fname:
        with open(options.traceback_fname, 'rb') as traceback_file:
            traceback_txt = traceback_file.read()
    else:
        traceback_txt = sys.stdin.read()

    whacker.whack(traceback_txt=traceback_txt,
                  config=config,
                  options=_extract_options(options))


if __name__ == '__main__':
    main()
