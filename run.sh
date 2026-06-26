#!/usr/bin/env bash
# Full 50-hard run: DeepSeek V4 Pro (mini-swe-agent + --yolo)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

export PYTHONPATH="${PYTHONPATH:-$ROOT/harness}"
export PATH="$ROOT/.venv/bin:${PATH}"

if [[ -n "${PYTHON:-}" ]]; then
  :
elif [[ -x "$ROOT/.venv/bin/python" ]]; then
  PYTHON="$ROOT/.venv/bin/python"
elif command -v python3.12 >/dev/null 2>&1; then
  PYTHON=python3.12
else
  PYTHON=python3
fi

AGENT_PROFILE="${AGENT_PROFILE:-deepseek_v4_pro}"

"$PYTHON" "$ROOT/harness/scripts/preflight.py" \
  --bootstrap \
  --agent-profile "$AGENT_PROFILE" \
  ${MINI_BIN:+--mini-bin "$MINI_BIN"}

if [[ -n "${RESUME_DIR:-}" ]]; then
  OUTPUT="${RESUME_DIR}"
  RESUME_FLAG=(--resume)
else
  RUN_ID="${RUN_ID:-benchmark-50-hard-pro-$(date +%Y%m%d-%H%M%S)}"
  OUTPUT="experiments/mini-swe-agent/${RUN_ID}"
  RESUME_FLAG=()
fi

EXTRA_AGENT_PASSES="${EXTRA_AGENT_PASSES:-0}"

echo "Profile: ${AGENT_PROFILE}"
echo "Output:  ${OUTPUT}"
echo "Python:  $PYTHON"
echo "Workers: ${NUM_WORKERS:-4}"
if [[ "${#RESUME_FLAG[@]}" -gt 0 ]]; then
  echo "Resume:  yes"
fi
if [[ "${EXTRA_AGENT_PASSES}" != "0" ]]; then
  echo "Extra agent passes: ${EXTRA_AGENT_PASSES}"
fi

$PYTHON -B -m featureliftbench.cli run-agent benchmark/tasks \
  --agent mini-swe-agent \
  --agent-config harness/config/agents.toml \
  --agent-profile "${AGENT_PROFILE}" \
  --env-file .env \
  --yolo \
  --num-workers "${NUM_WORKERS:-4}" \
  --retry-rate-limit 2 \
  --extra-agent-passes "${EXTRA_AGENT_PASSES}" \
  --no-progress \
  --output "${OUTPUT}" \
  "${RESUME_FLAG[@]}"

$PYTHON harness/scripts/analyze_benchmark_suite.py "${OUTPUT}"
$PYTHON harness/scripts/report_entanglement_coverage.py --suite-dir "${OUTPUT}"

echo "Done: ${OUTPUT}"
