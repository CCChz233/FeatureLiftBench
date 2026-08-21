#!/usr/bin/env bash
# Checkout pinned DeepSeek Harness and Codex sources. Does not merge into Main.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PINS="$ROOT/harness/config/runtime_pins.json"
DEST_ROOT="$ROOT/third_party/runtimes"

usage() {
  cat >&2 <<'EOF'
Usage:
  pin_runtime_agents.sh [deepseek-harness|codex|all]
EOF
}

TARGET="${1:-all}"
if [[ "$TARGET" != "all" && "$TARGET" != "deepseek-harness" && "$TARGET" != "codex" ]]; then
  usage
  exit 2
fi

python3 - "$PINS" "$DEST_ROOT" "$TARGET" <<'PY'
import json
import subprocess
import sys
from pathlib import Path

pins_path = Path(sys.argv[1])
dest_root = Path(sys.argv[2])
target = sys.argv[3]
data = json.loads(pins_path.read_text(encoding="utf-8"))
runtimes = data["runtimes"]
selected = list(runtimes) if target == "all" else [target]
dest_root.mkdir(parents=True, exist_ok=True)

for name in selected:
    spec = runtimes[name]
    dest = Path(spec["checkout"])
    if not dest.is_absolute():
        dest = pins_path.parents[2] / dest
    repo = spec["repository"]
    commit = spec["commit"]
    tag = spec["tag"]
    if dest.exists() and (dest / ".git").exists():
        subprocess.check_call(["git", "-C", str(dest), "fetch", "--tags", "origin"])
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            raise SystemExit(f"{dest} exists but is not a git checkout")
        subprocess.check_call(["git", "clone", repo, str(dest)])
    subprocess.check_call(["git", "-C", str(dest), "checkout", "--detach", commit])
    head = subprocess.check_output(
        ["git", "-C", str(dest), "rev-parse", "HEAD"], text=True
    ).strip()
    if head != commit:
        raise SystemExit(f"{name} HEAD {head} != pinned {commit}")
    print(f"pinned {name}: {tag} @ {head} -> {dest}")
PY
