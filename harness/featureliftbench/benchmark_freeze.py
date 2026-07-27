"""Read the active Full-Repository / No-Hint benchmark freeze."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


POLICY_ID = "featureliftbench.full_repository_no_hint_main.v3"
FREEZE_ENV = "FEATURELIFTBENCH_BENCHMARK_FREEZE"
DEFAULT_FREEZE = Path(
    "artifacts/research_analysis/v3/current_benchmark_freeze.json"
)


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def benchmark_freeze_path() -> Path:
    configured = os.environ.get(FREEZE_ENV, "").strip()
    if configured:
        return Path(configured).expanduser().resolve()
    return (project_root() / DEFAULT_FREEZE).resolve()


def benchmark_freeze_provenance(
    task_id: str,
    *,
    require: bool = False,
) -> dict[str, Any] | None:
    path = benchmark_freeze_path()
    if not path.is_file():
        if require:
            raise ValueError(
                "Python Main requires a passing v3 benchmark freeze; "
                "run scripts/build_v3_benchmark_freeze.py"
            )
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"benchmark freeze must be a JSON object: {path}")
    if (
        payload.get("policy_id") != POLICY_ID
        or payload.get("gate_pass") is not True
        or payload.get("task_count") != 150
    ):
        raise ValueError(f"benchmark freeze is not a passing v3 freeze: {path}")
    tasks = payload.get("tasks")
    task = tasks.get(task_id) if isinstance(tasks, dict) else None
    if not isinstance(task, dict):
        if require:
            raise ValueError(f"{task_id}: task is absent from active v3 freeze")
        return None
    environment = payload.get("environment")
    if not isinstance(environment, dict):
        environment = {}
    return {
        "policy_id": payload.get("policy_id"),
        "freeze_id": payload.get("freeze_id"),
        "split": payload.get("split"),
        "task_id": task_id,
        "task_revision": task.get("task_revision"),
        "spec_hash": task.get("spec_hash"),
        "generated_task_hash": task.get("generated_task_hash"),
        "source_snapshot_id": task.get("source_snapshot_id"),
        "source_tree_sha256": task.get("source_tree_sha256"),
        "source_archive_sha256": task.get("source_archive_sha256"),
        "primary_metric": payload.get("primary_metric"),
        "environment": environment,
    }
