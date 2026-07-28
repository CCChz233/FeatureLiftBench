#!/usr/bin/env bash
# Path-independent FeatureLiftBench experiment runner.
#
# Usage (from anywhere, after cloning the repo):
#   ./run_experiment.sh --arm main --tasks iniconfig__parse_config__001
#   ./run_experiment.sh --compare-arms main,entrypoint_hint,public_feedback,short_prompt \
#       --tasks iniconfig__parse_config__001,transitions__state_machine_core__hard3_001
#   ./run_experiment.sh --suite sanity --arm main
#
# All paths are resolved relative to the repository root (script location).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/lib/flb_env.sh
source "${SCRIPT_DIR}/lib/flb_env.sh"
flb_cd_root
PYTHON="$(flb_resolve_python)"
export PATH="${FLB_ROOT}/.venv/bin:${PATH}"

usage() {
  cat <<'EOF'
FeatureLiftBench experiment runner (relative paths; machine-independent)

Usage:
  ./run_experiment.sh [options]

Arms / profiles:
  --arm main|entrypoint_hint|public_feedback|short_prompt|pruned_context|td_cognition|p0
      Map to OpenHands DeepSeek profiles (uses harness/config/agents.example.toml)
  --profile NAME
      Explicit --agent-profile (overrides --arm mapping)
  --compare-arms a,b,c
      Run the same tasks once per arm (sequential)

Tasks:
  --tasks id1,id2,...          Comma-separated task ids under --tasks-root
  --task-file PATH             File with one task id per line (# comments ok)
  --suite sanity|main|pilot    Run all tasks under a known root
  --tasks-root REL_PATH        Default: benchmark/tasks
                               sanity -> benchmark/sanity
                               pilot  -> benchmark/batch3_pilot

Agent / eval:
  --agent NAME                 Default: openhands-agent
  --agent-config REL_PATH      Default: agents.example.toml for arms; else agents.toml
  --env-file REL_PATH          Default: .env
  --docker / --no-docker       Default: --docker (agent+eval docker)
  --agent-image NAME           Default: featureliftbench-agent:latest
                               (or FEATURELIFTBENCH_AGENT_DOCKER_IMAGE)
  --eval-image NAME            Default: featureliftbench-eval:latest
  --workers N                  Default: 1
  --timeout SEC                Default: 3600
  --retry-only-status LIST    Resume-only statuses to rerun
  --no-progress

Output:
  --output REL_OR_ABS          Suite output dir (default under experiments/ablation/...)
  --run-id NAME                Used when --output omitted
  --resume DIR                 Resume an existing suite dir

Examples:
  ./run_experiment.sh --arm main --tasks iniconfig__parse_config__001
  ./run_experiment.sh --compare-arms main,entrypoint_hint,public_feedback,short_prompt \
      --tasks iniconfig__parse_config__001,transitions__state_machine_core__hard3_001
  ./run_experiment.sh --suite sanity --arm main --docker
EOF
}

ARM=""
PROFILE=""
COMPARE_ARMS=""
TASKS_CSV=""
TASK_FILE=""
SUITE=""
TASKS_ROOT="benchmark/tasks"
AGENT="openhands-agent"
AGENT_CONFIG=""
ENV_FILE=".env"
USE_DOCKER=1
AGENT_IMAGE="${FEATURELIFTBENCH_AGENT_DOCKER_IMAGE:-featureliftbench-agent:latest}"
EVAL_IMAGE="${FEATURELIFTBENCH_EVAL_DOCKER_IMAGE:-featureliftbench-eval:latest}"
WORKERS="${NUM_WORKERS:-1}"
TIMEOUT="${TIMEOUT_SECONDS:-3600}"
RETRY_ONLY_STATUS=""
NO_PROGRESS=0
OUTPUT=""
RUN_ID=""
RESUME=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    --arm) ARM="$2"; shift 2 ;;
    --profile) PROFILE="$2"; shift 2 ;;
    --compare-arms) COMPARE_ARMS="$2"; shift 2 ;;
    --tasks) TASKS_CSV="$2"; shift 2 ;;
    --task-file) TASK_FILE="$2"; shift 2 ;;
    --suite) SUITE="$2"; shift 2 ;;
    --tasks-root) TASKS_ROOT="$2"; shift 2 ;;
    --agent) AGENT="$2"; shift 2 ;;
    --agent-config) AGENT_CONFIG="$2"; shift 2 ;;
    --env-file) ENV_FILE="$2"; shift 2 ;;
    --docker) USE_DOCKER=1; shift ;;
    --no-docker) USE_DOCKER=0; shift ;;
    --agent-image) AGENT_IMAGE="$2"; shift 2 ;;
    --eval-image) EVAL_IMAGE="$2"; shift 2 ;;
    --workers) WORKERS="$2"; shift 2 ;;
    --timeout) TIMEOUT="$2"; shift 2 ;;
    --retry-only-status) RETRY_ONLY_STATUS="$2"; shift 2 ;;
    --no-progress) NO_PROGRESS=1; shift ;;
    --output) OUTPUT="$2"; shift 2 ;;
    --run-id) RUN_ID="$2"; shift 2 ;;
    --resume) RESUME="$2"; shift 2 ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

arm_to_profile() {
  case "$1" in
    main) echo "openhands_deepseek_v4_flash_main" ;;
    entrypoint_hint|entrypoint-hint|hints) echo "openhands_deepseek_v4_flash_entrypoint_hint" ;;
    public_feedback|public-feedback|public) echo "openhands_deepseek_v4_flash_public_feedback" ;;
    nopublic|no_public|no-public) echo "openhands_deepseek_v4_flash_main" ;;
    short|short_prompt|short-prompt) echo "openhands_deepseek_v4_flash_short_prompt" ;;
    pruned|pruned_context|pruned-context) echo "openhands_deepseek_v4_flash_main" ;;
    td|td_cognition|td-cognition|cognition) echo "openhands_deepseek_v4_flash_td_cognition" ;;
    p0) echo "openhands_deepseek_v4_flash_rsg_pilot_p0" ;;
    *)
      echo "Unknown arm: $1 (use main|entrypoint_hint|public_feedback|short_prompt|pruned_context|td_cognition|p0 or --profile)" >&2
      return 2
      ;;
  esac
}

case "${SUITE}" in
  "") ;;
  sanity) TASKS_ROOT="benchmark/sanity" ;;
  main) TASKS_ROOT="benchmark/tasks" ;;
  pilot|batch3) TASKS_ROOT="benchmark/batch3_pilot" ;;
  *)
    echo "Unknown --suite: ${SUITE}" >&2
    exit 2
    ;;
esac

if [[ ! -d "${TASKS_ROOT}" ]]; then
  echo "tasks root not found (relative to repo): ${TASKS_ROOT}" >&2
  exit 2
fi

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "env file not found: ${ENV_FILE} (create .env in repo root)" >&2
  exit 2
fi

# Collect task ids
TASK_IDS=()
if [[ -n "${TASKS_CSV}" ]]; then
  IFS=',' read -r -a _raw <<<"${TASKS_CSV}"
  for t in "${_raw[@]}"; do
    t="$(echo "$t" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
    [[ -n "$t" ]] && TASK_IDS+=("$t")
  done
fi
if [[ -n "${TASK_FILE}" ]]; then
  while IFS= read -r line || [[ -n "$line" ]]; do
    line="$(echo "$line" | sed 's/#.*//;s/^[[:space:]]*//;s/[[:space:]]*$//')"
    [[ -n "$line" ]] && TASK_IDS+=("$line")
  done < "${TASK_FILE}"
fi

TASK_ARGS=()
if [[ ${#TASK_IDS[@]} -gt 0 ]]; then
  for t in "${TASK_IDS[@]}"; do
    TASK_ARGS+=(--task-id "$t")
  done
elif [[ -z "${SUITE}" && -z "${RESUME}" ]]; then
  echo "Specify --tasks, --task-file, --suite, or --resume" >&2
  exit 2
fi

if [[ -z "${AGENT_CONFIG}" ]]; then
  if [[ -n "${ARM}" || -n "${COMPARE_ARMS}" || -n "${PROFILE}" ]]; then
    # Ablation / OpenHands profiles
    if [[ "${AGENT}" == openhands-agent || "${AGENT}" == openhands ]]; then
      AGENT_CONFIG="$(flb_ablation_agent_config)"
    else
      AGENT_CONFIG="$(flb_default_agent_config)"
    fi
  else
    AGENT_CONFIG="$(flb_default_agent_config)"
  fi
fi
if [[ ! -f "${AGENT_CONFIG}" ]]; then
  echo "agent config not found: ${AGENT_CONFIG}" >&2
  exit 2
fi

DOCKER_FLAGS=()
if [[ "${USE_DOCKER}" -eq 1 ]]; then
  DOCKER_FLAGS+=(
    --agent-docker
    --eval-docker
    --agent-docker-image "${AGENT_IMAGE}"
    --eval-docker-image "${EVAL_IMAGE}"
  )
fi

PROGRESS_FLAGS=()
if [[ "${NO_PROGRESS}" -eq 1 ]]; then
  PROGRESS_FLAGS+=(--no-progress)
fi

RESUME_FLAGS=()
if [[ -n "${RESUME}" ]]; then
  RESUME_FLAGS+=(--resume "${RESUME}")
fi

RETRY_STATUS_FLAGS=()
if [[ -n "${RETRY_ONLY_STATUS}" ]]; then
  RETRY_STATUS_FLAGS+=(--retry-only-status "${RETRY_ONLY_STATUS}")
fi

run_one() {
  local profile="$1"
  local arm_label="$2"
  local out="$3"
  local arm_flags=()
  case "${arm_label}" in
    entrypoint_hint|entrypoint-hint|hints)
      arm_flags+=(--agent-source-hints --no-agent-public-tests --prompt-style standard --source-context full_repository --no-td-cognition)
      ;;
    public_feedback|public-feedback|public)
      arm_flags+=(--no-agent-source-hints --agent-public-tests --prompt-style standard --source-context full_repository --no-td-cognition)
      ;;
    short|short_prompt|short-prompt)
      arm_flags+=(--no-agent-source-hints --no-agent-public-tests --prompt-style short --source-context full_repository --no-td-cognition)
      ;;
    pruned|pruned_context|pruned-context)
      arm_flags+=(--no-agent-source-hints --no-agent-public-tests --prompt-style standard --source-context pruned_context --no-td-cognition)
      ;;
    td|td_cognition|td-cognition|cognition)
      arm_flags+=(--no-agent-source-hints --no-agent-public-tests --prompt-style standard --source-context full_repository --td-cognition)
      ;;
    *)
      arm_flags+=(--no-agent-source-hints --no-agent-public-tests --prompt-style standard --source-context full_repository --no-td-cognition)
      ;;
  esac

  mkdir -p "$out"
  echo "============================================================"
  echo "FLB_ROOT=${FLB_ROOT}"
  echo "Python:  ${PYTHON}"
  echo "Agent:   ${AGENT}"
  echo "Profile: ${profile}  (arm=${arm_label})"
  echo "Config:  ${AGENT_CONFIG}"
  echo "Tasks:   ${TASKS_ROOT} (${#TASK_IDS[@]} explicit ids)"
  echo "Output:  ${out}"
  echo "Docker:  ${USE_DOCKER}"
  echo "============================================================"

  # Bash 3.2 treats "${EMPTY_ARRAY[@]}" as unbound under `set -u`. Build the
  # command incrementally so optional empty arrays remain portable on macOS.
  local run_command=(
    "${PYTHON}" -B -m featureliftbench.cli run-agent
    "${TASKS_ROOT}"
    --agent "${AGENT}"
    --agent-config "${AGENT_CONFIG}"
    --agent-profile "${profile}"
    --env-file "${ENV_FILE}"
    --num-workers "${WORKERS}"
    --timeout-seconds "${TIMEOUT}"
    --extra-agent-passes 0
    --max-task-attempts 1
    --output "${out}"
  )
  run_command+=("${arm_flags[@]}")
  if [[ "${#DOCKER_FLAGS[@]}" -gt 0 ]]; then
    run_command+=("${DOCKER_FLAGS[@]}")
  fi
  if [[ "${#PROGRESS_FLAGS[@]}" -gt 0 ]]; then
    run_command+=("${PROGRESS_FLAGS[@]}")
  fi
  if [[ "${#RESUME_FLAGS[@]}" -gt 0 ]]; then
    run_command+=("${RESUME_FLAGS[@]}")
  fi
  if [[ "${#RETRY_STATUS_FLAGS[@]}" -gt 0 ]]; then
    run_command+=("${RETRY_STATUS_FLAGS[@]}")
  fi
  if [[ "${#TASK_ARGS[@]}" -gt 0 ]]; then
    run_command+=("${TASK_ARGS[@]}")
  fi

  set +e
  "${run_command[@]}"
  local status=$?
  set -e

  if [[ -f "${out}/suite.json" ]]; then
    OUT_DIR="$out" "${PYTHON}" -B - <<'PY' || true
import json
import os
from pathlib import Path
p = Path(os.environ["OUT_DIR"]) / "suite.json"
data = json.loads(p.read_text())
summary = data.get("summary") or {}
ablation = None
for run in data.get("runs") or []:
    if isinstance(run, dict) and run.get("ablation"):
        ablation = run["ablation"]
        break
print("suite summary:", json.dumps(summary.get("by_status", summary), sort_keys=True))
if ablation:
    print("ablation sample:", json.dumps(ablation, sort_keys=True))
PY
  fi

  if [[ "$status" -ge 2 ]]; then
    echo "run-agent hard-failed (exit ${status})" >&2
    return "$status"
  fi
  echo "Finished arm=${arm_label} -> ${out} (exit ${status})"
  return 0
}

STAMP="$(date +%Y%m%d-%H%M%S)"
BASE_OUT_ROOT="experiments/ablation"

if [[ -n "${COMPARE_ARMS}" ]]; then
  IFS=',' read -r -a ARMS <<<"${COMPARE_ARMS}"
  COMPARE_ROOT="${OUTPUT:-${BASE_OUT_ROOT}/compare-${STAMP}}"
  mkdir -p "${COMPARE_ROOT}"
  echo "COMPARE_ROOT=${COMPARE_ROOT}" | tee "${COMPARE_ROOT}/ROOT.txt"
  overall=0
  for arm in "${ARMS[@]}"; do
    arm="$(echo "$arm" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
    [[ -z "$arm" ]] && continue
    profile="$(arm_to_profile "$arm")"
    out="${COMPARE_ROOT}/${arm}"
    if ! run_one "$profile" "$arm" "$out"; then
      overall=1
    fi
  done
  echo "Compare done under ${COMPARE_ROOT}"
  exit "$overall"
fi

if [[ -z "${PROFILE}" ]]; then
  if [[ -z "${ARM}" ]]; then
    ARM="main"
  fi
  PROFILE="$(arm_to_profile "${ARM}")"
fi

if [[ -n "${OUTPUT}" ]]; then
  OUT="${OUTPUT}"
elif [[ -n "${RESUME}" ]]; then
  OUT="${RESUME}"
else
  RUN_ID="${RUN_ID:-${ARM:-custom}-${STAMP}}"
  OUT="${BASE_OUT_ROOT}/${RUN_ID}"
fi

run_one "${PROFILE}" "${ARM:-custom}" "${OUT}"
