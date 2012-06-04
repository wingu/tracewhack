#!/bin/bash

# Driver script if you're using a virtualenv called 'env' and want to
# activate it.

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
pushd $DIR > /dev/null

source env/bin/activate
pushd src > /dev/null

exec ./tw.py $@

popd > /dev/null
popd > /dev/null
