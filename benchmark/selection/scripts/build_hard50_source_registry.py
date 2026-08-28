#!/usr/bin/env python3
"""Build Hard-50 source archives and benchmark/sources/hard50_registry.json.

Uses the already-materialized hard50_pilot/<id>/repo trees (the agent-visible
snapshots), not a fresh upstream clone. Does not touch Python-150 or External-50.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "harness"))

from build_source_registry import canonicalize_url, source_repo_id  # noqa: E402
from featureliftbench.source_archive import sha256_file, tree_stats  # noqa: E402
from materialize_full_sources import _find_license, _write_deterministic_archive  # noqa: E402

PILOT_ROOT = ROOT / "benchmark/hard50_pilot"
SELECTION_PATH = ROOT / "benchmark/selection/hard50_expansion_20260827.json"
HARD50_REGISTRY = ROOT / "benchmark/sources/hard50_registry.json"
ARCHIVE_DIR = ROOT / "benchmark/sources/archives"


def selected_rows() -> list[dict[str, Any]]:
    selection = json.loads(SELECTION_PATH.read_text(encoding="utf-8"))
    return [row for row in selection["rows"] if row.get("disposition") == "selected"]


def license_path_for(repo: Path) -> str | None:
    try:
        return _find_license(repo)
    except ValueError:
        return None


def build() -> dict[str, Any]:
    rows = selected_rows()
    if len(rows) != 50:
        raise SystemExit(f"expected 50 selected Hard-50 rows, found {len(rows)}")
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    repositories: dict[str, dict[str, Any]] = {}
    snapshots: list[dict[str, Any]] = []

    for row in rows:
        task_id = str(row["task_id"])
        task_dir = PILOT_ROOT / task_id
        repo = task_dir / "repo"
        metadata = json.loads((task_dir / "metadata.json").read_text(encoding="utf-8"))
        source = metadata["source"]
        commit = str(source["commit"]).strip().lower()
        if len(commit) != 40:
            raise SystemExit(f"{task_id}: source.commit is not a 40-hex pin")
        url = str(source["url"]).strip()
        canonical, kind, org = canonicalize_url(url)
        repo_id = source_repo_id(canonical, kind)
        short = commit[:12]
        snapshot_id = f"{repo_id}__{short}"
        if not repo.is_dir():
            raise SystemExit(f"{task_id}: missing repo/")
        stats = tree_stats(repo)
        filename = f"{snapshot_id}--{stats.source_tree_sha256[:16]}.tar.gz"
        archive = ARCHIVE_DIR / filename
        _write_deterministic_archive(repo, archive)
        archive_sha = sha256_file(archive)
        display = str(source.get("name") or row.get("package") or task_id)
        license_id = str(source.get("license") or "UNKNOWN")
        repo_row = repositories.get(repo_id)
        if repo_row is None:
            repositories[repo_id] = {
                "canonical_url": canonical,
                "display_names": [display],
                "ecosystem_family": "unassigned",
                "licenses": [license_id],
                "snapshot_ids": [snapshot_id],
                "source_kind": kind,
                "source_repo_id": repo_id,
                "task_ids": [task_id],
                "upstream_org": org,
            }
        else:
            if snapshot_id not in repo_row["snapshot_ids"]:
                repo_row["snapshot_ids"].append(snapshot_id)
            if task_id not in repo_row["task_ids"]:
                repo_row["task_ids"].append(task_id)
            if display not in repo_row["display_names"]:
                repo_row["display_names"].append(display)
            if license_id not in repo_row["licenses"]:
                repo_row["licenses"].append(license_id)
        snapshots.append(
            {
                "acquisition_method": "git_checkout",
                "archive_path": f"benchmark/sources/archives/{filename}",
                "archive_sha256": archive_sha,
                "current_snapshot_scope": "full_tracked_tree",
                "license_text_path": license_path_for(repo),
                "max_path_depth": stats.max_path_depth,
                "python_file_count": stats.python_file_count,
                "python_loc": stats.python_loc,
                "requested_revision": commit,
                "resolved_commit": commit,
                "revision_kind": "git_commit",
                "source_repo_id": repo_id,
                "source_snapshot_id": snapshot_id,
                "source_tree_sha256": stats.source_tree_sha256,
                "status": "ready",
                "target_snapshot_scope": "full_tracked_tree",
                "task_ids": [task_id],
                "total_bytes": stats.total_bytes,
                "tracked_file_count": stats.tracked_file_count,
            }
        )
        print(f"{task_id}: {filename} files={stats.tracked_file_count}", flush=True)

    repo_list = sorted(repositories.values(), key=lambda item: item["source_repo_id"])
    snap_list = sorted(snapshots, key=lambda item: item["source_snapshot_id"])
    return {
        "schema_version": "featureliftbench.source_registry.v1",
        "policy_id": "featureliftbench.full_repository_source.v2",
        "generated_from": "hard50_pilot selected repo trees 2026-08-27",
        "repositories": repo_list,
        "snapshots": snap_list,
        "summary": {
            "repository_count": len(repo_list),
            "snapshot_count": len(snap_list),
            "task_count": len(rows),
            "external_repository_count": len(repo_list),
            "curated_repository_count": 0,
            "ready_snapshot_count": len(snap_list),
            "pending_snapshot_count": 0,
        },
    }


def main() -> int:
    registry = build()
    HARD50_REGISTRY.write_text(
        json.dumps(registry, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    summary = registry["summary"]
    print(
        f"wrote {HARD50_REGISTRY} "
        f"repos={summary['repository_count']} snapshots={summary['snapshot_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
