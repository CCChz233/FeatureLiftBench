#!/usr/bin/env python3
"""Build the lightweight External-50 release split and unified Python-200 root."""

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
STAGING_ROOT = ROOT / "benchmark/staging"
EXTERNAL_ROOT = ROOT / "benchmark/external50"
SUITE_ROOT = ROOT / "benchmark/python200_tasks"
SELECTION_PATH = ROOT / "benchmark/selection/external50_expansion_20260731.json"
SUITE_MANIFEST = ROOT / "benchmark/selection/python200_suite.json"
MAIN_REGISTRY = ROOT / "benchmark/sources/registry.json"
EXTERNAL_REGISTRY = ROOT / "benchmark/sources/external50_registry.json"
COMBINED_REGISTRY = ROOT / "benchmark/sources/python200_registry.json"
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
        return {name for name in names if name in EXCLUDED_NAMES or name.endswith(".pyc")}

    shutil.copytree(source, destination, ignore=ignore)
    repo_marker = destination / "repo/.source-archive-backed"
    repo_marker.parent.mkdir(parents=True, exist_ok=True)
    repo_marker.write_text(
        "Full repository source is materialized from benchmark/sources/python200_registry.json.\n",
        encoding="utf-8",
    )


def build_external_root(destination: Path, task_ids: list[str]) -> None:
    if all((STAGING_ROOT / task_id / "metadata.json").is_file() for task_id in task_ids):
        source_root = STAGING_ROOT
    elif all((EXTERNAL_ROOT / task_id / "metadata.json").is_file() for task_id in task_ids):
        source_root = EXTERNAL_ROOT
    else:
        raise FileNotFoundError(
            "selected External-50 tasks are incomplete in both staging and release roots"
        )
    destination.mkdir(parents=True)
    for task_id in task_ids:
        copy_release_task(source_root / task_id, destination / task_id)


def build_suite_root(destination: Path, main_ids: list[str], external_ids: list[str]) -> None:
    destination.mkdir(parents=True)
    for task_id in main_ids:
        os.symlink(Path("../tasks") / task_id, destination / task_id)
    for task_id in external_ids:
        os.symlink(Path("../external50") / task_id, destination / task_id)


def registry_summary(repositories: list[dict[str, Any]], snapshots: list[dict[str, Any]]) -> dict[str, int]:
    tasks = {task for row in snapshots for task in row.get("task_ids", [])}
    external = sum(row.get("source_kind") == "external_oss" for row in repositories)
    ready = sum(row.get("status") == "ready" for row in snapshots)
    return {
        "repository_count": len(repositories),
        "snapshot_count": len(snapshots),
        "task_count": len(tasks),
        "external_repository_count": external,
        "curated_repository_count": len(repositories) - external,
        "ready_snapshot_count": ready,
        "pending_snapshot_count": len(snapshots) - ready,
    }


def combined_registry() -> dict[str, Any]:
    main = load_json(MAIN_REGISTRY)
    external = load_json(EXTERNAL_REGISTRY)
    repositories = main["repositories"] + external["repositories"]
    snapshots = main["snapshots"] + external["snapshots"]
    repo_ids = [row["source_repo_id"] for row in repositories]
    snapshot_ids = [row["source_snapshot_id"] for row in snapshots]
    task_ids = [task for row in snapshots for task in row.get("task_ids", [])]
    if len(repo_ids) != len(set(repo_ids)):
        raise ValueError("Python-200 source registries contain duplicate repository IDs")
    if len(snapshot_ids) != len(set(snapshot_ids)):
        raise ValueError("Python-200 source registries contain duplicate snapshot IDs")
    if len(task_ids) != len(set(task_ids)):
        raise ValueError("Python-200 source registries contain duplicate task mappings")
    payload = {
        "schema_version": "featureliftbench.source_registry.v1",
        "policy_id": main["policy_id"],
        "generated_from": "frozen Python-150 registry + realized External-50 registry",
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


def suite_manifest(main_ids: list[str], external_ids: list[str], release_digest: str) -> dict[str, Any]:
    all_ids = sorted(main_ids + external_ids)
    task_hash = hashlib.sha256("".join(f"{task_id}\n" for task_id in all_ids).encode()).hexdigest()
    selection = load_json(SELECTION_PATH)
    return {
        "schema_version": "featureliftbench.python200_suite.v1",
        "suite_id": "python200-full-repository-no-hint-20260801-v1",
        "baseline_freeze_id": FREEZE_ID,
        "external_selection_id": selection["selection_id"],
        "task_count": 200,
        "baseline_count": len(main_ids),
        "external_count": len(external_ids),
        "task_set_sha256": task_hash,
        "external_release_tree_sha256": release_digest,
        "task_root": "benchmark/python200_tasks",
        "source_registry": "benchmark/sources/python200_registry.json",
        "task_ids": all_ids,
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
    external_ids = selected_ids()
    if len(main_ids) != 150:
        raise SystemExit(f"expected frozen Python-150, found {len(main_ids)}")
    if len(external_ids) != 50:
        raise SystemExit(f"expected selected External-50, found {len(external_ids)}")
    if set(main_ids) & set(external_ids):
        raise SystemExit("baseline and External-50 task IDs overlap")

    with tempfile.TemporaryDirectory(prefix="flb-python200-release-") as tmp:
        temporary = Path(tmp)
        expected_external = temporary / "external50"
        expected_suite = temporary / "python200_tasks"
        build_external_root(expected_external, external_ids)
        build_suite_root(expected_suite, main_ids, external_ids)
        release_digest = tree_digest(expected_external)
        registry = combined_registry()
        manifest = suite_manifest(main_ids, external_ids, release_digest)
        registry_text = json.dumps(registry, indent=2, sort_keys=True) + "\n"
        manifest_text = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"

        stale = []
        if not EXTERNAL_ROOT.is_dir() or tree_digest(EXTERNAL_ROOT) != release_digest:
            stale.append(str(EXTERNAL_ROOT.relative_to(ROOT)))
        if not SUITE_ROOT.is_dir() or tree_digest(SUITE_ROOT) != tree_digest(expected_suite):
            stale.append(str(SUITE_ROOT.relative_to(ROOT)))
        if not COMBINED_REGISTRY.is_file() or COMBINED_REGISTRY.read_text(encoding="utf-8") != registry_text:
            stale.append(str(COMBINED_REGISTRY.relative_to(ROOT)))
        if not SUITE_MANIFEST.is_file() or SUITE_MANIFEST.read_text(encoding="utf-8") != manifest_text:
            stale.append(str(SUITE_MANIFEST.relative_to(ROOT)))
        if args.check:
            if stale:
                raise SystemExit("stale Python-200 release artifacts: " + ", ".join(stale))
        else:
            replace_tree(expected_external, EXTERNAL_ROOT)
            replace_tree(expected_suite, SUITE_ROOT)
            COMBINED_REGISTRY.write_text(registry_text, encoding="utf-8")
            SUITE_MANIFEST.write_text(manifest_text, encoding="utf-8")

    print(
        f"Python-200 release: {len(main_ids)} frozen + {len(external_ids)} external; "
        f"registry={registry['summary']['task_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
