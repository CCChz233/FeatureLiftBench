#!/usr/bin/env bash
# Thin wrapper: featureliftbench run --suite pilot5
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

echo "Note: run_openhands_pilot5.sh is deprecated; prefer: featureliftbench run (suite=pilot5)" >&2

export PYTHONPATH="${PYTHONPATH:-$ROOT/harness}"
PYTHON="${PYTHON:-python3.12}"

OUTPUT_ARGS=()
if [[ -n "${RUN_ID:-}" ]]; then
  OUTPUT_ARGS=(--output "experiments/openhands-agent/${RUN_ID}")
fi

if [[ "${RESUME:-0}" == "1" && -n "${RUN_ID:-}" ]]; then
  exec "$PYTHON" -B -m featureliftbench.cli resume "experiments/openhands-agent/${RUN_ID}"
fi

exec "$PYTHON" -B -m featureliftbench.cli run --suite pilot5 "${OUTPUT_ARGS[@]}"
