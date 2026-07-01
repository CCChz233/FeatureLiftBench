#!/usr/bin/env bash
# Build the Go-capable reproducible evaluation Docker image.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="${1:-featureliftbench-eval-go:latest}"
GO_BASE="${FEATURELIFTBENCH_EVAL_GO_BASE:-golang:1.22-bookworm}"

docker build \
  --build-arg "GO_BASE=${GO_BASE}" \
  -f "${ROOT}/docker/Dockerfile.eval-go" \
  -t "${IMAGE}" \
  "${ROOT}"
echo "Built ${IMAGE} with ${GO_BASE}"
