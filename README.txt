# tracewhack: probabilistically match a python traceback to a known
  bug.

## Motivation

You are on call / handling bug triage for the week, when suddenly an
exception email comes in, complete with traceback.  There are, let's
say, 15 open bugs.  Is the exception an instance of one of them?  Or
is it a new bug?  Time to start clicking through the bug tracker and
looking at the pasted tracebacks in the comments...

With even a few open bugs it's a pain to track this down.  It becomes
almost impossible when you factor in closed bugs as well.

tracewhack fuzzily matches up the traceback in your email to the
tracebacks in your bug tracker, and helps you figure out quicker if an
exception represents a new or known bug.

## Limitations

Currently only works with python tracebacks and GitHub issues.  It
would be relatively easy to add stacktrace support for more languages
and bug db support for more bug trackers.  See "Contributing" below!

## Installation

Requirements are detailed in requirements.txt.

Tested with python 2.6 and 2.7.

## Running

You will need:

1. A configuration file (see "Configuration")

2. A file with the traceback you are trying to match against known
bugs.

Run "tw.py -h" for usage and options.

## Configuration

Check out the config.example.json file for a template.

## Contributing

Pull requests gladly accepted for bug fixes, feature ideas, and extra
language / bug db support.

A clean run of lint.sh will ensure any pull requests meet the style
guidelines.

## Bugs

Please report them through github.
