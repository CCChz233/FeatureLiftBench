#!/usr/bin/env bash
# Run the frozen Python-150 plus the balanced External-50 as one paper suite.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

usage() {
  cat >&2 <<'EOF'
Usage:
  run_python200_paper.sh <openhands-profile> [run-id] [options]

Options:
  --execute             Execute model calls; otherwise print a validated plan.
  --external-only       Run only the balanced External-50 extension.
  --resume DIR          Resume an existing suite output directory.
  --workers N           Parallel task workers (default: 1).
  --timeout SEC         Per-task wall timeout (default: 3600).
  --agent-image IMAGE   Agent image (default: featureliftbench-agent:latest).
  --eval-image IMAGE    Eval image (default: featureliftbench-eval:latest).
EOF
}

if [[ $# -lt 1 ]]; then
  usage
  exit 2
fi

PROFILE="$1"
shift
if [[ "$PROFILE" == "openhands_deepseek_v4_flash_paper" ]]; then
  PROFILE="openhands_deepseek_v4_flash"
fi

resolve_python() {
  local candidate
  for candidate in \
    "${PYTHON:-}" \
    "$ROOT/.venv/bin/python" \
    "$(command -v python3.12 2>/dev/null || true)" \
    "$(command -v python3.11 2>/dev/null || true)" \
    "$(command -v python3 2>/dev/null || true)"
  do
    if [[ -n "$candidate" && -x "$candidate" ]] && "$candidate" -c \
      'import sys, tomllib; assert sys.version_info >= (3, 11)' 2>/dev/null; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done
  echo "Python 3.11+ is required; set PYTHON=/path/to/python." >&2
  return 1
}

PYTHON="$(resolve_python)"
AGENT_CONFIG="$ROOT/harness/config/agents.toml"
if [[ ! -f "$AGENT_CONFIG" ]]; then
  echo "Missing $AGENT_CONFIG; copy agents.example.toml and configure a profile." >&2
  exit 2
fi

MODEL="$(
  PROFILE_NAME="$PROFILE" AGENT_CONFIG="$AGENT_CONFIG" "$PYTHON" - <<'PY'
import os
import tomllib
from pathlib import Path

data = tomllib.loads(Path(os.environ["AGENT_CONFIG"]).read_text(encoding="utf-8"))
name = os.environ["PROFILE_NAME"]
profile = (data.get("profiles") or {}).get(name)
if not isinstance(profile, dict):
    raise SystemExit(f"Unknown profile: {name}")
if bool(profile.get("mount_public_tests", False)):
    raise SystemExit(f"Python-200 Main cannot expose public tests: {name}")
if bool(profile.get("expose_source_hints", False)):
    raise SystemExit(f"Python-200 Main cannot expose source hints: {name}")
if str(profile.get("prompt_style", "standard")).lower() != "standard":
    raise SystemExit(f"Python-200 Main requires prompt_style=standard: {name}")
if str(profile.get("source_context", "full_repository")).lower() != "full_repository":
    raise SystemExit(f"Python-200 Main requires source_context=full_repository: {name}")
model = str(profile.get("model", "")).strip()
command = str(profile.get("openhands_command", "")).strip()
if not model or not command:
    raise SystemExit(f"Profile is missing model or openhands_command: {name}")
print(model)
PY
)"
MODEL_SLUG="$(printf '%s' "$MODEL" | tr '[:upper:]' '[:lower:]' | sed 's#^openai/##; s#^deepseek/##; s#[^a-z0-9._-]#-#g')"

RUN_ID="python200-${MODEL_SLUG}-$(date +%Y%m%d-%H%M%S)"
EXECUTE=0
EXTERNAL_ONLY=0
RESUME_DIR=""
WORKERS="${NUM_WORKERS:-1}"
TIMEOUT="${TIMEOUT_SECONDS:-3600}"
AGENT_IMAGE="${FEATURELIFTBENCH_AGENT_DOCKER_IMAGE:-featureliftbench-agent:latest}"
EVAL_IMAGE="${FEATURELIFTBENCH_EVAL_DOCKER_IMAGE:-featureliftbench-eval:latest}"
RUN_ID_SET=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --execute) EXECUTE=1; shift ;;
    --external-only) EXTERNAL_ONLY=1; shift ;;
    --resume) RESUME_DIR="${2:?--resume requires a directory}"; shift 2 ;;
    --workers) WORKERS="${2:?--workers requires a value}"; shift 2 ;;
    --timeout) TIMEOUT="${2:?--timeout requires a value}"; shift 2 ;;
    --agent-image) AGENT_IMAGE="${2:?--agent-image requires a value}"; shift 2 ;;
    --eval-image) EVAL_IMAGE="${2:?--eval-image requires a value}"; shift 2 ;;
    -*) echo "Unknown option: $1" >&2; usage; exit 2 ;;
    *)
      [[ "$RUN_ID_SET" -eq 0 ]] || { echo "Only one run-id is allowed." >&2; exit 2; }
      RUN_ID="$1"; RUN_ID_SET=1; shift ;;
  esac
done

if [[ "$EXTERNAL_ONLY" -eq 1 && "$RUN_ID_SET" -eq 0 && -z "$RESUME_DIR" ]]; then
  RUN_ID="python200-external50-${MODEL_SLUG}-$(date +%Y%m%d-%H%M%S)"
fi

[[ "$WORKERS" =~ ^[1-9][0-9]*$ ]] || { echo "--workers must be positive" >&2; exit 2; }
[[ "$TIMEOUT" =~ ^[1-9][0-9]*$ ]] || { echo "--timeout must be positive" >&2; exit 2; }
if [[ -n "$RESUME_DIR" && "$RUN_ID_SET" -eq 1 ]]; then
  echo "Do not combine a run-id with --resume." >&2
  exit 2
fi

export FEATURELIFTBENCH_SOURCE_REGISTRY="$ROOT/benchmark/sources/python200_registry.json"
export FEATURELIFTBENCH_MOUNT_PUBLIC_TESTS=0
export FEATURELIFTBENCH_PROMPT_STYLE=standard
export FEATURELIFTBENCH_EXPOSE_SOURCE_HINTS=0
export FEATURELIFTBENCH_SOURCE_CONTEXT=full_repository
export FEATURELIFTBENCH_OPENHANDS_MAX_STEPS="${FEATURELIFTBENCH_OPENHANDS_MAX_STEPS:-120}"

"$PYTHON" -B benchmark/selection/scripts/materialize_python200_release.py --check
"$PYTHON" -B benchmark/selection/scripts/finalize_python200_source_registry.py --check
"$PYTHON" -B benchmark/selection/scripts/finalize_python200_dependencies.py --check
"$PYTHON" -B benchmark/selection/scripts/audit_python200_balance.py --check
"$PYTHON" -B benchmark/selection/scripts/audit_python200_wheels.py --python-version 311
"$PYTHON" -B benchmark/selection/scripts/check_python200_baseline_freeze.py
"$PYTHON" -B scripts/materialize_full_sources.py --check

TASK_IDS=()
while IFS= read -r task_id; do
  TASK_IDS+=("$task_id")
done < <(
  "$PYTHON" - "$EXTERNAL_ONLY" <<'PY'
import json
import sys
from pathlib import Path

payload = json.loads(Path("benchmark/selection/python200_suite.json").read_text())
external_only = sys.argv[1] == "1"
for task_id in payload["task_ids"]:
    if external_only and not (Path("benchmark/external50") / task_id).is_dir():
        continue
    print(task_id)
PY
)
EXPECTED_TASKS=200
SELECTION_LABEL="200 tasks (150 frozen + 50 balanced External)"
if [[ "$EXTERNAL_ONLY" -eq 1 ]]; then
  EXPECTED_TASKS=50
  SELECTION_LABEL="50 tasks (balanced External extension only)"
fi
[[ "${#TASK_IDS[@]}" -eq "$EXPECTED_TASKS" ]] || {
  echo "Expected $EXPECTED_TASKS tasks, found ${#TASK_IDS[@]}" >&2
  exit 1
}

PYTHONPATH="$ROOT/harness${PYTHONPATH:+:$PYTHONPATH}" \
  "$PYTHON" -B - "$EXTERNAL_ONLY" <<'PY'
import json
import sys
from pathlib import Path
from featureliftbench.validate import validate_runnable_task

suite = json.loads(Path("benchmark/selection/python200_suite.json").read_text())
root = Path(suite["task_root"])
external_only = sys.argv[1] == "1"
failures = []
selected = 0
for task_id in suite["task_ids"]:
    if external_only and not (Path("benchmark/external50") / task_id).is_dir():
        continue
    selected += 1
    result = validate_runnable_task(root / task_id)
    if not result.valid:
        failures.append(f"{task_id}: {'; '.join(result.errors)}")
if failures:
    raise SystemExit("Python-200 compliance preflight failed:\n" + "\n".join(failures))
expected = 50 if external_only else 200
if selected != expected:
    raise SystemExit(f"Expected {expected} selected tasks, found {selected}")
label = "External-50" if external_only else "Python-200"
print(f"Compliance preflight: {selected}/{expected} runnable ({label})")
PY

if [[ -n "$RESUME_DIR" ]]; then
  OUTPUT_DIR="$(cd "$(dirname "$RESUME_DIR")" && pwd)/$(basename "$RESUME_DIR")"
else
  OUTPUT_DIR="$ROOT/experiments/python/openhands/$MODEL_SLUG/$RUN_ID"
fi
TASK_ARGS=()
for task_id in "${TASK_IDS[@]}"; do TASK_ARGS+=(--task-id "$task_id"); done

COMMAND=(
  "$PYTHON" -B -m featureliftbench.cli run-agent benchmark/python200_tasks
  --agent openhands-agent
  --agent-config harness/config/agents.toml
  --agent-profile "$PROFILE"
  --agent-command "openhands --headless --override-with-envs --exit-without-confirmation -f {prompt_file} --json"
  --no-agent-public-tests
  --no-agent-source-hints
  --prompt-style standard
  --source-context full_repository
  --env-file .env
  --num-workers "$WORKERS"
  --timeout-seconds "$TIMEOUT"
  --retry-rate-limit 5
  --extra-agent-passes 0
  --max-task-attempts 1
  --agent-docker --agent-docker-image "$AGENT_IMAGE"
  --eval-docker --eval-docker-image "$EVAL_IMAGE"
  --output "$OUTPUT_DIR"
)
[[ -z "$RESUME_DIR" ]] || COMMAND+=(--resume "$OUTPUT_DIR")
COMMAND+=("${TASK_ARGS[@]}")

echo "Profile: $PROFILE"
echo "Model: $MODEL"
echo "Arm: Full-Repository / No-Hint (benchmark tests hidden)"
echo "Selected: $SELECTION_LABEL"
echo "Workers: $WORKERS"
echo "Timeout: $TIMEOUT seconds/task"
echo "Agent image: $AGENT_IMAGE"
echo "Eval image: $EVAL_IMAGE"
echo "Output: $OUTPUT_DIR"
printf 'Command:'; printf ' %q' "${COMMAND[@]}"; printf '\n'

if [[ "$EXECUTE" -ne 1 ]]; then
  echo "Plan only. Re-run with --execute after approving API/data transmission and cost."
  exit 0
fi

PYTHONPATH="$ROOT/harness${PYTHONPATH:+:$PYTHONPATH}" \
  "$PYTHON" harness/scripts/preflight.py \
    --agent openhands-agent --agent-profile "$PROFILE" \
    --agent-docker-image "$AGENT_IMAGE" --eval-docker-image "$EVAL_IMAGE" \
    --docker-suite --output-dir "$OUTPUT_DIR" --strict

set +e
PYTHONPATH="$ROOT/harness${PYTHONPATH:+:$PYTHONPATH}" "${COMMAND[@]}"
RUN_STATUS=$?
set -e

if [[ -f "$OUTPUT_DIR/suite.json" ]]; then
  PYTHONPATH="$ROOT/harness${PYTHONPATH:+:$PYTHONPATH}" \
    "$PYTHON" harness/scripts/analyze_benchmark_suite.py "$OUTPUT_DIR"
  PYTHONPATH="$ROOT/harness${PYTHONPATH:+:$PYTHONPATH}" \
    "$PYTHON" harness/scripts/report_entanglement_coverage.py --suite-dir "$OUTPUT_DIR"
fi
exit "$RUN_STATUS"
