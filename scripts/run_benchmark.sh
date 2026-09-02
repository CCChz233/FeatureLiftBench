#!/usr/bin/env bash
# First-class FeatureLiftBench entry: benchmark × agent × method.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec "${ROOT}/scripts/run_experiment.sh" "$@"
