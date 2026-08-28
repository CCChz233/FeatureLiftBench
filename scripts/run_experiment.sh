#!/usr/bin/env bash
# Path-independent FeatureLiftBench experiment runner.
#
# Experiments are benchmark × agent × method. Catalogs:
#   benchmark/suites.toml  agent/registry.toml  method/registry.toml
#
# Usage (from anywhere, after cloning the repo):
#   ./scripts/run_benchmark.sh --benchmark python200_hard --agent openhands --method main
#   ./run_experiment.sh --arm main --tasks iniconfig__parse_config__001
#   ./run_experiment.sh --compare-methods main,entrypoint_hint \
#       --tasks iniconfig__parse_config__001
#   ./run_experiment.sh --suite sanity --method main
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
FeatureLiftBench experiment runner (benchmark × agent × method)

Usage:
  ./scripts/run_benchmark.sh --benchmark python200_hard --agent openhands --method main [options]
  ./scripts/run_experiment.sh --method main --suite sanity [options]

Catalog (list ids):
  PYTHONPATH=harness python -B -m featureliftbench.cli catalog list
  PYTHONPATH=harness python -B -m featureliftbench.cli catalog check

Benchmark:
  --benchmark python200_hard|python150|hard50|python200_legacy|sanity|staging|batch3_pilot
      Named suite from benchmark/suites.toml (sets --tasks-root and --source-registry)
  --suite sanity|main|staging|pilot
      Legacy alias. `main` means python150, not the paper Python-200' suite.
  --tasks-root REL_PATH        Override suite root. Default: benchmark/tasks
  --source-registry REL_PATH   Override the canonical source registry
  --tasks id1,id2,...          Comma-separated task ids under --tasks-root
  --task-file PATH             File with one task id per line (# comments ok)

Agent:
  --agent NAME                 Registry id or CLI name. Default: openhands-agent
                               openhands | deepseek-harness | codex | mini-swe-agent | ...
  --agent-config REL_PATH      Default: agents.example.toml for methods; else agents.toml
  --profile NAME               Explicit --agent-profile (overrides method mapping)

Method:
  --method NAME                Registry id from method/registry.toml. Default: main
  --arm NAME                   Alias of --method (kept for old scripts)
  --compare-methods a,b,c      Run the same tasks once per method (sequential)
  --compare-arms a,b,c         Alias of --compare-methods

Agent / eval:
  --env-file REL_PATH          Default: .env
  --docker / --no-docker       Default: --docker (agent+eval docker)
  --agent-image NAME           Default: featureliftbench-agent:latest
  --eval-image NAME            Default: featureliftbench-eval:latest
  --workers N                  Default: 1
  --timeout SEC                Default: 3600
  --retry-only-status LIST     Resume-only statuses to rerun
  --no-progress

Output:
  --output REL_OR_ABS          Suite output dir (default under experiments/methods/ablation/...)
  --run-id NAME                Used when --output omitted
  --resume DIR                 Resume an existing suite dir

Examples:
  ./scripts/run_benchmark.sh --benchmark python200_hard --agent openhands --method main \
      --docker --workers 1 --timeout 3600
  ./run_experiment.sh --method main --tasks iniconfig__parse_config__001
  ./run_experiment.sh --compare-methods main,entrypoint_hint,public_feedback,short_prompt \
      --tasks iniconfig__parse_config__001
  ./run_experiment.sh --suite sanity --method main --docker
EOF
}

ARM=""
PROFILE=""
COMPARE_ARMS=""
TASKS_CSV=""
TASK_FILE=""
SUITE=""
BENCHMARK=""
TASKS_ROOT="benchmark/tasks"
TASKS_ROOT_SET=0
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
SOURCE_REGISTRY=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    --arm|--method) ARM="$2"; shift 2 ;;
    --profile) PROFILE="$2"; shift 2 ;;
    --compare-arms|--compare-methods) COMPARE_ARMS="$2"; shift 2 ;;
    --tasks) TASKS_CSV="$2"; shift 2 ;;
    --task-file) TASK_FILE="$2"; shift 2 ;;
    --suite) SUITE="$2"; shift 2 ;;
    --benchmark) BENCHMARK="$2"; shift 2 ;;
    --tasks-root) TASKS_ROOT="$2"; TASKS_ROOT_SET=1; shift 2 ;;
    --source-registry) SOURCE_REGISTRY="$2"; shift 2 ;;
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

catalog() {
  "${PYTHON}" -B -m featureliftbench.cli catalog "$@"
}

if [[ "${SUITE}" == "main" ]]; then
  SUITE="python150"
fi
if [[ -n "${SUITE}" && -n "${BENCHMARK}" && "${SUITE}" != "${BENCHMARK}" ]]; then
  echo "Use either --benchmark or --suite, not both (${BENCHMARK} vs ${SUITE})" >&2
  exit 2
fi
if [[ -z "${BENCHMARK}" && -n "${SUITE}" ]]; then
  BENCHMARK="${SUITE}"
fi

if [[ -n "${BENCHMARK}" ]]; then
  eval "$(catalog suite --benchmark "${BENCHMARK}" --format bash)"
  if [[ "${TASKS_ROOT_SET}" -eq 0 ]]; then
    TASKS_ROOT="${CATALOG_TASKS_ROOT}"
  fi
  if [[ -z "${SOURCE_REGISTRY}" ]]; then
    SOURCE_REGISTRY="${CATALOG_SOURCE_REGISTRY}"
  fi
  SUITE="${CATALOG_BENCHMARK_ID}"
fi

eval "$(catalog agent --agent "${AGENT}" --format bash)"
AGENT="${CATALOG_AGENT_CLI}"
AGENT_ID="${CATALOG_AGENT_ID}"

method_profile() {
  catalog profile --agent "${AGENT_ID}" --method "$1"
}

method_flags() {
  catalog flags --method "$1"
}

if [[ -z "${SOURCE_REGISTRY}" ]]; then
  if [[ "${TASKS_ROOT}" == "benchmark/staging" ]]; then
    SOURCE_REGISTRY="benchmark/sources/external50_registry.json"
  else
    SOURCE_REGISTRY="benchmark/sources/registry.json"
  fi
fi

if [[ ! -f "${SOURCE_REGISTRY}" ]]; then
  echo "source registry not found: ${SOURCE_REGISTRY}" >&2
  exit 2
fi
export FEATURELIFTBENCH_SOURCE_REGISTRY="${SOURCE_REGISTRY}"

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
  echo "Specify --tasks, --task-file, --benchmark, --suite, or --resume" >&2
  exit 2
fi

if [[ -z "${AGENT_CONFIG}" ]]; then
  if [[ -n "${ARM}" || -n "${COMPARE_ARMS}" || -n "${PROFILE}" ]]; then
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
  local flag
  while IFS= read -r flag; do
    [[ -n "${flag}" ]] && arm_flags+=("${flag}")
  done < <(method_flags "${arm_label}")

  mkdir -p "$out"
  echo "============================================================"
  echo "FLB_ROOT=${FLB_ROOT}"
  echo "Python:  ${PYTHON}"
  echo "Agent:   ${AGENT} (${AGENT_ID})"
  echo "Method:  ${arm_label}"
  echo "Profile: ${profile}"
  echo "Config:  ${AGENT_CONFIG}"
  echo "Tasks:   ${TASKS_ROOT} (${#TASK_IDS[@]} explicit ids)"
  echo "Sources: ${SOURCE_REGISTRY}"
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
  echo "Finished method=${arm_label} -> ${out} (exit ${status})"
  return 0
}

STAMP="$(date +%Y%m%d-%H%M%S)"
BASE_OUT_ROOT="experiments/methods/ablation"

if [[ -n "${COMPARE_ARMS}" ]]; then
  IFS=',' read -r -a ARMS <<<"${COMPARE_ARMS}"
  COMPARE_ROOT="${OUTPUT:-${BASE_OUT_ROOT}/compare-${STAMP}}"
  mkdir -p "${COMPARE_ROOT}"
  echo "COMPARE_ROOT=${COMPARE_ROOT}" | tee "${COMPARE_ROOT}/ROOT.txt"
  overall=0
  for arm in "${ARMS[@]}"; do
    arm="$(echo "$arm" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
    [[ -z "$arm" ]] && continue
    profile="$(method_profile "$arm")"
    out="${COMPARE_ROOT}/${arm}"
    if ! run_one "$profile" "$arm" "$out"; then
      overall=1
    fi
  done
  echo "Compare done under ${COMPARE_ROOT}"
  exit "$overall"
fi

if [[ -z "${ARM}" ]]; then
  ARM="main"
fi
if [[ -z "${PROFILE}" ]]; then
  PROFILE="$(method_profile "${ARM}")"
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
