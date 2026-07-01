#!/usr/bin/env bash
# Build the Go-capable bounded agent Docker image.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="${1:-featureliftbench-agent-go:latest}"
GO_BASE="${FEATURELIFTBENCH_AGENT_GO_BASE:-golang:1.22-bookworm}"

docker build \
  --build-arg "GO_BASE=${GO_BASE}" \
  -f "${ROOT}/docker/Dockerfile.agent-go" \
  -t "${IMAGE}" \
  "${ROOT}"
echo "Built ${IMAGE} with ${GO_BASE}"
