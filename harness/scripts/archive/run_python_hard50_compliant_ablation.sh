#!/usr/bin/env bash
# Prepare or explicitly execute the paired compliant Hard-50
# test-blind Main/Public-feedback run.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT"

usage() {
  cat >&2 <<'EOF'
Usage:
  harness/scripts/archive/run_python_hard50_compliant_ablation.sh [options]

Options:
  --run-id ID       Stable run directory suffix (default: timestamp).
  --workers N       Number of parallel workers (default: 1).
  --resume          Resume the existing Main and Public-feedback suite directories.
  --execute         Execute instead of printing the plan.
  --approve-external-api-and-cost
                    Required with --execute. Confirms that 100 OpenHands runs
                    may transmit task code/specs externally and incur cost.

The default is plan-only and does not call an external model API.
EOF
}

RUN_ID="hard50-compliant-$(date +%Y%m%d-%H%M%S)"
WORKERS=1
RESUME=0
EXECUTE=0
APPROVED=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --run-id)
      RUN_ID="$2"
      shift 2
      ;;
    --workers)
      WORKERS="$2"
      shift 2
      ;;
    --resume)
      RESUME=1
      shift
      ;;
    --execute)
      EXECUTE=1
      shift
      ;;
    --approve-external-api-and-cost)
      APPROVED=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 2
      ;;
  esac
done

if ! [[ "$WORKERS" =~ ^[1-9][0-9]*$ ]]; then
  echo "--workers must be a positive integer" >&2
  exit 2
fi
if [[ ! "$RUN_ID" =~ ^[A-Za-z0-9._-]+$ ]]; then
  echo "--run-id may contain only letters, digits, dot, underscore, and hyphen" >&2
  exit 2
fi

TASK_FILE="$ROOT/reports/constitution/hard50_compliant_ids_20260724.txt"
if [[ ! -f "$TASK_FILE" ]]; then
  echo "Frozen task list not found: $TASK_FILE" >&2
  exit 1
fi

PYTHON="${PYTHON:-$ROOT/.venv/bin/python}"
if [[ ! -x "$PYTHON" ]]; then
  PYTHON="python3"
fi

TASK_COUNT="$("$PYTHON" - "$ROOT" "$TASK_FILE" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
task_file = Path(sys.argv[2])
task_ids = [
    line.strip()
    for line in task_file.read_text(encoding="utf-8").splitlines()
    if line.strip() and not line.lstrip().startswith("#")
]
if len(task_ids) != 50 or len(set(task_ids)) != 50:
    raise SystemExit(
        f"frozen Hard-50 list must contain 50 unique tasks; found {len(task_ids)}"
    )
for task_id in task_ids:
    metadata_path = root / "benchmark" / "tasks" / task_id / "metadata.json"
    if not metadata_path.is_file():
        raise SystemExit(f"missing task metadata: {metadata_path}")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata.get("status") != "main":
        raise SystemExit(f"{task_id}: expected metadata.status=main")
    if metadata.get("spec_status") != "compliant":
        raise SystemExit(f"{task_id}: expected metadata.spec_status=compliant")
print(len(task_ids))
PY
)"

OUTPUT="$ROOT/experiments/methods/ablation/$RUN_ID"
MAIN_COMMAND=(
  "$ROOT/scripts/run_experiment.sh"
  --arm main
  --task-file "$TASK_FILE"
  --workers "$WORKERS"
  --output "$OUTPUT/main"
)
PUBLIC_FEEDBACK_COMMAND=(
  "$ROOT/scripts/run_experiment.sh"
  --arm public_feedback
  --task-file "$TASK_FILE"
  --workers "$WORKERS"
  --output "$OUTPUT/public_feedback"
)
if [[ "$RESUME" -eq 1 ]]; then
  # Preserve every genuine completed Pass@1 outcome, including model failures.
  # Interrupted placeholders are normalized to `not_evaluated` before resume.
  MAIN_COMMAND+=(
    --resume "$OUTPUT/main"
    --retry-only-status not_evaluated
  )
  PUBLIC_FEEDBACK_COMMAND+=(
    --resume "$OUTPUT/public_feedback"
    --retry-only-status not_evaluated
  )
fi

echo "Frozen tasks: $TASK_COUNT compliant Hard-50 tasks"
echo "Arms: main,public_feedback (100 OpenHands runs total)"
echo "Model profile: deepseek/deepseek-v4-flash"
echo "Output: $OUTPUT"
printf 'Main command:'
printf ' %q' "${MAIN_COMMAND[@]}"
printf '\n'
printf 'Public-feedback command:'
printf ' %q' "${PUBLIC_FEEDBACK_COMMAND[@]}"
printf '\n'

if [[ "$EXECUTE" -ne 1 ]]; then
  echo "Plan only. No external API call was made."
  exit 0
fi
if [[ "$APPROVED" -ne 1 ]]; then
  echo "--execute requires --approve-external-api-and-cost" >&2
  exit 2
fi

"${MAIN_COMMAND[@]}"
"${PUBLIC_FEEDBACK_COMMAND[@]}"

for arm in main public_feedback; do
  suite_dir="$OUTPUT/$arm"
  if [[ -f "$suite_dir/suite.json" ]]; then
    PYTHONPATH="$ROOT/harness${PYTHONPATH:+:$PYTHONPATH}" \
      "$PYTHON" "$ROOT/harness/scripts/analyze_benchmark_suite.py" "$suite_dir"
  fi
done
