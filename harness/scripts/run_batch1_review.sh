#!/usr/bin/env bash
# Run Step 5 review packet for a promoted batch-1 task (benchmark/tasks/).
set -uo pipefail
cd "$(dirname "$0")/../.."
export PYTHONPATH=harness
PY=/Users/chz/anaconda3/bin/python3

usage() {
  echo "Usage: $0 <task_id> [--skip-build] [--task-dir PATH]"
  echo "  Default task dir: benchmark/tasks/<task_id>/"
  exit 1
}

TASK_ID="${1:-}"
shift || usage
SKIP_BUILD=0
TASK_DIR=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-build) SKIP_BUILD=1; shift ;;
    --task-dir) TASK_DIR="$2"; shift 2 ;;
    *) usage ;;
  esac
done

[[ -n "$TASK_ID" ]] || usage
[[ -n "$TASK_DIR" ]] || TASK_DIR="benchmark/tasks/$TASK_ID"
REVIEW_DIR="experiments/batch1/$TASK_ID/review"
SUBMISSIONS="benchmark/submissions/$TASK_ID"

mkdir -p "$REVIEW_DIR/oracle" "$REVIEW_DIR/naive" "$REVIEW_DIR/copy_all"

echo "=== $TASK_ID: validate-task ==="
if ! $PY -B -m featureliftbench.cli validate-task "$TASK_DIR" > "$REVIEW_DIR/validate-task.log" 2>&1; then
  echo "WARN: validate-task failed (see $REVIEW_DIR/validate-task.log)"
fi

echo "=== $TASK_ID: audit_output_imports ==="
if ! $PY harness/scripts/audit_output_imports.py "$TASK_DIR" --fail-on-gap > "$REVIEW_DIR/audit-output-imports.log" 2>&1; then
  echo "WARN: audit_output_imports failed"
fi

if [[ "$SKIP_BUILD" -eq 0 ]]; then
  echo "=== $TASK_ID: build oracle ==="
  $PY harness/scripts/build_oracle_submission.py "$TASK_DIR"
  echo "=== $TASK_ID: build copy_all ==="
  $PY harness/scripts/build_oracle_submission.py "$TASK_DIR" --variant copy_all
fi

echo "=== $TASK_ID: eval oracle ==="
$PY -B -m featureliftbench.cli eval "$TASK_DIR" "$SUBMISSIONS/oracle" --output "$REVIEW_DIR/oracle"

echo "=== $TASK_ID: verify_module_probes ==="
$PY harness/scripts/verify_module_probes.py "$TASK_DIR" --verify-oracle > "$REVIEW_DIR/module-probes.log" 2>&1

echo "=== $TASK_ID: eval naive ==="
$PY -B -m featureliftbench.cli eval "$TASK_DIR" "$SUBMISSIONS/naive" --output "$REVIEW_DIR/naive" || true

echo "=== $TASK_ID: eval copy_all ==="
$PY -B -m featureliftbench.cli eval "$TASK_DIR" "$SUBMISSIONS/copy_all" --output "$REVIEW_DIR/copy_all" || true

echo "=== $TASK_ID: generate gate_report ==="
$PY harness/scripts/generate_gate_report.py "$TASK_ID"

$PY - <<PY
import json
from pathlib import Path
rid = "$TASK_ID"
review = Path("experiments/batch1") / rid / "review"
for label in ("oracle", "naive", "copy_all"):
    p = review / label / "result.json"
    if p.exists():
        d = json.loads(p.read_text())
        s = d.get("scores", {})
        print(f"{rid} {label}: status={d.get('status')} pub={d.get('public_tests',{}).get('passed')} hid={d.get('hidden_tests',{}).get('passed')} ext={s.get('extraction_ratio')} final={s.get('final_score')}")
gate = review / "gate_report.json"
if gate.exists():
    g = json.loads(gate.read_text())
    print(f"{rid} gate: decision={g.get('decision')} blocking={g.get('blocking_gates')}")
PY
