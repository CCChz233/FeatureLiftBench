#!/usr/bin/env python3
"""Materialize a reproducible Python-200′ run input without editing benchmark tasks.

The Python-150 packages are read from the Git ref used by freeze 846. Hard-50
packages are copied from the reviewed release tree. The output is a disposable
validation input under experiments/, not a second benchmark editing root.

Rebuild:
    PYTHONPATH=harness python3.12 -B \
      harness/scripts/materialize_python200_hard_frozen_input.py \
      --output experiments/validation/preflight/python200-hard-freeze846-input

Validate an existing materialization:
    PYTHONPATH=harness python3.12 -B \
      harness/scripts/materialize_python200_hard_frozen_input.py \
      --output experiments/validation/preflight/python200-hard-freeze846-input \
      --check
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import shutil
import subprocess
import tarfile
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from featureliftbench.freeze import file_manifest, manifest_digest


ROOT = Path(__file__).resolve().parents[2]
# Commit whose benchmark/tasks matches the contract-hardened Python-150 freeze
# 0b106842. The earlier 8438e3a3 predates that hardening and materializes stale
# metadata/hidden tests for 48 baseline tasks.
BASE_REF = "f822ff2824f5ecef791eb8dbf6ed4ab4e99d0ffd"
FREEZE_PATH = ROOT / "artifacts/research_analysis/v3/current_benchmark_freeze.json"
SELECTION_PATH = ROOT / "benchmark/selection/python200_hard_suite.json"
HARD50_ROOT = ROOT / "benchmark/hard50"
SOURCE_REGISTRY = ROOT / "benchmark/sources/python200_hard_registry.json"
DEFAULT_OUTPUT = (
    ROOT / "experiments/validation/preflight/python200-hard-hardened-input"
)
EXCLUDED_NAMES = {"reference_solution", "__pycache__", ".pytest_cache"}


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tree_digest(path: Path) -> dict[str, Any]:
    files = file_manifest([path], root=path)
    return {
        "sha256": manifest_digest({"files": files}),
        "file_count": len(files),
    }


def git_archive_tasks(destination: Path) -> None:
    completed = subprocess.run(
        ["git", "archive", "--format=tar", BASE_REF, "benchmark/tasks"],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"git archive failed for {BASE_REF}: {detail}")
    with tarfile.open(fileobj=io.BytesIO(completed.stdout), mode="r:") as archive:
        for member in archive.getmembers():
            path = Path(member.name)
            if path.is_absolute() or ".." in path.parts:
                raise RuntimeError(f"unsafe git archive member: {member.name}")
        archive.extractall(destination, filter="data")


def copy_task(source: Path, destination: Path) -> None:
    def ignore(_directory: str, names: list[str]) -> set[str]:
        return {
            name
            for name in names
            if name in EXCLUDED_NAMES or name.endswith(".pyc")
        }

    shutil.copytree(source, destination, symlinks=True, ignore=ignore)


def expected_identity() -> tuple[dict[str, Any], dict[str, Any], list[str], list[str]]:
    freeze = read_json(FREEZE_PATH)
    selection = read_json(SELECTION_PATH)
    frozen_tasks = freeze.get("tasks")
    if not isinstance(frozen_tasks, dict) or len(frozen_tasks) != 150:
        raise RuntimeError("active freeze does not contain exactly 150 tasks")
    if selection.get("baseline_freeze_id") != freeze.get("freeze_id"):
        raise RuntimeError("Python-200′ selection and active freeze IDs disagree")
    selected = [str(value) for value in selection.get("task_ids") or []]
    baseline_ids = sorted(frozen_tasks)
    hard50_ids = sorted(set(selected) - set(baseline_ids))
    if len(selected) != 200 or len(hard50_ids) != 50:
        raise RuntimeError("expected 150 frozen baseline plus 50 Hard-50 tasks")
    return freeze, selection, baseline_ids, hard50_ids


def verify(output: Path) -> dict[str, Any]:
    freeze, selection, baseline_ids, hard50_ids = expected_identity()
    task_root = output / "tasks"
    manifest_path = output / "manifest.json"
    failures: list[str] = []
    actual_ids = sorted(
        path.name
        for path in task_root.iterdir()
        if path.is_dir() and (path / "metadata.json").is_file()
    ) if task_root.is_dir() else []
    if actual_ids != sorted(baseline_ids + hard50_ids):
        failures.append("task membership does not match Python-200′ selection")
    for task_id in baseline_ids:
        task_dir = task_root / task_id
        if not task_dir.is_dir():
            failures.append(f"{task_id}: frozen task missing")
            continue
        if tree_digest(task_dir) != freeze["tasks"][task_id].get("task_tree"):
            failures.append(f"{task_id}: frozen task tree mismatch")
    hard50_digest = tree_digest(task_root) if task_root.is_dir() else None
    manifest = read_json(manifest_path) if manifest_path.is_file() else {}
    if manifest.get("base_ref") != BASE_REF:
        failures.append("materialization base ref mismatch")
    if manifest.get("freeze_id") != freeze.get("freeze_id"):
        failures.append("materialization freeze ID mismatch")
    if manifest.get("task_set_sha256") != selection.get("task_set_sha256"):
        failures.append("materialization task-set hash mismatch")
    if failures:
        raise RuntimeError("; ".join(failures[:10]))
    return {
        "task_count": len(actual_ids),
        "baseline_count": len(baseline_ids),
        "hard50_count": len(hard50_ids),
        "freeze_id": freeze.get("freeze_id"),
        "task_set_sha256": selection.get("task_set_sha256"),
        "materialized_tree": hard50_digest,
    }


def materialize(output: Path) -> dict[str, Any]:
    freeze, selection, baseline_ids, hard50_ids = expected_identity()
    if output.exists():
        raise FileExistsError(
            f"output already exists; use --check or choose a new path: {output}"
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix="flb-python200-hard-input-", dir=output.parent
    ) as temporary_name:
        temporary = Path(temporary_name)
        git_root = temporary / "git"
        staged_output = temporary / "materialized"
        task_root = staged_output / "tasks"
        git_root.mkdir()
        task_root.mkdir(parents=True)
        git_archive_tasks(git_root)
        frozen_root = git_root / "benchmark/tasks"
        for task_id in baseline_ids:
            copy_task(frozen_root / task_id, task_root / task_id)
        for task_id in hard50_ids:
            copy_task(HARD50_ROOT / task_id, task_root / task_id)
        manifest = {
            "schema_version": "featureliftbench.python200_hard_frozen_input.v1",
            "status": "materialized_validation_input",
            "generated_at": datetime.now(UTC).isoformat(),
            "base_ref": BASE_REF,
            "freeze_id": freeze.get("freeze_id"),
            "freeze_path": str(FREEZE_PATH.relative_to(ROOT)),
            "freeze_sha256": sha256_file(FREEZE_PATH),
            "task_set_sha256": selection.get("task_set_sha256"),
            "hard50_selection_id": selection.get("hard50_selection_id"),
            "hard50_release_tree_sha256": selection.get("hard50_release_tree_sha256"),
            "source_registry": str(SOURCE_REGISTRY.relative_to(ROOT)),
            "source_registry_sha256": sha256_file(SOURCE_REGISTRY),
            "task_root": "tasks",
            "task_count": 200,
            "baseline_count": 150,
            "hard50_count": 50,
            "rebuild_command": (
                "PYTHONPATH=harness python3.12 -B "
                "harness/scripts/materialize_python200_hard_frozen_input.py "
                f"--output {output.relative_to(ROOT)}"
            ),
        }
        (staged_output / "manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        staged_output.rename(output)
    return verify(output)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output = args.output.resolve()
    try:
        result = verify(output) if args.check else materialize(output)
    except (FileExistsError, RuntimeError, OSError, subprocess.SubprocessError) as exc:
        print(f"python200-hard frozen input: ERROR: {exc}")
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
