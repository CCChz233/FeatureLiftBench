#!/usr/bin/env bash
# WSL + Docker Desktop (docker.exe): fix volume mounts and PATH.
set -euo pipefail

ROOT="${ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
DOCKER_BIN="${HOME}/.flb-docker-bin"
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
export PATH="$DOCKER_BIN:${ROOT}/.venv/bin:${PATH}"

if command -v powershell.exe >/dev/null 2>&1; then
  powershell.exe -NoProfile -Command "Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue" >/dev/null 2>&1 || true
fi
