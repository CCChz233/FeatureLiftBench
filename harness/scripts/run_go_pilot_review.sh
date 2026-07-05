#!/usr/bin/env bash
# Run Step 5 review packet for a Go pilot/staging task.
set -uo pipefail
cd "$(dirname "$0")/../.."
export PYTHONPATH=harness
PY="${PYTHON:-python3}"

usage() {
  echo "Usage: $0 <task_id> [--task-dir PATH] [--skip-audit] [--docker]"
  echo "  Default task dir: benchmark/go/staging/<task_id>/ then benchmark/go/tasks/<task_id>/"
  exit 1
}

TASK_ID="${1:-}"
shift || usage
TASK_DIR=""
SKIP_AUDIT=0
DOCKER_FLAG=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --task-dir) TASK_DIR="$2"; shift 2 ;;
    --skip-audit) SKIP_AUDIT=1; shift ;;
    --docker) DOCKER_FLAG=(--docker); shift ;;
    *) usage ;;
  esac
done

[[ -n "$TASK_ID" ]] || usage
if [[ -z "$TASK_DIR" ]]; then
  if [[ -d "benchmark/go/staging/$TASK_ID" ]]; then
    TASK_DIR="benchmark/go/staging/$TASK_ID"
  elif [[ -d "benchmark/go/tasks/$TASK_ID" ]]; then
    TASK_DIR="benchmark/go/tasks/$TASK_ID"
  elif [[ -d "benchmark/go/sanity/$TASK_ID" ]]; then
    TASK_DIR="benchmark/go/sanity/$TASK_ID"
  else
    echo "ERROR: task dir not found for $TASK_ID"
    exit 1
  fi
fi

REVIEW_DIR="experiments/go-pilot/$TASK_ID/review"
SUBMISSIONS="benchmark/submissions/$TASK_ID"

mkdir -p "$REVIEW_DIR/oracle" "$REVIEW_DIR/naive" "$REVIEW_DIR/copy_all"

echo "=== $TASK_ID: validate-task ==="
$PY -B -m featureliftbench.cli validate-task "$TASK_DIR" > "$REVIEW_DIR/validate-task.log" 2>&1 || true

if [[ "$SKIP_AUDIT" -eq 0 ]]; then
  echo "=== $TASK_ID: audit_output_imports ==="
  $PY harness/scripts/audit_output_imports.py "$TASK_DIR" --fail-on-gap > "$REVIEW_DIR/audit-output-imports.log" 2>&1 || true
else
  echo "[OK] audit skipped" > "$REVIEW_DIR/audit-output-imports.log"
fi

echo "=== $TASK_ID: eval oracle ==="
$PY -B -m featureliftbench.cli eval "$TASK_DIR" "$SUBMISSIONS/oracle" --output "$REVIEW_DIR/oracle" "${DOCKER_FLAG[@]}"

echo "=== $TASK_ID: verify_module_probes ==="
$PY harness/scripts/verify_module_probes.py "$TASK_DIR" --verify-oracle "${DOCKER_FLAG[@]}" > "$REVIEW_DIR/module-probes.log" 2>&1 || true

echo "=== $TASK_ID: eval naive ==="
$PY -B -m featureliftbench.cli eval "$TASK_DIR" "$SUBMISSIONS/naive" --output "$REVIEW_DIR/naive" "${DOCKER_FLAG[@]}" || true

echo "=== $TASK_ID: eval copy_all ==="
$PY -B -m featureliftbench.cli eval "$TASK_DIR" "$SUBMISSIONS/copy_all" --output "$REVIEW_DIR/copy_all" "${DOCKER_FLAG[@]}" || true

echo "=== $TASK_ID: generate gate_report ==="
$PY harness/scripts/generate_go_gate_report.py "$TASK_ID"

$PY - <<PY
import json
from pathlib import Path
rid = "$TASK_ID"
review = Path("experiments/go-pilot") / rid / "review"
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
