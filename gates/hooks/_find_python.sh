# Sourced by the hooks and gate.sh. Sets PY to a Python 3.11+ command, or exits 2.
# `python` comes first: on Windows, `python3` may be the Microsoft Store stub.
PY=""
for c in python python3 "py -3"; do
  if $c -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' >/dev/null 2>&1; then
    PY="$c"
    break
  fi
done
if [ -z "$PY" ]; then
  echo "agentic-dev-kit: Python 3.11+ not found on PATH; cannot run the gate." >&2
  exit 2
fi
