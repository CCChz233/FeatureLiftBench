#!/usr/bin/env bash
# One-shot bootstrap for a fresh clone (local or server).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$ROOT/harness/scripts/server_setup.sh"
