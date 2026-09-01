#!/usr/bin/env python3
"""Build the offline evidence-closure package for a Python-200' candidate run."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SELECTION = ROOT / "benchmark/selection/python200_hard_suite.json"
DEFAULT_REGISTRY = ROOT / "benchmark/sources/python200_hard_registry.json"
DEFAULT_TAXONOMY = ROOT / "artifacts/research_analysis/python200_hard_task_taxonomy.csv"
DEFAULT_BUNDLE = (
    ROOT
    / "experiments/bundles/incoming/frozen-results/python200-hard-main-20260829.tar.gz"
)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def bool_value(value: Any) -> bool | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return value
    return str(value).lower() == "true"


def int_value(value: Any) -> int | None:
    if value is None or value == "":
        return None
    return int(float(value))


def pct(numerator: int, denominator: int) -> str:
    return "—" if not denominator else f"{numerator / denominator:.1%}"


def markdown_table(headers: list[str], rows: Iterable[Iterable[Any]]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return lines


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = list(rows[0]) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def overage_band(overage: int) -> str:
    if overage <= 1024:
        return "≤1k"
    if overage <= 4096:
        return "1–4k"
    if overage <= 8192:
        return "4–8k"
    return ">8k"


def test_log_details(suite_dir: Path, task_id: str, stage: str) -> tuple[int, str]:
    log_dir = suite_dir / task_id / "eval/logs"
    prefixes = ["public"] if stage == "public_behavior" else ["hidden"]
    text = ""
    for prefix in prefixes:
        for suffix in ("stdout", "stderr"):
            path = log_dir / f"{prefix}.{suffix}"
            if path.is_file():
                text += "\n" + path.read_text(encoding="utf-8", errors="replace")
    failed = set(re.findall(r"(?m)^FAILED\s+([^\s]+)", text))
    error_types = sorted(
        set(
            re.findall(
                r"(?m)^E\s+(?:[\w.]+\.)?([A-Za-z_][A-Za-z0-9_]*(?:Error|Exception))\b",
                text,
            )
        )
    )
    return len(failed), ",".join(error_types)


def dependency_requirement(reason: str) -> str:
    match = re.search(r"requirement\s+([^\s]+)", reason, re.IGNORECASE)
    return match.group(1) if match else ""


def grouped_context(rows: list[dict[str, Any]], field: str) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[str(row[field])].append(row)
    result = []
    for group, values in sorted(groups.items()):
        passes = sum(bool(row["functional_pass"]) for row in values)
        overages = sorted(int(row["context_overage_tokens"]) for row in values)
        result.append(
            {
                "dimension": field,
                "group": group,
                "tasks": len(values),
                "passes": passes,
                "pass_rate": passes / len(values),
                "median_overage_tokens": overages[len(overages) // 2],
                "max_overage_tokens": max(overages),
            }
        )
    return result


def write_attestation(
    output_dir: Path,
    suite_dir: Path,
    suite: dict[str, Any],
    selection_path: Path,
    registry_path: Path,
    taxonomy_path: Path,
    bundle_path: Path,
    rows: list[dict[str, Any]],
    summary: dict[str, Any],
) -> None:
    selection = read_json(selection_path)
    actual_ids = {str(row["task_id"]) for row in rows}
    expected_ids = {str(value) for value in selection["task_ids"]}
    freeze_blocked = [row for row in rows if row["freeze_preflight_blocked"]]
    dependency_failed = [row for row in rows if row["dependency_install_failed"]]
    context_violations = [row for row in rows if row["context_violation"] is True]
    rerun_ids = sorted(
        {
            str(row["task_id"])
            for row in rows
            if row["freeze_preflight_blocked"]
            or row["dependency_install_failed"]
            or row["context_violation"] is True
        }
    )
    task_map = [
        {
            "task_id": row["task_id"],
            "suite_split": row["suite_split"],
            "selected": row["task_id"] in expected_ids,
            "agent_attempted": row["agent_attempted"],
            "functional_pass": row["functional_pass"],
            "freeze_preflight_blocked": row["freeze_preflight_blocked"],
            "dependency_install_failed": row["dependency_install_failed"],
            "context_violation": row["context_violation"],
            "strict_replacement_required": row["task_id"] in rerun_ids,
            "source_snapshot_id": row["source_snapshot_id"],
            "source_snapshot_match": row["source_snapshot_match"],
        }
        for row in sorted(rows, key=lambda value: str(value["task_id"]))
    ]
    write_csv(output_dir / "provenance_task_map.csv", task_map)
    files = {
        "received_bundle": bundle_path,
        "received_bundle_sidecar": bundle_path.with_name(bundle_path.name + ".sha256"),
        "suite_json": suite_dir / "suite.json",
        "selection": selection_path,
        "source_registry": registry_path,
        "taxonomy": taxonomy_path,
    }
    fingerprints = {
        name: {
            "path": path.relative_to(ROOT).as_posix(),
            "sha256": sha256_file(path),
            "size_bytes": path.stat().st_size,
        }
        for name, path in files.items()
        if path.is_file()
    }
    payload = {
        "schema_version": "featureliftbench.result_attestation.v1",
        "status": "candidate_blocked",
        "suite": suite_dir.name,
        "generated_at": suite.get("generated_at"),
        "statement": (
            "This attests the received bytes, selected task identity, emitted source identity, "
            "and runtime digests. It does not attest paper eligibility or retroactively add "
            "missing benchmark-freeze metadata."
        ),
        "identity": {
            "expected_suite_id": selection.get("suite_id"),
            "task_set_sha256": selection.get("task_set_sha256"),
            "baseline_freeze_id": selection.get("baseline_freeze_id"),
            "hard50_selection_id": selection.get("hard50_selection_id"),
            "selected_tasks": len(expected_ids),
            "recorded_tasks": len(actual_ids),
            "matching_tasks": len(expected_ids & actual_ids),
            "missing_tasks": sorted(expected_ids - actual_ids),
            "extra_tasks": sorted(actual_ids - expected_ids),
            "recorded_benchmark_freeze_id": summary["identity"]["recorded_benchmark_freeze_id"],
            "source_snapshot_matches": summary["identity"]["source_snapshot_matches"],
            "source_snapshot_mismatches": summary["identity"]["source_snapshot_mismatches"],
            "source_snapshot_unavailable": summary["identity"]["source_snapshot_unavailable"],
        },
        "runtime": summary["runtime"],
        "execution": {
            "assigned_tasks": len(rows),
            "agent_attempted": sum(bool(row["agent_attempted"]) for row in rows),
            "freeze_preflight_blocked": len(freeze_blocked),
            "dependency_install_failures": len(dependency_failed),
            "context_violation_runs": len(context_violations),
            "strict_replacement_union": len(rerun_ids),
            "strict_replacement_task_ids": rerun_ids,
        },
        "fingerprints": fingerprints,
        "blockers": [
            "suite metadata has no direct benchmark_freeze_id",
            "17 tasks were blocked before agent launch by active freeze spec hash mismatch",
            "16 tasks failed dependency installation because required offline wheels were unavailable",
            "59 attempted runs exceeded the configured prompt allowance",
        ],
    }
    (output_dir / "provenance_attestation.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    lines = [
        "# Python-200′ candidate provenance attestation",
        "",
        "> **Status: candidate blocked · Verified from received files: 2026-08-29**",
        "",
        "This document attests the received bytes and reconstructable identity. It does not "
        "promote the run into the paper leaderboard and does not alter the original suite.",
        "",
        "## What is positively attested",
        "",
        f"- Task identity: {len(expected_ids & actual_ids)}/200 selected IDs match; no missing or extra IDs.",
        f"- Source identity: {summary['identity']['source_snapshot_matches']} emitted snapshot IDs match and "
        f"{summary['identity']['source_snapshot_mismatches']} mismatch; "
        f"{summary['identity']['source_snapshot_unavailable']} are unavailable.",
        f"- Runtime identity: agent `{summary['runtime']['agent_docker_image']}`; evaluator "
        f"`{summary['runtime']['eval_docker_image']}`.",
        f"- Received archive SHA256: `{fingerprints['received_bundle']['sha256']}`.",
        f"- Selection task-set SHA256: `{selection.get('task_set_sha256')}`.",
        "",
        "## What is not attested",
        "",
        "- The original suite has no direct `benchmark_freeze_id` field.",
        f"- {len(freeze_blocked)} tasks never launched because the active spec hash disagreed with the freeze.",
        f"- {len(dependency_failed)} evaluations stopped at offline dependency installation.",
        f"- {len(context_violations)} attempted runs violated the prompt allowance.",
        f"- The strict replacement union is therefore **{len(rerun_ids)} tasks**.",
        "",
        "## Interpretation",
        "",
        "The package is authentic and task-set reconstruction is strong, but the execution is not a "
        "complete eligible Python-200′ Main result. `132/200` is retained only as the received-suite "
        "audit headline. Final paper scoring requires replacement runs for the frozen union in "
        "`strict_replacement_task_ids.txt`.",
        "",
    ]
    (output_dir / "provenance_attestation.md").write_text("\n".join(lines), encoding="utf-8")
    (output_dir / "strict_replacement_task_ids.txt").write_text(
        "\n".join(rerun_ids) + "\n", encoding="utf-8"
    )


def write_context_audit(
    output_dir: Path, rows: list[dict[str, Any]], summary: dict[str, Any]
) -> None:
    violations = []
    for row in rows:
        if row["context_violation"] is not True:
            continue
        overage = int(row["context_overage_tokens"])
        violations.append(
            {
                "task_id": row["task_id"],
                "suite_split": row["suite_split"],
                "lift_type": row["lift_type"],
                "feature_family": row["feature_family"],
                "functional_pass": row["functional_pass"],
                "audit_failure_class": row["audit_failure_class"],
                "max_allowed_prompt_tokens": row["max_allowed_prompt_tokens"],
                "max_prompt_tokens_per_call": row["max_prompt_tokens_per_call"],
                "context_overage_tokens": overage,
                "overage_band": overage_band(overage),
                "total_tokens": row["total_tokens"],
                "effective_uncached_prompt_tokens": row["effective_uncached_prompt_tokens"],
            }
        )
    violations.sort(key=lambda value: (-int(value["context_overage_tokens"]), str(value["task_id"])))
    write_csv(output_dir / "context_audit.csv", violations)
    bands = Counter(str(row["overage_band"]) for row in violations)
    group_rows = []
    for field in ("suite_split", "lift_type", "audit_failure_class", "overage_band"):
        group_rows.extend(grouped_context(violations, field))
    fixed_ids = set(summary["eligibility"]["strict_rerun_task_ids"])
    fixed_rows = [row for row in rows if row["task_id"] not in fixed_ids]
    fixed_passes = sum(bool(row["functional_pass"]) for row in fixed_rows)
    payload = {
        "schema_version": "featureliftbench.context_audit.v1",
        "violation_tasks": len(violations),
        "violation_passes": sum(bool(row["functional_pass"]) for row in violations),
        "max_allowed_prompt_tokens": sorted(
            {int(row["max_allowed_prompt_tokens"]) for row in violations}
        ),
        "overage_tokens": {
            "min": min(int(row["context_overage_tokens"]) for row in violations),
            "median": sorted(int(row["context_overage_tokens"]) for row in violations)[
                len(violations) // 2
            ],
            "max": max(int(row["context_overage_tokens"]) for row in violations),
            "bands": dict(sorted(bands.items())),
        },
        "groups": group_rows,
        "strict_replacement_sensitivity": {
            "fixed_tasks": len(fixed_rows),
            "fixed_passes": fixed_passes,
            "unresolved_union": len(fixed_ids),
            "possible_final_pass_count_range": [fixed_passes, fixed_passes + len(fixed_ids)],
            "possible_final_rate_range": [fixed_passes / len(rows), (fixed_passes + len(fixed_ids)) / len(rows)],
            "note": "Logical bounds only; not an estimate of strict-run performance.",
        },
    }
    (output_dir / "context_audit.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    lines = [
        "# Context-window eligibility audit",
        "",
        "> **Status: complete offline audit · No replacement runs executed**",
        "",
        f"There are **{len(violations)}** context-violation runs; "
        f"**{payload['violation_passes']}** currently pass. The configured maximum is "
        f"{payload['max_allowed_prompt_tokens'][0]:,} prompt tokens per call.",
        "",
        "## Overage severity",
        "",
    ]
    lines.extend(
        markdown_table(
            ["Overage band", "Tasks", "Share of violations"],
            [
                (band, bands.get(band, 0), pct(bands.get(band, 0), len(violations)))
                for band in ("≤1k", "1–4k", "4–8k", ">8k")
            ],
        )
    )
    lines.extend(
        [
            "",
            f"Median overage is **{payload['overage_tokens']['median']:,} tokens**; maximum "
            f"overage is **{payload['overage_tokens']['max']:,}**. Most violations are not "
            "borderline events: 44/59 exceed the allowance by more than 8k tokens.",
            "",
            "## Eligibility sensitivity",
            "",
            f"After removing the union of context violations, freeze-preflight blocks, and "
            f"dependency-install failures, **{len(fixed_rows)} tasks / {fixed_passes} passes** "
            "remain fixed. Before replacement runs, the purely logical final range is "
            f"{fixed_passes}/200 to {fixed_passes + len(fixed_ids)}/200 "
            f"({fixed_passes / len(rows):.1%}–{(fixed_passes + len(fixed_ids)) / len(rows):.1%}). "
            "This is a stress range, not a performance estimate.",
            "",
            "## Frozen replacement policy",
            "",
            "- Replace exactly the union in `strict_replacement_task_ids.txt`; do not select by outcome.",
            "- Use the same model, OpenHands profile, 120-step budget, prompt, task selection, and image pins.",
            "- Enforce the prompt allowance rather than merely auditing it.",
            "- Repair the offline dependency cache before the run and verify it in preflight.",
            "- Preserve the received results and publish both original and replacement provenance.",
            "- Merge by task ID with the frozen rule: replacement for union tasks, original for all others.",
            "",
        ]
    )
    (output_dir / "context_audit.md").write_text("\n".join(lines), encoding="utf-8")


def write_failure_audit(output_dir: Path, suite_dir: Path, rows: list[dict[str, Any]]) -> None:
    failures = []
    for row in rows:
        if row["functional_pass"]:
            continue
        stage = str(row["audit_failure_class"])
        failed_tests = 0
        error_types = ""
        if stage in {"public_behavior", "hidden_only_behavior"}:
            failed_tests, error_types = test_log_details(suite_dir, str(row["task_id"]), stage)
        failures.append(
            {
                "task_id": row["task_id"],
                "suite_split": row["suite_split"],
                "lift_type": row["lift_type"],
                "feature_family": row["feature_family"],
                "audit_failure_class": stage,
                "paper_attribution": (
                    "infrastructure"
                    if stage in {"freeze_preflight_blocked", "dependency_install_infrastructure"}
                    else "model_or_output"
                ),
                "context_violation": row["context_violation"],
                "dependency_requirement": dependency_requirement(str(row["dependency_failure_reason"])),
                "failed_test_count": failed_tests,
                "error_types": error_types,
                "evidence": (
                    row["run_error"]
                    or row["dependency_failure_reason"]
                    or stage.replace("_", " ")
                )[:500],
            }
        )
    failures.sort(key=lambda value: (str(value["audit_failure_class"]), str(value["task_id"])))
    write_csv(output_dir / "failure_audit.csv", failures)
    class_counts = Counter(str(row["audit_failure_class"]) for row in failures)
    split_class: dict[str, Counter[str]] = defaultdict(Counter)
    for row in failures:
        split_class[str(row["suite_split"])][str(row["audit_failure_class"])] += 1
    infra = sum(row["paper_attribution"] == "infrastructure" for row in failures)
    behavior = len(failures) - infra
    payload = {
        "schema_version": "featureliftbench.failure_audit.v1",
        "nominal_nonpasses": len(failures),
        "infrastructure_nonpasses": infra,
        "model_or_output_nonpasses": behavior,
        "class_counts": dict(sorted(class_counts.items())),
        "class_counts_by_split": {
            key: dict(sorted(value.items())) for key, value in sorted(split_class.items())
        },
        "dependency_requirements": dict(
            sorted(
                Counter(
                    str(row["dependency_requirement"])
                    for row in failures
                    if row["dependency_requirement"]
                ).items()
            )
        ),
    }
    (output_dir / "failure_audit.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    display_order = [
        ("freeze_preflight_blocked", "Freeze preflight blocked"),
        ("dependency_install_infrastructure", "Offline dependency unavailable"),
        ("agent_no_submission", "Agent produced no submission"),
        ("submission_build", "Submission build"),
        ("public_behavior", "Public behavior"),
        ("hidden_only_behavior", "Hidden-only behavior"),
        ("isolation", "Isolation"),
    ]
    lines = [
        "# Functional non-pass attribution",
        "",
        "> **Status: complete evidence-level audit · No new experiment executed**",
        "",
        f"The received suite has **{len(failures)} nominal non-passes**, but "
        f"**{infra} ({infra / len(failures):.1%}) are infrastructure outcomes** rather than "
        "model-behavior evidence. The remaining 35 consist of two no-submission outcomes, "
        "25 public-behavior failures, and eight hidden-only failures.",
        "",
        "## Audited attribution",
        "",
    ]
    lines.extend(
        markdown_table(
            ["Audit class", "Tasks", "Paper treatment"],
            [
                (
                    label,
                    class_counts.get(key, 0),
                    "rerun after infrastructure repair"
                    if key in {"freeze_preflight_blocked", "dependency_install_infrastructure"}
                    else "retain as observed model/output evidence",
                )
                for key, label in display_order
                if class_counts.get(key, 0)
            ],
        )
    )
    lines.extend(
        [
            "",
            "## Key corrections",
            "",
            "- The 17 freeze-preflight blocks all occur in Python-150 and never launched an agent.",
            "- The 16 nominal build failures all occur in Hard-50 and are dependency-install failures, "
            "not invalid generated Python packages.",
            "- All dependency failures report an unavailable locked requirement in the offline wheel set.",
            "- No task first fails isolation.",
            "- Public and hidden failures remain valid behavioral evidence, subject to the separate "
            "context-window eligibility flag on affected runs.",
            "",
            "The task-level audit is in `failure_audit.csv`. Test names are intentionally omitted; "
            "the file retains counts and exception types without exposing hidden-test content.",
            "",
        ]
    )
    (output_dir / "failure_audit.md").write_text("\n".join(lines), encoding="utf-8")


def write_paper_materials(output_dir: Path, summary: dict[str, Any], failure: dict[str, Any]) -> None:
    h = summary["headline"]
    split = summary["by_split"]
    eligibility = summary["eligibility"]
    lines = [
        "# Python-200′ candidate paper tables",
        "",
        "> **Status: internal candidate tables · Not eligible for the final leaderboard**",
        "",
        "## Received-suite audit headline",
        "",
    ]
    lines.extend(
        markdown_table(
            ["Scope", "Functional passes", "Assigned", "Raw rate", "Eligibility"],
            [
                ("Python-150", split["python150"]["passed"], 150, f"{split['python150']['rate']:.1%}", "17 preflight blocks; context audit open"),
                ("Hard-50", split["hard50"]["passed"], 50, f"{split['hard50']['rate']:.1%}", "16 dependency failures; context audit open"),
                ("Python-200′", h["passed"], 200, f"{h['rate']:.1%}", "candidate blocked"),
            ],
        )
    )
    lines.extend(
        [
            "",
            "Do not caption this as a leaderboard table. It reports the received package exactly, "
            "including infrastructure outcomes.",
            "",
            "## Eligibility partition",
            "",
        ]
    )
    lines.extend(
        markdown_table(
            ["Partition", "Tasks", "Passes", "Treatment"],
            [
                ("Fixed clean subset", eligibility["fixed_eligible_tasks"], eligibility["fixed_eligible_passes"], "retain"),
                ("Strict replacement union", eligibility["strict_rerun_union"], "unknown", "replace by frozen task ID"),
                ("Total", 200, "unknown", "final score after replacement"),
            ],
        )
    )
    lines.extend(
        [
            "",
            "The replacement union contains 59 context violations, 17 freeze-preflight blocks, "
            "and 16 dependency failures with overlap removed. The fixed subset is 95/116; this "
            "is not a standalone benchmark score.",
            "",
            "## Failure attribution for discussion",
            "",
        ]
    )
    label_map = {
        "freeze_preflight_blocked": "Freeze preflight blocked",
        "dependency_install_infrastructure": "Offline dependency unavailable",
        "agent_no_submission": "No submission",
        "public_behavior": "Public behavior",
        "hidden_only_behavior": "Hidden-only behavior",
    }
    lines.extend(
        markdown_table(
            ["Outcome", "Tasks", "Claim class"],
            [
                (
                    label_map.get(key, key),
                    value,
                    "infrastructure" if key in {"freeze_preflight_blocked", "dependency_install_infrastructure"} else "model/output",
                )
                for key, value in failure["class_counts"].items()
                if key != "pass"
            ],
        )
    )
    lines.append("")
    (output_dir / "paper_candidate_tables.md").write_text("\n".join(lines), encoding="utf-8")

    draft = f"""# Results draft: Python-200′ DeepSeek V4 Flash candidate

> **Draft status: audit-ready candidate; replace bracketed eligibility language after strict replacement runs.**

## Main result is not yet leaderboard-eligible

The received OpenHands suite records {h['passed']} functional passes across 200 selected tasks
({h['rate']:.1%}; Wilson 95% {h['wilson_95'][0]:.1%}–{h['wilson_95'][1]:.1%}). We do not report
this value as the Python-200′ leaderboard result. Although all task IDs match the registered
selection, 17 Python-150 tasks were rejected before agent launch by a freeze-spec hash check,
16 Hard-50 tasks failed offline dependency installation, and 59 attempted runs exceeded the
configured prompt allowance. Their union contains {eligibility['strict_rerun_union']} tasks.

## Infrastructure accounts for nearly half of nominal non-passes

The received package contains {failure['nominal_nonpasses']} nominal non-passes. Of these,
{failure['infrastructure_nonpasses']} ({failure['infrastructure_nonpasses']/failure['nominal_nonpasses']:.1%})
are infrastructure outcomes: 17 freeze-preflight blocks and 16 unavailable-dependency failures.
The remaining model/output evidence comprises two runs with no submission, 25 first failing public
tests, and eight passing public tests but failing hidden tests. No task first fails isolation.
This separation prevents execution-environment failures from being interpreted as model capability.

## Raw split rates are confounded

The raw package yields {split['python150']['passed']}/150 ({split['python150']['rate']:.1%}) on
Python-150 and {split['hard50']['passed']}/50 ({split['hard50']['rate']:.1%}) on Hard-50. These rates
must not be used as a clean difficulty comparison: the 17 freeze blocks occur only in Python-150,
whereas all 16 dependency-install failures occur in Hard-50. The independent Hard-50 calibration
remains benchmark-design evidence; the new full-suite comparison awaits the frozen replacement set.

## Taxonomy and compactness analyses are prepared but provisional

The received outcomes show Direct 60/68, Adapted 63/100, and Composite 9/32. Pass-conditioned
median RRES differs sharply by split (Python-150 0.990; Hard-50 0.286). We retain these cuts as
analysis specifications rather than final findings because replacement outcomes may change the
composition. Final reporting will preserve split-specific RRES and use paired subsets for method or
cross-model comparisons.

## Eligibility sensitivity and next step

After freezing the {eligibility['strict_rerun_union']}-task replacement union, the untouched subset
contains {eligibility['fixed_eligible_passes']} passes among {eligibility['fixed_eligible_tasks']}
tasks. The logical final range before replacement is
{eligibility['final_pass_count_range_before_rerun'][0]}/200–{eligibility['final_pass_count_range_before_rerun'][1]}/200;
this is a stress bound, not an estimate. The final table will merge replacement outcomes for the
frozen union with original outcomes for all other task IDs and will retain both provenance layers.
"""
    (output_dir / "results_draft.md").write_text(draft, encoding="utf-8")


def write_checklist(output_dir: Path) -> None:
    text = """# Python-200′ offline evidence-closure checklist

> **Status: offline work complete · No new model experiment executed**

## Completed in this pass

- [x] Verify and fingerprint the received archive, suite, selection, source registry, and taxonomy.
- [x] Produce a non-retroactive provenance attestation and per-task identity map.
- [x] Identify 17 freeze-preflight blocks that never launched an agent.
- [x] Audit all 59 context-window violations, their overage severity, and current outcomes.
- [x] Identify all 16 build-stage outcomes as unavailable offline dependencies.
- [x] Separate infrastructure outcomes from model/output failures across all 68 nominal non-passes.
- [x] Freeze an outcome-independent strict replacement union of 84 task IDs.
- [x] Produce candidate paper tables and a Results draft with eligibility-safe language.
- [x] Produce a checksum manifest for the offline evidence package.

## Still requires experiment execution

- [ ] Repair and preflight the offline wheel set for all 16 dependency failures.
- [ ] Resolve the 17 task-spec/freeze mismatches against the intended immutable task packages.
- [ ] Execute the frozen 84-task strict replacement set with hard context enforcement.
- [ ] Merge replacement outcomes by the preregistered task-ID rule and regenerate the final table.
- [ ] Run the planned stratified stability repeats, or keep the limitation explicit.
- [ ] Run at least one additional model on the eligible Python-200′ suite, or narrow cross-model claims.

## Promotion rule

Do not promote `132/200` into the abstract or final leaderboard. Promotion requires a direct freeze
binding, zero unresolved dependency/preflight failures, hard context compliance, and a reproducible
paper bundle built from the merged eligible result.
"""
    (output_dir / "offline_closure_checklist.md").write_text(text, encoding="utf-8")


def write_manifest(output_dir: Path) -> None:
    included = []
    for path in sorted(output_dir.iterdir()):
        if not path.is_file() or path.name in {"paper_bundle_manifest.json", "artifact.json"}:
            continue
        included.append(
            {
                "path": path.relative_to(ROOT).as_posix(),
                "sha256": sha256_file(path),
                "size_bytes": path.stat().st_size,
            }
        )
    payload = {
        "schema_version": "featureliftbench.paper_evidence_manifest.v1",
        "status": "candidate_blocked",
        "generated_on": "2026-08-29",
        "files": included,
        "promotion_rule": (
            "Regenerate after the frozen strict replacement set; do not use the candidate "
            "headline as the final leaderboard result."
        ),
    }
    (output_dir / "paper_bundle_manifest.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("suite_dir", type=Path)
    parser.add_argument("--analysis-dir", type=Path, required=True)
    parser.add_argument("--selection", type=Path, default=DEFAULT_SELECTION)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--taxonomy", type=Path, default=DEFAULT_TAXONOMY)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    args = parser.parse_args()

    suite_dir = args.suite_dir.resolve()
    output_dir = args.analysis_dir.resolve()
    summary = read_json(output_dir / "summary.json")
    suite = read_json(suite_dir / "suite.json")
    with (output_dir / "task_results.csv").open(newline="", encoding="utf-8") as handle:
        raw_rows = list(csv.DictReader(handle))
    rows = []
    for row in raw_rows:
        converted = dict(row)
        for field in (
            "functional_pass",
            "agent_attempted",
            "freeze_preflight_blocked",
            "dependency_install_failed",
            "context_violation",
            "source_snapshot_match",
        ):
            converted[field] = bool_value(row.get(field))
        for field in (
            "max_prompt_tokens_per_call",
            "max_allowed_prompt_tokens",
            "context_overage_tokens",
            "total_tokens",
            "effective_uncached_prompt_tokens",
        ):
            converted[field] = int_value(row.get(field))
        rows.append(converted)

    write_attestation(
        output_dir,
        suite_dir,
        suite,
        args.selection.resolve(),
        args.registry.resolve(),
        args.taxonomy.resolve(),
        args.bundle.resolve(),
        rows,
        summary,
    )
    write_context_audit(output_dir, rows, summary)
    write_failure_audit(output_dir, suite_dir, rows)
    failure = read_json(output_dir / "failure_audit.json")
    write_paper_materials(output_dir, summary, failure)
    write_checklist(output_dir)
    write_manifest(output_dir)
    print(
        json.dumps(
            {
                "output_dir": output_dir.relative_to(ROOT).as_posix(),
                "strict_replacement_tasks": summary["eligibility"]["strict_rerun_union"],
                "fixed_tasks": summary["eligibility"]["fixed_eligible_tasks"],
                "fixed_passes": summary["eligibility"]["fixed_eligible_passes"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
