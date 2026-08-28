#!/usr/bin/env bash
# Runtime ablation: DeepSeek Harness or Codex on the Core-12 slice.
# Same Main information boundary + evaluator. Not Official Main / not Python-200 table.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

TASK_LIST="$ROOT/harness/config/experiments/runtime_ablation_core12_v1.txt"
AGENT_CONFIG="$ROOT/harness/config/agents.toml"
SLICE_NAME="core12"
RUNTIME_BIN="$ROOT/third_party/runtimes/bin"
export PATH="$RUNTIME_BIN:$PATH"

usage() {
  cat >&2 <<'EOF'
Usage:
  run_runtime_ablation.sh <adapter> <profile> [run-id] [options]

Adapters:
  deepseek-harness    pinned dsh --profile headless (same CLI level as OpenHands)
  codex               pinned codex exec (non-interactive)

Options:
  --execute             Execute model calls; otherwise print a validated plan.
  --slice NAME          core12 (default) or a task-id list file path
  --resume DIR          Resume an existing suite output directory.
  --workers N           Parallel task workers (default: 1).
  --timeout SEC         Per-task wall timeout (default: 3600).
  --eval-image IMAGE    Eval image (default: featureliftbench-eval:latest).
  --agent-docker        Run the runtime inside FEATURELIFTBENCH_AGENT_DOCKER_IMAGE.
                        Rebuild that image with FEATURELIFTBENCH_INSTALL_RUNTIME_AGENTS=1.

Examples:
  ./harness/scripts/run_runtime_ablation.sh deepseek-harness dsh_deepseek_v4_flash_main
  ./harness/scripts/run_runtime_ablation.sh codex codex_gpt_main runtime-codex-core12 --execute
EOF
}

if [[ $# -lt 2 ]]; then
  usage
  exit 2
fi

ADAPTER="$1"
PROFILE="$2"
shift 2

case "$ADAPTER" in
  deepseek-harness|codex) ;;
  *) echo "Unsupported adapter: $ADAPTER" >&2; usage; exit 2 ;;
esac

resolve_python() {
  local candidate
  for candidate in \
    "${PYTHON:-}" \
    "$ROOT/.venv/bin/python" \
    "$(command -v python3.12 2>/dev/null || true)" \
    "$(command -v python3.11 2>/dev/null || true)" \
    "$(command -v python3 2>/dev/null || true)"
  do
    if [[ -n "$candidate" && -x "$candidate" ]] && "$candidate" -c \
      'import sys; assert sys.version_info >= (3, 11)' 2>/dev/null; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done
  echo "Python 3.11+ is required; set PYTHON=/path/to/python." >&2
  return 1
}

PYTHON="$(resolve_python)"
if [[ ! -f "$AGENT_CONFIG" ]]; then
  echo "Missing $AGENT_CONFIG; run ./setup.sh or copy agents.example.toml." >&2
  exit 2
fi

EXECUTE=0
RESUME_DIR=""
WORKERS="${NUM_WORKERS:-1}"
TIMEOUT="${TIMEOUT_SECONDS:-3600}"
EVAL_IMAGE="${FEATURELIFTBENCH_EVAL_DOCKER_IMAGE:-featureliftbench-eval:latest}"
AGENT_DOCKER=0
RUN_ID=""
RUN_ID_SET=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --execute) EXECUTE=1; shift ;;
    --slice)
      SLICE_NAME="${2:?--slice requires a value}"
      if [[ -f "$SLICE_NAME" ]]; then
        TASK_LIST="$SLICE_NAME"
        SLICE_NAME="$(basename "$TASK_LIST" .txt)"
      elif [[ "$SLICE_NAME" == "core12" ]]; then
        TASK_LIST="$ROOT/harness/config/experiments/runtime_ablation_core12_v1.txt"
      else
        echo "Unknown slice: $SLICE_NAME" >&2
        exit 2
      fi
      shift 2
      ;;
    --resume) RESUME_DIR="${2:?--resume requires a directory}"; shift 2 ;;
    --workers) WORKERS="${2:?--workers requires a value}"; shift 2 ;;
    --timeout) TIMEOUT="${2:?--timeout requires a value}"; shift 2 ;;
    --eval-image) EVAL_IMAGE="${2:?--eval-image requires a value}"; shift 2 ;;
    --agent-docker) AGENT_DOCKER=1; shift ;;
    --help|-h) usage; exit 0 ;;
    -*) echo "Unknown option: $1" >&2; usage; exit 2 ;;
    *)
      [[ "$RUN_ID_SET" -eq 0 ]] || { echo "Only one run-id is allowed." >&2; exit 2; }
      RUN_ID="$1"; RUN_ID_SET=1; shift ;;
  esac
done

[[ "$WORKERS" =~ ^[1-9][0-9]*$ ]] || { echo "--workers must be positive" >&2; exit 2; }
[[ "$TIMEOUT" =~ ^[1-9][0-9]*$ ]] || { echo "--timeout must be positive" >&2; exit 2; }

RUNTIME_BIN_NAME="dsh"
if [[ "$ADAPTER" == "codex" ]]; then
  RUNTIME_BIN_NAME="codex"
fi
if [[ "$AGENT_DOCKER" -eq 0 && ! -x "$RUNTIME_BIN/$RUNTIME_BIN_NAME" && -z "$(command -v "$RUNTIME_BIN_NAME" || true)" ]]; then
  echo "Installing pinned $ADAPTER CLI..."
  PYTHONPATH="$ROOT/harness${PYTHONPATH:+:$PYTHONPATH}" \
    "$PYTHON" -m featureliftbench.runtime_install "$ADAPTER"
fi

PROFILE_INFO="$(
  PROFILE_NAME="$PROFILE" AGENT_CONFIG="$AGENT_CONFIG" ADAPTER="$ADAPTER" "$PYTHON" - <<'PY'
import os
import tomllib
from pathlib import Path

data = tomllib.loads(Path(os.environ["AGENT_CONFIG"]).read_text(encoding="utf-8"))
name = os.environ["PROFILE_NAME"]
adapter = os.environ["ADAPTER"]
profile = (data.get("profiles") or {}).get(name)
if not isinstance(profile, dict):
    raise SystemExit(f"Unknown profile: {name}")
if bool(profile.get("mount_public_tests", False)):
    raise SystemExit(f"Runtime ablation cannot expose public tests: {name}")
if bool(profile.get("expose_source_hints", False)):
    raise SystemExit(f"Runtime ablation cannot expose source hints: {name}")
if str(profile.get("prompt_style", "standard")).lower() != "standard":
    raise SystemExit(f"Runtime ablation requires prompt_style=standard: {name}")
if str(profile.get("source_context", "full_repository")).lower() != "full_repository":
    raise SystemExit(f"Runtime ablation requires source_context=full_repository: {name}")
model = str(profile.get("model", "")).strip()
if not model:
    raise SystemExit(f"Profile is missing model: {name}")
print(f"{model}\t{adapter}")
PY
)"
MODEL="${PROFILE_INFO%%$'\t'*}"
MODEL_SLUG="$(printf '%s' "$MODEL" | tr '[:upper:]' '[:lower:]' | sed 's#^openai/##; s#^deepseek/##; s#[^a-z0-9._-]#-#g')"

if [[ -z "$RUN_ID" ]]; then
  RUN_ID="runtime-${ADAPTER}-${MODEL_SLUG}-${SLICE_NAME}-$(date +%Y%m%d-%H%M%S)"
fi

TASK_IDS=()
while IFS= read -r task_id; do
  [[ -n "$task_id" ]] || continue
  TASK_IDS+=("$task_id")
done < <(grep -vE '^\s*(#|$)' "$TASK_LIST")
if [[ ${#TASK_IDS[@]} -eq 0 ]]; then
  echo "No task ids in $TASK_LIST" >&2
  exit 2
fi

if [[ -n "$RESUME_DIR" ]]; then
  OUTPUT_DIR="$(cd "$(dirname "$RESUME_DIR")" && pwd)/$(basename "$RESUME_DIR")"
else
  OUTPUT_DIR="$ROOT/experiments/python/runtime/${ADAPTER}/${MODEL_SLUG}/$RUN_ID"
fi

TASK_ARGS=()
for task_id in "${TASK_IDS[@]}"; do TASK_ARGS+=(--task-id "$task_id"); done

COMMAND=(
  "$PYTHON" -B -m featureliftbench.cli run-agent benchmark/python200_tasks
  --agent "$ADAPTER"
  --agent-config harness/config/agents.toml
  --agent-profile "$PROFILE"
  --no-agent-public-tests
  --no-agent-source-hints
  --prompt-style standard
  --source-context full_repository
  --env-file .env
  --num-workers "$WORKERS"
  --timeout-seconds "$TIMEOUT"
  --retry-rate-limit 1
  --extra-agent-passes 0
  --max-task-attempts 1
  --eval-docker --eval-docker-image "$EVAL_IMAGE"
  --output "$OUTPUT_DIR"
)
if [[ "$AGENT_DOCKER" -eq 1 ]]; then
  AGENT_IMAGE="${FEATURELIFTBENCH_AGENT_DOCKER_IMAGE:-featureliftbench-agent:latest}"
  COMMAND+=(--agent-docker --agent-docker-image "$AGENT_IMAGE")
fi
COMMAND+=("${TASK_ARGS[@]}")

echo "Runtime ablation (not Official Main / not Python-200 table)"
echo "  adapter:  $ADAPTER"
echo "  profile:  $PROFILE"
echo "  model:    $MODEL"
echo "  slice:    $SLICE_NAME (${#TASK_IDS[@]} tasks)"
echo "  output:   $OUTPUT_DIR"
echo "  eval:     $EVAL_IMAGE"
if [[ "$AGENT_DOCKER" -eq 1 ]]; then
  echo "  agent:    docker ($AGENT_IMAGE)"
else
  echo "  agent:    host CLI ($RUNTIME_BIN/$RUNTIME_BIN_NAME or PATH)"
fi
echo
printf ' %q' "${COMMAND[@]}"
echo
echo

if [[ "$EXECUTE" -ne 1 ]]; then
  echo "Plan only. Re-run with --execute to start."
  exit 0
fi

export FEATURELIFTBENCH_SOURCE_REGISTRY="$ROOT/benchmark/sources/python200_registry.json"
export FEATURELIFTBENCH_MOUNT_PUBLIC_TESTS=0
export FEATURELIFTBENCH_PROMPT_STYLE=standard
export FEATURELIFTBENCH_EXPOSE_SOURCE_HINTS=0
export FEATURELIFTBENCH_SOURCE_CONTEXT=full_repository
mkdir -p "$OUTPUT_DIR"
exec "${COMMAND[@]}"
