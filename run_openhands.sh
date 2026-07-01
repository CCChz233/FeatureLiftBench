#!/usr/bin/env bash
# OpenHands sanity suite: 3 smoke tasks under benchmark/sanity/.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

export FEATURELIFTBENCH_AGENT_DOCKER="${FEATURELIFTBENCH_AGENT_DOCKER:-1}"
export FEATURELIFTBENCH_EVAL_DOCKER="${FEATURELIFTBENCH_EVAL_DOCKER:-1}"
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

AGENT_PROFILE="${AGENT_PROFILE:-openhands_deepseek_v4_flash}"
RESUME_FLAG=()
if [[ $# -ge 1 && "${1:-}" != "" ]]; then
  TASK_ROOT="$1"
else
  TASK_ROOT="${TASK_ROOT:-benchmark/sanity}"
fi
if [[ $# -ge 2 ]]; then
  OUTPUT="$2"
else
  if [[ -n "${RESUME_DIR:-}" ]]; then
    OUTPUT="${RESUME_DIR}"
    RESUME_FLAG=(--resume)
  else
    RUN_ID="${RUN_ID:-openhands-sanity-$(date +%Y%m%d-%H%M%S)}"
    OUTPUT="experiments/openhands-agent/${RUN_ID}"
  fi
fi

mkdir -p "$OUTPUT"

PREFLIGHT_ARGS=(
  --bootstrap
  --agent openhands-agent
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

echo "Agent:   openhands-agent"
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
if [[ -n "${FEATURELIFTBENCH_AGENT_DOCKER:-}" ]]; then
  echo "Note: OpenHands Docker runs require a 3.12 agent image with openhands installed:"
  echo "  FEATURELIFTBENCH_AGENT_PYTHON_BASE=python:3.12-slim FEATURELIFTBENCH_INSTALL_OPENHANDS=1 ./docker/build_agent_image.sh"
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
  --agent openhands-agent \
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

if [[ -f "${OUTPUT}/suite.json" ]]; then
  $PYTHON harness/scripts/analyze_featurelift_suite.py "${OUTPUT}"
  $PYTHON harness/scripts/analyze_benchmark_suite.py "${OUTPUT}"
  $PYTHON harness/scripts/report_entanglement_coverage.py --suite-dir "${OUTPUT}"
fi

if [[ "${RUN_AGENT_STATUS}" -eq 1 ]]; then
  echo "Suite completed with benchmark failures; analysis was generated." >&2
fi
echo "Done: ${OUTPUT}"
echo "Inspect per-task: agent/openhands_task.md agent/openhands_stdout.log agent/usage.json run.json"
