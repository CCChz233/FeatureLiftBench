#!/usr/bin/env bash
# Rebuild the deployable, evaluator-frozen Python-150 v3 release bundle.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BASE_REF="8438e3a3c05e9c8ed65a835f42321c7cf07d5977"
FREEZE_REF="8fc6c11"
FREEZE_ID="846b814726217623fa205cb7688bee61e6c21c43efda1ebd05e79b5ed8cb4fbd"
STAMP="${BUNDLE_STAMP:-$(date +%Y%m%d-%H%M%S)}"
OUT_DIR="${OUT_DIR:-$ROOT/experiments/bundles/outgoing}"
NAME="FeatureLiftBench-v3-846-${STAMP}"
OUT_TGZ="$OUT_DIR/$NAME.tar.gz"
STAGE="${TMPDIR:-/tmp}/$NAME.stage.$$"
RELEASE="$STAGE/$NAME"
TRACKED_TAR="$STAGE/base.tar"

mkdir -p "$OUT_DIR" "$RELEASE"
cleanup() { rm -rf "$STAGE"; }
trap cleanup EXIT

resolve_python() {
  local candidate
  for candidate in \
    "${PYTHON:-}" \
    "$ROOT/.venv/bin/python" \
    "$(command -v python3.12 2>/dev/null || true)" \
    "$(command -v python3 2>/dev/null || true)"
  do
    if [[ -n "$candidate" && -x "$candidate" ]] && "$candidate" -c \
      'import sys, tomllib; assert sys.version_info >= (3, 11)' 2>/dev/null; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done
  echo "Python 3.11+ is required" >&2
  return 1
}

write_git_file() {
  local ref="$1"
  local path="$2"
  mkdir -p "$RELEASE/$(dirname "$path")"
  git -C "$ROOT" show "$ref:$path" >"$RELEASE/$path"
}

BUNDLE_PYTHON="$(resolve_python)"

echo "Extracting frozen base $BASE_REF ..."
git -C "$ROOT" archive --format=tar "$BASE_REF" -o "$TRACKED_TAR"
tar -xf "$TRACKED_TAR" -C "$RELEASE"

# Freeze 846 differs from the hardened base only by excluding machine-local
# files from manifests and by pointing at the server-reproduced freeze record.
write_git_file "$FREEZE_REF" "harness/featureliftbench/freeze.py"
write_git_file "$FREEZE_REF" \
  "artifacts/research_analysis/v3/current_benchmark_freeze.json"
write_git_file "$FREEZE_REF" \
  "artifacts/research_analysis/v3/freezes/$FREEZE_ID.json"

rm -rf "$RELEASE/benchmark/submissions"
mkdir -p "$RELEASE/benchmark/submissions"
for task_dir in "$RELEASE"/benchmark/tasks/*; do
  if [[ ! -f "$task_dir/metadata.json" ]]; then
    continue
  fi
  task_id="$(basename "$task_dir")"
  oracle_source="$ROOT/benchmark/submissions/$task_id/oracle"
  if [[ ! -d "$oracle_source" ]]; then
    echo "Missing Main oracle: $oracle_source" >&2
    exit 1
  fi
  mkdir -p "$RELEASE/benchmark/submissions/$task_id"
  cp -R "$oracle_source" "$RELEASE/benchmark/submissions/$task_id/oracle"
done

ARCHIVE_LIST="$STAGE/main-archives.txt"
"$BUNDLE_PYTHON" - "$RELEASE/benchmark/sources/registry.json" \
  >"$ARCHIVE_LIST" <<'PY'
import json
import sys
from pathlib import Path

registry = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
for path in sorted(
    str(snapshot.get("archive_path") or "")
    for snapshot in registry.get("snapshots", [])
):
    if path:
        print(path)
PY
while IFS= read -r archive_path; do
  archive_source="$ROOT/$archive_path"
  if [[ ! -f "$archive_source" ]]; then
    echo "Missing Main source archive: $archive_source" >&2
    exit 1
  fi
  mkdir -p "$RELEASE/$(dirname "$archive_path")"
  cp "$archive_source" "$RELEASE/$archive_path"
done <"$ARCHIVE_LIST"

ORACLE_N="$(find "$RELEASE/benchmark/submissions" -mindepth 2 -maxdepth 2 -type d -name oracle | wc -l | tr -d ' ')"
ARCHIVE_N="$(find "$RELEASE/benchmark/sources/archives" -type f -name '*.tar.gz' | wc -l | tr -d ' ')"

cat >"$RELEASE/BUNDLE.md" <<EOF
# FeatureLiftBench v3 frozen release

Built: $STAMP
Base ref: $BASE_REF
Freeze ref: $FREEZE_REF
Freeze id: $FREEZE_ID
Oracle dirs: $ORACLE_N
Source archives: $ARCHIVE_N

This is the mechanically reproducible Python External-150 Full-Repository /
No-Hint release. It intentionally excludes machine-local \`.env\` and
\`harness/config/agents.toml\`.

After unpacking, run \`PYTHON=python3.12 SKIP_MINI=1 ./setup.sh\`, create the
machine-local config files, build the agent/evaluator Docker images, and use
\`harness/scripts/archive/run_python150_paper.sh\`. Add \`--execute\` only after the
plan-only invocation succeeds.
EOF

echo "Verifying frozen release ..."
(
  cd "$RELEASE"
  "$BUNDLE_PYTHON" -B scripts/build_source_registry.py --check
  "$BUNDLE_PYTHON" -B scripts/materialize_full_sources.py --check
  "$BUNDLE_PYTHON" -B scripts/audit_v3_main_readiness.py --strict --check
  "$BUNDLE_PYTHON" -B scripts/build_v3_benchmark_freeze.py --check
)

echo "Compressing $OUT_TGZ ..."
COPYFILE_DISABLE=1 tar -C "$STAGE" -czf "$OUT_TGZ" "$NAME"
if command -v sha256sum >/dev/null 2>&1; then
  (
    cd "$OUT_DIR"
    sha256sum "$(basename "$OUT_TGZ")" >"$(basename "$OUT_TGZ").sha256"
  )
else
  (
    cd "$OUT_DIR"
    shasum -a 256 "$(basename "$OUT_TGZ")" >"$(basename "$OUT_TGZ").sha256"
  )
fi

ls -lh "$OUT_TGZ" "$OUT_TGZ.sha256"
echo "freeze_id=$FREEZE_ID oracle_dirs=$ORACLE_N archives=$ARCHIVE_N"
