#!/usr/bin/env python3
"""Build or verify the evidence ledger for the Python-200-prime v2 repair.

The ledger is intentionally conservative: mechanical remediation can be
verified from existing gate and Oracle artifacts, but semantic scope
preservation remains pending until a separate review record is attached.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = "featureliftbench.python200_prime_repair_ledger.v1"
PROTOCOL_ID = "featureliftbench.benchmark_repair.v1"

DEFAULT_OLD_GATE = (
    ROOT / "reports/benchmark_gate/python200_hard_20260902_p1_l4l5"
)
DEFAULT_NEW_GATE = (
    ROOT / "reports/benchmark_gate/python200_hard_20260903_v2_repair2"
)
DEFAULT_C1 = (
    ROOT / "experiments/validation/c1c2_repair_v2/c1_members_wrote.json"
)
DEFAULT_C2 = (
    ROOT / "experiments/validation/c1c2_repair_v2/c2_mapping_wrote.json"
)
DEFAULT_C4_NOTE = ROOT / "experiments/registry/c4_overlap_trial_20260902.md"
DEFAULT_PROTOCOL = ROOT / "docs/BENCHMARK_REPAIR_PROTOCOL.md"
DEFAULT_PRE_REPAIR_REF = "50fcf71fc71f3231761376c17eaeffba4dc2ba22"
DEFAULT_OUTPUT = (
    ROOT
    / "artifacts/research_analysis/python200_prime/current_repair_ledger_v2.json"
)
DEFAULT_MARKDOWN_OUTPUT = (
    ROOT
    / "artifacts/research_analysis/python200_prime/current_repair_ledger_v2.md"
)
DEFAULT_SEMANTIC_REVIEW = (
    ROOT
    / "artifacts/research_analysis/python200_prime"
    / "current_repair_semantic_review_v2_closed.json"
)
DEFAULT_MAINTAINER_ADJUDICATION = (
    ROOT
    / "artifacts/research_analysis/python200_prime"
    / "current_repair_maintainer_adjudication_v2.json"
)

C4_REPAIRS = {
    "anyio__task_group_core__001": {
        "behavior_ids": ["B003"],
        "change": "Use a distinct deadline pair (0.01/0.2) for the Hidden timeout case.",
    },
    "copier__template_answers_core__001": {
        "behavior_ids": ["B003"],
        "change": "Exercise a different question with two invalid answers.",
    },
    "mitmproxy__url_parse_core__001": {
        "behavior_ids": ["B003"],
        "change": "Exercise the declared bytes URL input rather than duplicate the public string case.",
    },
    "pika__channel_spec_core__001": {
        "behavior_ids": ["B001"],
        "change": "Add remarshal equality to the distinct Hidden heartbeat round trip.",
    },
    "pre_commit__config_load_core__001": {
        "behavior_ids": ["B002"],
        "change": "Use a differently named file and assert the declared empty repos default.",
    },
    "pylint__config_find_core__001": {
        "behavior_ids": ["B003"],
        "change": "Check message enablement before and after the configuration change.",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--old-gate", type=Path, default=DEFAULT_OLD_GATE)
    parser.add_argument("--new-gate", type=Path, default=DEFAULT_NEW_GATE)
    parser.add_argument("--c1", type=Path, default=DEFAULT_C1)
    parser.add_argument("--c2", type=Path, default=DEFAULT_C2)
    parser.add_argument("--c4-note", type=Path, default=DEFAULT_C4_NOTE)
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    parser.add_argument("--pre-repair-ref", default=DEFAULT_PRE_REPAIR_REF)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN_OUTPUT)
    parser.add_argument(
        "--semantic-review",
        type=Path,
        default=DEFAULT_SEMANTIC_REVIEW,
        help="Closed 38-task semantic review used to mark scope preservation",
    )
    parser.add_argument(
        "--maintainer-adjudication",
        type=Path,
        default=DEFAULT_MAINTAINER_ADJUDICATION,
    )
    parser.add_argument(
        "--freeze-id",
        default="",
        help="Final freeze_id; when set with --candidate-id, marks the ledger frozen.",
    )
    parser.add_argument(
        "--candidate-id",
        default="",
        help="Candidate id bound by the final freeze.",
    )
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_digest(payload: Any) -> str:
    data = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def evidence_record(path: Path) -> dict[str, Any]:
    return {
        "path": relative(path),
        "sha256": sha256_file(path),
        "size_bytes": path.stat().st_size,
    }


def pre_repair_metadata(task_id: str, ref: str) -> tuple[str, dict[str, Any]]:
    split = "hard50" if (ROOT / "benchmark/hard50" / task_id).is_dir() else "tasks"
    path = f"benchmark/{split}/{task_id}/metadata.json"
    completed = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        raise ValueError(f"{task_id}: pre-repair metadata unavailable at {ref}: {path}")
    value = json.loads(completed.stdout)
    if not isinstance(value, dict):
        raise ValueError(f"{task_id}: pre-repair metadata is not an object")
    return path, value


def load_gate_task(gate_dir: Path, task_id: str) -> dict[str, Any]:
    return load_json(gate_dir / "tasks" / f"{task_id}.json")


def report_task_ids(report: dict[str, Any]) -> set[str]:
    rows = report.get("tasks") or []
    result: set[str] = set()
    for row in rows:
        task_id = row.get("task_id") if isinstance(row, dict) else row
        if not isinstance(task_id, str) or not task_id:
            raise ValueError("gate report contains an invalid task record")
        result.add(task_id)
    return result


def check_status(record: dict[str, Any], check_id: str) -> str:
    return str(((record.get("checks") or {}).get(check_id) or {}).get("status") or "")


def relevant_evidence(record: dict[str, Any], check_ids: list[str]) -> list[dict[str, Any]]:
    rows = []
    for check_id in check_ids:
        check = (record.get("checks") or {}).get(check_id) or {}
        rows.append(
            {
                "check_id": check_id,
                "status": check.get("status"),
                "blocking": check.get("blocking"),
                "mechanical_result": check.get("mechanical_result"),
                "adjudication": check.get("adjudication"),
                "reason": check.get("reason"),
                "evidence": check.get("evidence") or [],
                "details": check.get("details") or {},
            }
        )
    return rows


def oracle_preservation(record: dict[str, Any]) -> dict[str, Any]:
    oracle = ((record.get("checks") or {}).get("L3_ORACLE_N3") or {})
    isolation = ((record.get("checks") or {}).get("L4_ISOLATION_N3") or {})
    oracle_evidence = oracle.get("evidence") or []
    evidence = oracle_evidence[0] if oracle_evidence else {}
    return {
        "oracle_status": oracle.get("status"),
        "isolation_status": isolation.get("status"),
        "repetitions": evidence.get("repetitions") or [],
        "passed": evidence.get("passed") or [],
        "fingerprints": evidence.get("fingerprints") or [],
        "source_digests": evidence.get("source_digests") or [],
    }


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    old_report_path = args.old_gate / "gate_report.json"
    new_report_path = args.new_gate / "gate_report.json"
    old_report = load_json(old_report_path)
    new_report = load_json(new_report_path)
    c1_rows = {row["task_id"]: row for row in load_json(args.c1)}
    c2_rows = {row["task_id"]: row for row in load_json(args.c2)}

    old_task_ids = report_task_ids(old_report)
    new_task_ids = report_task_ids(new_report)
    if old_task_ids != new_task_ids or len(old_task_ids) != 200:
        raise ValueError("old and new gates must cover the same 200 task IDs")

    records: dict[str, Any] = {}
    category_counts = {"C1": 0, "C2": 0, "C4": 0}
    for task_id in sorted(old_task_ids):
        before = load_gate_task(args.old_gate, task_id)
        after = load_gate_task(args.new_gate, task_id)
        categories: list[str] = []
        if check_status(before, "L2_C1_SURFACE") == "fail":
            categories.append("C1")
        if check_status(before, "L2_C2_ENTRYPOINT") == "fail":
            categories.append("C2")
        if check_status(before, "L5_C4_TEST_OVERLAP") == "undetermined":
            categories.append("C4")
        if not categories:
            continue
        for category in categories:
            category_counts[category] += 1

        relevant_checks = {
            "C1": "L2_C1_SURFACE",
            "C2": "L2_C2_ENTRYPOINT",
            "C4": "L5_C4_TEST_OVERLAP",
        }
        check_ids = [relevant_checks[value] for value in categories]
        post_checks_pass = all(check_status(after, value) == "pass" for value in check_ids)
        oracle = oracle_preservation(after)
        oracle_pass = (
            oracle["oracle_status"] == "pass"
            and oracle["isolation_status"] == "pass"
            and oracle["repetitions"] == [1, 2, 3]
            and oracle["passed"] == [True, True, True]
            and len(oracle["fingerprints"]) == 1
        )

        changes: dict[str, Any] = {}
        if "C1" in categories:
            row = c1_rows.get(task_id)
            if not row or row.get("status") != "ok" or row.get("c1_status") != "pass":
                raise ValueError(f"{task_id}: missing successful C1 repair record")
            changes["C1"] = {
                "added_required_api_members": row.get("added") or [],
                "skipped": row.get("skipped") or [],
                "repair_record_spec_hash": row.get("spec_hash"),
            }
        if "C2" in categories:
            row = c2_rows.get(task_id)
            if not row or row.get("status") != "ok" or row.get("c2_status") != "pass":
                raise ValueError(f"{task_id}: missing successful C2 repair record")
            changes["C2"] = {
                "before": row.get("before") or [],
                "after": row.get("proposed") or [],
                "resolution": row.get("resolved") or [],
                "repair_record_spec_hash": row.get("spec_hash"),
            }
        if "C4" in categories:
            if task_id not in C4_REPAIRS:
                raise ValueError(f"{task_id}: missing curated C4 repair rationale")
            changes["C4"] = C4_REPAIRS[task_id]

        before_identity = before.get("input_identity") or {}
        after_identity = after.get("input_identity") or {}
        old_metadata_path, old_metadata = pre_repair_metadata(task_id, args.pre_repair_ref)
        if old_metadata.get("spec_hash") != before_identity.get("spec_hash"):
            raise ValueError(
                f"{task_id}: pre-repair ref spec hash does not match the old gate"
            )
        agent_visible_changed = (
            before_identity.get("generated_task_hash")
            != after_identity.get("generated_task_hash")
        )
        records[task_id] = {
            "repair_categories": categories,
            "trigger_class": (
                "confirmed_blocking_violation"
                if any(value in categories for value in ("C1", "C2"))
                else "advisory_overlap_finding"
            ),
            "pre_repair": {
                "label": before.get("label"),
                "input_identity": before_identity,
                "git_ref": args.pre_repair_ref,
                "metadata_path": old_metadata_path,
                "public_spec": old_metadata.get("public_spec") or {},
                "findings": relevant_evidence(before, check_ids),
            },
            "repair": changes,
            "change_surface": {
                "agent_visible_task_changed": agent_visible_changed,
                "public_spec_changed": (
                    before_identity.get("spec_hash") != after_identity.get("spec_hash")
                ),
                "task_package_changed": (
                    before_identity.get("task_input_sha256")
                    != after_identity.get("task_input_sha256")
                ),
                "evaluator_changed": "C1" in categories or "C4" in categories,
                "private_provenance_changed": "C2" in categories,
                "model_score_used_as_acceptance_criterion": False,
                "semantic_scope_change_claim": "none",
                "semantic_scope_claim_basis": "repair_protocol_and_rule_adjudication",
            },
            "post_repair": {
                "label": after.get("label"),
                "input_identity": after_identity,
                "checks": relevant_evidence(after, check_ids),
                "oracle_and_isolation": oracle,
            },
            "acceptance": {
                "mechanical_status": "pass" if post_checks_pass else "fail",
                "oracle_isolation_status": "pass" if oracle_pass else "fail",
                "semantic_review_status": "pending",
                "freeze_status": "pending_new_candidate",
                "publication_ready": False,
            },
        }

    semantic = load_json(args.semantic_review)
    if semantic.get("semantic_scope_gate_pass") is not True:
        raise ValueError("closed semantic review is not scope-gate-pass")
    review_rows = {
        row["task_id"]: row
        for row in (semantic.get("tasks") or [])
        if isinstance(row, dict) and row.get("task_id")
    }
    if set(review_rows) != set(records):
        raise ValueError("semantic review task set differs from the repair ledger")
    if any(row.get("repair_scope") != "scope_preserved" for row in review_rows.values()):
        raise ValueError("semantic review is not 38/38 scope_preserved")
    for task_id, row in records.items():
        row["acceptance"]["semantic_review_status"] = "pass"
        row["acceptance"]["repair_scope"] = "scope_preserved"
        row["acceptance"]["semantic_review_source"] = review_rows[task_id].get(
            "selected_attempt"
        )
        if args.freeze_id and args.candidate_id:
            row["acceptance"]["freeze_status"] = "frozen"
            row["acceptance"]["freeze_id"] = args.freeze_id
            row["acceptance"]["candidate_id"] = args.candidate_id
            row["acceptance"]["publication_ready"] = (
                row["acceptance"]["mechanical_status"] == "pass"
                and row["acceptance"]["oracle_isolation_status"] == "pass"
                and row["acceptance"]["semantic_review_status"] == "pass"
            )

    if len(records) != 38 or category_counts != {"C1": 21, "C2": 12, "C4": 6}:
        raise ValueError(
            f"unexpected repair inventory: tasks={len(records)} categories={category_counts}"
        )
    if set(c1_rows) != {task_id for task_id, row in records.items() if "C1" in row["repair_categories"]}:
        raise ValueError("C1 repair inventory differs from the pre-repair gate")
    if set(c2_rows) != {task_id for task_id, row in records.items() if "C2" in row["repair_categories"]}:
        raise ValueError("C2 repair inventory differs from the pre-repair gate")
    if set(C4_REPAIRS) != {task_id for task_id, row in records.items() if "C4" in row["repair_categories"]}:
        raise ValueError("C4 repair inventory differs from the pre-repair gate")

    mechanically_closed = sum(
        row["acceptance"]["mechanical_status"] == "pass"
        and row["acceptance"]["oracle_isolation_status"] == "pass"
        for row in records.values()
    )
    frozen = bool(args.freeze_id and args.candidate_id)
    if bool(args.freeze_id) != bool(args.candidate_id):
        raise ValueError("--freeze-id and --candidate-id must be passed together")
    publication_ready = sum(
        bool(row["acceptance"].get("publication_ready")) for row in records.values()
    )
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "protocol_id": PROTOCOL_ID,
        "status": "frozen" if frozen else "semantically_validated_pending_freeze",
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "summary": {
            "parent_task_count": 200,
            "pre_repair_meets_standard": old_report.get("label_counts", {}).get("meets_standard"),
            "post_repair_meets_standard": new_report.get("label_counts", {}).get("meets_standard"),
            "changed_task_count": len(records),
            "blocking_task_count": sum(
                row["trigger_class"] == "confirmed_blocking_violation"
                for row in records.values()
            ),
            "advisory_only_task_count": sum(
                row["trigger_class"] == "advisory_overlap_finding"
                for row in records.values()
            ),
            "category_task_counts": category_counts,
            "mechanically_closed_task_count": mechanically_closed,
            "semantic_review_complete_task_count": len(records),
            "semantic_review_pending_task_count": 0,
            "publication_ready_task_count": publication_ready,
        },
        "claims": {
            "supported": [
                "All 38 changed tasks are tied to pre-repair rule findings.",
                "All relevant implemented gate rows pass after repair.",
                "All 38 changed tasks have stable three-repetition Oracle and isolation evidence in the repair gate ledger.",
                "All 38 repairs preserve semantic scope under AI-assisted review plus maintainer adjudication; this is not independent human gold.",
            ]
            + (
                [
                    "The repaired 200-task suite has a final candidate-bound Docker Oracle and freeze."
                ]
                if frozen
                else []
            ),
            "not_yet_supported": (
                [
                    "All 200 Hidden evaluators are semantically fair.",
                    "Predecessor Agent scores are valid for the repaired freeze.",
                ]
                if frozen
                else [
                    "All 200 Hidden evaluators are semantically fair.",
                    "The repaired 200-task suite has a final candidate-bound Docker Oracle and freeze.",
                    "Predecessor Agent scores are valid for the repaired freeze.",
                ]
            ),
        },
        "evidence_files": {
            "protocol": evidence_record(args.protocol),
            "pre_repair_gate": evidence_record(old_report_path),
            "post_repair_gate": evidence_record(new_report_path),
            "c1_repairs": evidence_record(args.c1),
            "c2_repairs": evidence_record(args.c2),
            "c4_trial": evidence_record(args.c4_note),
            "semantic_review": evidence_record(args.semantic_review),
            "maintainer_adjudication": evidence_record(args.maintainer_adjudication),
        },
        "pre_repair_git_ref": args.pre_repair_ref,
        "tasks": records,
    }
    if frozen:
        payload["freeze"] = {
            "freeze_id": args.freeze_id,
            "candidate_id": args.candidate_id,
        }
    digest_payload = dict(payload)
    digest_payload.pop("generated_at", None)
    payload["ledger_id"] = canonical_digest(digest_payload)
    return payload


def normalized(payload: dict[str, Any]) -> dict[str, Any]:
    result = dict(payload)
    result.pop("generated_at", None)
    result.pop("ledger_id", None)
    return result


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Python-200-prime repair ledger v2",
        "",
        f"> **Status: `{payload['status']}` · Ledger: `{payload['ledger_id']}`**",
        "",
        "This is a generated view. The JSON ledger is authoritative.",
        "",
        "## Summary",
        "",
        "| Measure | Value |",
        "| --- | ---: |",
        f"| Parent suite | {summary['parent_task_count']} |",
        f"| Pre-repair meets standard | {summary['pre_repair_meets_standard']} |",
        f"| Post-repair mechanically meets standard | {summary['post_repair_meets_standard']} |",
        f"| Changed tasks | {summary['changed_task_count']} |",
        f"| Blocking tasks | {summary['blocking_task_count']} |",
        f"| Advisory-only tasks | {summary['advisory_only_task_count']} |",
        f"| C1 / C2 / C4 task counts | {summary['category_task_counts']['C1']} / {summary['category_task_counts']['C2']} / {summary['category_task_counts']['C4']} |",
        f"| Mechanically closed changed tasks | {summary['mechanically_closed_task_count']} |",
        f"| Semantic reviews complete / pending | {summary['semantic_review_complete_task_count']} / {summary['semantic_review_pending_task_count']} |",
        "",
        "## Claim boundary",
        "",
        "Supported:",
        "",
    ]
    lines.extend(f"- {claim}" for claim in payload["claims"]["supported"])
    lines.extend(["", "Not yet supported:", ""])
    lines.extend(f"- {claim}" for claim in payload["claims"]["not_yet_supported"])
    lines.extend(
        [
            "",
            "## Changed tasks",
            "",
            "| Task | Repair | Agent TASK changed | Evaluator changed | Mechanical | Oracle/isolation | Semantic review |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for task_id, row in sorted(payload["tasks"].items()):
        surface = row["change_surface"]
        acceptance = row["acceptance"]
        lines.append(
            "| `{}` | {} | {} | {} | {} | {} | {} |".format(
                task_id,
                "+".join(row["repair_categories"]),
                "yes" if surface["agent_visible_task_changed"] else "no",
                "yes" if surface["evaluator_changed"] else "no",
                acceptance["mechanical_status"],
                acceptance["oracle_isolation_status"],
                acceptance["semantic_review_status"],
            )
        )
    lines.extend(
        [
            "",
            "## Evidence inputs",
            "",
            "| Evidence | Path | SHA-256 |",
            "| --- | --- | --- |",
        ]
    )
    for name, record in sorted(payload["evidence_files"].items()):
        lines.append(f"| `{name}` | `{record['path']}` | `{record['sha256']}` |")
    next_gate = (
        "Freeze v2 is published. Paper Main/ablation scores must be collected "
        "on this freeze; predecessor Agent scores must not be transferred."
        if payload.get("status") == "frozen"
        else (
            "Semantic scope is closed for all 38 repaired tasks "
            "(`scope_preserved`, AI-assisted plus maintainer adjudication, not human gold). "
            "Next gate is the candidate-bound Docker Oracle and freeze v2 cut."
        )
    )
    lines.extend(
        [
            "",
            "## Next gate",
            "",
            next_gate,
            "",
        ]
    )
    return "\n".join(lines)


def verify_existing(existing: dict[str, Any], expected: dict[str, Any]) -> None:
    if existing.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unexpected repair ledger schema")
    if existing.get("ledger_id") != canonical_digest(normalized(existing)):
        raise ValueError("stored repair ledger ID is invalid")
    if normalized(existing) != normalized(expected):
        raise ValueError("stored repair ledger is stale relative to its evidence")


def main() -> int:
    args = parse_args()
    expected = build_payload(args)
    output = args.output.resolve()
    if args.check:
        existing = load_json(output)
        verify_existing(existing, expected)
        markdown = args.markdown_output.resolve()
        if markdown.read_text(encoding="utf-8") != render_markdown(existing):
            raise ValueError("stored repair ledger Markdown is stale")
        print(f"Verified Python-200-prime repair ledger: {expected['ledger_id']}")
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(expected, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    stored = load_json(output)
    verify_existing(stored, expected)
    markdown = args.markdown_output.resolve()
    markdown.parent.mkdir(parents=True, exist_ok=True)
    markdown.write_text(render_markdown(stored), encoding="utf-8")
    print(f"Wrote Python-200-prime repair ledger: {expected['ledger_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
