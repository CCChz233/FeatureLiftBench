#!/usr/bin/env bash
# Run (or plan) the canonical Full-Repository / No-Hint Python-150 Main suite.
#
# Invariants:
# - OpenHands with an explicitly selected model profile
# - all 150 tasks from verified canonical complete source snapshots
# - Main arm (no source-location hints; benchmark evaluator tests hidden)
# - agent Docker + eval Docker
# - one agent attempt per task (Pass@1; rate-limit retries are infra retries)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

usage() {
  cat >&2 <<'EOF'
Usage:
  run_python150_paper.sh <openhands-profile> [run-id] [options]

Options:
  --execute             Run the 150 external model tasks. Without this flag,
                        validate and print the plan without calling an API.
  --resume DIR          Resume the same suite output directory.
  --workers N           Parallel task workers (default: 1).
  --timeout SEC         Per-task agent wall timeout (default: 3600).
  --agent-image IMAGE   Agent image (default: featureliftbench-agent:latest).
  --eval-image IMAGE    Eval image (default: featureliftbench-eval:latest).

Common profiles:
  openhands_deepseek_v4_flash
  openhands_qwen3_6_27b_fp8_paper
  openhands_qwen3_6_35b_a3b_fp8_paper
  openhands_qwen3_coder_30b_paper
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
  if [[ -n "${PYTHON:-}" ]]; then
    if command -v "$PYTHON" >/dev/null 2>&1; then
      candidate="$(command -v "$PYTHON")"
    else
      candidate="$PYTHON"
    fi
    if [[ -x "$candidate" ]] && "$candidate" -c \
      'import sys, tomllib; assert sys.version_info >= (3, 11)' 2>/dev/null; then
      printf '%s\n' "$candidate"
      return 0
    fi
    echo "PYTHON must point to Python 3.11+ with tomllib: $PYTHON" >&2
    return 1
  fi
  for candidate in \
    "$ROOT/.venv/bin/python" \
    "$(command -v python3.12 2>/dev/null || true)" \
    "$(command -v python3 2>/dev/null || true)" \
    "$(command -v python 2>/dev/null || true)"
  do
    if [[ -n "$candidate" && -x "$candidate" ]] && "$candidate" -c \
      'import sys, tomllib; assert sys.version_info >= (3, 11)' 2>/dev/null; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done
  echo "No Python 3.11+ interpreter found; set PYTHON=/path/to/python3.12." >&2
  return 1
}
PYTHON="$(resolve_python)"
AGENT_CONFIG="$ROOT/harness/config/agents.toml"
if [[ ! -f "$AGENT_CONFIG" ]]; then
  echo "Missing $AGENT_CONFIG; run ./setup.sh first." >&2
  exit 2
fi

MODEL="$(
  PROFILE_NAME="$PROFILE" AGENT_CONFIG="$AGENT_CONFIG" "$PYTHON" - <<'PY'
import os
import tomllib
from pathlib import Path

data = tomllib.loads(Path(os.environ["AGENT_CONFIG"]).read_text(encoding="utf-8"))
profile_name = os.environ["PROFILE_NAME"]
profile = (data.get("profiles") or {}).get(profile_name)
if not isinstance(profile, dict):
    raise SystemExit(f"Unknown profile in agents.toml: {profile_name}")
model = str(profile.get("model", "")).strip()
command = str(profile.get("openhands_command", "")).strip()
if not model:
    raise SystemExit(f"Profile has no model: {profile_name}")
if not command:
    raise SystemExit(f"Profile is not configured for OpenHands: {profile_name}")
if bool(profile.get("mount_public_tests", False)):
    raise SystemExit(f"Main profile exposes benchmark public tests: {profile_name}")
if bool(profile.get("expose_source_hints", False)):
    raise SystemExit(f"Main profile exposes source hints: {profile_name}")
if str(profile.get("prompt_style", "standard")).strip().lower() != "standard":
    raise SystemExit(f"Main profile must use prompt_style=standard: {profile_name}")
if str(profile.get("source_context", "full_repository")).strip().lower() != "full_repository":
    raise SystemExit(f"Main profile must use source_context=full_repository: {profile_name}")
print(model)
PY
)"
MODEL_SLUG="$(
  printf '%s' "$MODEL" \
    | tr '[:upper:]' '[:lower:]' \
    | sed 's#^openai/##; s#^deepseek/##; s#[^a-z0-9._-]#-#g'
)"

RUN_ID="python150-${MODEL_SLUG}-$(date +%Y%m%d-%H%M%S)"
EXECUTE=0
RESUME_DIR=""
WORKERS="${NUM_WORKERS:-1}"
TIMEOUT="${TIMEOUT_SECONDS:-3600}"
AGENT_IMAGE="${FEATURELIFTBENCH_AGENT_DOCKER_IMAGE:-featureliftbench-agent:latest}"
EVAL_IMAGE="${FEATURELIFTBENCH_EVAL_DOCKER_IMAGE:-featureliftbench-eval:latest}"
OPENHANDS_COMMAND="openhands --headless --override-with-envs --exit-without-confirmation -f {prompt_file} --json"
RUN_ID_SET=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --execute)
      EXECUTE=1
      shift
      ;;
    --resume)
      if [[ $# -lt 2 ]]; then
        echo "--resume requires a directory." >&2
        exit 2
      fi
      RESUME_DIR="$2"
      shift 2
      ;;
    --workers)
      if [[ $# -lt 2 ]]; then
        echo "--workers requires a positive integer." >&2
        exit 2
      fi
      WORKERS="$2"
      shift 2
      ;;
    --timeout)
      if [[ $# -lt 2 ]]; then
        echo "--timeout requires a positive integer." >&2
        exit 2
      fi
      TIMEOUT="$2"
      shift 2
      ;;
    --agent-image)
      if [[ $# -lt 2 ]]; then
        echo "--agent-image requires an image name." >&2
        exit 2
      fi
      AGENT_IMAGE="$2"
      shift 2
      ;;
    --eval-image)
      if [[ $# -lt 2 ]]; then
        echo "--eval-image requires an image name." >&2
        exit 2
      fi
      EVAL_IMAGE="$2"
      shift 2
      ;;
    -*)
      echo "Unknown option: $1" >&2
      usage
      exit 2
      ;;
    *)
      if [[ "$RUN_ID_SET" -eq 1 ]]; then
        echo "Only one positional run-id is allowed." >&2
        usage
        exit 2
      fi
      RUN_ID="$1"
      RUN_ID_SET=1
      shift
      ;;
  esac
done

if [[ ! "$WORKERS" =~ ^[1-9][0-9]*$ ]]; then
  echo "--workers must be a positive integer, got: $WORKERS" >&2
  exit 2
fi
if [[ ! "$TIMEOUT" =~ ^[1-9][0-9]*$ ]]; then
  echo "--timeout must be a positive integer, got: $TIMEOUT" >&2
  exit 2
fi
if [[ -n "$RESUME_DIR" && "$RUN_ID_SET" -eq 1 ]]; then
  echo "Do not pass a run-id with --resume; the resume directory is the run identity." >&2
  exit 2
fi

SELECTOR="$ROOT/.agents/skills/featureliftbench-run-eval/scripts/select_featurelift_tasks.py"
TASK_IDS=()
while IFS= read -r task_id; do
  TASK_IDS+=("$task_id")
done < <("$PYTHON" "$SELECTOR" --suite main --format ids)
if [[ "${#TASK_IDS[@]}" -ne 150 ]]; then
  echo "Expected Python-150 main suite, selected ${#TASK_IDS[@]} tasks" >&2
  exit 1
fi

PYTHONPATH="$ROOT/harness${PYTHONPATH:+:$PYTHONPATH}" \
  "$PYTHON" -B - <<'PY'
import json
from pathlib import Path

from featureliftbench.validate import validate_runnable_task

root = Path("benchmark/tasks")
task_dirs = sorted(
    path for path in root.iterdir() if (path / "metadata.json").is_file()
)
if len(task_dirs) != 150:
    raise SystemExit(f"Expected 150 main tasks, found {len(task_dirs)}")
failures = []
for task_dir in task_dirs:
    metadata = json.loads((task_dir / "metadata.json").read_text(encoding="utf-8"))
    if metadata.get("spec_status") != "compliant":
        failures.append(f"{task_dir.name}: spec_status={metadata.get('spec_status')!r}")
        continue
    result = validate_runnable_task(task_dir)
    if not result.valid:
        failures.append(f"{task_dir.name}: {'; '.join(result.errors)}")
if failures:
    raise SystemExit("Python-150 compliance preflight failed:\n" + "\n".join(failures))
print("Compliance preflight: 150/150 compliant and valid")
PY

"$PYTHON" -B scripts/materialize_full_sources.py --check
"$PYTHON" -B scripts/build_v3_benchmark_freeze.py --check
"$PYTHON" -B scripts/audit_v3_main_readiness.py --strict --check

if [[ -n "$RESUME_DIR" ]]; then
  OUTPUT_DIR="$(cd "$(dirname "$RESUME_DIR")" && pwd)/$(basename "$RESUME_DIR")"
else
  OUTPUT_DIR="$ROOT/experiments/python/openhands/$MODEL_SLUG/$RUN_ID"
fi
TASK_ARGS=()
for task_id in "${TASK_IDS[@]}"; do
  TASK_ARGS+=(--task-id "$task_id")
done

COMMAND=(
  "$PYTHON" -B -m featureliftbench.cli run-agent benchmark/tasks
  --agent openhands-agent
  --agent-config harness/config/agents.toml
  --agent-profile "$PROFILE"
  --agent-command "$OPENHANDS_COMMAND"
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
  --agent-docker
  --agent-docker-image "$AGENT_IMAGE"
  --eval-docker
  --eval-docker-image "$EVAL_IMAGE"
  --output "$OUTPUT_DIR"
)
if [[ -n "$RESUME_DIR" ]]; then
  COMMAND+=(--resume "$OUTPUT_DIR")
fi
COMMAND+=("${TASK_ARGS[@]}")

echo "Profile: $PROFILE"
echo "Model: $MODEL"
echo "Arm: Full-Repository / No-Hint Main (benchmark evaluator tests hidden)"
echo "Selected: ${#TASK_IDS[@]} main tasks (Python-150)"
echo "Pass metric: Pass@1 (one agent attempt per task)"
echo "Release status: v3 hardened benchmark freeze passed; empirical difficulty labels are reported post hoc"
echo "Workers: $WORKERS"
echo "Timeout: $TIMEOUT seconds/task"
echo "Agent image: $AGENT_IMAGE"
echo "Eval image: $EVAL_IMAGE"
echo "Output: $OUTPUT_DIR"
printf 'Command:'
printf ' %q' "${COMMAND[@]}"
printf '\n'

if [[ "$EXECUTE" -ne 1 ]]; then
  echo "Plan only. Re-run with --execute after approving API/data transmission and cost."
  exit 0
fi

export FEATURELIFTBENCH_MOUNT_PUBLIC_TESTS=0
export FEATURELIFTBENCH_PROMPT_STYLE=standard
export FEATURELIFTBENCH_EXPOSE_SOURCE_HINTS=0
export FEATURELIFTBENCH_SOURCE_CONTEXT=full_repository
export FEATURELIFTBENCH_OPENHANDS_MAX_STEPS="${FEATURELIFTBENCH_OPENHANDS_MAX_STEPS:-120}"

PYTHONPATH="$ROOT/harness${PYTHONPATH:+:$PYTHONPATH}" \
  "$PYTHON" harness/scripts/preflight.py \
    --agent openhands-agent \
    --agent-profile "$PROFILE" \
    --agent-docker-image "$AGENT_IMAGE" \
    --eval-docker-image "$EVAL_IMAGE" \
    --docker-suite \
    --output-dir "$OUTPUT_DIR" \
    --strict

set +e
PYTHONPATH="$ROOT/harness${PYTHONPATH:+:$PYTHONPATH}" "${COMMAND[@]}"
RUN_STATUS=$?
set -e

if [[ -f "$OUTPUT_DIR/suite.json" ]]; then
  PYTHONPATH="$ROOT/harness${PYTHONPATH:+:$PYTHONPATH}" \
    "$PYTHON" harness/scripts/analyze_benchmark_suite.py "$OUTPUT_DIR"
  PYTHONPATH="$ROOT/harness${PYTHONPATH:+:$PYTHONPATH}" \
    "$PYTHON" harness/scripts/report_entanglement_coverage.py \
      --suite-dir "$OUTPUT_DIR"
fi

if [[ "$RUN_STATUS" -ge 2 ]]; then
  echo "Suite infrastructure failed (exit $RUN_STATUS)." >&2
elif [[ "$RUN_STATUS" -eq 1 ]]; then
  echo "Suite completed with benchmark failures; analysis was generated." >&2
fi
exit "$RUN_STATUS"
