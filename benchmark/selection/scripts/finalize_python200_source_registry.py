#!/usr/bin/env python3
"""Filter and verify the source registry for the realized External-50 split."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
SELECTION_PATH = ROOT / "benchmark/selection/external50_expansion_20260731.json"
REGISTRY_PATH = ROOT / "benchmark/sources/external50_registry.json"
RELEASE_ROOT = ROOT / "benchmark/external50"
STAGING_ROOT = ROOT / "benchmark/staging"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def task_dir(task_id: str) -> Path:
    released = RELEASE_ROOT / task_id
    if (released / "metadata.json").is_file():
        return released
    return STAGING_ROOT / task_id


def selected_ids() -> set[str]:
    selection = load_json(SELECTION_PATH)
    return {
        row["task_id"]
        for row in selection["rows"]
        if row.get("disposition") == "selected"
    }


def summary(payload: dict[str, Any]) -> dict[str, int]:
    repositories = payload["repositories"]
    snapshots = payload["snapshots"]
    tasks = {
        task_id for snapshot in snapshots for task_id in snapshot.get("task_ids", [])
    }
    external = sum(row.get("source_kind") == "external_oss" for row in repositories)
    ready = sum(row.get("status") == "ready" for row in snapshots)
    return {
        "curated_repository_count": len(repositories) - external,
        "external_repository_count": external,
        "pending_snapshot_count": len(snapshots) - ready,
        "ready_snapshot_count": ready,
        "repository_count": len(repositories),
        "snapshot_count": len(snapshots),
        "task_count": len(tasks),
    }


def filtered_registry(payload: dict[str, Any], selected: set[str]) -> dict[str, Any]:
    snapshots: list[dict[str, Any]] = []
    for raw in payload.get("snapshots", []):
        kept = sorted(selected & set(raw.get("task_ids", [])))
        if not kept:
            continue
        row = dict(raw)
        row["task_ids"] = kept
        snapshots.append(row)
    snapshot_ids = {row["source_snapshot_id"] for row in snapshots}

    repositories: list[dict[str, Any]] = []
    for raw in payload.get("repositories", []):
        kept_snapshots = sorted(snapshot_ids & set(raw.get("snapshot_ids", [])))
        kept_tasks = sorted(selected & set(raw.get("task_ids", [])))
        if not kept_snapshots:
            continue
        row = dict(raw)
        row["snapshot_ids"] = kept_snapshots
        row["task_ids"] = kept_tasks
        repositories.append(row)

    result = {
        "schema_version": payload["schema_version"],
        "policy_id": payload["policy_id"],
        "generated_from": "realized External-50 selection external50-expansion-20260801-v2",
        "repositories": sorted(repositories, key=lambda row: row["source_repo_id"]),
        "snapshots": sorted(snapshots, key=lambda row: row["source_snapshot_id"]),
    }
    result["summary"] = summary(result)
    return result


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify(payload: dict[str, Any], selected: set[str]) -> list[str]:
    issues: list[str] = []
    mapped: dict[str, list[dict[str, Any]]] = {task_id: [] for task_id in selected}
    for snapshot in payload["snapshots"]:
        for task_id in snapshot.get("task_ids", []):
            if task_id in mapped:
                mapped[task_id].append(snapshot)
    for task_id in sorted(selected):
        snapshots = mapped[task_id]
        if len(snapshots) != 1:
            issues.append(f"{task_id}: expected one snapshot, found {len(snapshots)}")
            continue
        snapshot = snapshots[0]
        if snapshot.get("status") != "ready":
            issues.append(f"{task_id}: source snapshot is not ready")
        metadata = load_json(task_dir(task_id) / "metadata.json")
        commit = metadata.get("source", {}).get("commit")
        if commit != snapshot.get("resolved_commit"):
            issues.append(f"{task_id}: metadata/source registry commit mismatch")
        archive = ROOT / snapshot.get("archive_path", "")
        if not archive.is_file():
            issues.append(f"{task_id}: source archive missing: {archive}")
        elif sha256(archive) != snapshot.get("archive_sha256"):
            issues.append(f"{task_id}: source archive SHA256 mismatch")
    if payload["summary"].get("task_count") != 50:
        issues.append(f"registry task_count is {payload['summary'].get('task_count')}, expected 50")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    selected = selected_ids()
    if len(selected) != 50:
        raise SystemExit(f"expected 50 selected tasks, found {len(selected)}")
    current = load_json(REGISTRY_PATH)
    expected = filtered_registry(current, selected)
    text = json.dumps(expected, indent=2, sort_keys=True) + "\n"
    if args.check and REGISTRY_PATH.read_text(encoding="utf-8") != text:
        raise SystemExit("external50 source registry is stale or contains non-selected tasks")
    if not args.check:
        REGISTRY_PATH.write_text(text, encoding="utf-8")
    issues = verify(expected, selected)
    for issue in issues:
        print(f"ERROR {issue}")
    print(
        f"External-50 sources: {expected['summary']['task_count']}/50 mapped, "
        f"{expected['summary']['ready_snapshot_count']} ready"
    )
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
