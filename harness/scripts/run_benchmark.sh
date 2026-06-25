#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

RUN_ID="${1:-benchmark-$(date +%Y%m%d-%H%M%S)}"
if [[ $# -gt 0 ]]; then
  shift
fi

OUTPUT_DIR="${ROOT}/experiments/mini-swe-agent/${RUN_ID}"

python3 -B -m featureliftbench.cli run-agent benchmark/tasks \
  --agent mini-swe-agent \
  --agent-config harness/config/agents.toml \
  --agent-profile deepseek_v4_flash \
  --env-file .env \
  --yolo \
  --num-workers "${NUM_WORKERS:-4}" \
  --output "$OUTPUT_DIR" \
  "$@"

echo "Suite output: $OUTPUT_DIR"
