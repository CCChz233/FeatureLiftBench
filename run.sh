#!/usr/bin/env bash
# Full 50-hard run: DeepSeek V4 Pro (mini-swe-agent + --yolo)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

export PYTHONPATH="${PYTHONPATH:-$ROOT/harness}"

if [[ -n "${PYTHON:-}" ]]; then
  :
elif [[ -x "$ROOT/.venv/bin/python" ]]; then
  PYTHON="$ROOT/.venv/bin/python"
elif command -v python3.12 >/dev/null 2>&1; then
  PYTHON=python3.12
else
  PYTHON=python3
fi

RUN_ID="${RUN_ID:-benchmark-50-hard-pro-$(date +%Y%m%d-%H%M%S)}"
OUTPUT="experiments/mini-swe-agent/${RUN_ID}"

echo "Profile: deepseek_v4_pro"
echo "Output:  ${OUTPUT}"
echo "Python:  $PYTHON"
echo "Workers: ${NUM_WORKERS:-4}"

$PYTHON -B -m featureliftbench.cli run-agent benchmark/tasks \
  --agent mini-swe-agent \
  --agent-config harness/config/agents.toml \
  --agent-profile deepseek_v4_pro \
  --env-file .env \
  --yolo \
  --num-workers "${NUM_WORKERS:-4}" \
  --retry-rate-limit 2 \
  --no-progress \
  --output "${OUTPUT}"

$PYTHON harness/scripts/analyze_benchmark_suite.py "${OUTPUT}"
$PYTHON harness/scripts/report_entanglement_coverage.py --suite-dir "${OUTPUT}"

echo "Done: ${OUTPUT}"
