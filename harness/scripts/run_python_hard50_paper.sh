#!/usr/bin/env bash
# Prepare or explicitly execute one frozen-paper OpenHands run on hard-extension-50.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

usage() {
  echo "Usage: $0 <agent-profile> [run-id] [--execute]" >&2
  echo "Without --execute, prints the selected task count and command without calling an API." >&2
}

if [[ $# -lt 1 ]]; then
  usage
  exit 2
fi

PROFILE="$1"
shift
case "$PROFILE" in
  openhands_qwen3_6_27b_fp8_paper)
    MODEL_SLUG="qwen3.6-27b-fp8"
    ;;
  openhands_qwen3_6_35b_a3b_fp8_paper)
    MODEL_SLUG="qwen3.6-35b-a3b-fp8"
    ;;
  openhands_qwen3_coder_30b_paper)
    MODEL_SLUG="qwen3-coder-30b-a3b-instruct"
    ;;
  *)
    echo "Unsupported frozen-paper profile: $PROFILE" >&2
    usage
    exit 2
    ;;
esac

RUN_ID="hard50-${MODEL_SLUG}-$(date +%Y%m%d-%H%M%S)"
if [[ $# -gt 0 && "$1" != "--execute" ]]; then
  RUN_ID="$1"
  shift
fi

EXECUTE=0
if [[ $# -gt 0 && "$1" == "--execute" ]]; then
  EXECUTE=1
  shift
fi
if [[ $# -ne 0 ]]; then
  usage
  exit 2
fi

PYTHON="${PYTHON:-$ROOT/.venv/bin/python}"
if [[ ! -x "$PYTHON" ]]; then
  PYTHON="python3"
fi
SELECTOR="$ROOT/.agents/skills/featureliftbench-run-eval/scripts/select_featurelift_tasks.py"
TASK_IDS=()
while IFS= read -r task_id; do
  TASK_IDS+=("$task_id")
done < <("$PYTHON" "$SELECTOR" --suite batch3-main --format ids)
if [[ "${#TASK_IDS[@]}" -ne 50 ]]; then
  echo "Expected hard-extension-50, selected ${#TASK_IDS[@]} tasks" >&2
  exit 1
fi

OUTPUT_DIR="$ROOT/experiments/python/openhands/$MODEL_SLUG/$RUN_ID"
TASK_ARGS=()
for task_id in "${TASK_IDS[@]}"; do
  TASK_ARGS+=(--task-id "$task_id")
done

COMMAND=(
  "$PYTHON" -B -m featureliftbench.cli run-agent benchmark/tasks
  --agent openhands-agent
  --agent-config harness/config/agents.toml
  --agent-profile "$PROFILE"
  --env-file .env
  --num-workers 1
  --retry-rate-limit 5
  --agent-docker
  --eval-docker
  --output "$OUTPUT_DIR"
  "${TASK_ARGS[@]}"
)

echo "Profile: $PROFILE"
echo "Selected: ${#TASK_IDS[@]} hard-extension tasks"
echo "Output: $OUTPUT_DIR"
printf 'Command:'
printf ' %q' "${COMMAND[@]}"
printf '\n'

if [[ "$EXECUTE" -ne 1 ]]; then
  echo "Plan only. Re-run with --execute after approving API/data transmission and cost."
  exit 0
fi

PYTHONPATH="$ROOT/harness${PYTHONPATH:+:$PYTHONPATH}" "${COMMAND[@]}"
PYTHONPATH="$ROOT/harness${PYTHONPATH:+:$PYTHONPATH}" \
  "$PYTHON" harness/scripts/analyze_benchmark_suite.py "$OUTPUT_DIR"
