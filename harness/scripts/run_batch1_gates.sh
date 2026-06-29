#!/usr/bin/env bash
set -uo pipefail
cd "$(dirname "$0")/../.."
export PYTHONPATH=harness
PY=/Users/chz/anaconda3/bin/python3
TASK_ID="$1"
TASK_DIR="benchmark/staging/$TASK_ID"
REVIEW_DIR="experiments/batch1/$TASK_ID/review"
mkdir -p "$REVIEW_DIR/oracle" "$REVIEW_DIR/naive" "$REVIEW_DIR/copy_all"

echo "=== $TASK_ID: validate-task ==="
$PY -B -m featureliftbench.cli validate-task "$TASK_DIR" > "$REVIEW_DIR/validate-task.log" 2>&1

echo "=== $TASK_ID: audit_output_imports ==="
$PY harness/scripts/audit_output_imports.py "$TASK_DIR" --fail-on-gap > "$REVIEW_DIR/audit-output-imports.log" 2>&1

echo "=== $TASK_ID: build oracle ==="
$PY harness/scripts/build_oracle_submission.py "$TASK_DIR"

echo "=== $TASK_ID: build copy_all ==="
$PY harness/scripts/build_oracle_submission.py "$TASK_DIR" --variant copy_all

echo "=== $TASK_ID: eval oracle ==="
$PY -B -m featureliftbench.cli eval "$TASK_DIR" "benchmark/submissions/$TASK_ID/oracle" --output "$REVIEW_DIR/oracle"

echo "=== $TASK_ID: verify_module_probes ==="
$PY harness/scripts/verify_module_probes.py "$TASK_DIR" --verify-oracle > "$REVIEW_DIR/module-probes.log" 2>&1

echo "=== $TASK_ID: eval naive ==="
$PY -B -m featureliftbench.cli eval "$TASK_DIR" "benchmark/submissions/$TASK_ID/naive" --output "$REVIEW_DIR/naive" || true

echo "=== $TASK_ID: eval copy_all ==="
$PY -B -m featureliftbench.cli eval "$TASK_DIR" "benchmark/submissions/$TASK_ID/copy_all" --output "$REVIEW_DIR/copy_all" || true

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
PY
