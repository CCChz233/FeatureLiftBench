#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="${PYTHONPATH:-$ROOT/harness}"
PYTHON="${PYTHON:-$ROOT/.venv/bin/python}"
exec "$PYTHON" -B -m featureliftbench.cli run "$@"
