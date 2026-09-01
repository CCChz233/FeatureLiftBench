#!/usr/bin/env bash
set -euo pipefail
echo "DEPRECATED: check_env.sh is a WSL-specific legacy check; use harness/scripts/preflight.py or catalog check." >&2
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

echo "=== 环境检查 ==="
echo -n "Docker daemon: "
docker info >/dev/null 2>&1 && echo OK || { echo FAIL; exit 1; }
echo -n "Python venv: "
"$ROOT/.venv/bin/python" --version
echo -n "API Key: "
grep -E '^FEATURELIFTBENCH_API_KEY=' .env | sed 's/=.*/=已配置/'
echo "Docker 镜像:"
docker images --format '  {{.Repository}}:{{.Tag}}' | grep featureliftbench || true

echo
echo "=== Preflight ==="
"$ROOT/.venv/bin/python" harness/scripts/preflight.py \
  --bootstrap \
  --agent-profile deepseek_v4_flash \
  --docker-suite \
  --mini-bin "$ROOT/.venv/bin/mini"

echo
echo "=== 上次 smoke 结果 ==="
LAST=$(ls -td experiments/mini-swe-agent/smoke-iniconfig-* 2>/dev/null | head -1 || true)
if [[ -n "$LAST" && -f "$LAST/run.json" ]]; then
  "$ROOT/.venv/bin/python" - <<PY
import json
from pathlib import Path
p = Path("$LAST/run.json")
data = json.loads(p.read_text())
print(f"目录: {p.parent}")
print(f"状态: {data.get('status')}")
print(f"Agent: {data.get('agent_backend')} passed={data.get('agent', {}).get('passed')}")
print(f"Eval: {data.get('eval_backend')} status={data.get('evaluation', {}).get('status')}")
print(f"分数: {data.get('evaluation', {}).get('scores', {})}")
PY
else
  echo "未找到 smoke 结果"
fi
