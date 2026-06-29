#!/usr/bin/env bash
# Read-only diagnostics for long-running benchmark suites.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

OUTPUT="${1:-}"
if [[ -z "$OUTPUT" ]]; then
  echo "Usage: $0 <suite-output-dir>" >&2
  echo "Example: $0 experiments/mini-swe-agent/benchmark-batch1-flash-docker-20260629-114427" >&2
  exit 1
fi

if [[ ! -d "$OUTPUT" ]]; then
  echo "ERROR: not a directory: $OUTPUT" >&2
  exit 1
fi

echo "=== FeatureLiftBench run health ==="
echo "Output: $OUTPUT"
echo

completed=0
latest_mtime=""
latest_task=""
while IFS= read -r run_json; do
  completed=$((completed + 1))
  task_dir="$(dirname "$run_json")"
  task_id="$(basename "$task_dir")"
  mtime="$(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$run_json" 2>/dev/null || stat -c "%y" "$run_json" 2>/dev/null | cut -d. -f1)"
  if [[ -z "$latest_mtime" || "$mtime" > "$latest_mtime" ]]; then
    latest_mtime="$mtime"
    latest_task="$task_id"
  fi
done < <(find "$OUTPUT" -mindepth 2 -maxdepth 2 -name run.json 2>/dev/null | sort)

echo "Completed tasks (run.json): $completed"
if [[ -n "$latest_task" ]]; then
  echo "Latest finished: $latest_task at $latest_mtime"
fi

if [[ -f "$OUTPUT/suite.json" ]]; then
  if command -v python3 >/dev/null 2>&1; then
    OUTPUT="$OUTPUT" python3 - <<'PY'
import json
import os
from pathlib import Path

suite = json.loads(Path(os.environ["OUTPUT"]).joinpath("suite.json").read_text(encoding="utf-8"))
summary = suite.get("summary") or {}
checkpoint = suite.get("checkpoint")
print(
    f"suite.json: checkpoint={bool(checkpoint)} "
    f"passed={summary.get('passed', '?')}/{summary.get('total', '?')}"
)
PY
  else
    echo "suite.json: present"
  fi
else
  echo "suite.json: missing (mid-run or pre-checkpoint)"
fi
echo

lock_dir="$OUTPUT/.run.lock"
if [[ -d "$lock_dir" ]]; then
  holder=""
  if [[ -f "$lock_dir/pid" ]]; then
    holder="$(cat "$lock_dir/pid" 2>/dev/null || true)"
  fi
  echo "Run lock: HELD at $lock_dir${holder:+ (pid $holder)}"
else
  echo "Run lock: none"
fi
echo

runners="$(pgrep -fl "featureliftbench.cli run-agent" 2>/dev/null || true)"
if [[ -n "$runners" ]]; then
  echo "Active run-agent processes:"
  echo "$runners"
else
  echo "Active run-agent processes: none"
fi
echo

if command -v docker >/dev/null 2>&1; then
  containers="$(docker ps --filter name=flb- --format '{{.Names}}\t{{.Status}}' 2>/dev/null || true)"
  if [[ -n "$containers" ]]; then
    echo "flb-* containers:"
    echo "$containers"
  else
    echo "flb-* containers: none running"
  fi
else
  echo "docker: not available"
fi
