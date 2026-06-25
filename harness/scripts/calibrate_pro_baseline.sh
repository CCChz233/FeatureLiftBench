#!/usr/bin/env bash
# Run Pro baseline on the main hard benchmark (benchmark/tasks/).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
exec "$ROOT/harness/scripts/run_baseline.sh" deepseek_v4_pro "$@"
