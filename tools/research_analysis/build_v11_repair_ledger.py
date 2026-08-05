#!/usr/bin/env python3
"""Version quarantined Oracle repairs without rewriting history."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "benchmark/quarantine/python_v1_1_revision_2.json"
RUN_ROOT = ROOT / "experiments/validation/v1_1/v1_1_repair_preflight/revision_3"
LEDGER = ROOT / "artifacts/research_analysis/v1_1/oracle_repair_ledger.json"
OUTPUT = ROOT / "benchmark/quarantine/python_v1_1_revision_3.json"
CURRENT_POINTER = ROOT / "artifacts/research_analysis/v1_1/current_oracle_freeze.json"
REPAIR_REVISION = 3
BENCHMARK_VERSION = "python-v1.1-revision-3"

REPAIRS = {
    "babel__plural_core__001": "locale pickle unpickler maps babel.* to featurelifted.* with dates/numbers stubs",
    "bleach__sanitize_core__001": "vendored webencodings under featurelifted/_vendor with import bootstrap",
    "deepdiff__deep_compare_core__001": "vendored orderly_set and inlined LRU cache for lfucache",
    "dynaconf__settings_merge_core__001": "rewrote dynaconf.* loader module path strings to featurelifted.*",
    "environs__typed_env_core__001": "removed runtime Field[...] subscript from oracle fields.py",
    "jinja2__compile_render_core__001": "generated runtime imports target featurelifted instead of jinja2",
    "jinja2__extensions_core__001": "generated runtime imports target featurelifted instead of jinja2",
    "jinja2__filters_tests_core__001": "generated runtime imports target featurelifted instead of jinja2",
    "lark__parse_tree_core__001": "stdlib grammar loader uses featurelifted package name",
    "lark__visitor_transform_core__001": "stdlib grammar loader uses featurelifted package name",
    "passlib__hash_context_core__001": "handler registry module path strings target featurelifted.handlers.*",
    "pygments__formatter_core__001": "dynamic pygments module strings rewritten; bundled default style",
    "pygments__lexer_core__001": "dynamic pygments module strings rewritten; lex() honors stripall Text filtering",
}


def passed(path: Path) -> bool:
    result = json.loads(path.read_text(encoding="utf-8"))
    return bool(
        result.get("build_pass")
        and (result.get("public_tests") or {}).get("passed")
        and (result.get("hidden_tests") or {}).get("passed")
        and result.get("original_import_pass")
    )


def main() -> int:
    base = json.loads(BASE.read_text(encoding="utf-8"))
    prior_resolved = list(base.get("resolved_tasks") or [])
    resolved = list(prior_resolved)
    for task_id, repair in REPAIRS.items():
        paths = [RUN_ROOT / task_id / f"run_{repeat}/result.json" for repeat in (1, 2, 3)]
        if not all(path.is_file() and passed(path) for path in paths):
            missing = [str(path.relative_to(ROOT)) for path in paths if not path.is_file()]
            raise RuntimeError(f"repair validation incomplete: {task_id}; missing={missing}")
        resolved.append(
            {
                "task_id": task_id,
                "repair": repair,
                "repetitions": 3,
                "all_build_public_hidden_isolation_pass": True,
                "result_paths": [str(path.relative_to(ROOT)) for path in paths],
                "review_status": "author_repaired_three_repeat_docker_validated",
            }
        )
    resolved_ids = {str(row.get("task_id")) for row in resolved}
    active = [
        row
        for row in base.get("active_tasks") or []
        if str(row.get("task_id")) not in resolved_ids
    ]
    pointer = json.loads(CURRENT_POINTER.read_text(encoding="utf-8")) if CURRENT_POINTER.is_file() else {}
    current_freeze_id = str(pointer.get("freeze_id") or "")
    current_root = ROOT / "experiments/validation/v1_1/v1_1_oracle_validation" / current_freeze_id if current_freeze_id else None
    full_summary_path = current_root / "full/summary.json" if current_root else None
    full_summary = (
        json.loads(full_summary_path.read_text(encoding="utf-8"))
        if full_summary_path and full_summary_path.is_file()
        else {}
    )
    active_ids = {str(row.get("task_id")) for row in active}
    failed_ids = set(full_summary.get("failed_task_ids") or [])
    full_revision_validated = bool(
        full_summary.get("run_count") == 450
        and not full_summary.get("unstable_task_ids")
        and not full_summary.get("incomplete_task_ids")
        and not full_summary.get("invalid_artifact_task_ids")
        and failed_ids == active_ids
    )
    if full_revision_validated and current_root:
        for row in active:
            task_id = str(row["task_id"])
            row["current_freeze_id"] = current_freeze_id
            row["current_result_paths"] = [
                str((current_root / "full" / f"rep-{repeat}" / task_id / "result.json").relative_to(ROOT))
                for repeat in (1, 2, 3)
            ]
        for row in resolved:
            if row.get("current_full_result_paths"):
                continue
            task_id = str(row["task_id"])
            if not (current_root / "full" / "rep-1" / task_id / "result.json").is_file():
                continue
            row["current_freeze_id"] = current_freeze_id
            row["current_full_result_paths"] = [
                str((current_root / "full" / f"rep-{repeat}" / task_id / "result.json").relative_to(ROOT))
                for repeat in (1, 2, 3)
            ]
    payload = {
        "schema_version": "featureliftbench.versioned_quarantine.v2",
        "benchmark_version": BENCHMARK_VERSION,
        "repair_revision": REPAIR_REVISION,
        "source_freeze_id": base.get("current_freeze_id") or base.get("source_freeze_id"),
        "physical_deletion": False,
        "policy": base.get("policy"),
        "active_tasks": active,
        "resolved_tasks": resolved,
        "active_task_count": len(active),
        "resolved_task_count": len(resolved),
        "current_freeze_id": current_freeze_id or None,
        "full_revalidation_pending_due_asset_revision": not full_revision_validated,
        "interpretation_boundary": (
            "Sixteen tasks passed targeted three-repeat Docker validation after Oracle packaging repairs. "
            "A current 450-run freeze is linked when its stable failure set exactly equals the active "
            "quarantine; formal annotation review remains separate."
        ),
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    LEDGER.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if full_revision_validated and current_root:
        (current_root / "quarantine_manifest.json").write_text(
            json.dumps(
                {
                    "schema_version": f"featureliftbench.quarantine.v1_1_revision_{REPAIR_REVISION}",
                    "freeze_id": current_freeze_id,
                    "physical_deletion": False,
                    "tasks": active,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
    print(f"active={len(active)} resolved={len(resolved)} full_revision_validated={full_revision_validated}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
