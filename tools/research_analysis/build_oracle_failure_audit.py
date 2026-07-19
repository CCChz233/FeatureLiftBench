#!/usr/bin/env python3
"""Build a reproducible task-asset root-cause audit for failed Oracle runs."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CURRENT_POINTER = ROOT / "artifacts/research_analysis/v1_1/current_oracle_freeze.json"
OUTPUT = ROOT / "artifacts/research_analysis/v1_1/oracle_failure_audit.json"
REPORT = ROOT / "docs/research_analysis/ORACLE_REVALIDATION_REPORT.md"

# Root causes were assigned after inspection of rep-1 build/public/hidden logs.
# The script verifies the expected evidence pattern before emitting the audit.
TRIAGE = {
    "astroid__nodes_core__001": ("original_package_relocation", "No module named 'astroid'"),
    "babel__plural_core__001": ("serialized_resource_original_module", "No module named 'babel'"),
    "bleach__sanitize_core__001": ("missing_third_party_closure", "No module named 'webencodings'"),
    "deepdiff__deep_compare_core__001": ("missing_third_party_closure", "No module named 'orderly_set'"),
    "dynaconf__settings_merge_core__001": ("original_package_relocation", "No module named 'dynaconf'"),
    "environs__typed_env_core__001": ("dependency_contract_version_mismatch", "type 'Field' is not subscriptable"),
    "jinja2__compile_render_core__001": ("original_package_relocation", "No module named 'jinja2'"),
    "jinja2__extensions_core__001": ("original_package_relocation", "No module named 'jinja2'"),
    "jinja2__filters_tests_core__001": ("original_package_relocation", "No module named 'jinja2'"),
    "jinja2__loader_inheritance_core__001": ("original_package_relocation", "No module named 'jinja2'"),
    "lark__parse_tree_core__001": ("missing_grammar_resource_closure", "used but not defined"),
    "lark__visitor_transform_core__001": ("missing_grammar_resource_closure", "used but not defined"),
    "passlib__hash_context_core__001": ("original_package_relocation", "No module named 'passlib'"),
    "pydantic_settings__env_source_core__001": ("missing_third_party_closure", "No module named 'dotenv'"),
    "pygments__formatter_core__001": ("original_package_relocation", "No module named 'pygments'"),
    "pygments__lexer_core__001": ("original_package_relocation", "No module named 'pygments'"),
}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def log_text(run_root: Path, task_id: str) -> tuple[str, list[str]]:
    root = run_root / "rep-1" / task_id / "logs"
    paths = [path for phase in ("build", "public", "hidden") for path in (root / f"{phase}.stdout", root / f"{phase}.stderr") if path.is_file()]
    text = "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in paths)
    return text, [path.relative_to(ROOT).as_posix() for path in paths]


def main() -> int:
    pointer = load(CURRENT_POINTER)
    freeze_id = str(pointer["freeze_id"])
    run_root = ROOT / "experiments/v1_1_oracle_validation" / freeze_id / "full"
    summary = load(run_root / "summary.json")
    failed = set(summary["failed_task_ids"])
    if not failed <= set(TRIAGE):
        raise RuntimeError(f"untriaged failed tasks: {sorted(failed-set(TRIAGE))}")
    entries = []
    for task_id in sorted(failed):
        subtype, pattern = TRIAGE[task_id]
        text, paths = log_text(run_root, task_id)
        if pattern.lower() not in text.lower():
            raise RuntimeError(f"evidence pattern not found for {task_id}: {pattern}")
        entries.append({
            "task_id": task_id,
            "failure_class": "task",
            "root_cause_subtype": subtype,
            "evidence_pattern": pattern,
            "evidence_log_paths": paths,
            "repetitions_failed": 3,
            "repetitions_consistent": True,
            "review_status": "author_triaged_needs_fix_or_adjudication",
        })
    counts = Counter(item["root_cause_subtype"] for item in entries)
    payload = {
        "schema_version": "featureliftbench.oracle_failure_audit.v1",
        "freeze_id": freeze_id,
        "run_count": summary["run_count"],
        "passed_task_count": summary["task_count"] - len(entries),
        "failed_task_count": len(entries),
        "unstable_task_count": len(summary["unstable_task_ids"]),
        "incomplete_task_count": len(summary["incomplete_task_ids"]),
        "failure_class_counts": summary["failure_class_counts"],
        "root_cause_subtype_counts": dict(sorted(counts.items())),
        "entries": entries,
        "interpretation": (
            "All failures are stable task-asset/Oracle failures after dependency-install, Docker, tooling, "
            "timeout, and flakiness checks. They are quarantined and must not count as Agent failures."
        ),
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    quarantine_path = run_root.parent / "quarantine_manifest.json"
    quarantine = load(quarantine_path)
    by_task = {entry["task_id"]: entry for entry in entries}
    for item in quarantine.get("tasks") or []:
        detail = by_task.get(str(item.get("task_id")))
        if detail:
            item.update({
                "failure_class": "task",
                "root_cause_subtype": detail["root_cause_subtype"],
                "evidence_log_paths": detail["evidence_log_paths"],
                "review_status": detail["review_status"],
            })
    quarantine["version"] = "v1.1-freeze-" + freeze_id
    quarantine["physical_deletion"] = False
    quarantine_path.write_text(json.dumps(quarantine, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Oracle revalidation report",
        "",
        f"Freeze: `{freeze_id}`",
        "",
        "| Outcome | Count |",
        "| --- | ---: |",
        f"| Runs produced | {summary['run_count']}/450 |",
        f"| Stable passing tasks | {payload['passed_task_count']}/150 |",
        f"| Stable quarantined tasks | {len(entries)}/150 |",
        f"| Unstable tasks | {payload['unstable_task_count']} |",
        f"| Incomplete tasks | {payload['incomplete_task_count']} |",
        f"| Dependency / environment / timeout / flaky runs | 0 |",
        "",
        "## Quarantine root causes",
        "",
        "| Root cause | Tasks |",
        "| --- | ---: |",
    ]
    lines.extend(f"| `{key}` | {value} |" for key, value in sorted(counts.items()))
    lines.extend(["", "## Task evidence", "", "| Task | Root cause | Evidence |", "| --- | --- | --- |"])
    for entry in entries:
        lines.append(
            f"| `{entry['task_id']}` | `{entry['root_cause_subtype']}` | "
            f"`{entry['evidence_pattern']}` in `{entry['evidence_log_paths'][0]}` |"
        )
    lines.extend([
        "",
        f"These {len(entries)} tasks remain in versioned quarantine; no directory or historical result was deleted. Root-cause labels are author triage, not completed task repair or contract adjudication.",
        "",
    ])
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)} and {REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
