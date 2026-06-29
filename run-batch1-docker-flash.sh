#!/usr/bin/env bash
# batch-1 (50 hard): DeepSeek V4 Flash with agent-docker + eval-docker
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

export PYTHONPATH="${PYTHONPATH:-$ROOT/harness}"
export FEATURELIFTBENCH_AGENT_DOCKER=1
export FEATURELIFTBENCH_EVAL_DOCKER=1
export FEATURELIFTBENCH_LIVE_TRAJECTORY=1
# Live trajectory snapshots let suite progress read per-step token totals.
# (mini stdout in Docker reports step + $cost, not token counts.)

if [[ -n "${PYTHON:-}" ]]; then
  :
elif [[ -n "${CONDA_PREFIX:-}" && -x "${CONDA_PREFIX}/bin/python" ]]; then
  PYTHON="${CONDA_PREFIX}/bin/python"
elif [[ -x "$ROOT/.venv/bin/python" ]]; then
  PYTHON="$ROOT/.venv/bin/python"
elif command -v python3.12 >/dev/null 2>&1; then
  PYTHON=python3.12
else
  PYTHON=python3
fi

export PATH="$ROOT/.venv/bin:${PATH}"
export EVAL_MEMORY_MB="${EVAL_MEMORY_MB:-4096}"
export AGENT_MEMORY_MB="${AGENT_MEMORY_MB:-8192}"
export NUM_WORKERS="${NUM_WORKERS:-1}"
export AGENT_PROFILE="${AGENT_PROFILE:-deepseek_v4_flash}"
export RETRY_RATE_LIMIT="${RETRY_RATE_LIMIT:-5}"

BATCH1_TASKS=()
while IFS= read -r tid; do
  [[ -n "$tid" ]] && BATCH1_TASKS+=("$tid")
done < <(
  "$PYTHON" - <<'PY'
import sys
sys.path.insert(0, "harness/scripts")
from generate_gate_report import list_batch1_task_ids
for tid in list_batch1_task_ids():
    print(tid)
PY
)

TASK_ID_ARGS=()
for tid in "${BATCH1_TASKS[@]}"; do
  TASK_ID_ARGS+=(--task-id "$tid")
done

if [[ -n "${RESUME_DIR:-}" ]]; then
  OUTPUT="${RESUME_DIR}"
  RESUME_FLAG=(--resume)
else
  RUN_ID="${RUN_ID:-benchmark-batch1-flash-docker-$(date +%Y%m%d-%H%M%S)}"
  OUTPUT="experiments/mini-swe-agent/${RUN_ID}"
  RESUME_FLAG=()
fi

mkdir -p "$OUTPUT"

"$PYTHON" "$ROOT/harness/scripts/preflight.py" \
  --bootstrap \
  --agent-profile "$AGENT_PROFILE" \
  --docker-suite \
  --output-dir "$OUTPUT" \
  ${MINI_BIN:+--mini-bin "$MINI_BIN"}

# shellcheck source=harness/scripts/run_lock.sh
source "$ROOT/harness/scripts/run_lock.sh"
acquire_run_lock "$OUTPUT"

RESUME_ARGS=()
if [[ ${#RESUME_FLAG[@]} -gt 0 ]]; then
  RESUME_ARGS=("${RESUME_FLAG[@]}")
fi
echo "Profile:     ${AGENT_PROFILE}"
echo "Output:      ${OUTPUT}"
echo "Tasks:       ${#BATCH1_TASKS[@]} (batch-1)"
echo "Docker:      agent + eval"
echo "Python:      $PYTHON"
echo "Workers:     ${NUM_WORKERS}"
if [[ ${#RESUME_ARGS[@]} -gt 0 ]]; then
  echo "Resume:      yes"
fi

CLI_ARGS=(
  --agent mini-swe-agent
  --agent-config harness/config/agents.toml
  --agent-profile "${AGENT_PROFILE}"
  --env-file .env
  --yolo
  --agent-docker
  --eval-docker
  --num-workers "${NUM_WORKERS}"
  --retry-rate-limit "${RETRY_RATE_LIMIT}"
  --output "${OUTPUT}"
)
if [[ -n "${NO_PROGRESS:-}" ]]; then
  CLI_ARGS+=(--no-progress)
fi
if [[ ${#RESUME_ARGS[@]} -gt 0 ]]; then
  CLI_ARGS+=("${RESUME_ARGS[@]}")
fi
CLI_ARGS+=("${TASK_ID_ARGS[@]}")

set +e
"$PYTHON" -B -m featureliftbench.cli run-agent benchmark/tasks "${CLI_ARGS[@]}"
RUN_AGENT_STATUS=$?
set -e

if [[ "${RUN_AGENT_STATUS}" -ge 2 ]]; then
  echo "run-agent failed before completing the suite (exit ${RUN_AGENT_STATUS}); skipping analysis" >&2
  exit "${RUN_AGENT_STATUS}"
fi

"$PYTHON" harness/scripts/analyze_benchmark_suite.py "${OUTPUT}"
"$PYTHON" harness/scripts/report_entanglement_coverage.py --suite-dir "${OUTPUT}"

if [[ "${RUN_AGENT_STATUS}" -eq 1 ]]; then
  echo "Suite completed with benchmark failures; analysis was generated." >&2
fi
echo "Done: ${OUTPUT}"
