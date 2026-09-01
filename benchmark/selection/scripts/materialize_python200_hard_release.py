#!/usr/bin/env python3
"""Build Hard-50 release split and Python-200-hard unified root.

Does not touch benchmark/external50 or the frozen Python-150 tree.
Fails until 50 validated tasks exist under benchmark/hard50_pilot or benchmark/hard50.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
BASELINE_ROOT = ROOT / "benchmark/tasks"
PILOT_ROOT = ROOT / "benchmark/hard50_pilot"
HARD50_ROOT = ROOT / "benchmark/hard50"
SUITE_ROOT = ROOT / "benchmark/python200_hard_tasks"
SELECTION_PATH = ROOT / "benchmark/selection/hard50_expansion_20260827.json"
SUITE_MANIFEST = ROOT / "benchmark/selection/python200_hard_suite.json"
MAIN_REGISTRY = ROOT / "benchmark/sources/registry.json"
HARD50_REGISTRY = ROOT / "benchmark/sources/hard50_registry.json"
COMBINED_REGISTRY = ROOT / "benchmark/sources/python200_hard_registry.json"
FREEZE_ID = "846b814726217623fa205cb7688bee61e6c21c43efda1ebd05e79b5ed8cb4fbd"
EXCLUDED_NAMES = {"repo", "reference_solution", "__pycache__", ".pytest_cache"}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def selected_ids() -> list[str]:
    selection = load_json(SELECTION_PATH)
    return sorted(
        row["task_id"]
        for row in selection["rows"]
        if row.get("disposition") == "selected"
    )


def baseline_ids() -> list[str]:
    return sorted(
        path.name
        for path in BASELINE_ROOT.iterdir()
        if path.is_dir() and (path / "metadata.json").is_file()
    )


def copy_release_task(source: Path, destination: Path) -> None:
    def ignore(_directory: str, names: list[str]) -> set[str]:
        return {
            name
            for name in names
            if name in EXCLUDED_NAMES
            or name.startswith("_runtime_")
            or name.endswith(".pyc")
        }

    shutil.copytree(source, destination, ignore=ignore)
    repo_marker = destination / "repo/.source-archive-backed"
    repo_marker.parent.mkdir(parents=True, exist_ok=True)
    repo_marker.write_text(
        "Full repository source is materialized from benchmark/sources/python200_hard_registry.json.\n",
        encoding="utf-8",
    )


def source_root_for(task_ids: list[str]) -> Path:
    if all((PILOT_ROOT / task_id / "metadata.json").is_file() for task_id in task_ids):
        return PILOT_ROOT
    if all((HARD50_ROOT / task_id / "metadata.json").is_file() for task_id in task_ids):
        return HARD50_ROOT
    raise FileNotFoundError(
        "Hard-50 selected tasks are incomplete in hard50_pilot and hard50 "
        "(Phase 0 cards only; pin and materialize Pilot 10 first)"
    )


def build_hard50_root(destination: Path, task_ids: list[str]) -> None:
    source_root = source_root_for(task_ids)
    destination.mkdir(parents=True)
    for task_id in task_ids:
        copy_release_task(source_root / task_id, destination / task_id)


def build_suite_root(destination: Path, main_ids: list[str], hard_ids: list[str]) -> None:
    destination.mkdir(parents=True)
    for task_id in main_ids:
        os.symlink(Path("../tasks") / task_id, destination / task_id)
    for task_id in hard_ids:
        os.symlink(Path("../hard50") / task_id, destination / task_id)


def registry_summary(repositories: list[dict[str, Any]], snapshots: list[dict[str, Any]]) -> dict[str, int]:
    tasks = {task for row in snapshots for task in row.get("task_ids", [])}
    return {
        "repository_count": len(repositories),
        "snapshot_count": len(snapshots),
        "task_count": len(tasks),
    }


def combined_registry() -> dict[str, Any]:
    main = load_json(MAIN_REGISTRY)
    hard = load_json(HARD50_REGISTRY)
    repositories = list(main["repositories"]) + list(hard.get("repositories") or [])
    snapshots = list(main["snapshots"]) + list(hard.get("snapshots") or [])
    repo_ids = [row["source_repo_id"] for row in repositories]
    snapshot_ids = [row["source_snapshot_id"] for row in snapshots]
    task_ids = [task for row in snapshots for task in row.get("task_ids", [])]
    if len(repo_ids) != len(set(repo_ids)):
        raise ValueError("Python-200-hard registries contain duplicate repository IDs")
    if len(snapshot_ids) != len(set(snapshot_ids)):
        raise ValueError("Python-200-hard registries contain duplicate snapshot IDs")
    if len(task_ids) != len(set(task_ids)):
        raise ValueError("Python-200-hard registries contain duplicate task mappings")
    payload = {
        "schema_version": "featureliftbench.source_registry.v1",
        "policy_id": main["policy_id"],
        "generated_from": "frozen Python-150 registry + Hard-50 registry (excludes External-50)",
        "repositories": sorted(repositories, key=lambda row: row["source_repo_id"]),
        "snapshots": sorted(snapshots, key=lambda row: row["source_snapshot_id"]),
    }
    payload["summary"] = registry_summary(payload["repositories"], payload["snapshots"])
    return payload


def tree_digest(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(path.rglob("*"), key=lambda value: value.as_posix()):
        relative = item.relative_to(path).as_posix()
        if item.is_symlink():
            payload = f"L\0{relative}\0{os.readlink(item)}\n".encode()
        elif item.is_file():
            payload = b"F\0" + relative.encode() + b"\0" + item.read_bytes()
        else:
            continue
        digest.update(payload)
    return digest.hexdigest()


def suite_manifest(main_ids: list[str], hard_ids: list[str], release_digest: str) -> dict[str, Any]:
    all_ids = sorted(main_ids + hard_ids)
    task_hash = hashlib.sha256("".join(f"{task_id}\n" for task_id in all_ids).encode()).hexdigest()
    selection = load_json(SELECTION_PATH)
    return {
        "schema_version": "featureliftbench.python200_hard_suite.v1",
        "suite_id": "python200-hard-full-repository-no-hint-unreleased",
        "baseline_freeze_id": FREEZE_ID,
        "hard50_selection_id": selection.get("selection_id"),
        "task_count": 200,
        "baseline_count": len(main_ids),
        "hard50_count": len(hard_ids),
        "task_set_sha256": task_hash,
        "hard50_release_tree_sha256": release_digest,
        "task_root": "benchmark/python200_hard_tasks",
        "source_registry": "benchmark/sources/python200_hard_registry.json",
        "task_ids": all_ids,
        "excludes_external50": True,
    }


def replace_tree(source: Path, destination: Path) -> None:
    if destination.exists() or destination.is_symlink():
        shutil.rmtree(destination)
    source.rename(destination)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    main_ids = baseline_ids()
    hard_ids = selected_ids()
    if len(main_ids) != 150:
        raise SystemExit(f"expected frozen Python-150, found {len(main_ids)}")
    if len(hard_ids) != 50:
        raise SystemExit(f"expected selected Hard-50, found {len(hard_ids)}")
    if set(main_ids) & set(hard_ids):
        raise SystemExit("baseline and Hard-50 task IDs overlap")

    try:
        source_root_for(hard_ids)
    except FileNotFoundError as exc:
        if args.check:
            print(f"python200-hard release not ready: {exc}")
            return 2
        raise

    with tempfile.TemporaryDirectory(prefix="flb-python200-hard-release-") as tmp:
        temporary = Path(tmp)
        expected_hard = temporary / "hard50"
        expected_suite = temporary / "python200_hard_tasks"
        build_hard50_root(expected_hard, hard_ids)
        build_suite_root(expected_suite, main_ids, hard_ids)
        release_digest = tree_digest(expected_hard)
        registry = combined_registry()
        manifest = suite_manifest(main_ids, hard_ids, release_digest)
        registry_text = json.dumps(registry, indent=2, sort_keys=True) + "\n"
        manifest_text = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"

        if args.check:
            print(
                f"python200-hard would release {len(main_ids)} frozen + {len(hard_ids)} hard; "
                f"digest={release_digest[:12]}"
            )
            return 0

        replace_tree(expected_hard, HARD50_ROOT)
        replace_tree(expected_suite, SUITE_ROOT)
        COMBINED_REGISTRY.write_text(registry_text, encoding="utf-8")
        SUITE_MANIFEST.write_text(manifest_text, encoding="utf-8")

    print(f"Python-200-hard release: {len(main_ids)} frozen + {len(hard_ids)} hard")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
