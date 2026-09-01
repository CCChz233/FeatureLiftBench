#!/usr/bin/env bash
# Run the frozen Python-200-prime paper suite (Python-150 + promoted Hard-50).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

usage() {
  cat >&2 <<'EOF'
Usage:
  run_python200_prime_paper.sh <openhands-profile> [run-id] [options]

Options:
  --execute             Execute paid model calls; otherwise print a validated plan.
  --resume DIR          Resume an existing suite output directory.
  --workers N           Parallel task workers (default: 1).
  --timeout SEC         Per-task wall timeout (default: 3600).
  --agent-image IMAGE   Frozen Agent image.
  --eval-image IMAGE    Frozen evaluator image.
  --freeze FILE         Final Python-200-prime freeze manifest.
EOF
}

if [[ $# -lt 1 ]]; then
  usage
  exit 2
fi

PROFILE="$1"
shift

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
SUITE="$ROOT/benchmark/selection/python200_hard_suite.json"
TASK_ROOT="$ROOT/benchmark/python200_hard_tasks"
SOURCE_REGISTRY="$ROOT/benchmark/sources/python200_hard_registry.json"
DEFAULT_CANDIDATE_ID="769f2486c0abb9f0df6324f74b8313da6e1711febce1208c945a2511bd3a7c18"
DEFAULT_IMAGE_SUFFIX="${DEFAULT_CANDIDATE_ID:0:8}"
AGENT_IMAGE="featureliftbench-agent:python200-prime-$DEFAULT_IMAGE_SUFFIX"
EVAL_IMAGE="featureliftbench-eval:python200-prime-$DEFAULT_IMAGE_SUFFIX"
FREEZE="$ROOT/artifacts/research_analysis/python200_prime/current_benchmark_freeze.json"
WORKERS="${NUM_WORKERS:-1}"
TIMEOUT="${TIMEOUT_SECONDS:-3600}"
EXECUTE=0
RESUME_DIR=""
RUN_ID=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --execute) EXECUTE=1; shift ;;
    --resume) RESUME_DIR="${2:?--resume requires a directory}"; shift 2 ;;
    --workers) WORKERS="${2:?--workers requires a value}"; shift 2 ;;
    --timeout) TIMEOUT="${2:?--timeout requires a value}"; shift 2 ;;
    --agent-image) AGENT_IMAGE="${2:?--agent-image requires a value}"; shift 2 ;;
    --eval-image) EVAL_IMAGE="${2:?--eval-image requires a value}"; shift 2 ;;
    --freeze) FREEZE="${2:?--freeze requires a file}"; shift 2 ;;
    -*) echo "Unknown option: $1" >&2; usage; exit 2 ;;
    *)
      [[ -z "$RUN_ID" ]] || { echo "Only one run-id is allowed." >&2; exit 2; }
      RUN_ID="$1"; shift ;;
  esac
done

[[ "$WORKERS" =~ ^[1-9][0-9]*$ ]] || { echo "--workers must be positive" >&2; exit 2; }
[[ "$TIMEOUT" =~ ^[1-9][0-9]*$ ]] || { echo "--timeout must be positive" >&2; exit 2; }
[[ -f "$AGENT_CONFIG" ]] || { echo "Missing $AGENT_CONFIG" >&2; exit 2; }
[[ -f "$FREEZE" ]] || { echo "Missing final freeze: $FREEZE" >&2; exit 2; }
if [[ -n "$RESUME_DIR" && -n "$RUN_ID" ]]; then
  echo "Do not combine a run-id with --resume." >&2
  exit 2
fi

PROFILE_INFO="$(
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
    raise SystemExit(f"Python-200-prime cannot expose public tests: {name}")
if bool(profile.get("expose_source_hints", False)):
    raise SystemExit(f"Python-200-prime cannot expose source hints: {name}")
if str(profile.get("prompt_style", "standard")).lower() != "standard":
    raise SystemExit(f"Python-200-prime requires prompt_style=standard: {name}")
if str(profile.get("source_context", "full_repository")).lower() != "full_repository":
    raise SystemExit(f"Python-200-prime requires source_context=full_repository: {name}")
method_flags = [
    "td_cognition",
    "exec_contract",
    "self_contract",
    "test_first_lift",
    "contract_closure_gate",
    "contract_closure_gate_lite",
    "contract_closure_gate_lite_v1",
    "contract_closure_gate_lite_rescue",
    "contract_closure_gate_lite_rescue_plus",
    "contract_closure_gate_v3",
    "contract_closure_budget_control",
    "adaptive_budget_v2",
    "pre_submit_contract_audit",
    "spec_adversarial_self_test",
]
enabled = [key for key in method_flags if bool(profile.get(key, False))]
if enabled:
    raise SystemExit(f"Main-table runner refuses method flags: {enabled}")
model = str(profile.get("model", "")).strip()
command = str(profile.get("openhands_command", "")).strip()
if not model or not command:
    raise SystemExit(f"Profile is missing model or openhands_command: {name}")
print(f"{model}\tmain")
PY
)"
MODEL="${PROFILE_INFO%%$'\t'*}"
MODEL_SLUG="$(printf '%s' "$MODEL" | tr '[:upper:]' '[:lower:]' | sed 's#^openai/##; s#^deepseek/##; s#[^a-z0-9._-]#-#g')"
if [[ -z "$RUN_ID" ]]; then
  RUN_ID="python200-prime-${MODEL_SLUG}-$(date +%Y%m%d-%H%M%S)"
fi
if [[ -n "$RESUME_DIR" ]]; then
  OUTPUT_DIR="$(cd "$(dirname "$RESUME_DIR")" && pwd)/$(basename "$RESUME_DIR")"
else
  OUTPUT_DIR="$ROOT/experiments/python/openhands/$MODEL_SLUG/$RUN_ID"
fi

export FEATURELIFTBENCH_SOURCE_REGISTRY="$SOURCE_REGISTRY"
export FEATURELIFTBENCH_MOUNT_PUBLIC_TESTS=0
export FEATURELIFTBENCH_PROMPT_STYLE=standard
export FEATURELIFTBENCH_EXPOSE_SOURCE_HINTS=0
export FEATURELIFTBENCH_SOURCE_CONTEXT=full_repository
export FEATURELIFTBENCH_OPENHANDS_MAX_STEPS="${FEATURELIFTBENCH_OPENHANDS_MAX_STEPS:-120}"

"$PYTHON" scripts/build_python200_prime_final_freeze.py --check \
  --output "$FREEZE" --agent-image "$AGENT_IMAGE" --evaluator-image "$EVAL_IMAGE"

TASK_IDS=()
while IFS= read -r task_id; do
  TASK_IDS+=("$task_id")
done < <(
  SUITE_PATH="$SUITE" "$PYTHON" - <<'PY'
import json
import os
from pathlib import Path

suite = json.loads(Path(os.environ["SUITE_PATH"]).read_text(encoding="utf-8"))
for task_id in suite["task_ids"]:
    print(task_id)
PY
)
[[ "${#TASK_IDS[@]}" -eq 200 ]] || {
  echo "Expected 200 tasks, found ${#TASK_IDS[@]}" >&2
  exit 1
}

PYTHONPATH="$ROOT/harness${PYTHONPATH:+:$PYTHONPATH}" \
  SUITE_PATH="$SUITE" TASK_ROOT_PATH="$TASK_ROOT" FREEZE_PATH="$FREEZE" \
  "$PYTHON" - <<'PY'
import json
import os
from pathlib import Path
from featureliftbench.validate import validate_runnable_task

suite = json.loads(Path(os.environ["SUITE_PATH"]).read_text(encoding="utf-8"))
freeze = json.loads(Path(os.environ["FREEZE_PATH"]).read_text(encoding="utf-8"))
root = Path(os.environ["TASK_ROOT_PATH"])
task_ids = suite.get("task_ids") or []
if suite.get("task_root") != "benchmark/python200_hard_tasks":
    raise SystemExit("Python-200-prime suite points to the wrong task root")
if len(task_ids) != 200 or len(set(task_ids)) != 200:
    raise SystemExit("Python-200-prime suite must contain 200 unique tasks")
if set(task_ids) != set(freeze.get("tasks") or {}):
    raise SystemExit("suite membership differs from final freeze")
failures = []
for task_id in task_ids:
    result = validate_runnable_task(root / task_id)
    if not result.valid:
        failures.append(f"{task_id}: {'; '.join(result.errors)}")
if failures:
    raise SystemExit("Python-200-prime compliance failed:\n" + "\n".join(failures))
print(f"Compliance preflight: {len(task_ids)}/200 runnable; freeze={freeze['freeze_id']}")
PY

TASK_ARGS=()
for task_id in "${TASK_IDS[@]}"; do TASK_ARGS+=(--task-id "$task_id"); done
COMMAND=(
  "$PYTHON" -B -m featureliftbench.cli run-agent "$TASK_ROOT"
  --agent openhands-agent
  --agent-config "$AGENT_CONFIG"
  --agent-profile "$PROFILE"
  --agent-command "openhands --headless --override-with-envs --exit-without-confirmation -f {prompt_file} --json"
  --no-agent-public-tests
  --no-agent-source-hints
  --prompt-style standard
  --source-context full_repository
  --env-file "$ROOT/.env"
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

FREEZE_ID="$(FREEZE_PATH="$FREEZE" "$PYTHON" - <<'PY'
import json
import os
from pathlib import Path
print(json.loads(Path(os.environ["FREEZE_PATH"]).read_text())["freeze_id"])
PY
)"
echo "Release: Python-200-prime"
echo "Freeze: $FREEZE_ID"
echo "Profile: $PROFILE"
echo "Model: $MODEL"
echo "Method arm: main"
echo "Information condition: Full-Repository / No-Hint (benchmark tests hidden)"
echo "Selected: 200 tasks (Python-150 + promoted Hard-50)"
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

mkdir -p "$OUTPUT_DIR"
FREEZE_PATH="$FREEZE" OUTPUT_PATH="$OUTPUT_DIR/run_manifest.json" \
  PROFILE_NAME="$PROFILE" MODEL_NAME="$MODEL" AGENT_IMAGE_NAME="$AGENT_IMAGE" \
  EVAL_IMAGE_NAME="$EVAL_IMAGE" SUITE_PATH="$SUITE" "$PYTHON" - <<'PY'
import json
import os
from datetime import UTC, datetime
from pathlib import Path

freeze_path = Path(os.environ["FREEZE_PATH"])
freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
suite = json.loads(Path(os.environ["SUITE_PATH"]).read_text(encoding="utf-8"))
payload = {
    "schema_version": "featureliftbench.python200_prime_model_run.v1",
    "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
    "release": "Python-200-prime",
    "freeze_id": freeze["freeze_id"],
    "candidate_id": freeze["candidate_id"],
    "task_set_sha256": freeze["task_set_sha256"],
    "task_count": len(suite["task_ids"]),
    "profile": os.environ["PROFILE_NAME"],
    "model": os.environ["MODEL_NAME"],
    "method_arm": "main",
    "agent_image": os.environ["AGENT_IMAGE_NAME"],
    "evaluator_image": os.environ["EVAL_IMAGE_NAME"],
    "information_condition": "full_repository_no_hint_tests_hidden",
    "max_task_attempts": 1,
}
Path(os.environ["OUTPUT_PATH"]).write_text(
    json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)
PY

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
