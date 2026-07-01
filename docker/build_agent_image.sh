#!/usr/bin/env bash
# Build the bounded agent Docker image.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="${1:-featureliftbench-agent:latest}"
PYTHON_BASE="${FEATURELIFTBENCH_AGENT_PYTHON_BASE:-python:3.11-slim}"
INSTALL_OPENHANDS="${FEATURELIFTBENCH_INSTALL_OPENHANDS:-0}"
OPENHANDS_VERSION="${FEATURELIFTBENCH_OPENHANDS_VERSION:-1.16.0}"

docker build \
  --build-arg "PYTHON_BASE=${PYTHON_BASE}" \
  --build-arg "INSTALL_OPENHANDS=${INSTALL_OPENHANDS}" \
  --build-arg "OPENHANDS_VERSION=${OPENHANDS_VERSION}" \
  -f "${ROOT}/docker/Dockerfile.agent" \
  -t "${IMAGE}" \
  "${ROOT}"
echo "Built ${IMAGE} with ${PYTHON_BASE} (INSTALL_OPENHANDS=${INSTALL_OPENHANDS})"
