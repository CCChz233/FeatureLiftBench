"""Assemble traceable, anonymous construction evidence for the paper's Python-150.

This is a retrospective packaging/audit command. It does not reconstruct a
historical selection funnel, rerun reference solutions, or assert human review.
"""

from __future__ import annotations

import ast
from collections import Counter
import csv
from datetime import date
import hashlib
import io
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
MEMBERSHIP = ROOT / "docs/paper-workbench/writing/python150_membership.json"
FREEZE = ROOT / "artifacts/research_analysis/python200_prime/current_benchmark_freeze.json"
ORACLE_EVIDENCE = ROOT / "docs/paper-workbench/writing/chapter2_python150_evidence.json"
AUTHOR_STATEMENT = ROOT / "docs/paper-workbench/writing/author_review_statement.json"
SELECTION_SCRIPT = ROOT / "scripts/archive/build_external150_selection_ledger.py"
REPLACEMENT_LEDGER = ROOT / "benchmark/selection/external150_replacement_20260727.json"
OUTPUT = HERE / "anonymous_construction_evidence.zip"
SUMMARY = HERE / "construction_evidence_summary.json"
REVIEW_DATE = date(2026, 9, 27).isoformat()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def jsonl_bytes(rows: list[dict]) -> bytes:
    return ("\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n").encode()


def review_template_bytes(task_ids: list[str]) -> bytes:
    out = io.StringIO(newline="")
    columns = (
        "task_id", "reviewer_id", "review_date", "source_snapshot_checked",
        "public_contract_checked", "public_test_assertions_checked",
        "hidden_test_assertions_checked", "adaptations_and_exclusions_checked",
        "mapping_corrections", "decision", "evidence_notes",
    )
    writer = csv.DictWriter(out, fieldnames=columns)
    writer.writeheader()
    for task_id in task_ids:
        writer.writerow({"task_id": task_id, "decision": "pending_human_review"})
    return out.getvalue().encode()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def declared_replacement_candidates() -> list[dict]:
    tree = ast.parse(SELECTION_SCRIPT.read_text(encoding="utf-8"))
    assignment = next(
        node for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "CANDIDATES" for target in node.targets)
    )
    columns = ("package", "repository_url", "license", "script_disposition", "domain", "primary_entanglement")
    return [dict(zip(columns, values, strict=True)) for values in ast.literal_eval(assignment.value)]


def mapping_check(metadata: dict, contract: dict) -> list[str]:
    errors = []
    evaluation = metadata["evaluation_spec"]
    if contract.get("spec_sha256") != metadata.get("generated_task_hash"):
        errors.append("behavior_contract spec hash differs from generated TASK hash")
    clause_fields = ("behavior_id", "clause_kind", "text")
    recorded_clauses = [
        {key: row.get(key) for key in clause_fields}
        for row in evaluation.get("public_clauses", [])
    ]
    companion_clauses = [
        {key: row.get(key) for key in clause_fields}
        for row in contract.get("public_clauses", [])
    ]
    if recorded_clauses != companion_clauses:
        errors.append("behavior_contract public clauses differ from metadata")
    for key in ("public_test_mappings", "hidden_test_mappings"):
        recorded = {
            row["nodeid"]: sorted(row.get("behavior_ids", []))
            for row in evaluation.get(key, [])
        }
        companion = {
            row["nodeid"]: sorted(row.get("public_clause_ids", []))
            for row in contract.get(key, [])
        }
        if recorded != companion:
            errors.append(f"behavior_contract {key} differ from metadata")
    return errors


def add_file(payload: dict[str, bytes], path: str, source: Path) -> None:
    payload[path] = source.read_bytes()


def build() -> None:
    import sys
    sys.path.insert(0, str(ROOT / "harness"))
    from featureliftbench.constitution_validate import validate_constitution

    membership = read_json(MEMBERSHIP)
    freeze = read_json(FREEZE)
    oracle = read_json(ORACLE_EVIDENCE)
    task_ids = sorted(membership["task_ids"])
    assert len(task_ids) == 150 == len(set(task_ids))
    assert membership["source_manifest_sha256"] == sha256(FREEZE.read_bytes())
    assert all(freeze["tasks"][task_id]["stratum"] == "python150" for task_id in task_ids)

    payload: dict[str, bytes] = {}
    selection_rows: list[dict] = []
    review_rows: list[dict] = []
    mapping_rows: list[dict] = []
    review_status = Counter()
    audit_status = Counter()
    selection_status = Counter()

    for task_id in task_ids:
        task_dir = ROOT / "benchmark/tasks" / task_id
        metadata_path = task_dir / "metadata.json"
        contract_path = task_dir / "evaluation/behavior_contract.json"
        metadata = read_json(metadata_path)
        contract = read_json(contract_path)
        frozen = freeze["tasks"][task_id]
        assert metadata["task_id"] == contract["task_id"] == task_id
        assert metadata["spec_hash"] == frozen["spec_hash"]
        assert metadata["generated_task_hash"] == frozen["generated_task_hash"]

        selection_id = metadata.get("selection_id")
        selection_evidence = (
            "metadata tag and archived 21-candidate script declaration; original selection ledger absent"
            if selection_id else "final freeze membership only; original candidate/disposition ledger absent"
        )
        selection_status["replacement_tagged" if selection_id else "freeze_only"] += 1
        selection_rows.append({
            "task_id": task_id,
            "stratum": frozen["stratum"],
            "selection_id": selection_id,
            "selection_evidence": selection_evidence,
            "source_repo_id": frozen["source_repo_id"],
            "source_snapshot_id": frozen["source_snapshot_id"],
            "source_resolved_commit": frozen["source_resolved_commit"],
            "source_archive_sha256": frozen["source_archive_sha256"],
            "source_tree_sha256": frozen["source_tree_sha256"],
            "spec_hash": frozen["spec_hash"],
            "generated_task_hash": frozen["generated_task_hash"],
            "task_tree_sha256": frozen["task_tree"]["sha256"],
        })

        checks = validate_constitution(task_dir, metadata)
        checks.extend(mapping_check(metadata, contract))
        audit_status["pass" if not checks else "fix_required"] += 1
        review_status[contract.get("review_status", "unrecorded")] += 1
        review_rows.append({
            "task_id": task_id,
            "historical_metadata_review": metadata["evaluation_spec"].get("manual_review"),
            "historical_contract_review": contract.get("review"),
            "historical_contract_review_status": contract.get("review_status"),
            "independent_human_ledger_located": False,
            "current_audit_date": REVIEW_DATE,
            "current_reviewer_type": "Codex automated retrospective structural audit",
            "current_audit_scope": "generated TASK, spec hashes, declared API/behavior coverage, test nodeids, static test API use, leakage checks, companion mapping agreement",
            "current_audit_errors": checks,
            "current_audit_result": "pass" if not checks else "fix_required",
            "semantic_fairness_verdict": "not established by structural audit",
            "metadata_sha256": sha256(metadata_path.read_bytes()),
            "behavior_contract_sha256": sha256(contract_path.read_bytes()),
        })
        mapping_rows.append({
            "task_id": task_id,
            "spec_hash": metadata["spec_hash"],
            "public_spec": metadata["public_spec"],
            "public_clauses": metadata["evaluation_spec"].get("public_clauses", []),
            "public_test_mappings": metadata["evaluation_spec"].get("public_test_mappings", []),
            "hidden_test_mappings": metadata["evaluation_spec"].get("hidden_test_mappings", []),
            "required_api_coverage": metadata["evaluation_spec"].get("required_api_coverage", []),
        })

        prefix = f"tasks/{task_id}"
        add_file(payload, f"{prefix}/TASK.md", task_dir / "TASK.md")
        add_file(payload, f"{prefix}/behavior_contract.json", contract_path)
        for test_dir in ("public_tests", "hidden_tests"):
            for source in sorted((task_dir / test_dir).rglob("*.py")):
                add_file(payload, f"{prefix}/{source.relative_to(task_dir).as_posix()}", source)

    replay_rows = oracle["oracle_membership"]
    assert len(replay_rows) == 450
    assert {row["task_id"] for row in replay_rows} == set(task_ids)
    assert all(row["passed"] for row in replay_rows)
    payload["selection/frozen_membership.jsonl"] = jsonl_bytes(selection_rows)
    payload["selection/replacement_candidate_declarations.json"] = json_bytes({
        "provenance": "Constants extracted from archived builder script, not an independently preserved selection ledger",
        "script_path": SELECTION_SCRIPT.relative_to(ROOT).as_posix(),
        "script_sha256": sha256(SELECTION_SCRIPT.read_bytes()),
        "original_output_ledger_present": REPLACEMENT_LEDGER.is_file(),
        "candidates": declared_replacement_candidates(),
    })
    payload["contracts/contract_test_mappings.jsonl"] = jsonl_bytes(mapping_rows)
    payload["reviews/historical_and_current_review_index.jsonl"] = jsonl_bytes(review_rows)
    payload["reviews/human_semantic_review_template.csv"] = review_template_bytes(task_ids)
    payload["replays/recorded_reference_replays.jsonl"] = jsonl_bytes(replay_rows)
    payload["reviews/author_statement_provenance.json"] = json_bytes(read_json(AUTHOR_STATEMENT))

    summary = {
        "schema": "featureliftbench.anonymous_construction_evidence.v1",
        "assembled_at_date": REVIEW_DATE,
        "task_count": len(task_ids),
        "selection_evidence_counts": dict(selection_status),
        "historical_contract_review_status_counts": dict(review_status),
        "current_structural_audit_counts": dict(audit_status),
        "recorded_reference_replay_count": len(replay_rows),
        "independent_per_task_human_review_ledger_located": False,
        "original_143_task_candidate_funnel_located": False,
        "seven_replacement_original_ledger_located": REPLACEMENT_LEDGER.is_file(),
        "input_sha256": {
            path.relative_to(ROOT).as_posix(): sha256(path.read_bytes())
            for path in (MEMBERSHIP, FREEZE, ORACLE_EVIDENCE, AUTHOR_STATEMENT, SELECTION_SCRIPT)
        },
        "limits": [
            "A final membership list does not reveal candidate rejection counts or historical selection decisions.",
            "Recorded AI-assisted or maintainer-labeled metadata is not a complete independent human review ledger.",
            "Constitution validation establishes structural consistency, not semantic fairness of every test assertion.",
            "Reference replay rows are historical evidence; this assembly performs no new benchmark execution.",
        ],
    }
    payload["summary.json"] = json_bytes(summary)
    payload["README.md"] = (HERE / "CONSTRUCTION_EVIDENCE_README.md").read_bytes()
    payload["reviews/blinker_current_example_review.md"] = (HERE / "BLINKER_CURRENT_EXAMPLE_REVIEW.md").read_bytes()
    payload["build_construction_evidence.py"] = Path(__file__).read_bytes()
    manifest = {path: sha256(data) for path, data in sorted(payload.items())}
    payload["SHA256SUMS.json"] = json_bytes(manifest)

    with ZipFile(OUTPUT, "w", compression=ZIP_DEFLATED) as archive:
        for path, data in sorted(payload.items()):
            info = ZipInfo(path, date_time=(2026, 9, 27, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            archive.writestr(info, data)
    SUMMARY.write_bytes(json_bytes(summary))
    print(json.dumps({"zip": str(OUTPUT), "files": len(payload), "summary": summary}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    build()
