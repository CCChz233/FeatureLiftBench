#!/usr/bin/env bash
# Minimal Go track baseline loop (10 gold tasks, not 100).
#
# Three baselines (run in this order on gold-ready tasks only):
#   1. copy_all  — whole-repo copy; eval only (no LLM). Verifies extraction penalty.
#   2. mini       — mini-swe-agent + deepseek_v4_flash, max 120 steps.
#   3. strong     — mini-swe-agent + yolo (autonomous shell), same model/step cap.
#
# Usage:
#   ./harness/scripts/run_go_baseline.sh copy_all [task_id]
#   ./harness/scripts/run_go_baseline.sh mini semver__version_parse_core__001
#   ./harness/scripts/run_go_baseline.sh strong humanize__bytes_format_core__001
#   ./harness/scripts/run_go_baseline.sh mini   # all gold-ready tasks
#
# Env:
#   AGENT_PROFILE=deepseek_v4_flash_120  (default; 120-step cap via MSWEA_GLOBAL_CALL_LIMIT)
#   NUM_WORKERS=1
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH=harness
PY="${PYTHON:-python3}"

usage() {
  echo "Usage: $0 <copy_all|mini|strong> [task_id]" >&2
  exit 1
}

BASELINE="${1:-}"
shift || usage

TASK_ID="${1:-}"
if [[ -n "$TASK_ID" ]]; then
  TASK_IDS=("$TASK_ID")
else
  mapfile -t TASK_IDS < <("$PY" - <<'PY'
from pathlib import Path
ready = []
for task_dir in sorted((Path("benchmark/go/tasks")).iterdir()):
    if not (task_dir / "metadata.json").is_file():
        continue
    repo = task_dir / "repo"
    if not repo.is_dir():
        continue
    # Skip hello-template repos (single add.go stub).
    go_files = list(repo.glob("*.go"))
    if len(go_files) == 1 and go_files[0].name == "add.go":
        continue
    ready.append(task_dir.name)
for name in ready:
    print(name)
PY
)
fi

if [[ ${#TASK_IDS[@]} -eq 0 ]]; then
  echo "No gold-ready Go tasks found (need real repo snapshots, not hello add.go)." >&2
  exit 1
fi

PROFILE="${AGENT_PROFILE:-deepseek_v4_flash_120}"
RUN_TS="$(date +%Y%m%d-%H%M%S)"

case "$BASELINE" in
  copy_all)
    OUT="experiments/go-baselines/copy_all-${RUN_TS}"
    mkdir -p "$OUT"
    for tid in "${TASK_IDS[@]}"; do
      echo "=== copy_all eval: $tid ==="
      SUB="benchmark/submissions/${tid}/copy_all"
      if [[ ! -d "$SUB" ]]; then
        "$PY" harness/scripts/sync_go_copy_all.py "$tid"
      fi
      "$PY" -B -m featureliftbench.cli eval \
        "benchmark/go/tasks/${tid}" "$SUB" \
        --output "${OUT}/${tid}" --docker
    done
    echo "copy_all baseline: $OUT"
    ;;
  mini|strong)
  OUT="experiments/go-baselines/${BASELINE}-flash-${RUN_TS}"
  EXTRA=()
  if [[ "$BASELINE" == "strong" ]]; then
    EXTRA+=(--yolo)
  fi
  echo "Profile: $PROFILE | tasks: ${TASK_IDS[*]} | max steps: 120"
  "$PY" -B -m featureliftbench.cli run-agent benchmark/go/tasks \
    --agent mini-swe-agent \
    --agent-config harness/config/agents.toml \
    --agent-profile "$PROFILE" \
    --env-file .env \
    --docker \
    --num-workers "${NUM_WORKERS:-1}" \
    --output "$OUT" \
    --task-id "${TASK_IDS[@]}" \
    "${EXTRA[@]}"
  if [[ -f harness/scripts/analyze_benchmark_suite.py ]]; then
    "$PY" harness/scripts/analyze_benchmark_suite.py "$OUT" || true
  fi
  echo "${BASELINE} baseline: $OUT"
  ;;
  *)
    usage
    ;;
esac
