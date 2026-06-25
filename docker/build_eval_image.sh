#!/usr/bin/env bash
# Build the reproducible evaluation Docker image.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="${1:-featureliftbench-eval:latest}"

docker build -f "${ROOT}/docker/Dockerfile.eval" -t "${IMAGE}" "${ROOT}"
echo "Built ${IMAGE}"
