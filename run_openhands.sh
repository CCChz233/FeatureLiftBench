#!/usr/bin/env bash
# Thin wrapper around featureliftbench run (see flb.local.toml.example).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

echo "Note: run_openhands.sh is deprecated; prefer: featureliftbench run" >&2

export PYTHONPATH="${PYTHONPATH:-$ROOT/harness}"

if [[ -n "${PYTHON:-}" ]]; then
  :
elif [[ -x "$ROOT/.venv/bin/python" ]]; then
  PYTHON="$ROOT/.venv/bin/python"
elif command -v python3.12 >/dev/null 2>&1; then
  PYTHON=python3.12
else
  PYTHON=python3
fi

SUITE="${FLB_SUITE:-sanity}"
OUTPUT_ARGS=()
RESUME_ARGS=()

if [[ $# -ge 1 && "${1:-}" != "" ]]; then
  case "$1" in
    benchmark/sanity) SUITE=sanity ;;
    benchmark/tasks) SUITE=main ;;
    *)
      echo "Unsupported task root: $1; set [run].suite in flb.local.toml or use FLB_SUITE" >&2
      exit 2
      ;;
  esac
fi

if [[ $# -ge 2 && "${2:-}" != "" ]]; then
  OUTPUT_ARGS=(--output "$2")
elif [[ -n "${RESUME_DIR:-}" ]]; then
  RESUME_ARGS=(resume "${RESUME_DIR}")
fi

if [[ ${#RESUME_ARGS[@]} -gt 0 ]]; then
  exec "$PYTHON" -B -m featureliftbench.cli "${RESUME_ARGS[@]}"
fi

exec "$PYTHON" -B -m featureliftbench.cli run --suite "$SUITE" "${OUTPUT_ARGS[@]}"
