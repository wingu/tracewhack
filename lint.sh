#!/bin/sh

set -e

cd src
pep8 .
pylint -r n tw.py tracewhack
