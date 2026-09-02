#!/usr/bin/env python3
"""Split External-50 staging sources out of the canonical Main registry."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MAIN_TASKS = ROOT / "benchmark" / "tasks"
DEFAULT_COMBINED = ROOT / "benchmark" / "sources" / "registry.json"
DEFAULT_EXTERNAL50 = (
    ROOT / "benchmark" / "sources" / "external50_registry.json"
)

sys.path.insert(0, str(ROOT / "scripts"))
from build_source_registry import (  # noqa: E402
    build_registry,
    merge_existing_evidence,
    validate_registry,
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--combined", type=Path, default=DEFAULT_COMBINED)
    parser.add_argument("--main-output", type=Path, default=DEFAULT_COMBINED)
    parser.add_argument("--external50-output", type=Path, default=DEFAULT_EXTERNAL50)
    return parser.parse_args()


def _summary(payload: dict[str, Any]) -> dict[str, int]:
    repositories = payload["repositories"]
    snapshots = payload["snapshots"]
    task_ids = {
        str(task_id)
        for snapshot in snapshots
        for task_id in snapshot.get("task_ids", [])
    }
    external = sum(
        row.get("source_kind") == "external_oss" for row in repositories
    )
    ready = sum(row.get("status") == "ready" for row in snapshots)
    return {
        "repository_count": len(repositories),
        "snapshot_count": len(snapshots),
        "task_count": len(task_ids),
        "external_repository_count": external,
        "curated_repository_count": len(repositories) - external,
        "ready_snapshot_count": ready,
        "pending_snapshot_count": len(snapshots) - ready,
    }


def _extension_registry(
    combined: dict[str, Any],
    main_task_ids: set[str],
) -> dict[str, Any]:
    snapshots: list[dict[str, Any]] = []
    for raw in combined.get("snapshots", []):
        if not isinstance(raw, dict):
            continue
        extension_ids = sorted(
            str(task_id)
            for task_id in raw.get("task_ids", [])
            if str(task_id) not in main_task_ids
        )
        if not extension_ids:
            continue
        row = dict(raw)
        row["task_ids"] = extension_ids
        snapshots.append(row)

    snapshot_ids = {
        str(row.get("source_snapshot_id")) for row in snapshots
    }
    task_ids = {
        str(task_id)
        for row in snapshots
        for task_id in row.get("task_ids", [])
    }
    repositories: list[dict[str, Any]] = []
    for raw in combined.get("repositories", []):
        if not isinstance(raw, dict):
            continue
        kept_snapshots = sorted(
            str(snapshot_id)
            for snapshot_id in raw.get("snapshot_ids", [])
            if str(snapshot_id) in snapshot_ids
        )
        kept_tasks = sorted(
            str(task_id)
            for task_id in raw.get("task_ids", [])
            if str(task_id) in task_ids
        )
        if not kept_snapshots:
            continue
        row = dict(raw)
        row["snapshot_ids"] = kept_snapshots
        row["task_ids"] = kept_tasks
        repositories.append(row)

    payload = {
        "schema_version": "featureliftbench.source_registry.v1",
        "policy_id": combined.get("policy_id"),
        "generated_from": "benchmark/staging External-50 source assets",
        "repositories": sorted(
            repositories, key=lambda row: str(row.get("source_repo_id"))
        ),
        "snapshots": sorted(
            snapshots, key=lambda row: str(row.get("source_snapshot_id"))
        ),
    }
    payload["summary"] = _summary(payload)
    return payload


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    args = _parse_args()
    combined_path = args.combined.resolve()
    external50_path = args.external50_output.resolve()
    combined = json.loads(combined_path.read_text(encoding="utf-8"))
    main_task_ids = {
        path.name
        for path in MAIN_TASKS.iterdir()
        if path.is_dir() and (path / "metadata.json").is_file()
    }

    main = merge_existing_evidence(build_registry(MAIN_TASKS), combined)
    external50 = _extension_registry(combined, main_task_ids)
    if external50["summary"]["task_count"] == 0 and external50_path.is_file():
        # After the first split, the canonical Main registry intentionally has
        # no staging rows. Keep the already-separated extension registry so a
        # repeated migration is idempotent instead of erasing it.
        external50 = json.loads(external50_path.read_text(encoding="utf-8"))
    for label, payload in (("main", main), ("external50", external50)):
        errors = validate_registry(payload)
        if errors:
            for error in errors:
                print(f"{label}: {error}", file=sys.stderr)
            return 1

    _write(args.main_output.resolve(), main)
    _write(external50_path, external50)
    print(
        "main: "
        f"{main['summary']['repository_count']} repos / "
        f"{main['summary']['snapshot_count']} snapshots / "
        f"{main['summary']['task_count']} tasks"
    )
    print(
        "external50: "
        f"{external50['summary']['repository_count']} repos / "
        f"{external50['summary']['snapshot_count']} snapshots / "
        f"{external50['summary']['task_count']} tasks"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
