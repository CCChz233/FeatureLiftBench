#!/usr/bin/env bash
# Build the reproducible evaluation Docker image.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="${1:-featureliftbench-eval:latest}"
PYTHON_BASE="${FEATURELIFTBENCH_EVAL_PYTHON_BASE:-python:3.11-slim}"
PLATFORM="${FEATURELIFTBENCH_DOCKER_PLATFORM:-linux/amd64}"
BENCHMARK_ID="${FEATURELIFTBENCH_BENCHMARK_ID:-unfrozen}"
SOURCE_REVISION="${FEATURELIFTBENCH_SOURCE_REVISION:-$(git -C "$ROOT" rev-parse HEAD)}"

docker build \
  --platform "${PLATFORM}" \
  --label "org.opencontainers.image.revision=${SOURCE_REVISION}" \
  --label "io.featureliftbench.benchmark-id=${BENCHMARK_ID}" \
  --label "io.featureliftbench.platform=${PLATFORM}" \
  --build-arg "PYTHON_BASE=${PYTHON_BASE}" \
  -f "${ROOT}/docker/Dockerfile.eval" \
  -t "${IMAGE}" \
  "${ROOT}"
echo "Built ${IMAGE} for ${PLATFORM} with ${PYTHON_BASE} (benchmark=${BENCHMARK_ID})"
