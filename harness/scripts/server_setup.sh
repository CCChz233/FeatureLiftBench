#!/usr/bin/env bash
# Bootstrap FeatureLiftBench on a Linux server for long agent suites.
#
# Usage (on server, after git clone):
#   ./harness/scripts/server_setup.sh
#   cp .env.example .env   # fill API keys
#   ./run.sh
#
# Optional env:
#   PYTHON=python3.12  VENV_DIR=.venv  SKIP_MINI=1
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

PYTHON="${PYTHON:-}"
if [[ -z "$PYTHON" ]]; then
  if command -v python3.12 >/dev/null 2>&1; then
    PYTHON=python3.12
  elif command -v python3 >/dev/null 2>&1; then
    PYTHON=python3
  else
    echo "Need Python 3.11+ (python3.12 preferred)." >&2
    exit 1
  fi
fi

"$PYTHON" - <<'PY' || { echo "Python 3.11+ required (tomllib)." >&2; exit 1; }
import sys
assert sys.version_info >= (3, 11)
PY

VENV_DIR="${VENV_DIR:-$ROOT/.venv}"
if [[ ! -d "$VENV_DIR" ]]; then
  echo "Creating venv: $VENV_DIR"
  "$PYTHON" -m venv "$VENV_DIR"
fi
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
python -m pip install -U pip wheel

echo "Installing harness test deps + mini-swe-agent..."
python -m pip install pytest==7.4.4 rich

if [[ "${SKIP_MINI:-0}" != "1" ]]; then
  python -m pip install mini-swe-agent
fi

MINI_BIN="${MINI_BIN:-$(command -v mini || true)}"
if [[ -z "$MINI_BIN" ]]; then
  echo "Warning: 'mini' not on PATH. Install mini-swe-agent or set MINI_BIN." >&2
  MINI_BIN="/usr/local/bin/mini"
fi

AGENTS_TOML="$ROOT/harness/config/agents.toml"
if [[ ! -f "$AGENTS_TOML" ]]; then
  cp "$ROOT/harness/config/agents.example.toml" "$AGENTS_TOML"
fi

# Patch agent_bin in agents.toml (idempotent enough for fresh copy).
"$PYTHON" - <<PY
from pathlib import Path
import re

path = Path("$AGENTS_TOML")
text = path.read_text(encoding="utf-8")
mini = "$MINI_BIN"
if "agent_bin" in text:
    text = re.sub(
        r'^agent_bin\s*=\s*".*"$',
        f'agent_bin = "{mini}"',
        text,
        flags=re.MULTILINE,
    )
else:
    text = text.replace(
        "# agent_bin = ",
        f'agent_bin = "{mini}"\n# agent_bin = ",
        1,
    )
path.write_text(text, encoding="utf-8")
print(f"Updated agent_bin -> {mini}")
PY

if [[ ! -f "$ROOT/.env" ]]; then
  cp "$ROOT/.env.example" "$ROOT/.env"
  echo "Created .env from .env.example — add API keys before running suites."
fi

export PYTHONPATH="$ROOT/harness"
python -m pytest harness/tests/ -q --tb=no -q 2>/dev/null | tail -3 || true

cat <<EOF

Setup complete.

  source $VENV_DIR/bin/activate
  export PYTHONPATH=$ROOT/harness
  # edit .env with API keys
  ./run.sh

Long runs (recommended):
  tmux new -s flb
  ./run.sh
  # Ctrl-B D to detach

Resume after interrupt:
  ./run.sh   # or add --skip-completed experiments/mini-swe-agent/<previous-run>

EOF
