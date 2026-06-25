#!/usr/bin/env bash
# Run a 50-hard baseline for any agent profile in harness/config/agents.toml.
#
# Usage:
#   ./harness/scripts/run_baseline.sh <profile> [run_id]
#   ./harness/scripts/run_baseline.sh nex_n2_pro
#   NUM_WORKERS=2 ./harness/scripts/run_baseline.sh deepseek_v4_flash my-run-001
#
# Extra args after run_id are passed to featureliftbench.cli run-agent.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <agent-profile> [run_id] [extra run-agent args...]" >&2
  exit 1
fi

PROFILE="$1"
shift

PYTHON="${PYTHON:-/Users/chz/anaconda3/bin/python3.12}"
RUN_ID="${1:-benchmark-50-hard-${PROFILE}-$(date +%Y%m%d-%H%M%S)}"
if [[ $# -gt 0 ]]; then
  shift
fi

OUTPUT_DIR="${ROOT}/experiments/mini-swe-agent/${RUN_ID}"

echo "Profile: ${PROFILE}"
echo "Main hard tasks:"
"$PYTHON" harness/scripts/list_tasks.py --paths

"$PYTHON" -B -m featureliftbench.cli run-agent benchmark/tasks \
  --agent mini-swe-agent \
  --agent-config harness/config/agents.toml \
  --agent-profile "$PROFILE" \
  --env-file .env \
  --yolo \
  --num-workers "${NUM_WORKERS:-4}" \
  --output "$OUTPUT_DIR" \
  "$@"

"$PYTHON" harness/scripts/analyze_benchmark_suite.py "$OUTPUT_DIR"
"$PYTHON" harness/scripts/report_entanglement_coverage.py --suite-dir "$OUTPUT_DIR"

echo "Suite output: $OUTPUT_DIR"
