#!/usr/bin/env python3
"""Aggregate Flash-33 tool-agent audit records into task-level provenance labels."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO / "harness") not in sys.path:
    sys.path.insert(0, str(_REPO / "harness"))


SEVERITY = {
    "underdetermined": 4,
    "ambiguous": 3,
    "recoverable": 2,
    "explicit": 1,
    "abstain": 0,
}

DEFAULT_OUTPUT = (
    _REPO
    / "artifacts/research_analysis/hidden_provenance/flash33_agent_labels.json"
)


def _json_text(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def _rationale(record: dict[str, Any]) -> str:
    claims = [
        str(item.get("claim") or "").strip()
        for item in (record.get("evidence") or [])
        if isinstance(item, dict)
    ]
    claims = [claim for claim in claims if claim]
    if claims:
        return " | ".join(claims[:3])
    reason = str(record.get("abstain_reason") or "").strip()
    if reason:
        return reason
    return f"Agent verdict={record.get('verdict')}"


def _load_case_rows(run_dir: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for validation_path in sorted(run_dir.glob("*/validation.json")):
        case_id = validation_path.parent.name
        validation = json.loads(validation_path.read_text(encoding="utf-8"))
        record_path = validation_path.parent / "audit_record.json"
        record: dict[str, Any] | None = None
        if record_path.is_file():
            try:
                payload = json.loads(record_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                payload = None
            if isinstance(payload, dict):
                record = payload
        packet_path = None
        # Prefer suite case audit packet if the runner preserved nothing.
        rows.append(
            {
                "case_id": case_id,
                "valid": bool(validation.get("valid")),
                "validation_errors": list(validation.get("errors") or []),
                "record": record,
                "validation": validation,
            }
        )
        del packet_path
    return rows


def _task_id_from_case(case_id: str, record: dict[str, Any] | None) -> str:
    if record and record.get("task_id"):
        return str(record["task_id"])
    # case_id = {task_id}__{test_name}; task ids contain __ separators.
    parts = case_id.split("__")
    if len(parts) >= 3:
        return "__".join(parts[:-1])
    return case_id


def _test_name_from_case(case_id: str, record: dict[str, Any] | None) -> str:
    if record and record.get("nodeid"):
        nodeid = str(record["nodeid"])
        if "::" in nodeid:
            return nodeid.rsplit("::", 1)[-1]
    if "__" in case_id:
        return case_id.rsplit("__", 1)[-1]
    return case_id


def aggregate(
    *,
    run_dir: Path,
    suite_manifest: Path | None,
    output: Path,
    reviewer: str,
) -> dict[str, Any]:
    rows = _load_case_rows(run_dir)
    case_meta: dict[str, dict[str, Any]] = {}
    if suite_manifest and suite_manifest.is_file():
        manifest = json.loads(suite_manifest.read_text(encoding="utf-8"))
        for row in manifest.get("cases") or []:
            if isinstance(row, dict) and row.get("case_id"):
                case_meta[str(row["case_id"])] = row

    by_task: dict[str, list[dict[str, Any]]] = {}
    valid_count = 0
    invalid_count = 0
    abstain_count = 0
    for row in rows:
        case_id = row["case_id"]
        record = row["record"]
        meta = case_meta.get(case_id) or {}
        task_id = str(meta.get("task_id") or _task_id_from_case(case_id, record))
        test_name = str(
            meta.get("test_name") or _test_name_from_case(case_id, record)
        )
        if not row["valid"] or record is None:
            invalid_count += 1
            assertion = {
                "test": test_name,
                "label": "abstain",
                "rationale": "; ".join(row["validation_errors"])
                or "invalid or missing audit record",
                "case_id": case_id,
                "valid": False,
            }
            by_task.setdefault(task_id, []).append(assertion)
            abstain_count += 1
            continue
        valid_count += 1
        verdict = str(record.get("verdict") or "abstain").lower()
        if verdict == "abstain":
            abstain_count += 1
        assertion = {
            "test": test_name,
            "label": verdict,
            "rationale": _rationale(record),
            "case_id": case_id,
            "valid": True,
            "confidence": record.get("confidence"),
            "public_obligation_ids": record.get("public_obligation_ids") or [],
            "evidence": record.get("evidence") or [],
            "counterevidence": record.get("counterevidence") or [],
            "nodeid": record.get("nodeid"),
        }
        by_task.setdefault(task_id, []).append(assertion)

    labels: list[dict[str, Any]] = []
    for task_id in sorted(by_task):
        assertions = by_task[task_id]
        primary = max(
            assertions,
            key=lambda item: SEVERITY.get(str(item.get("label")), -1),
        )
        labels.append(
            {
                "task_id": task_id,
                "failed_hidden_tests": [item["test"] for item in assertions],
                "task_primary": primary["label"],
                "assertions": assertions,
                "confidence": "agent",
            }
        )

    counts = Counter(str(item["task_primary"]) for item in labels)
    payload = {
        "schema_version": "featureliftbench.hidden_provenance_labels.v1",
        "slice": "hidden_provenance_flash33_v1",
        "generated_at": date.today().isoformat(),
        "labeling": {
            "codebook": "docs/HIDDEN_CONTRACT_PROVENANCE.md",
            "reviewer": reviewer,
            "gold": False,
            "note": (
                "Agent-adjudicated labels from the Flash-33 tool-agent audit. "
                "Not human gold. Invalid audit records are recorded as abstain."
            ),
            "run_dir": str(run_dir.resolve()),
            "suite_manifest": str(suite_manifest.resolve())
            if suite_manifest
            else None,
        },
        "n": len(labels),
        "case_stats": {
            "case_count": len(rows),
            "valid_count": valid_count,
            "invalid_count": invalid_count,
            "abstain_count": abstain_count,
            "valid_rate": round(valid_count / len(rows), 6) if rows else 0.0,
        },
        "counts": {
            "explicit": int(counts.get("explicit", 0)),
            "recoverable": int(counts.get("recoverable", 0)),
            "ambiguous": int(counts.get("ambiguous", 0)),
            "underdetermined": int(counts.get("underdetermined", 0)),
            "abstain": int(counts.get("abstain", 0)),
        },
        "labels": labels,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(_json_text(payload), encoding="utf-8")
    return payload


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    parser.add_argument(
        "--suite-manifest",
        type=Path,
        default=_REPO
        / "artifacts/research_analysis/agentic_evidence/flash33_suite_v1"
        / "suite_manifest.json",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--reviewer",
        default="agentic_evidence_tool_r1",
    )
    return parser


def main() -> int:
    args = _parser().parse_args()
    run_dir = args.run_dir.resolve()
    if not run_dir.is_dir():
        print(f"missing run directory: {run_dir}", file=sys.stderr)
        return 2
    payload = aggregate(
        run_dir=run_dir,
        suite_manifest=args.suite_manifest.resolve()
        if args.suite_manifest
        else None,
        output=args.output.resolve(),
        reviewer=args.reviewer,
    )
    stats = payload["case_stats"]
    print(
        f"wrote {args.output} n_tasks={payload['n']} "
        f"valid={stats['valid_count']}/{stats['case_count']} "
        f"counts={payload['counts']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
