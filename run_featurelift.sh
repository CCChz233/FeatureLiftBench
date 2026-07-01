#!/usr/bin/env bash
# FeatureLiftAgent sanity suite: 3 smoke tasks under benchmark/sanity/.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

export PYTHONPATH="${PYTHONPATH:-$ROOT/harness}"

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

AGENT_PROFILE="${AGENT_PROFILE:-featurelift_v4_flash}"
TASK_ROOT="${TASK_ROOT:-benchmark/sanity}"

if [[ -n "${RESUME_DIR:-}" ]]; then
  OUTPUT="${RESUME_DIR}"
  RESUME_FLAG=(--resume)
else
  RUN_ID="${RUN_ID:-featurelift-sanity-$(date +%Y%m%d-%H%M%S)}"
  OUTPUT="experiments/featurelift-agent/${RUN_ID}"
  RESUME_FLAG=()
fi

mkdir -p "$OUTPUT"

PREFLIGHT_ARGS=(
  --bootstrap
  --agent featurelift-agent
  --agent-profile "$AGENT_PROFILE"
  --output-dir "$OUTPUT"
)
if [[ -n "${FEATURELIFTBENCH_AGENT_DOCKER:-}" || -n "${FEATURELIFTBENCH_EVAL_DOCKER:-}" ]]; then
  PREFLIGHT_ARGS+=(--docker-suite)
fi
"$PYTHON" "$ROOT/harness/scripts/preflight.py" "${PREFLIGHT_ARGS[@]}"

# shellcheck source=harness/scripts/run_lock.sh
source "$ROOT/harness/scripts/run_lock.sh"
acquire_run_lock "$OUTPUT"

EXTRA_AGENT_PASSES="${EXTRA_AGENT_PASSES:-0}"
RETRY_RATE_LIMIT="${RETRY_RATE_LIMIT:-5}"

echo "Agent:   featurelift-agent"
echo "Profile: ${AGENT_PROFILE}"
echo "Tasks:   ${TASK_ROOT}"
echo "Output:  ${OUTPUT}"
echo "Python:  $PYTHON"
echo "Workers: ${NUM_WORKERS}"
echo "Eval memory MB: ${EVAL_MEMORY_MB}"
echo "Agent memory MB: ${AGENT_MEMORY_MB}"
if [[ "${#RESUME_FLAG[@]}" -gt 0 ]]; then
  echo "Resume:  yes"
fi
if [[ "${EXTRA_AGENT_PASSES}" != "0" ]]; then
  echo "Extra agent passes: ${EXTRA_AGENT_PASSES}"
fi

AGENT_DOCKER_FLAG=()
EVAL_DOCKER_FLAG=()
if [[ -n "${FEATURELIFTBENCH_AGENT_DOCKER:-}" ]]; then
  AGENT_DOCKER_FLAG=(--agent-docker)
fi
if [[ -n "${FEATURELIFTBENCH_EVAL_DOCKER:-}" ]]; then
  EVAL_DOCKER_FLAG=(--eval-docker)
fi

set +e
$PYTHON -B -m featureliftbench.cli run-agent "$TASK_ROOT" \
  --agent featurelift-agent \
  --agent-config harness/config/agents.toml \
  --agent-profile "${AGENT_PROFILE}" \
  --env-file .env \
  --num-workers "${NUM_WORKERS}" \
  --retry-rate-limit "${RETRY_RATE_LIMIT}" \
  --extra-agent-passes "${EXTRA_AGENT_PASSES}" \
  ${NO_PROGRESS:+--no-progress} \
  ${AGENT_DOCKER_FLAG[@]+"${AGENT_DOCKER_FLAG[@]}"} \
  ${EVAL_DOCKER_FLAG[@]+"${EVAL_DOCKER_FLAG[@]}"} \
  --output "${OUTPUT}" \
  ${RESUME_FLAG[@]+"${RESUME_FLAG[@]}"}
RUN_AGENT_STATUS=$?
set -e

if [[ "${RUN_AGENT_STATUS}" -ge 2 ]]; then
  echo "run-agent failed before completing the suite (exit ${RUN_AGENT_STATUS}); skipping analysis" >&2
  exit "${RUN_AGENT_STATUS}"
fi

$PYTHON harness/scripts/analyze_featurelift_suite.py "${OUTPUT}"
$PYTHON harness/scripts/analyze_benchmark_suite.py "${OUTPUT}"
$PYTHON harness/scripts/report_entanglement_coverage.py --suite-dir "${OUTPUT}"

if [[ "${RUN_AGENT_STATUS}" -eq 1 ]]; then
  echo "Suite completed with benchmark failures; analysis was generated." >&2
fi
echo "Done: ${OUTPUT}"
