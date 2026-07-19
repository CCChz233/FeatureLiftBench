#!/usr/bin/env python3
"""Materialize v1.1 public clauses and private audit annotation scaffolds.

The script never reads hidden-test bodies to author behavior.  Public clauses
come exclusively from metadata.feature.included_behaviors.  Hidden test nodeids
are inspected only after the public clause block is frozen and are stored in a
private evaluator-side mapping for human review.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
HARNESS = REPO_ROOT / "harness"
if str(HARNESS) not in sys.path:
    sys.path.insert(0, str(HARNESS))

from featureliftbench.closure_gold import load_closure_gold  # noqa: E402

TASKS_ROOT = REPO_ROOT / "benchmark/tasks"
DEFAULT_SUBSET = REPO_ROOT / "artifacts/research_analysis/v1_1/diagnostic_subset_manifest.json"
DEFAULT_TAXONOMY = REPO_ROOT / "artifacts/research_analysis/python150_task_taxonomy.csv"
CLAUSE_START = "<!-- featureliftbench:behavior-clauses:start -->"
CLAUSE_END = "<!-- featureliftbench:behavior-clauses:end -->"
TOKEN_RE = re.compile(r"[a-z0-9]+")
STOPWORDS = {
    "a", "an", "and", "as", "be", "by", "for", "from", "in", "is", "of", "on", "or",
    "the", "to", "with", "without", "support", "supports", "behavior", "behaviors",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tasks-root", type=Path, default=TASKS_ROOT)
    parser.add_argument("--subset-manifest", type=Path, default=DEFAULT_SUBSET)
    parser.add_argument("--check", action="store_true", help="Report changes without writing")
    parser.add_argument("--force-closure-templates", action="store_true")
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def public_clauses(metadata: dict[str, Any]) -> list[dict[str, str]]:
    feature = metadata.get("feature") if isinstance(metadata.get("feature"), dict) else {}
    behaviors = feature.get("included_behaviors") if isinstance(feature.get("included_behaviors"), list) else []
    clauses = []
    for index, value in enumerate(behaviors):
        if not isinstance(value, str) or not value.strip():
            continue
        clauses.append(
            {
                "behavior_id": f"B{index + 1:03d}",
                "text": value.strip(),
                "spec_anchor": f"metadata.json#/feature/included_behaviors/{index}",
                "clause_kind": "included_behavior",
            }
        )
    output = metadata.get("output") if isinstance(metadata.get("output"), dict) else {}
    api_import = str(output.get("import") or "").strip()
    if api_import:
        clauses.append(
            {
                "behavior_id": f"B{len(clauses) + 1:03d}",
                "text": (
                    "the declared target API remains importable and preserves upstream-observable "
                    "semantics within the included and excluded feature scope"
                ),
                "spec_anchor": "metadata.json#/output/import",
                "clause_kind": "api_surface",
            }
        )
    environment = metadata.get("environment") if isinstance(metadata.get("environment"), dict) else {}
    forbidden = [str(value) for value in environment.get("forbidden_imports") or [] if str(value)]
    if forbidden:
        clauses.append(
            {
                "behavior_id": f"B{len(clauses) + 1:03d}",
                "text": "the submitted package does not import forbidden upstream packages: " + ", ".join(forbidden),
                "spec_anchor": "metadata.json#/environment/forbidden_imports",
                "clause_kind": "isolation_constraint",
            }
        )
    return clauses


def task_document(metadata: dict[str, Any], clauses: list[dict[str, str]]) -> str:
    feature = metadata["feature"]
    output = metadata["output"]
    environment = metadata["environment"]
    excluded = feature.get("excluded_behaviors") or []
    lines = [
        f"# FeatureLift Task: {feature['name']}",
        "",
        str(feature["description"]),
        "",
        "## Target API",
        "",
        f"- Import: `{output.get('import', '')}`",
        f"- Callable: `{output.get('callable', '')}`",
        f"- Signature: `{output.get('signature', '')}`",
        "",
        "## Excluded Behavior",
        "",
    ]
    lines.extend(f"- {value}" for value in excluded)
    lines.extend(
        [
            "",
            "## Constraints",
            "",
            f"- Output package: `{output.get('package', 'featurelifted')}`",
            f"- Network access: `{str(bool(environment.get('network'))).lower()}`",
            "- Forbidden upstream imports: "
            + ", ".join(f"`{value}`" for value in environment.get("forbidden_imports") or []),
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def clause_block(clauses: list[dict[str, str]]) -> str:
    lines = [
        CLAUSE_START,
        "## Public Behavior Contract",
        "",
        "The stable clause IDs below define the public behavior contract. Hidden tests may exercise",
        "these clauses but do not introduce additional requirements.",
        "",
    ]
    lines.extend(f"- **{item['behavior_id']}** — {item['text']}" for item in clauses)
    lines.extend([CLAUSE_END, ""])
    return "\n".join(lines)


def with_clause_block(text: str, clauses: list[dict[str, str]]) -> str:
    block = clause_block(clauses)
    if CLAUSE_START in text and CLAUSE_END in text:
        start = text.index(CLAUSE_START)
        end = text.index(CLAUSE_END, start) + len(CLAUSE_END)
        return text[:start].rstrip() + "\n\n" + block + text[end:].lstrip("\n")
    return text.rstrip() + "\n\n" + block


def pytest_nodeids(root: Path, task_dir: Path) -> list[str]:
    result: list[str] = []
    if not root.is_dir():
        return result
    for path in sorted(root.rglob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError):
            continue
        relative = path.relative_to(task_dir).as_posix()
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
                result.append(f"{relative}::{node.name}")
            elif isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name.startswith("test_"):
                        result.append(f"{relative}::{node.name}::{child.name}")
    return result


def tokens(text: str) -> set[str]:
    return {value for value in TOKEN_RE.findall(text.lower().replace("_", " ")) if value not in STOPWORDS and len(value) > 1}


def map_nodeid(nodeid: str, clauses: list[dict[str, str]]) -> dict[str, Any]:
    test_tokens = tokens(nodeid.rsplit("::", 1)[-1])
    ranked: list[tuple[float, str]] = []
    for clause in clauses:
        clause_tokens = tokens(clause["text"])
        overlap = len(test_tokens & clause_tokens)
        score = overlap / max(1, len(test_tokens | clause_tokens))
        ranked.append((score, clause["behavior_id"]))
    best = max(ranked, default=(0.0, ""))
    if best[0] <= 0:
        return {"nodeid": nodeid, "public_clause_ids": [], "mapping_method": "unmapped"}
    return {
        "nodeid": nodeid,
        "public_clause_ids": [best[1]],
        "mapping_method": "token_similarity",
    }


def behavior_contract(task_dir: Path, metadata: dict[str, Any], clauses: list[dict[str, str]], task_text: str) -> dict[str, Any]:
    public = [map_nodeid(value, clauses) for value in pytest_nodeids(task_dir / "public_tests", task_dir)]
    hidden = [map_nodeid(value, clauses) for value in pytest_nodeids(task_dir / "hidden_tests", task_dir)]
    unmapped_public = [item["nodeid"] for item in public if not item["public_clause_ids"]]
    unmapped_hidden = [item["nodeid"] for item in hidden if not item["public_clause_ids"]]
    entanglement = metadata.get("entanglement") if isinstance(metadata.get("entanglement"), dict) else {}
    return {
        "schema_version": "featureliftbench.behavior_contract.v1",
        "task_id": task_dir.name,
        "spec_sha256": hashlib.sha256(task_text.encode("utf-8")).hexdigest(),
        "spec_authored_from": [
            "metadata.json#/feature/name",
            "metadata.json#/feature/description",
            "metadata.json#/feature/included_behaviors",
            "metadata.json#/feature/excluded_behaviors",
            "metadata.json#/output",
        ],
        "public_clauses": clauses,
        "public_test_mappings": public,
        "hidden_test_mappings": hidden,
        "risk_tags": [str(value) for value in entanglement.get("types") or []],
        "unmapped_public_test_nodeids": unmapped_public,
        "unmapped_hidden_test_nodeids": unmapped_hidden,
        "mapping_policy": (
            "Public clauses were frozen from metadata before test-node mapping. "
            "Nodeids are evaluator-private; no hidden inputs, examples, or assertions are stored here."
        ),
        "review_status": "needs_review" if unmapped_public or unmapped_hidden else "auto_assigned",
    }


def closure_template(task_dir: Path, metadata: dict[str, Any]) -> dict[str, Any]:
    legacy = load_closure_gold(task_dir)
    requirements = []
    for index, value in enumerate(sorted(legacy.approved_artifact_values("file"))):
        requirements.append(
            {
                "requirement_id": f"file_requirement_{index + 1:03d}",
                "kind": "file",
                "necessity": "must",
                "satisfied_by": [
                    {
                        "solution_id": "original_file",
                        "artifacts": [{"kind": "file", "source_path": value}],
                    }
                ],
                "behavior_ids": [],
                "evidence_paths": [
                    f"evaluation/oracle_manifest.json#{legacy.source}"
                ],
                "rationale": "Auto-imported from the legacy oracle manifest; human necessity review pending.",
            }
        )
    feature = metadata.get("feature") if isinstance(metadata.get("feature"), dict) else {}
    return {
        "schema_version": "featureliftbench.closure_gold.v1",
        "task_id": task_dir.name,
        "entrypoints": [str(value) for value in feature.get("source_entrypoints") or []],
        "closure_variants": [
            {"variant_id": "legacy_reference", "requirements": requirements}
        ] if requirements else [],
        "annotation_scope": {
            "file": "auto_imported_legacy_manifest" if requirements else "unresolved",
            "symbol": "unresolved",
            "runtime": "unresolved",
            "behavioral": "unresolved",
        },
        "gold_completeness": {
            "file": "partial" if requirements else "unresolved",
            "symbol": "unresolved",
            "resource": "unresolved",
            "runtime_state": "unresolved",
            "third_party": "unresolved",
            "adapter": "unresolved",
        },
        "review": {
            "reviewer_1": "",
            "reviewer_2": "",
            "disagreements": [],
            "adjudicator": "",
            "status": "needs_review",
        },
    }


def main() -> int:
    args = parse_args()
    subset = load_json(args.subset_manifest)
    diagnostic_ids = set(subset["representative_20"]) | set(subset["challenge_20"])
    task_paths = sorted(path for path in args.tasks_root.iterdir() if (path / "metadata.json").is_file())
    changed_tasks = 0
    behavior_files = 0
    closure_files = 0
    hard50_updates = 0
    for task_dir in task_paths:
        metadata_path = task_dir / "metadata.json"
        metadata = load_json(metadata_path)
        if "hard3" in task_dir.name and metadata.get("split_role") != "mechanism_challenging":
            metadata["split_role"] = "mechanism_challenging"
            hard50_updates += 1
            if not args.check:
                write_json(metadata_path, metadata)
        clauses = public_clauses(metadata)
        if not clauses:
            raise ValueError(f"task has no public included_behaviors: {task_dir.name}")
        task_path = task_dir / "TASK.md"
        original = task_path.read_text(encoding="utf-8") if task_path.is_file() else task_document(metadata, clauses)
        task_text = with_clause_block(original, clauses)
        if not task_path.is_file() or task_path.read_text(encoding="utf-8") != task_text:
            changed_tasks += 1
            if not args.check:
                task_path.write_text(task_text, encoding="utf-8")
        contract = behavior_contract(task_dir, metadata, clauses, task_text)
        behavior_files += 1
        if not args.check:
            write_json(task_dir / "evaluation" / "behavior_contract.json", contract)
        closure_path = task_dir / "evaluation" / "closure_gold.json"
        if task_dir.name in diagnostic_ids and (args.force_closure_templates or not closure_path.exists()):
            closure_files += 1
            if not args.check:
                write_json(closure_path, closure_template(task_dir, metadata))
    print(
        f"tasks={len(task_paths)} TASK_changes={changed_tasks} behavior_contracts={behavior_files} "
        f"closure_templates={closure_files} hard50_split_role_updates={hard50_updates} "
        f"mode={'check' if args.check else 'write'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
