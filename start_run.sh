#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

sed -i 's/\r$//' run.sh harness/scripts/wsl_docker_setup.sh 2>/dev/null || true

export FEATURELIFTBENCH_AGENT_DOCKER=1
export FEATURELIFTBENCH_EVAL_DOCKER=1
export AGENT_PROFILE="${AGENT_PROFILE:-deepseek_v4_flash}"
export NUM_WORKERS="${NUM_WORKERS:-1}"
export RETRY_RATE_LIMIT="${RETRY_RATE_LIMIT:-5}"
export RUN_ID="${RUN_ID:-benchmark-main-flash-$(date +%Y%m%d-%H%M%S)}"

LOG="experiments/mini-swe-agent/${RUN_ID}.log"
mkdir -p experiments/mini-swe-agent

echo "Starting run: ${RUN_ID}"
echo "Log: ${LOG}"
nohup bash run.sh > "${LOG}" 2>&1 &
echo "PID=$!"
echo "RUN_ID=${RUN_ID}"
