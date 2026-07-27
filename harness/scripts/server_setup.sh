#!/usr/bin/env bash
# Bootstrap FeatureLiftBench on a fresh clone (local or Linux server).
#
# Usage:
#   ./setup.sh
#   # edit .env with API keys if preflight warns
#   ./harness/scripts/run_python150_paper.sh <openhands-profile>
#
# Optional env:
#   PYTHON=python3.12  VENV_DIR=.venv  SKIP_MINI=1  MINI_BIN=/path/to/mini
#   INSTALL_OPENHANDS=1  # only needed for non-Docker local OpenHands runs
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

PY_VER="$("$PYTHON" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"

_venv_module_hint() {
  cat >&2 <<EOF

ERROR: $PYTHON ($PY_VER) cannot import the venv module.
Debian/Ubuntu minimal images ship python3.12 without venv — install the OS package first:

  sudo apt update
  sudo apt install -y python${PY_VER}-venv python${PY_VER}-pip

Other distros (examples):
  Fedora/RHEL:  sudo dnf install python${PY_VER}-venv
  Arch:         sudo pacman -S python

Then re-run: ./setup.sh
EOF
}

if ! "$PYTHON" -c "import venv" 2>/dev/null; then
  _venv_module_hint
  exit 1
fi

VENV_DIR="${VENV_DIR:-$ROOT/.venv}"
if [[ ! -d "$VENV_DIR" ]]; then
  echo "Creating venv: $VENV_DIR"
  if ! "$PYTHON" -m venv "$VENV_DIR" 2>/dev/null; then
    echo "ERROR: failed to create venv at $VENV_DIR" >&2
    _venv_module_hint
    exit 1
  fi
fi
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
python -m pip install -U pip wheel

echo "Installing harness dependencies..."
python -m pip install pytest==7.4.4 rich

if [[ "${SKIP_MINI:-0}" != "1" ]]; then
  echo "Installing optional mini-swe-agent..."
  python -m pip install mini-swe-agent
fi

PY_MINOR="$("$PYTHON" -c 'import sys; print(sys.version_info.minor)')"
if [[ "${INSTALL_OPENHANDS:-0}" == "1" && "$PY_MINOR" -ge 12 ]]; then
  echo "Installing openhands CLI via uv (Python 3.12+)..."
  python -m pip install "uv>=0.11.6"
  uv tool install "openhands==${OPENHANDS_VERSION:-1.16.0}" --python "$PYTHON" --force
elif [[ "${INSTALL_OPENHANDS:-0}" == "1" ]]; then
  echo "WARNING: INSTALL_OPENHANDS=1 requires Python 3.12+; skipping openhands install." >&2
fi

export PYTHONPATH="$ROOT/harness"
export PATH="$VENV_DIR/bin:$PATH"
if [[ "${SKIP_MINI:-0}" == "1" ]]; then
  echo "Skipping host mini-swe-agent; formal OpenHands runs use the agent Docker image."
  python "$ROOT/harness/scripts/preflight.py" \
    --bootstrap \
    --agent openhands-agent \
    --agent-profile openhands_deepseek_v4_flash || true
else
  if [[ -n "${MINI_BIN:-}" ]]; then
    MINI="$MINI_BIN"
  elif [[ -x "$VENV_DIR/bin/mini" ]]; then
    MINI="$VENV_DIR/bin/mini"
  else
    MINI="$(command -v mini || true)"
  fi
  if [[ -z "$MINI" || ! -x "$MINI" ]]; then
    echo "ERROR: mini CLI not found. pip install mini-swe-agent in $VENV_DIR or set MINI_BIN." >&2
    exit 1
  fi
  echo "Using mini: $MINI"
  python "$ROOT/harness/scripts/preflight.py" --bootstrap --mini-bin "$MINI" || true
fi

if [[ ! -f "$ROOT/.env" ]]; then
  echo "Created .env from example — add API keys before executing a benchmark run"
fi

python -m pytest harness/tests/ -q --tb=no 2>/dev/null | tail -3 || true

cat <<EOF

Setup complete.

Canonical compliant Python-150 plan (no API call):

  ./harness/scripts/run_python150_paper.sh openhands_deepseek_v4_flash

Build the OpenHands agent and evaluator images before execution:

  FEATURELIFTBENCH_AGENT_PYTHON_BASE=python:3.12-slim \\
  FEATURELIFTBENCH_INSTALL_OPENHANDS=1 \\
    docker/build_agent_image.sh featureliftbench-agent:latest
  docker/build_eval_image.sh featureliftbench-eval:latest

Full server runbook:

  docs/SERVER_RUNBOOK_V2_PYTHON150.md

EOF
