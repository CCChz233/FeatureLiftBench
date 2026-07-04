#!/usr/bin/env bash
# Preflight checks for Go OpenHands agent experiments.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH=harness
PY="${PYTHON:-python3}"

FAIL=0
pass() { echo "[OK] $*"; }
warn() { echo "[WARN] $*"; }
fail() { echo "[FAIL] $*"; FAIL=1; }

echo "=== Go OpenHands preflight ==="

if command -v openhands >/dev/null 2>&1; then
  pass "openhands: $(command -v openhands) ($(openhands --version 2>/dev/null || echo version_unknown))"
else
  fail "openhands not in PATH"
fi

if command -v go >/dev/null 2>&1; then
  pass "go: $(go version)"
else
  warn "go not on host PATH (agent may fail go test in workspace; Docker eval still works)"
fi

if docker image inspect featureliftbench-eval:latest >/dev/null 2>&1; then
  pass "docker image featureliftbench-eval:latest"
else
  fail "missing featureliftbench-eval:latest (run docker/build_eval_image.sh)"
fi

if [[ -f .env ]]; then
  pass ".env present"
else
  warn ".env missing (need LLM_API_KEY / API base for --override-with-envs)"
fi

if [[ -f harness/config/agents.toml ]]; then
  pass "harness/config/agents.toml"
elif [[ -f harness/config/agents.example.toml ]]; then
  warn "only agents.example.toml (optional for OpenHands)"
fi

GOLD_READY=0
for task_dir in benchmark/go/tasks/*/; do
  tid=$(basename "$task_dir")
  repo="$task_dir/repo"
  [[ -d "$repo" ]] || continue
  n=$(find "$repo" -maxdepth 1 -name '*.go' | wc -l)
  if [[ "$n" -eq 1 && -f "$repo/add.go" ]]; then
    continue
  fi
  GOLD_READY=$((GOLD_READY + 1))
  pass "gold-ready task: $tid"
done
if [[ "$GOLD_READY" -eq 0 ]]; then
  fail "no gold-ready Go tasks found"
fi

echo "=== mechanical gate spot-check: semver ==="
if [[ "${SKIP_GATE:-0}" == "1" ]]; then
  warn "SKIP_GATE=1: skipping run_go_pilot_review"
elif bash harness/scripts/run_go_pilot_review.sh semver__version_parse_core__001 --docker >/tmp/flb-preflight-gate.log 2>&1; then
  pass "semver gate review"
else
  fail "semver gate review (see /tmp/flb-preflight-gate.log)"
fi

if [[ "$FAIL" -ne 0 ]]; then
  echo "Preflight FAILED"
  exit 1
fi
echo "Preflight PASSED"
