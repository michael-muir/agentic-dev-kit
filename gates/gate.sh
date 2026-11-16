#!/bin/sh
# POSIX wrapper: finds Python 3.11+ and runs gate.py with the same arguments.
DIR="$(cd "$(dirname "$0")" && pwd)"
. "$DIR/hooks/_find_python.sh"
exec $PY "$DIR/gate.py" "$@"
