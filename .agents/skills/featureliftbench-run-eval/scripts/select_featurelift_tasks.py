#!/usr/bin/env python3
"""Select FeatureLiftBench task IDs for batch and suite runs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Optional


def find_repo_root() -> Path:
    cwd = Path.cwd().resolve()
    for candidate in (cwd, *cwd.parents):
        if (candidate / "benchmark" / "manifest.json").is_file():
            return candidate
    return cwd


ROOT = find_repo_root()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def manifest_exclusions(split_id: str) -> set[str]:
    manifest_path = ROOT / "benchmark" / "manifest.json"
    if not manifest_path.is_file():
        return set()
    manifest = load_json(manifest_path)
    excluded = manifest.get("exclude_task_ids", {}).get(split_id, [])
    return set(excluded) if isinstance(excluded, list) else set()


def task_records(root: Path, excluded: Optional[set[str]] = None) -> list[tuple[str, Path, dict[str, Any]]]:
    excluded = excluded or set()
    records: list[tuple[str, Path, dict[str, Any]]] = []
    if not root.is_dir():
        return records
    for task_dir in sorted(path for path in root.iterdir() if path.is_dir()):
        if task_dir.name in excluded:
            continue
        meta_path = task_dir / "metadata.json"
        if not meta_path.is_file():
            continue
        try:
            meta = load_json(meta_path)
        except json.JSONDecodeError:
            continue
        records.append((task_dir.name, task_dir, meta))
    return records


def has_tag(meta: dict[str, Any], tag: str) -> bool:
    tags = meta.get("tags")
    return isinstance(tags, list) and tag in tags


def select(args: argparse.Namespace) -> list[tuple[str, Path, dict[str, Any]]]:
    if args.suite in {"main", "batch1", "batch2", "batch3-main"}:
        records = task_records(ROOT / "benchmark" / "tasks", manifest_exclusions("python_main_candidate"))
        if args.suite == "batch1":
            records = [record for record in records if has_tag(record[2], "batch-1")]
        elif args.suite == "batch2":
            records = [
                record
                for record in records
                if not has_tag(record[2], "batch-1") and not has_tag(record[2], "batch-3")
            ]
        elif args.suite == "batch3-main":
            records = [record for record in records if has_tag(record[2], "batch-3")]
    elif args.suite == "batch3-pilot":
        records = task_records(ROOT / "benchmark" / "batch3_pilot")
        statuses = set(args.status or ["materialized_candidate"])
        if not args.include_blocked:
            records = [record for record in records if record[2].get("status") != "blocked"]
        if statuses:
            records = [record for record in records if record[2].get("status") in statuses]
    elif args.suite == "staging":
        records = task_records(ROOT / "benchmark" / "staging")
        if args.status:
            statuses = set(args.status)
            records = [record for record in records if record[2].get("status") in statuses]
    elif args.suite == "sanity":
        records = task_records(ROOT / "benchmark" / "sanity", manifest_exclusions("python_sanity"))
    else:
        raise SystemExit(f"unknown suite: {args.suite}")

    if args.limit is not None:
        records = records[: args.limit]
    return records


def print_output(records: list[tuple[str, Path, dict[str, Any]]], fmt: str) -> None:
    ids = [record[0] for record in records]
    if fmt == "ids":
        for task_id in ids:
            print(task_id)
    elif fmt == "args":
        for task_id in ids:
            print("--task-id")
            print(task_id)
    elif fmt == "json":
        print(json.dumps({"count": len(ids), "task_ids": ids}, indent=2))
    else:
        raise SystemExit(f"unknown format: {fmt}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--suite",
        required=True,
        choices=["main", "batch1", "batch2", "batch3-main", "batch3-pilot", "staging", "sanity"],
    )
    parser.add_argument("--status", action="append", help="metadata status filter; may be repeated")
    parser.add_argument("--include-blocked", action="store_true", help="include blocked batch3-pilot tasks")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--format", choices=["ids", "args", "json"], default="ids")
    args = parser.parse_args()
    print_output(select(args), args.format)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
