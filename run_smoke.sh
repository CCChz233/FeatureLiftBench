#!/usr/bin/env bash
set -euo pipefail
echo "DEPRECATED: this WSL-specific smoke wrapper is historical; use featureliftbench smoke or ./scripts/run_benchmark.sh --benchmark sanity." >&2
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

DOCKER_BIN="$HOME/.flb-docker-bin"
mkdir -p "$DOCKER_BIN"
cat > "$DOCKER_BIN/docker" << 'EOF'
#!/usr/bin/env bash
args=()
for arg in "$@"; do
  if [[ "$arg" == /mnt/?/* ]]; then
    arg=$(echo "$arg" | sed -E 's|^/mnt/([a-z])/|/\1/|')
  fi
  args+=("$arg")
done
exec "/mnt/c/Program Files/Docker/Docker/resources/bin/docker.exe" "${args[@]}"
EOF
chmod +x "$DOCKER_BIN/docker"

export PATH="$DOCKER_BIN:$ROOT/.venv/bin:$PATH"
export PYTHONPATH="$ROOT/harness"

# docker.exe reads Windows env for `--env PYTHONPATH`; clear stale Windows value.
if command -v powershell.exe >/dev/null 2>&1; then
  powershell.exe -NoProfile -Command "Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue" >/dev/null 2>&1 || true
fi

echo "=== Preflight ==="
"$ROOT/.venv/bin/python" harness/scripts/preflight.py \
  --bootstrap \
  --agent-profile deepseek_v4_flash \
  --docker-suite \
  --mini-bin "$ROOT/.venv/bin/mini"

OUT="experiments/mini-swe-agent/smoke-iniconfig-$(date +%Y%m%d-%H%M%S)"
echo "=== Smoke run -> $OUT ==="
"$ROOT/.venv/bin/python" -B -m featureliftbench.cli run-agent \
  benchmark/sanity/iniconfig__parse_config__001 \
  --agent mini-swe-agent \
  --agent-config harness/config/agents.toml \
  --agent-profile deepseek_v4_flash \
  --env-file .env \
  --yolo \
  --agent-docker \
  --eval-docker \
  --output "$OUT"

echo "=== Result ==="
"$ROOT/.venv/bin/python" -m json.tool "$OUT/run.json"
