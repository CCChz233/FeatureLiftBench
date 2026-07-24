#!/usr/bin/env bash
# Shared FeatureLiftBench environment helpers (path-independent).
# shellcheck shell=bash

flb_repo_root() {
  local here
  here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  # scripts/lib -> repo root
  cd "${here}/../.." && pwd
}

flb_cd_root() {
  FLB_ROOT="$(flb_repo_root)"
  export FLB_ROOT
  cd "$FLB_ROOT"
  export PYTHONPATH="${FLB_ROOT}/harness${PYTHONPATH:+:${PYTHONPATH}}"
}

flb_resolve_python() {
  if [[ -n "${PYTHON:-}" && -x "${PYTHON}" ]]; then
    printf '%s\n' "$PYTHON"
    return 0
  fi
  if [[ -n "${PYTHON:-}" ]]; then
    # Allow bare command names (python3) via PATH
    if command -v "$PYTHON" >/dev/null 2>&1; then
      command -v "$PYTHON"
      return 0
    fi
  fi
  if [[ -n "${CONDA_PREFIX:-}" && -x "${CONDA_PREFIX}/bin/python" ]]; then
    printf '%s\n' "${CONDA_PREFIX}/bin/python"
    return 0
  fi
  if [[ -x "${FLB_ROOT}/.venv/bin/python" ]]; then
    printf '%s\n' "${FLB_ROOT}/.venv/bin/python"
    return 0
  fi
  if command -v python3.12 >/dev/null 2>&1; then
    command -v python3.12
    return 0
  fi
  if command -v python3 >/dev/null 2>&1; then
    command -v python3
    return 0
  fi
  echo "No suitable Python found. Set PYTHON=/path/to/python3.12+" >&2
  return 1
}

flb_default_agent_config() {
  # Prefer local agents.toml when present; fall back to example (has ablation profiles).
  if [[ -f "${FLB_ROOT}/harness/config/agents.toml" ]]; then
    # Ablation OpenHands profiles live in agents.example.toml; use example if requested arm needs them.
    printf '%s\n' "harness/config/agents.toml"
  else
    printf '%s\n' "harness/config/agents.example.toml"
  fi
}

flb_ablation_agent_config() {
  # OpenHands ablation profiles are defined in agents.example.toml.
  printf '%s\n' "harness/config/agents.example.toml"
}
