#!/usr/bin/env bash
# OpenHands 5-task pilot: 3 sanity + 2 batch-1 (two roots; sanity ids are not under benchmark/tasks).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

export FEATURELIFTBENCH_AGENT_DOCKER="${FEATURELIFTBENCH_AGENT_DOCKER:-1}"
export FEATURELIFTBENCH_EVAL_DOCKER="${FEATURELIFTBENCH_EVAL_DOCKER:-1}"
export PYTHONPATH="${PYTHONPATH:-$ROOT/harness}"
PYTHON="${PYTHON:-python3.12}"
PROFILE="${AGENT_PROFILE:-openhands_deepseek_v4_flash}"

RUN_ID="${RUN_ID:-openhands-pilot5-$(date +%Y%m%d-%H%M%S)}"
OUTPUT="experiments/openhands-agent/${RUN_ID}"
SANITY_OUTPUT="$OUTPUT/sanity3"
BATCH_OUTPUT="$OUTPUT/batch2"
mkdir -p "$SANITY_OUTPUT" "$BATCH_OUTPUT"

# shellcheck source=harness/scripts/run_lock.sh
source "$ROOT/harness/scripts/run_lock.sh"
acquire_run_lock "$OUTPUT"

RESUME_FLAG=()
if [[ "${RESUME:-0}" == "1" ]]; then
  RESUME_FLAG=(--resume)
fi

COMMON_ARGS=(
  --agent openhands-agent
  --agent-config harness/config/agents.toml
  --agent-profile "$PROFILE"
  --env-file .env
  --agent-docker
  --eval-docker
  --num-workers "${NUM_WORKERS:-1}"
)

"$PYTHON" harness/scripts/preflight.py \
  --bootstrap \
  --agent openhands-agent \
  --agent-profile "$PROFILE" \
  --docker-suite \
  --output-dir "$OUTPUT/preflight"

echo "==> 1/2: 3 sanity tasks (benchmark/sanity)"
set +e
"$PYTHON" -B -m featureliftbench.cli run-agent benchmark/sanity \
  "${COMMON_ARGS[@]}" \
  --output "$SANITY_OUTPUT" \
  ${RESUME_FLAG[@]+"${RESUME_FLAG[@]}"}
SANITY_STATUS=$?
set -e
if [[ "${SANITY_STATUS}" -ge 2 ]]; then
  echo "sanity3 failed before completing the suite (exit ${SANITY_STATUS}); aborting pilot5" >&2
  exit "${SANITY_STATUS}"
fi

echo "==> 2/2: 2 batch-1 tasks (benchmark/tasks)"
set +e
"$PYTHON" -B -m featureliftbench.cli run-agent benchmark/tasks \
  "${COMMON_ARGS[@]}" \
  --output "$BATCH_OUTPUT" \
  ${RESUME_FLAG[@]+"${RESUME_FLAG[@]}"} \
  --task-id arrow__parse_format_core__001 \
  --task-id bleach__sanitize_core__001
BATCH_STATUS=$?
set -e
if [[ "${BATCH_STATUS}" -ge 2 ]]; then
  echo "batch2 failed before completing the suite (exit ${BATCH_STATUS}); skipping pilot5 merge" >&2
  exit "${BATCH_STATUS}"
fi

if [[ -f "$SANITY_OUTPUT/suite.json" ]]; then
  "$PYTHON" harness/scripts/analyze_benchmark_suite.py "$SANITY_OUTPUT"
fi
if [[ -f "$BATCH_OUTPUT/suite.json" ]]; then
  "$PYTHON" harness/scripts/analyze_benchmark_suite.py "$BATCH_OUTPUT"
fi
if [[ -f "$SANITY_OUTPUT/suite.json" && -f "$BATCH_OUTPUT/suite.json" ]]; then
  "$PYTHON" harness/scripts/merge_openhands_pilot.py "$OUTPUT" "$SANITY_OUTPUT" "$BATCH_OUTPUT"
fi
echo "Done: $OUTPUT"
if [[ "${SANITY_STATUS}" -eq 1 || "${BATCH_STATUS}" -eq 1 ]]; then
  echo "Pilot5 completed with benchmark failures; merged outputs were generated when possible." >&2
  exit 1
fi
