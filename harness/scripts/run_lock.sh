#!/usr/bin/env bash
# Portable suite run lock (mkdir-based; works on macOS and Linux).
# Usage: source harness/scripts/run_lock.sh && acquire_run_lock "$OUTPUT"

acquire_run_lock() {
  local output_dir="${1:?output directory required}"
  RUN_LOCK_DIR="${output_dir}/.run.lock"
  if ! mkdir "$RUN_LOCK_DIR" 2>/dev/null; then
    echo "ERROR: another suite run holds ${RUN_LOCK_DIR}" >&2
    if [[ -f "${RUN_LOCK_DIR}/pid" ]]; then
      echo "  holder pid: $(cat "${RUN_LOCK_DIR}/pid" 2>/dev/null)" >&2
    fi
    echo "  If the prior run crashed, remove the lock: rmdir ${RUN_LOCK_DIR}" >&2
    exit 1
  fi
  echo "$$" > "${RUN_LOCK_DIR}/pid"
  trap 'rm -f "${RUN_LOCK_DIR}/pid" 2>/dev/null; rmdir "${RUN_LOCK_DIR}" 2>/dev/null || true' EXIT
}

release_run_lock() {
  if [[ -n "${RUN_LOCK_DIR:-}" && -d "${RUN_LOCK_DIR}" ]]; then
    rm -f "${RUN_LOCK_DIR}/pid" 2>/dev/null
    rmdir "${RUN_LOCK_DIR}" 2>/dev/null || true
  fi
}
