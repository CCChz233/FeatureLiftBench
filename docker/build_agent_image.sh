#!/usr/bin/env bash
# Build the bounded agent Docker image.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="${1:-featureliftbench-agent:latest}"
PYTHON_BASE="${FEATURELIFTBENCH_AGENT_PYTHON_BASE:-python:3.11-slim}"
PLATFORM="${FEATURELIFTBENCH_DOCKER_PLATFORM:-linux/amd64}"
BENCHMARK_ID="${FEATURELIFTBENCH_BENCHMARK_ID:-unfrozen}"
SOURCE_REVISION="${FEATURELIFTBENCH_SOURCE_REVISION:-$(git -C "$ROOT" rev-parse HEAD)}"
INSTALL_OPENHANDS="${FEATURELIFTBENCH_INSTALL_OPENHANDS:-0}"
OPENHANDS_VERSION="${FEATURELIFTBENCH_OPENHANDS_VERSION:-1.16.0}"
INSTALL_RUNTIME_AGENTS="${FEATURELIFTBENCH_INSTALL_RUNTIME_AGENTS:-0}"
NODE_VERSION="${FEATURELIFTBENCH_NODE_VERSION:-22.19.0}"

docker build \
  --platform "${PLATFORM}" \
  --label "org.opencontainers.image.revision=${SOURCE_REVISION}" \
  --label "io.featureliftbench.benchmark-id=${BENCHMARK_ID}" \
  --label "io.featureliftbench.platform=${PLATFORM}" \
  --build-arg "PYTHON_BASE=${PYTHON_BASE}" \
  --build-arg "INSTALL_OPENHANDS=${INSTALL_OPENHANDS}" \
  --build-arg "OPENHANDS_VERSION=${OPENHANDS_VERSION}" \
  --build-arg "INSTALL_RUNTIME_AGENTS=${INSTALL_RUNTIME_AGENTS}" \
  --build-arg "NODE_VERSION=${NODE_VERSION}" \
  -f "${ROOT}/docker/Dockerfile.agent" \
  -t "${IMAGE}" \
  "${ROOT}"
echo "Built ${IMAGE} for ${PLATFORM} with ${PYTHON_BASE} (benchmark=${BENCHMARK_ID}, INSTALL_OPENHANDS=${INSTALL_OPENHANDS}, INSTALL_RUNTIME_AGENTS=${INSTALL_RUNTIME_AGENTS})"
