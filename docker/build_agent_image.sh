#!/usr/bin/env bash
# Build the bounded agent Docker image.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="${1:-featureliftbench-agent:latest}"
PYTHON_BASE="${FEATURELIFTBENCH_AGENT_PYTHON_BASE:-python:3.11-slim}"

docker build \
  --build-arg "PYTHON_BASE=${PYTHON_BASE}" \
  -f "${ROOT}/docker/Dockerfile.agent" \
  -t "${IMAGE}" \
  "${ROOT}"
echo "Built ${IMAGE} with ${PYTHON_BASE}"
