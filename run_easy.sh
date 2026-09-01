#!/usr/bin/env bash
set -euo pipefail
echo "DEPRECATED: run_easy.sh is a legacy config runner; use featureliftbench run or ./scripts/run_benchmark.sh." >&2
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="${PYTHONPATH:-$ROOT/harness}"
PYTHON="${PYTHON:-$ROOT/.venv/bin/python}"
exec "$PYTHON" -B -m featureliftbench.cli run "$@"
