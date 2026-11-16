#!/bin/sh
# Install or update agentic-dev-kit in a project. Arguments pass through to install.py:
#   install.sh --target ~/code/my-project --stacks rust,go --tools claude,copilot
#   install.sh --target ~/code/my-project --update
DIR="$(cd "$(dirname "$0")" && pwd)"
. "$DIR/../gates/hooks/_find_python.sh"
exec $PY "$DIR/install.py" "$@"
