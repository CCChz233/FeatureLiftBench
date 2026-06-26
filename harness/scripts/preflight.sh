#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

if [[ -n "${PYTHON:-}" ]]; then
  :
elif [[ -x "$ROOT/.venv/bin/python" ]]; then
  PYTHON="$ROOT/.venv/bin/python"
elif command -v python3.12 >/dev/null 2>&1; then
  PYTHON=python3.12
else
  PYTHON=python3
fi

export PYTHONPATH="${PYTHONPATH:-$ROOT/harness}"
export PATH="$ROOT/.venv/bin:${PATH}"

exec "$PYTHON" "$ROOT/harness/scripts/preflight.py" --bootstrap "$@"
