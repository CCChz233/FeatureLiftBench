#!/usr/bin/env bash
set -euo pipefail

exec python -B -m featureliftbench.cli "$@"
