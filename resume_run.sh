#!/usr/bin/env bash
# Resume an interrupted suite run (same output dir, --resume).
#
# Usage:
#   RESUME_DIR=experiments/mini-swe-agent/<run_id> bash resume_run.sh
#   nohup bash resume_run.sh > experiments/mini-swe-agent/<run_id>-resume.log 2>&1 &
#
# See RUN.md §4 and docs/WINDOWS.md §4.3.
set -euo pipefail
echo "DEPRECATED: resume_run.sh resumes the legacy run.sh path; use ./scripts/run_benchmark.sh --resume DIR." >&2
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

if [[ -z "${RESUME_DIR:-}" ]]; then
  echo "ERROR: set RESUME_DIR to the existing run directory." >&2
  echo "Example: RESUME_DIR=experiments/mini-swe-agent/benchmark-main-flash-20260703-122657 bash resume_run.sh" >&2
  exit 1
fi

sed -i 's/\r$//' run.sh harness/scripts/wsl_docker_setup.sh 2>/dev/null || true
source harness/scripts/wsl_docker_setup.sh
export PYTHONPATH=harness
export FEATURELIFTBENCH_AGENT_DOCKER=1
export FEATURELIFTBENCH_EVAL_DOCKER=1
export AGENT_PROFILE="${AGENT_PROFILE:-deepseek_v4_flash}"
export NUM_WORKERS="${NUM_WORKERS:-1}"
export RETRY_RATE_LIMIT="${RETRY_RATE_LIMIT:-5}"

LOG="${RESUME_LOG:-experiments/mini-swe-agent/$(basename "$RESUME_DIR")-resume.log}"
mkdir -p "$(dirname "$LOG")"
echo "Resume: $RESUME_DIR -> log: $LOG"
exec bash run.sh >> "$LOG" 2>&1
