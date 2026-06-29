#!/usr/bin/env bash
# Build the reproducible evaluation Docker image.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="${1:-featureliftbench-eval:latest}"
PYTHON_BASE="${FEATURELIFTBENCH_EVAL_PYTHON_BASE:-python:3.11-slim}"

docker build \
  --build-arg "PYTHON_BASE=${PYTHON_BASE}" \
  -f "${ROOT}/docker/Dockerfile.eval" \
  -t "${IMAGE}" \
  "${ROOT}"
echo "Built ${IMAGE} with ${PYTHON_BASE}"
