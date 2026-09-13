"""Shared inputs for the current paper; standard library only, no evaluations."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parents[1]
MANIFEST_PATH = PAPER / "paper_sources.json"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def boolean(value: str) -> bool:
    if value.lower() not in {"true", "false"}:
        raise ValueError(f"Invalid boolean: {value!r}")
    return value.lower() == "true"


MANIFEST = read_json(MANIFEST_PATH)
MODELS = tuple(item["id"] for item in MANIFEST["models"])
MODEL_RECORDS = {item["id"]: item for item in MANIFEST["models"]}
SHORT = {model: MODEL_RECORDS[model]["short"] for model in MODELS}
DISPLAY_NAMES = {SHORT[model]: MODEL_RECORDS[model]["display"] for model in MODELS}


def input_path(name: str) -> Path:
    return ROOT / MANIFEST["inputs"][name]


def run_directory(model: str) -> Path:
    return ROOT / MODEL_RECORDS[model]["run_directory"]


RESULTS = input_path("main_results")
FREEZE_PATH = input_path("release_manifest")
STATS_PATH = input_path("paired_statistics")
CHAPTER2_PATH = input_path("task_evidence")


def paper_task_ids() -> set[str]:
    selection = read_json(input_path("task_selection"))
    assert selection["source_manifest"] == MANIFEST["inputs"]["release_manifest"]
    assert selection["source_manifest_sha256"] == hashlib.sha256(FREEZE_PATH.read_bytes()).hexdigest()
    ids = selection["task_ids"]
    assert len(ids) == len(set(ids)) == MANIFEST["benchmark"]["tasks"] == 150
    return set(ids)


def paper_tasks() -> dict:
    """Select the fixed Python-150 membership from the historical source freeze."""
    historical = read_json(FREEZE_PATH)["tasks"]
    ids = paper_task_ids()
    assert ids == {t for t, v in historical.items() if v["stratum"] == "python150"}
    return {t: historical[t] for t in sorted(ids)}


def validate_scope() -> dict:
    """Check declared membership, outcomes and counts without executing task code."""
    assert MANIFEST["schema_version"] == 1
    for name in MANIFEST["inputs"]:
        assert input_path(name).is_file(), input_path(name)
    release = paper_tasks()
    inventory = read_json(input_path("task_inventory"))["tasks"]
    assert len(inventory) == len({t["task_id"] for t in inventory}) == len(release)
    assert {t["task_id"] for t in inventory} == set(release)
    scope = MANIFEST["benchmark"]
    assert len(release) == scope["tasks"] == 150
    assert len({t["source_repo_id"] for t in release.values()}) == scope["repositories"]
    assert len({t["source_snapshot_id"] for t in release.values()}) == scope["snapshots"]
    for task in inventory:
        for field in ("source_repo_id", "source_snapshot_id"):
            assert task[field] == release[task["task_id"]][field], (task["task_id"], field)
    evidence = read_json(CHAPTER2_PATH)
    assert evidence["strata"]["complete"] == {k: scope[k] for k in ("tasks", "repositories", "snapshots")}
    replay = evidence["oracle_membership"]
    assert len(replay) == 450 and all(r["passed"] for r in replay)
    assert {(r["task_id"], r["repetition"]) for r in replay} == {
        (t, n) for t in release for n in (1, 2, 3)}
    coverage = read_json(input_path("coverage_data"))
    assert coverage["release_tasks"] == coverage["mechanism_tasks"] == len(release)
    assert {t["task_id"] for t in coverage["complete_tasks"]} == set(release)

    rows = read_csv(RESULTS)
    comparison = MANIFEST["comparison"]
    assert len(MODELS) == len(set(MODELS)) == comparison["configurations"] == 6
    cells = {(row["model"], row["task_id"]): row for row in rows}
    task_ids = {row["task_id"] for row in rows}
    assert len(rows) == len(cells) == comparison["outcomes"] == 900
    assert len(task_ids) == comparison["tasks"] == 150
    assert task_ids == set(release)
    assert set(cells) == {(model, task) for model in MODELS for task in task_ids}
    for row in rows:
        passed = boolean(row["usable_submission"]) and all(
            boolean(row[field]) for field in ("build_pass", "public_pass", "hidden_pass", "isolation_pass")
        )
        assert boolean(row["functional_pass"]) == passed, (row["model"], row["task_id"])

    counts = {}
    for model in MODELS:
        count = sum(boolean(cells[model, task]["functional_pass"]) for task in task_ids)
        assert count == MODEL_RECORDS[model]["main_passes"], model
        counts[SHORT[model]] = count
    for relative in MANIFEST["paper_files"]:
        assert (PAPER / relative).is_file(), relative
    return {"benchmark_tasks": len(release), "repositories": scope["repositories"],
            "snapshots": scope["snapshots"], "common_tasks": len(task_ids),
            "configurations": len(MODELS), "outcomes": len(rows),
            "main_passes": counts}
