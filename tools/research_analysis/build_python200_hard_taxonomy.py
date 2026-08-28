#!/usr/bin/env python3
"""Merge Python-150 taxonomy v2 + Hard-50 ledger into a Python-200' analysis table.

This is an analysis layer, not a release gate. It does not read experiments,
submissions, or Functional Pass. Hard-50 rows are ledger-seeded; they are not
a full v2 structural taxonomy (no frozen repo-domain map, no oracle closure).

Reproduction:
    python3.12 tools/research_analysis/build_python200_hard_taxonomy.py
    python3.12 tools/research_analysis/build_python200_hard_taxonomy.py --check
"""

from __future__ import annotations

import argparse
import ast
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SUITE_PATH = ROOT / "benchmark/selection/python200_hard_suite.json"
LEDGER_PATH = ROOT / "benchmark/selection/hard50_expansion_20260827.json"
TAXONOMY_150 = ROOT / "artifacts/research_analysis/python150_task_taxonomy.csv"
LIFT_150 = ROOT / "reports/lift_taxonomy/LIFT_LABELS.jsonl"
CSV_OUT = ROOT / "artifacts/research_analysis/python200_hard_task_taxonomy.csv"
JSON_OUT = ROOT / "artifacts/research_analysis/python200_hard_task_taxonomy_summary.json"
REPORT_OUT = ROOT / "docs/reference/research_analysis/PYTHON200_HARD_TAXONOMY_REPORT.md"

NA = "NA"
TAXONOMY_VERSION = "python200_hard_v1"

FEATURE_FAMILIES_V2 = {
    "parse_tokenize_decode",
    "protocol_state_transition",
    "validate_normalize_construct",
    "serialize_format_render",
    "registry_plugin_dispatch",
    "config_resolve_discover",
    "resource_metadata_loading",
    "algorithm_data_structure",
    "cache_retry_policy",
    "workflow_session_orchestration",
}

PAPER_SITUATIONS = {
    "plugin_registry",
    "config_merge",
    "session_lifecycle",
    "schema_validate",
    "parse_codec",
    "resource_or_copytrap",
}

SITUATION_FROM_V2 = {
    "registry_plugin_dispatch": "plugin_registry",
    "config_resolve_discover": "config_merge",
    "workflow_session_orchestration": "session_lifecycle",
    "cache_retry_policy": "session_lifecycle",
    "validate_normalize_construct": "schema_validate",
    "algorithm_data_structure": "schema_validate",
    "parse_tokenize_decode": "parse_codec",
    "protocol_state_transition": "parse_codec",
    "serialize_format_render": "parse_codec",
    "resource_metadata_loading": "resource_or_copytrap",
}

# Selection-slot copytrap tasks still need a v2 behavior family.
COPYTRAP_V2_FAMILY = {
    "httpretty__uri_stub_core__001": "protocol_state_transition",
    "betamax__cassette_match_core__001": "resource_metadata_loading",
    "webob__request_response_core__001": "protocol_state_transition",
    "mimesis__person_address_core__001": "resource_metadata_loading",
    "mitmproxy__url_parse_core__001": "parse_tokenize_decode",
}

ORIGINAL_ENTANGLEMENT_MAP = {
    "implicit_dependency_coupling": "implicit_runtime_dependency",
    "data_model_coupling": "data_model_invariant",
    "parser_state_coupling": "parser_state",
    "framework_coupling": "framework_lifecycle",
    "global_state_registry_coupling": "global_state_registry",
    "config_environment_coupling": "config_environment",
    "resource_coupling": "resource_packaging",
    "third_party_dependency_coupling": "third_party_contract",
}

FIELDNAMES = (
    "task_id",
    "suite_split",
    "construction_split_150",
    "source_repo",
    "source_commit",
    "feature_family_selection",
    "feature_family_v2",
    "copytrap",
    "paper_situation",
    "lift_type",
    "lift_label_status",
    "entanglement_primary_original",
    "entanglement_types_original",
    "normalized_entanglement_types",
    "public_test_count",
    "hidden_test_count",
    "paper_fit",
    "taxonomy_coverage",
    "classification_evidence",
    "taxonomy_version",
)


def join_tags(values: Any) -> str:
    if values is None:
        return ""
    if isinstance(values, str):
        parts = [part.strip() for part in values.replace(",", ";").split(";") if part.strip()]
        return ";".join(parts)
    if isinstance(values, (list, tuple, set)):
        return ";".join(str(item) for item in values if str(item).strip())
    return str(values)


def normalize_entanglement(types: list[str]) -> str:
    mapped = []
    seen: set[str] = set()
    for raw in types:
        label = ORIGINAL_ENTANGLEMENT_MAP.get(raw)
        if label and label not in seen:
            seen.add(label)
            mapped.append(label)
    return ";".join(mapped)


def count_static_tests(directory: Path) -> str:
    if not directory.is_dir():
        return NA
    count = 0
    for path in sorted(directory.rglob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        except (SyntaxError, OSError):
            continue
        count += sum(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name.startswith("test")
            for node in ast.walk(tree)
        )
    return str(count)


def paper_situation(family_v2: str, copytrap: bool) -> str:
    if copytrap:
        return "resource_or_copytrap"
    situation = SITUATION_FROM_V2.get(family_v2)
    if situation is None:
        raise ValueError(f"no paper_situation for feature_family_v2={family_v2}")
    return situation


def load_suite_ids() -> list[str]:
    data = json.loads(SUITE_PATH.read_text(encoding="utf-8"))
    ids = list(data["task_ids"])
    if len(ids) != 200 or len(set(ids)) != 200:
        raise SystemExit(f"suite must list 200 unique ids, got {len(ids)}")
    return ids


def load_lift_150() -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for line in LIFT_150.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        out[row["task_id"]] = {
            "lift_type": str(row["lift_type"]),
            "lift_label_status": str(row.get("label_status") or "labeled"),
        }
    return out


def load_taxonomy_150() -> dict[str, dict[str, str]]:
    with TAXONOMY_150.open(encoding="utf-8", newline="") as handle:
        return {row["task_id"]: row for row in csv.DictReader(handle)}


def load_hard50_selected() -> list[dict[str, Any]]:
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    rows = [row for row in ledger["rows"] if row.get("disposition") == "selected"]
    if len(rows) != 50:
        raise SystemExit(f"ledger selected must be 50, got {len(rows)}")
    return rows


def python150_row(task_id: str, tax: dict[str, str], lift: dict[str, str]) -> dict[str, str]:
    family = tax["feature_family_primary"]
    if family not in FEATURE_FAMILIES_V2:
        raise SystemExit(f"{task_id}: unknown v2 family {family}")
    return {
        "task_id": task_id,
        "suite_split": "python150",
        "construction_split_150": tax.get("split") or NA,
        "source_repo": tax.get("source_repo") or NA,
        "source_commit": tax.get("source_commit") or NA,
        "feature_family_selection": family,
        "feature_family_v2": family,
        "copytrap": "false",
        "paper_situation": paper_situation(family, False),
        "lift_type": lift["lift_type"],
        "lift_label_status": lift["lift_label_status"],
        "entanglement_primary_original": tax.get("entanglement_primary_original") or NA,
        "entanglement_types_original": tax.get("entanglement_types_original") or "",
        "normalized_entanglement_types": tax.get("normalized_entanglement_types") or "",
        "public_test_count": tax.get("public_test_count") or NA,
        "hidden_test_count": tax.get("hidden_test_count") or NA,
        "paper_fit": "",
        "taxonomy_coverage": "v2_full",
        "classification_evidence": (
            f"{TAXONOMY_150.relative_to(ROOT)};{LIFT_150.relative_to(ROOT)};"
            f"benchmark/tasks/{task_id}/metadata.json"
        ),
        "taxonomy_version": TAXONOMY_VERSION,
    }


def hard50_row(ledger: dict[str, Any]) -> dict[str, str]:
    task_id = str(ledger["task_id"])
    task_dir = ROOT / "benchmark/hard50" / task_id
    meta_path = task_dir / "metadata.json"
    if not meta_path.is_file():
        raise SystemExit(f"missing Hard-50 metadata: {meta_path}")
    metadata = json.loads(meta_path.read_text(encoding="utf-8"))
    source = metadata.get("source") or {}
    entanglement = metadata.get("entanglement") or {}
    types = list(entanglement.get("types") or ledger.get("entanglement_types") or [])
    primary = str(entanglement.get("primary") or (types[0] if types else NA))
    selection_family = str(ledger["feature_family"])
    copytrap = selection_family == "direct_tooling_copytrap"
    if copytrap:
        family_v2 = COPYTRAP_V2_FAMILY[task_id]
    else:
        family_v2 = selection_family
    if family_v2 not in FEATURE_FAMILIES_V2:
        raise SystemExit(f"{task_id}: Hard-50 family_v2 not in v2 vocab: {family_v2}")
    evidence = [
        str(LEDGER_PATH.relative_to(ROOT)),
        str(meta_path.relative_to(ROOT)),
    ]
    card = ledger.get("design_card")
    if card:
        evidence.append(str(card))
    return {
        "task_id": task_id,
        "suite_split": "hard50",
        "construction_split_150": NA,
        "source_repo": str(source.get("name") or ledger.get("package") or NA),
        "source_commit": str(source.get("commit") or ledger.get("commit") or NA),
        "feature_family_selection": selection_family,
        "feature_family_v2": family_v2,
        "copytrap": "true" if copytrap else "false",
        "paper_situation": paper_situation(family_v2, copytrap),
        "lift_type": str(ledger["planned_lift_type"]),
        "lift_label_status": "planned_ledger",
        "entanglement_primary_original": primary,
        "entanglement_types_original": join_tags(types),
        "normalized_entanglement_types": normalize_entanglement([str(item) for item in types]),
        "public_test_count": count_static_tests(task_dir / "public_tests"),
        "hidden_test_count": count_static_tests(task_dir / "hidden_tests"),
        "paper_fit": str(ledger.get("paper_fit") or ""),
        "taxonomy_coverage": "ledger_seed",
        "classification_evidence": ";".join(evidence),
        "taxonomy_version": TAXONOMY_VERSION,
    }


def build_rows() -> list[dict[str, str]]:
    suite_ids = load_suite_ids()
    tax150 = load_taxonomy_150()
    lift150 = load_lift_150()
    hard50 = {row["task_id"]: row for row in load_hard50_selected()}
    if set(tax150) & set(hard50):
        overlap = sorted(set(tax150) & set(hard50))
        raise SystemExit(f"150/Hard-50 id overlap: {overlap[:8]}")
    expected_150 = [task_id for task_id in suite_ids if task_id in tax150]
    expected_50 = [task_id for task_id in suite_ids if task_id in hard50]
    if len(expected_150) != 150 or len(expected_50) != 50:
        raise SystemExit(
            f"suite membership mismatch: 150={len(expected_150)} hard50={len(expected_50)}"
        )
    missing_lift = sorted(set(expected_150) - set(lift150))
    if missing_lift:
        raise SystemExit(f"150 lift labels missing: {missing_lift[:8]}")
    rows = []
    for task_id in suite_ids:
        if task_id in tax150:
            rows.append(python150_row(task_id, tax150[task_id], lift150[task_id]))
        else:
            rows.append(hard50_row(hard50[task_id]))
    if len(rows) != 200:
        raise SystemExit(f"expected 200 rows, got {len(rows)}")
    return rows


def count_field(rows: list[dict[str, str]], field: str) -> list[tuple[str, int]]:
    return Counter(row[field] for row in rows).most_common()


def markdown_table(title: str, counts: list[tuple[str, int]], total: int) -> str:
    lines = [
        f"### {title}",
        "",
        "| label | n | share |",
        "| --- | ---: | ---: |",
    ]
    for label, n in counts:
        lines.append(f"| `{label}` | {n} | {n / total:.1%} |")
    lines.append("")
    return "\n".join(lines)


def write_report(rows: list[dict[str, str]]) -> dict[str, Any]:
    total = len(rows)
    hard50 = [row for row in rows if row["suite_split"] == "hard50"]
    python150 = [row for row in rows if row["suite_split"] == "python150"]
    summary = {
        "taxonomy_version": TAXONOMY_VERSION,
        "task_count": total,
        "python150_count": len(python150),
        "hard50_count": len(hard50),
        "copytrap_count": sum(row["copytrap"] == "true" for row in rows),
        "by_suite_split": dict(count_field(rows, "suite_split")),
        "by_paper_situation": dict(count_field(rows, "paper_situation")),
        "by_feature_family_v2": dict(count_field(rows, "feature_family_v2")),
        "by_lift_type": dict(count_field(rows, "lift_type")),
        "hard50_by_feature_family_selection": dict(
            count_field(hard50, "feature_family_selection")
        ),
        "hard50_by_lift_type": dict(count_field(hard50, "lift_type")),
        "python150_by_paper_situation": dict(count_field(python150, "paper_situation")),
        "hard50_by_paper_situation": dict(count_field(hard50, "paper_situation")),
        "csv": str(CSV_OUT.relative_to(ROOT)),
    }
    report = "\n".join(
        [
            "# FeatureLiftBench Python-200' Task Taxonomy",
            "",
            f"> **Documentation status: generated/reference · Last verified: 2026-08-28**  ",
            f"> Version `{TAXONOMY_VERSION}`. Analysis layer, not a release gate.  ",
            "> Does not include Functional Pass, RRES, or trajectories.",
            "",
            f"- Rows: **{total}** (`python150` {len(python150)} + `hard50` {len(hard50)})",
            f"- Copy-trap flag: **{summary['copytrap_count']}** (Hard-50 selection slot only)",
            f"- CSV: `{CSV_OUT.relative_to(ROOT)}`",
            "- 150 coverage: taxonomy v2 + lift JSONL (`v2_full`)",
            "- Hard-50 coverage: ledger + `benchmark/hard50/*/metadata.json` (`ledger_seed`)",
            "- `direct_tooling_copytrap` is a RQ2 flag, not an 11th feature family;",
            "  those five tasks still have a v2 behavior family.",
            "- Do not mix this table with superseded 150+External-50 balance counts.",
            "- `construction_split_150` is the old 150 core100/hard50 construction",
            "  stratum. It is **not** the new Hard-50 expansion split.",
            "",
            markdown_table("Paper situation (200')", count_field(rows, "paper_situation"), total),
            markdown_table("Feature family v2 (200')", count_field(rows, "feature_family_v2"), total),
            markdown_table("Lift type (200')", count_field(rows, "lift_type"), total),
            markdown_table(
                "Hard-50 selection family (includes copytrap slot)",
                count_field(hard50, "feature_family_selection"),
                len(hard50),
            ),
            markdown_table(
                "Python-150 paper situation",
                count_field(python150, "paper_situation"),
                len(python150),
            ),
            markdown_table(
                "Hard-50 paper situation",
                count_field(hard50, "paper_situation"),
                len(hard50),
            ),
            "## Reproduction",
            "",
            "```bash",
            "python3.12 tools/research_analysis/build_python200_hard_taxonomy.py --check",
            "```",
            "",
        ]
    )
    REPORT_OUT.write_text(report, encoding="utf-8")
    JSON_OUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return summary


def write_csv(rows: list[dict[str, str]]) -> None:
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    with CSV_OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def validate(rows: list[dict[str, str]]) -> None:
    errors: list[str] = []
    if len(rows) != 200:
        errors.append(f"row count {len(rows)}")
    ids = [row["task_id"] for row in rows]
    if len(set(ids)) != 200:
        errors.append("duplicate task_id")
    suite = set(load_suite_ids())
    if set(ids) != suite:
        errors.append("CSV ids != python200_hard_suite.json")
    for row in rows:
        if row["paper_situation"] not in PAPER_SITUATIONS:
            errors.append(f"{row['task_id']}: bad situation")
        if row["feature_family_v2"] not in FEATURE_FAMILIES_V2:
            errors.append(f"{row['task_id']}: bad v2 family")
        if row["lift_type"] not in {"Direct", "Adapted", "Composite"}:
            errors.append(f"{row['task_id']}: bad lift")
        if row["copytrap"] not in {"true", "false"}:
            errors.append(f"{row['task_id']}: bad copytrap")
        if row["suite_split"] == "python150" and row["copytrap"] != "false":
            errors.append(f"{row['task_id']}: 150 marked copytrap")
        if (
            row["suite_split"] == "hard50"
            and row["feature_family_selection"] == "direct_tooling_copytrap"
            and row["copytrap"] != "true"
        ):
            errors.append(f"{row['task_id']}: copytrap slot not flagged")
        if row["taxonomy_version"] != TAXONOMY_VERSION:
            errors.append(f"{row['task_id']}: taxonomy_version")
    copytrap_n = sum(row["copytrap"] == "true" for row in rows)
    if copytrap_n != 5:
        errors.append(f"copytrap count {copytrap_n}, expected 5")
    if errors:
        raise SystemExit("validation failed:\n  " + "\n  ".join(errors[:20]))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="rebuild and validate")
    args = parser.parse_args()
    rows = build_rows()
    validate(rows)
    write_csv(rows)
    summary = write_report(rows)
    print(
        f"Python-200' taxonomy: {summary['task_count']} rows "
        f"(150={summary['python150_count']}, hard50={summary['hard50_count']}, "
        f"copytrap={summary['copytrap_count']})"
    )
    print(f"wrote {CSV_OUT.relative_to(ROOT)}")
    print(f"wrote {REPORT_OUT.relative_to(ROOT)}")
    if args.check:
        print("check: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
