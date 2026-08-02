#!/usr/bin/env python3
"""Audit and design a balanced Python-200 selection without touching Main tasks."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_POLICY = ROOT / "benchmark/selection/python200_balance_policy.json"
DEFAULT_JSON = ROOT / "reports/audits/python200_balance_design.json"
DEFAULT_MD = ROOT / "reports/audits/python200_balance_design.md"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def counts(rows: list[dict[str, str]], field: str) -> dict[str, int]:
    return dict(sorted(Counter(row[field] for row in rows).items()))


def combined_counts(
    baseline: dict[str, int], expansion: dict[str, int]
) -> dict[str, int]:
    keys = set(baseline) | set(expansion)
    return {key: baseline.get(key, 0) + expansion.get(key, 0) for key in sorted(keys)}


def with_shares(values: dict[str, int], total: int) -> dict[str, dict[str, Any]]:
    return {
        key: {"count": value, "share": round(value / total, 6)}
        for key, value in values.items()
    }


def build_report(policy: dict[str, Any]) -> dict[str, Any]:
    selection = load_json(ROOT / policy["expansion"]["selection_path"])
    selected = [
        row for row in selection["rows"] if row.get("disposition") == "selected"
    ]
    selected_ids = {row["task_id"] for row in selected}
    main_ids = {
        path.name
        for path in (ROOT / "benchmark/tasks").iterdir()
        if (path / "metadata.json").is_file()
    }

    old_taxonomy = list(
        csv.DictReader(
            (ROOT / "artifacts/research_analysis/python150_task_taxonomy.csv").open(
                encoding="utf-8"
            )
        )
    )
    old_lift_rows = load_jsonl(ROOT / "reports/lift_taxonomy/LIFT_LABELS.jsonl")
    baseline_rows = [
        {
            "feature_family": row["feature_family_primary"],
            "entanglement": row["entanglement_primary_original"],
        }
        for row in old_taxonomy
    ]
    baseline_lift = dict(
        sorted(Counter(row["lift_type"] for row in old_lift_rows).items())
    )
    baseline_family = counts(baseline_rows, "feature_family")
    baseline_entanglement = counts(baseline_rows, "entanglement")

    replacements = policy["replace_candidates"]
    replacement_candidate_ids = set(replacements)
    assignments = policy.get("replacement_assignments", [])
    replacement_ids = {
        assignment["replacement_task_id"] for assignment in assignments
    }
    reclassifications = policy.get("label_reclassification_review", {})
    evidence = policy.get("redesign_evidence", {})
    member_gap_ids = set(evidence.get("undeclared_member_gap_task_ids", []))
    dependency_gap_ids = set(evidence.get("offline_dependency_gap_task_ids", []))
    care_ids = set(evidence.get("pass_with_care_task_ids", []))

    task_reviews: list[dict[str, Any]] = []
    retained_rows: list[dict[str, str]] = []
    for row in selected:
        task_id = row["task_id"]
        effective_family = reclassifications.get(task_id, {}).get(
            "feature_family", row["feature_family"]
        )
        effective = {
            "lift_type": row["final_lift_type"],
            "feature_family": effective_family,
            "entanglement": row["entanglement"],
        }
        reasons: list[str] = []
        flags: list[str] = []
        if task_id in replacement_ids:
            decision = "replacement_selected"
            assignment = next(
                value
                for value in assignments
                if value["replacement_task_id"] == task_id
            )
            reasons.append(
                f"Realizes balance slot {assignment['slot_id']} in place of "
                f"{assignment['candidate_task_id']}."
            )
        else:
            if task_id in member_gap_ids:
                flags.append("undeclared_member_gap")
                reasons.append("Close required class/member/signature API surface.")
            if task_id in dependency_gap_ids:
                flags.append("offline_dependency_gap")
                reasons.append("Vendor and verify the complete offline dependency closure.")
            if task_id in care_ids:
                flags.append("pass_with_care")
                reasons.append("Resolve the design-card stability warning before promotion.")
            if task_id in reclassifications:
                reasons.append(reclassifications[task_id]["reason"])
                if row["feature_family"] != reclassifications[task_id]["feature_family"]:
                    flags.append("label_reclassification_review")
            decision = "redesign" if flags else "keep"
        retained_rows.append(effective)

        released = ROOT / "benchmark/external50" / task_id
        task_dir = (
            released
            if (released / "metadata.json").is_file()
            else ROOT / "benchmark/staging" / task_id
        )
        metadata = load_json(task_dir / "metadata.json")
        card_text = (ROOT / row["design_card"]).read_text(encoding="utf-8")
        card_match = re.search(r"\*\*status:\*\* `([^`]+)`", card_text)
        task_reviews.append(
            {
                "task_id": task_id,
                "decision": decision,
                "current_labels": {
                    "lift_type": row["final_lift_type"],
                    "feature_family": row["feature_family"],
                    "entanglement": row["entanglement"],
                },
                "effective_labels": effective,
                "flags": flags,
                "reasons": reasons,
                "card_status": card_match.group(1) if card_match else "missing",
                "metadata_status": metadata.get("status"),
            }
        )

    slots = policy["replacement_slots"]
    proposed_expansion_rows = retained_rows
    raw_expansion_rows = [
        {
            "lift_type": row["final_lift_type"],
            "feature_family": row["feature_family"],
            "entanglement": row["entanglement"],
        }
        for row in selected
    ]

    baseline_count = policy["baseline"]["task_count"]
    target_total = policy["expansion"]["target_total"]
    raw = {
        "lift_type": combined_counts(
            baseline_lift, counts(raw_expansion_rows, "lift_type")
        ),
        "feature_family": combined_counts(
            baseline_family, counts(raw_expansion_rows, "feature_family")
        ),
        "entanglement": combined_counts(
            baseline_entanglement, counts(raw_expansion_rows, "entanglement")
        ),
    }
    proposed = {
        "lift_type": combined_counts(
            baseline_lift, counts(proposed_expansion_rows, "lift_type")
        ),
        "feature_family": combined_counts(
            baseline_family, counts(proposed_expansion_rows, "feature_family")
        ),
        "entanglement": combined_counts(
            baseline_entanglement, counts(proposed_expansion_rows, "entanglement")
        ),
    }

    checks: list[dict[str, Any]] = []

    def add_check(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": passed, "detail": detail})

    add_check(
        "baseline_task_count",
        len(main_ids) == baseline_count,
        f"expected {baseline_count}, found {len(main_ids)}",
    )
    add_check(
        "selected_task_count",
        len(selected) == policy["expansion"]["selected_count"],
        f"expected {policy['expansion']['selected_count']}, found {len(selected)}",
    )
    add_check(
        "selected_task_ids_unique",
        len(selected_ids) == len(selected),
        f"unique={len(selected_ids)} selected={len(selected)}",
    )
    overlap = sorted(selected_ids & main_ids)
    add_check("no_baseline_overlap", not overlap, f"overlap={overlap}")
    add_check(
        "replacement_slots_match_candidates",
        len(slots) == len(replacement_candidate_ids),
        f"slots={len(slots)} candidates={len(replacement_candidate_ids)}",
    )
    assigned_candidates = {
        assignment["candidate_task_id"] for assignment in assignments
    }
    assigned_slots = {assignment["slot_id"] for assignment in assignments}
    add_check(
        "replacement_assignments_complete",
        assigned_candidates == replacement_candidate_ids
        and assigned_slots == {slot["slot_id"] for slot in slots}
        and len(assignments) == len(slots),
        f"assignments={len(assignments)} candidates={len(assigned_candidates)} slots={len(assigned_slots)}",
    )
    add_check(
        "replacement_tasks_selected",
        replacement_ids <= selected_ids
        and not (replacement_candidate_ids & selected_ids),
        f"selected_replacements={len(replacement_ids & selected_ids)} "
        f"selected_candidates={sorted(replacement_candidate_ids & selected_ids)}",
    )
    add_check(
        "proposed_expansion_count",
        len(proposed_expansion_rows) == policy["expansion"]["selected_count"],
        f"proposed={len(proposed_expansion_rows)}",
    )

    bounds = policy["final_distribution_bounds"]
    for label, (minimum, maximum) in bounds["lift_type_share"].items():
        share = proposed["lift_type"].get(label, 0) / target_total
        add_check(
            f"lift_type_share:{label}",
            minimum <= share <= maximum,
            f"share={share:.1%} bounds={minimum:.1%}-{maximum:.1%}",
        )
    family_minimum = bounds["feature_family_share"]["minimum"]
    family_maximum = bounds["feature_family_share"]["maximum"]
    for label, value in proposed["feature_family"].items():
        share = value / target_total
        add_check(
            f"feature_family_share:{label}",
            family_minimum <= share <= family_maximum,
            f"share={share:.1%} bounds={family_minimum:.1%}-{family_maximum:.1%}",
        )
    for label, (minimum, maximum) in bounds[
        "entanglement_primary_share"
    ].items():
        share = proposed["entanglement"].get(label, 0) / target_total
        add_check(
            f"entanglement_share:{label}",
            minimum <= share <= maximum,
            f"share={share:.1%} bounds={minimum:.1%}-{maximum:.1%}",
        )

    return {
        "schema_version": "featureliftbench.python200_balance_design.v1",
        "policy_id": policy["policy_id"],
        "baseline": policy["baseline"],
        "summary": {
            "selected": len(selected),
            "keep": sum(r["decision"] == "keep" for r in task_reviews),
            "redesign": sum(r["decision"] == "redesign" for r in task_reviews),
            "replacement_selected": sum(
                r["decision"] == "replacement_selected" for r in task_reviews
            ),
            "replaced_candidates": len(replacement_candidate_ids),
            "replacement_slots": len(slots),
            "all_balance_checks_pass": all(check["passed"] for check in checks),
            "promotion_ready": False,
        },
        "raw_python200_distribution": {
            key: with_shares(value, target_total) for key, value in raw.items()
        },
        "proposed_python200_distribution": {
            key: with_shares(value, target_total) for key, value in proposed.items()
        },
        "task_reviews": sorted(task_reviews, key=lambda row: row["task_id"]),
        "replacement_slots": slots,
        "checks": checks,
        "next_gate": "Run offline reference, isolation, Docker, and lifecycle gates for the realized External-50 selection.",
    }


def render_table(title: str, values: dict[str, dict[str, Any]]) -> list[str]:
    lines = [f"## {title}", "", "| label | count | share |", "| --- | ---: | ---: |"]
    for label, value in values.items():
        lines.append(f"| {label} | {value['count']} | {value['share']:.1%} |")
    lines.append("")
    return lines


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Python-200 Balance Design",
        "",
        f"Policy: `{report['policy_id']}`",
        f"Frozen baseline: `{report['baseline']['freeze_id']}` ({report['baseline']['task_count']} tasks)",
        "",
        "This is a selection-design artifact. It does not promote tasks or modify the frozen Python-150 baseline.",
        "",
        "## Decision Summary",
        "",
        f"- keep: {summary['keep']}",
        f"- redesign: {summary['redesign']}",
        f"- replacement_selected: {summary['replacement_selected']}",
        f"- replaced_candidates: {summary['replaced_candidates']}",
        f"- replacement_slots: {summary['replacement_slots']}",
        f"- balance checks: {'PASS' if summary['all_balance_checks_pass'] else 'FAIL'}",
        f"- promotion ready: {str(summary['promotion_ready']).lower()}",
        "",
    ]
    proposed = report["proposed_python200_distribution"]
    lines.extend(render_table("Proposed Lift Distribution", proposed["lift_type"]))
    lines.extend(
        render_table("Proposed Feature-Family Distribution", proposed["feature_family"])
    )
    lines.extend(
        render_table("Proposed Primary-Coupling Distribution", proposed["entanglement"])
    )
    lines.extend(
        [
            "## Task Decisions",
            "",
            "| task_id | decision | flags |",
            "| --- | --- | --- |",
        ]
    )
    for row in report["task_reviews"]:
        lines.append(
            f"| `{row['task_id']}` | {row['decision']} | {', '.join(row['flags']) or '-'} |"
        )
    lines.extend(["", "## Replacement Slots", ""])
    for slot in report["replacement_slots"]:
        lines.append(
            f"- `{slot['slot_id']}`: {slot['lift_type']} / {slot['feature_family']} / "
            f"{slot['entanglement']} - {slot['design_requirement']}"
        )
    lines.extend(["", "## Checks", ""])
    for check in report["checks"]:
        lines.append(
            f"- {'PASS' if check['passed'] else 'FAIL'} `{check['name']}`: {check['detail']}"
        )
    lines.extend(["", f"Next gate: {report['next_gate']}", ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_MD)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    report = build_report(load_json(args.policy))
    json_text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    markdown_text = render_markdown(report)
    if args.check:
        mismatches = []
        if not args.output_json.is_file() or args.output_json.read_text() != json_text:
            mismatches.append(str(args.output_json))
        if not args.output_md.is_file() or args.output_md.read_text() != markdown_text:
            mismatches.append(str(args.output_md))
        if mismatches:
            raise SystemExit("stale Python-200 balance outputs: " + ", ".join(mismatches))
    else:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json_text, encoding="utf-8")
        args.output_md.write_text(markdown_text, encoding="utf-8")
        print(f"wrote {args.output_json.relative_to(ROOT)}")
        print(f"wrote {args.output_md.relative_to(ROOT)}")

    failed = [check for check in report["checks"] if not check["passed"]]
    print(
        "Python-200 balance design: "
        f"keep={report['summary']['keep']} redesign={report['summary']['redesign']} "
        f"replacements={report['summary']['replacement_selected']} "
        f"checks={'PASS' if not failed else 'FAIL'}"
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
