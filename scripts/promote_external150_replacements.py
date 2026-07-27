#!/usr/bin/env python3
"""Atomically replace Curated-7 with the preregistered External-7."""

from __future__ import annotations

import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "benchmark" / "tasks"
STAGING = ROOT / "benchmark" / "staging"
CURATED = ROOT / "benchmark" / "curated"
SUBMISSIONS = ROOT / "benchmark" / "submissions"

CURATED_TASKS = (
    "vibe_app__csv_transform_core__001",
    "vibe_app__orm_query_ast_core__001",
    "vibe_app__plugin_registry_core__001",
    "vibe_app__pricing_rules_core__001",
    "vibe_app__rules_engine_core__001",
    "vibe_app__session_registry_core__001",
    "vibe_app__yaml_config_bootstrap__001",
)
EXTERNAL_TASKS = (
    "itsdangerous__timed_serializer_core__001",
    "flask__route_dispatch_core__001",
    "parse__format_parser_core__001",
    "filelock__reentrant_lock_core__001",
    "blinker__signal_registry_core__001",
    "python_decouple__config_repository_core__001",
    "decorator__signature_preserving_core__001",
)


def _set_split_metadata(task_dir: Path, *, split: str, status: str) -> None:
    path = task_dir / "metadata.json"
    metadata = json.loads(path.read_text(encoding="utf-8"))
    metadata["status"] = status
    metadata["benchmark_split"] = split
    metadata["selection_id"] = (
        "external150-replacement-20260727-v1"
        if split == "external_main"
        else "legacy-curated-v1"
    )
    path.write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    curated_tasks_root = CURATED / "tasks"
    curated_references_root = CURATED / "references"
    curated_tasks_root.mkdir(parents=True, exist_ok=True)
    curated_references_root.mkdir(parents=True, exist_ok=True)

    for task_id in CURATED_TASKS:
        source = MAIN / task_id
        target = curated_tasks_root / task_id
        if target.exists():
            raise FileExistsError(target)
        if not source.is_dir():
            raise FileNotFoundError(source)
        shutil.move(str(source), str(target))
        _set_split_metadata(target, split="curated", status="curated")
        oracle = SUBMISSIONS / task_id / "oracle"
        if oracle.is_dir():
            shutil.copytree(oracle, curated_references_root / task_id)
            shutil.rmtree(oracle.parent)

    curated_source = ROOT / "benchmark" / "sources" / "vibe_app"
    curated_source_target = CURATED / "sources" / "vibe_app"
    if curated_source.is_dir():
        curated_source_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(curated_source), str(curated_source_target))

    for task_id in EXTERNAL_TASKS:
        source = STAGING / task_id
        target = MAIN / task_id
        if target.exists():
            raise FileExistsError(target)
        if not source.is_dir():
            raise FileNotFoundError(source)
        shutil.copytree(source, target)
        _set_split_metadata(target, split="external_main", status="main")
        shutil.rmtree(source)

    main_tasks = [
        path
        for path in MAIN.iterdir()
        if path.is_dir() and (path / "metadata.json").is_file()
    ]
    curated_tasks = [
        path
        for path in curated_tasks_root.iterdir()
        if path.is_dir() and (path / "metadata.json").is_file()
    ]
    if len(main_tasks) != 150:
        raise ValueError(f"External Main must contain 150 tasks, found {len(main_tasks)}")
    if len(curated_tasks) != 7:
        raise ValueError(f"Curated split must contain 7 tasks, found {len(curated_tasks)}")
    if any(path.name.startswith("vibe_app__") for path in main_tasks):
        raise ValueError("Curated task leaked into External Main")
    print("Promoted External-7 and moved Curated-7")
    print("External Main: 150 tasks; Curated: 7 tasks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
