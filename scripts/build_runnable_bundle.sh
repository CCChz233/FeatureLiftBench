#!/usr/bin/env bash
# Build a self-contained FeatureLiftBench runnable bundle for server deploy.
#
# Includes code + Python-200 task definitions, source archives, offline wheels,
# and frozen Python-150 oracles for server-side paper experiments.
#
# Still required after unpack (too large / secrets): Docker images, .env, venv.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

STAMP="${BUNDLE_STAMP:-$(date +%Y%m%d-%H%M%S)}"
OUT_DIR="${OUT_DIR:-$ROOT/experiments/bundles/outgoing}"
NAME="FeatureLiftBench-runnable-${STAMP}"
OUT_TGZ="${OUT_DIR}/${NAME}.tar.gz"
STAGE="${TMPDIR:-/tmp}/${NAME}.stage.$$"

mkdir -p "$OUT_DIR"
rm -rf "$STAGE"
mkdir -p "$STAGE/$NAME"

cleanup() { rm -rf "$STAGE"; }
trap cleanup EXIT

echo "Staging into ${STAGE}/${NAME} ..."

# Build from committed files, then add the ignored runtime asset trees required
# by the Python-200 runner. This avoids broad tar exclusions silently
# dropping nested paths such as harness/config/experiments/.
TRACKED_TAR="$STAGE/tracked.tar"
git -C "$ROOT" archive --format=tar HEAD -o "$TRACKED_TAR"
tar -xf "$TRACKED_TAR" -C "$STAGE/$NAME"
rm -f "$TRACKED_TAR"

mkdir -p "$STAGE/$NAME/benchmark/submissions"
cp -R "$ROOT/benchmark/submissions/." "$STAGE/$NAME/benchmark/submissions"
mkdir -p "$STAGE/$NAME/benchmark/sources/archives"
cp -R "$ROOT/benchmark/sources/archives/." \
  "$STAGE/$NAME/benchmark/sources/archives"
mkdir -p "$STAGE/$NAME/benchmark/vendor-wheels"
cp -R "$ROOT/benchmark/vendor-wheels/." \
  "$STAGE/$NAME/benchmark/vendor-wheels"

# Ensure critical assets exist
if [[ ! -d "$STAGE/$NAME/benchmark/submissions" ]]; then
  echo "ERROR: benchmark/submissions missing in stage" >&2
  exit 1
fi
if [[ ! -d "$STAGE/$NAME/benchmark/sources/archives" ]]; then
  echo "ERROR: benchmark/sources/archives missing; run materialize_full_sources.py first" >&2
  exit 1
fi
if [[ ! -d "$STAGE/$NAME/benchmark/vendor-wheels" ]]; then
  echo "ERROR: benchmark/vendor-wheels missing; run bootstrap_vendor_wheels.py first" >&2
  exit 1
fi
if [[ ! -f "$STAGE/$NAME/harness/config/experiments/rsg_openhands_pilot_v1.toml" ]]; then
  echo "ERROR: rooted tar exclusions removed a frozen harness config" >&2
  exit 1
fi

ORACLE_N="$(find "$STAGE/$NAME/benchmark/submissions" -mindepth 2 -maxdepth 2 -type d -name oracle | wc -l | tr -d ' ')"
ARCHIVE_N="$(find "$STAGE/$NAME/benchmark/sources/archives" -type f -name '*.tar.gz' | wc -l | tr -d ' ')"
WHEEL_N="$(find "$STAGE/$NAME/benchmark/vendor-wheels" -type f -name '*.whl' | wc -l | tr -d ' ')"

GIT_REV="$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || echo unknown)"
GIT_DESC="$(git -C "$ROOT" describe --always HEAD 2>/dev/null || echo unknown)"

cat >"$STAGE/$NAME/BUNDLE.md" <<EOF
# FeatureLiftBench runnable bundle

Built: ${STAMP}
Git: ${GIT_REV} (${GIT_DESC})
Oracle dirs: ${ORACLE_N}
Source archives: ${ARCHIVE_N}
Vendor wheels: ${WHEEL_N}

## What this package contains

- Benchmark code, harness, docs, Docker build scripts
- \`benchmark/tasks/\` (frozen Python-150 tasks)
- \`benchmark/external50/\` and \`benchmark/python200_tasks/\` (balanced expansion and unified task root)
- \`benchmark/submissions/*/oracle/\` (Python-150 reference trees for freeze check)
- \`benchmark/sources/archives/\` (canonical full-repo archives; normally gitignored)
- \`benchmark/vendor-wheels/\` (offline Linux dependency wheels; normally gitignored)

## What you still set up on the server

1. Python 3.12+ and Docker
2. \`./setup.sh\` (creates \`.venv\`)
3. Copy \`harness/config/agents.example.toml\` → \`harness/config/agents.toml\` and edit profiles
4. Create \`.env\` with API keys / base URLs
5. Build images (once):

\`\`\`bash
FEATURELIFTBENCH_AGENT_PYTHON_BASE=python:3.11-slim \\
FEATURELIFTBENCH_INSTALL_OPENHANDS=1 \\
  docker/build_agent_image.sh featureliftbench-agent:latest
FEATURELIFTBENCH_EVAL_PYTHON_BASE=python:3.11-slim \\
  docker/build_eval_image.sh featureliftbench-eval:latest
\`\`\`

## Unpack

\`\`\`bash
tar -xzf ${NAME}.tar.gz
cd ${NAME}
\`\`\`

## Verify then run

\`\`\`bash
PYTHON=python3.12 SKIP_MINI=1 ./setup.sh
cp -n harness/config/agents.example.toml harness/config/agents.toml
# edit agents.toml + .env

python3 scripts/materialize_full_sources.py --check
python3 benchmark/selection/scripts/check_python200_baseline_freeze.py
python3 benchmark/selection/scripts/finalize_python200_source_registry.py --check
python3 benchmark/selection/scripts/finalize_python200_dependencies.py --check
python3 benchmark/selection/scripts/materialize_python200_release.py --check
python3 benchmark/selection/scripts/audit_python200_balance.py --check
python3 benchmark/selection/scripts/audit_python200_wheels.py --python-version 311

./harness/scripts/run_python200_paper.sh <openhands-profile> <run-id>
# add --execute after plan looks correct
\`\`\`

The runner keeps the frozen Python-150 task tree unchanged and adds the
balanced External-50 through the unified release root.
EOF

# Prefer agents.example as the only config in the bundle (agents.toml is machine-local).
if [[ ! -f "$STAGE/$NAME/harness/config/agents.example.toml" ]]; then
  echo "ERROR: agents.example.toml missing" >&2
  exit 1
fi

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
  echo "ERROR: Python 3.11+ is required to verify the runnable bundle" >&2
  return 1
}

BUNDLE_PYTHON="$(resolve_python)"
echo "Verifying staged Python-200 source, selection, and baseline freeze ..."
(
  cd "$STAGE/$NAME"
  "$BUNDLE_PYTHON" -B scripts/materialize_full_sources.py --check
  "$BUNDLE_PYTHON" -B benchmark/selection/scripts/check_python200_baseline_freeze.py
  "$BUNDLE_PYTHON" -B benchmark/selection/scripts/finalize_python200_source_registry.py --check
  "$BUNDLE_PYTHON" -B benchmark/selection/scripts/finalize_python200_dependencies.py --check
  "$BUNDLE_PYTHON" -B benchmark/selection/scripts/materialize_python200_release.py --check
  "$BUNDLE_PYTHON" -B benchmark/selection/scripts/audit_python200_balance.py --check
  "$BUNDLE_PYTHON" -B benchmark/selection/scripts/audit_python200_wheels.py --python-version 311
)

echo "Compressing -> ${OUT_TGZ} ..."
COPYFILE_DISABLE=1 tar -C "$STAGE" -czf "$OUT_TGZ" "$NAME"

if command -v sha256sum >/dev/null 2>&1; then
  (cd "$OUT_DIR" && sha256sum "$(basename "$OUT_TGZ")" >"$(basename "$OUT_TGZ").sha256")
else
  (cd "$OUT_DIR" && shasum -a 256 "$(basename "$OUT_TGZ")" >"$(basename "$OUT_TGZ").sha256")
fi

ls -lh "$OUT_TGZ" "${OUT_TGZ}.sha256"
echo "oracle_dirs=${ORACLE_N} archives=${ARCHIVE_N} wheels=${WHEEL_N}"
echo "Wrote ${OUT_TGZ}"
