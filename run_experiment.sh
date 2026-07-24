#!/usr/bin/env bash
# Convenience entrypoint at repo root (path-independent).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "${ROOT}/scripts/run_experiment.sh" "$@"
