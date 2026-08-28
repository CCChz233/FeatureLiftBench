#!/usr/bin/env bash
# Install pinned DeepSeek Harness and Codex CLIs (OpenHands-level bootstrap).
# Does not merge scores into Official Main.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

usage() {
  cat >&2 <<'EOF'
Usage:
  pin_runtime_agents.sh [deepseek-harness|codex|all] [--force]
EOF
}

TARGET="all"
FORCE=()
for arg in "$@"; do
  case "$arg" in
    --help|-h) usage; exit 0 ;;
    --force) FORCE=(--force) ;;
    all|deepseek-harness|codex) TARGET="$arg" ;;
    *) usage; exit 2 ;;
  esac
done

PYTHON="${PYTHON:-}"
if [[ -z "$PYTHON" ]]; then
  if [[ -x "$ROOT/.venv/bin/python" ]]; then
    PYTHON="$ROOT/.venv/bin/python"
  else
    PYTHON="$(command -v python3)"
  fi
fi

export PYTHONPATH="$ROOT/harness${PYTHONPATH:+:$PYTHONPATH}"
exec "$PYTHON" -m featureliftbench.runtime_install "$TARGET" "${FORCE[@]}"
