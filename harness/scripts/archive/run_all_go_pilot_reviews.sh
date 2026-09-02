#!/usr/bin/env bash
set -uo pipefail
cd "$(dirname "$0")/../.."
for task_dir in benchmark/go/tasks/*/; do
  tid=$(basename "$task_dir")
  echo "=== BATCH $tid ==="
  bash harness/scripts/run_go_pilot_review.sh "$tid" --task-dir "$task_dir" || true
done
