#!/usr/bin/env bash
# Run a gold-ready Go task with OpenHands (not mini-swe-agent) + Docker eval.
#
# Prerequisites (WSL):
#   - openhands CLI installed and configured (or LLM_* env vars)
#   - .env with API keys if using --override-with-envs
#   - featureliftbench-eval-go:latest image
#
# Usage:
#   ./harness/scripts/run_go_openhands.sh semver__version_parse_core__001
#   ./harness/scripts/run_go_openhands.sh humanize__bytes_format_core__001 my-run-id
#
# Env:
#   OPENHANDS_BIN=openhands
#   LLM_MODEL=deepseek/deepseek-v4-flash   (passed via --override-with-envs)
#   LLM_API_KEY / LLM_BASE_URL             (from .env or OpenHands settings)
#   MAX_ITERATIONS=120                     (written to temp OpenHands config if set)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH=harness
PY="${PYTHON:-python3}"
if ! command -v "$PY" >/dev/null 2>&1; then
  PY=python
fi

TASK_ID="${1:-}"
RUN_ID="${2:-go-openhands-${TASK_ID}-$(date +%Y%m%d-%H%M%S)}"

if [[ -z "$TASK_ID" ]]; then
  echo "Usage: $0 <task_id> [run_id]" >&2
  echo "Gold-ready now: semver__version_parse_core__001, humanize__bytes_format_core__001, mapstructure__decode_core__001" >&2
  exit 1
fi

TASK_DIR="benchmark/go/tasks/${TASK_ID}"
if [[ ! -d "$TASK_DIR" ]]; then
  echo "ERROR: task not found: $TASK_DIR" >&2
  exit 1
fi

OPENHANDS_BIN="${OPENHANDS_BIN:-openhands}"
MODEL="${LLM_MODEL:-deepseek/deepseek-v4-flash}"
MODEL_SLUG="$("$PY" -c "from featureliftbench.paths import model_experiment_slug; print(model_experiment_slug('${MODEL}'))")"
OUTPUT="experiments/GO/openhands/${MODEL_SLUG}/${RUN_ID}"
PIPELINE_SMOKE="${PIPELINE_SMOKE:-0}"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi
export LLM_MODEL="$MODEL"
export LLM_API_KEY="${LLM_API_KEY:-${FEATURELIFTBENCH_API_KEY:-${DEEPSEEK_API_KEY:-}}}"
export LLM_BASE_URL="${LLM_BASE_URL:-${FEATURELIFTBENCH_API_BASE:-${DEEPSEEK_API_BASE:-}}}"

# OpenHands headless: cwd = agent workspace; task prompt from TASK.md
if [[ "$PIPELINE_SMOKE" == "1" ]]; then
  AGENT_CMD="$PY -B $ROOT/harness/scripts/go_copy_naive_agent.py"
  AGENT_LABEL="pipeline-smoke (naive copy)"
elif command -v "$OPENHANDS_BIN" >/dev/null 2>&1; then
  AGENT_CMD="${OPENHANDS_BIN} --headless --exit-without-confirmation --override-with-envs -f {task_file}"
  AGENT_LABEL="OpenHands headless"
else
  echo "ERROR: ${OPENHANDS_BIN} not found. Install OpenHands or set PIPELINE_SMOKE=1." >&2
  exit 127
fi

EXTRA_ENV=()
if [[ -f .env ]]; then
  EXTRA_ENV+=(--env-file .env)
fi

echo "Task:     $TASK_ID"
echo "Model:    $MODEL (set LLM_MODEL / OpenHands settings)"
echo "Output:   $OUTPUT"
echo "Agent:    $AGENT_LABEL"
echo "Eval:     Docker"

"$PY" -B -m featureliftbench.cli run-agent "$TASK_DIR" \
  --agent command \
  --agent-command "$AGENT_CMD" \
  --output "$OUTPUT" \
  --eval-docker \
  --timeout-seconds "${TIMEOUT_SECONDS:-3600}" \
  "${EXTRA_ENV[@]}"

echo ""
echo "=== Pipeline check ==="
"$PY" - <<PY
import json
from pathlib import Path
run = Path("$OUTPUT/run.json")
if not run.is_file():
    print("MISSING run.json")
    raise SystemExit(1)
data = json.loads(run.read_text())
print("status:", data.get("status"))
agent = data.get("agent", {})
print("agent passed:", agent.get("passed"))
sub = data.get("submission", {})
print("submission exists:", sub.get("exists"))
ev = data.get("evaluation") or {}
result_json = ev.get("result_json")
if result_json and Path(result_json).is_file():
    ev = json.loads(Path(result_json).read_text())
scores = ev.get("scores") or {}
pub = (ev.get("public_tests") or {}).get("passed")
hid = (ev.get("hidden_tests") or {}).get("passed")
print("public:", pub, "hidden:", hid)
print("functional_gate:", scores.get("functional_gate"))
print("extraction_ratio:", scores.get("extraction_ratio"))
print("final_score:", scores.get("final_score"))
print("")
print("Difficulty read:")
if pub and not hid:
    print("  A-tier signal: public pass, hidden fail (good discriminator)")
elif pub and hid and scores.get("extraction_ratio", 1) < 0.45:
    print("  B-tier: compact pass (check if too easy vs oracle)")
elif pub and hid:
    print("  C-tier risk: full pass — hidden may not block; review task hardness")
else:
    print("  Agent/eval failure — fix pipeline before judging difficulty")
PY

echo "Full artifacts: $OUTPUT/"
