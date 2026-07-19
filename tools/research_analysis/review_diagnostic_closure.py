#!/usr/bin/env python3
"""Build auditable AI-assisted file closure for Diagnostic-40.

The output is complete enough for provisional engineering measurements, but
is deliberately marked ``ai_assisted_reviewed``.  It does not satisfy the
paper-release requirement for two independent human annotators.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from collections import deque
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HARNESS = ROOT / "harness"
sys.path.insert(0, str(HARNESS))

from featureliftbench.closure_gold import normalize_source_path  # noqa: E402


TASKS = ROOT / "benchmark/tasks"
SUBSET = ROOT / "artifacts/research_analysis/v1_1/diagnostic_subset_manifest.json"
OUTPUT = ROOT / "artifacts/research_analysis/v1_1/diagnostic_closure_review_audit.json"
HUMAN_STATUSES = {"author_reviewed", "double_reviewed", "adjudicated"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--force", action="store_true", help="Allow replacing a human-reviewed file")
    return parser.parse_args()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def source_files(task: Path) -> list[Path]:
    return sorted(
        path for path in (task / "repo").rglob("*.py")
        if ".git" not in path.parts and "__pycache__" not in path.parts
    )


def package_name(metadata: dict[str, Any], manifest: dict[str, Any]) -> str:
    explicit = str(manifest.get("source_package_name") or "").strip()
    if explicit:
        return explicit.replace("-", "_")
    entrypoints = ((metadata.get("feature") or {}).get("source_entrypoints") or [])
    if entrypoints:
        return str(entrypoints[0]).split(".", 1)[0].replace("-", "_")
    return ""


def module_index(task: Path, package: str) -> dict[str, Path]:
    index: dict[str, Path] = {}
    for path in source_files(task):
        relative = path.relative_to(task / "repo")
        parts = list(relative.with_suffix("").parts)
        while parts and parts[0] in {"src", "lib"}:
            parts.pop(0)
        if not parts:
            continue
        if parts[-1] == "__init__":
            parts.pop()
        module = ".".join(parts)
        if module and (not package or module == package or module.startswith(package + ".")):
            index[module] = path
    return index


def entrypoint_modules(metadata: dict[str, Any], index: dict[str, Path]) -> set[str]:
    modules: set[str] = set()
    for raw in ((metadata.get("feature") or {}).get("source_entrypoints") or []):
        parts = str(raw).split(".")
        for size in range(len(parts), 0, -1):
            candidate = ".".join(parts[:size])
            if candidate in index:
                modules.add(candidate)
                break
    return modules


def imported_modules(path: Path, module: str, package: str, index: dict[str, Path]) -> set[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return set()
    imported: set[str] = set()
    current_package = module.rsplit(".", 1)[0] if path.name != "__init__.py" else module
    for node in ast.walk(tree):
        candidates: list[str] = []
        if isinstance(node, ast.Import):
            candidates.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ""
            if node.level:
                parent = current_package.split(".")
                keep = max(0, len(parent) - node.level + 1)
                base = ".".join(parent[:keep] + ([base] if base else []))
            candidates.append(base)
            candidates.extend(f"{base}.{alias.name}" if base else alias.name for alias in node.names)
        for candidate in candidates:
            if not candidate or (package and not (candidate == package or candidate.startswith(package + "."))):
                continue
            probe = candidate
            while probe:
                if probe in index:
                    imported.add(probe)
                    break
                probe = probe.rsplit(".", 1)[0] if "." in probe else ""
    return imported


def static_closure(task: Path, metadata: dict[str, Any], manifest: dict[str, Any]) -> list[str]:
    package = package_name(metadata, manifest)
    index = module_index(task, package)
    queue = deque(sorted(entrypoint_modules(metadata, index)))
    seen: set[str] = set()
    while queue:
        module = queue.popleft()
        if module in seen or module not in index:
            continue
        seen.add(module)
        queue.extend(sorted(imported_modules(index[module], module, package, index) - seen))
    return sorted((Path("repo") / index[module].relative_to(task / "repo")).as_posix() for module in seen)


def manifest_files(task: Path, manifest: dict[str, Any]) -> tuple[list[str], str]:
    values = manifest.get("required_source_files")
    field = "required_source_files"
    if not isinstance(values, list) or not values:
        values = manifest.get("source_files")
        field = "source_files"
    normalized = []
    for raw in values or []:
        if isinstance(raw, str) and (value := normalize_source_path(raw, task)):
            normalized.append(value)
    return sorted(set(normalized)), field


def third_party_requirements(task: Path, manifest: dict[str, Any]) -> list[dict[str, Any]]:
    values: set[str] = set()
    lock = task / "requirements.lock"
    if lock.is_file():
        for line in lock.read_text(encoding="utf-8").splitlines():
            value = re.split(r"[<>=!~\[]", line.strip(), maxsplit=1)[0].strip()
            if value and not value.startswith("#"):
                values.add(value)
    values.update(str(value) for value in manifest.get("runtime_dependencies") or [] if str(value))
    return [
        {
            "requirement_id": f"third_party_requirement_{index:03d}",
            "kind": "third_party",
            "necessity": "must",
            "satisfied_by": [
                {"solution_id": "approved_dependency", "artifacts": [{"kind": "third_party", "value": value}]}
            ],
            "behavior_ids": [],
            "evidence_paths": ["requirements.lock" if lock.is_file() else "evaluation/oracle_manifest.json"],
            "rationale": "Pinned evaluator dependency; necessity beyond the reference implementation remains human-review pending.",
        }
        for index, value in enumerate(sorted(values), 1)
    ]


def main() -> int:
    args = parse_args()
    subset = load(SUBSET)
    representative = set(subset["representative_20"])
    challenge = set(subset["challenge_20"])
    diagnostic = sorted(representative | challenge)
    audit_rows: list[dict[str, Any]] = []
    unresolved: list[str] = []
    total_requirements = 0
    for task_id in diagnostic:
        task = TASKS / task_id
        path = task / "evaluation/closure_gold.json"
        previous = load(path)
        previous_status = str((previous.get("review") or {}).get("status") or "")
        if previous_status in HUMAN_STATUSES and not args.force:
            raise RuntimeError(f"refusing to replace human-reviewed closure: {task_id}")
        metadata = load(task / "metadata.json")
        manifest = load(task / "evaluation/oracle_manifest.json")
        manifest_values, manifest_field = manifest_files(task, manifest)
        static_values = static_closure(task, metadata, manifest)
        selected = manifest_values or static_values
        source = f"oracle_manifest.{manifest_field}" if manifest_values else "static_entrypoint_import_closure"
        if not selected:
            unresolved.append(task_id)
        behavior = load(task / "evaluation/behavior_contract.json")
        behavior_ids = [str(row["behavior_id"]) for row in behavior.get("public_clauses") or [] if row.get("clause_kind") == "included_behavior"]
        file_requirements = [
            {
                "requirement_id": f"file_requirement_{index:03d}",
                "kind": "file",
                "necessity": "must",
                "satisfied_by": [
                    {
                        "solution_id": "original_source_file",
                        "artifacts": [{"kind": "file", "source_path": value}],
                    }
                ],
                "behavior_ids": behavior_ids,
                "evidence_paths": [
                    f"evaluation/oracle_manifest.json#{manifest_field}" if manifest_values
                    else "metadata.json#/feature/source_entrypoints"
                ],
                "rationale": (
                    "Reference closure requirement confirmed by the legacy oracle manifest and a separate static pass."
                    if manifest_values
                    else "Reference closure requirement recovered from the public entrypoints and transitive internal imports."
                ),
            }
            for index, value in enumerate(selected, 1)
        ]
        third_party = third_party_requirements(task, manifest)
        payload = {
            "schema_version": "featureliftbench.closure_gold.v1",
            "task_id": task_id,
            "entrypoints": [str(value) for value in (metadata.get("feature") or {}).get("source_entrypoints") or []],
            "closure_variants": [
                {"variant_id": "reference_source_closure", "requirements": file_requirements + third_party}
            ],
            "annotation_scope": {
                "file": "complete_ai_assisted_reference_closure" if selected else "unresolved",
                "symbol": "unresolved",
                "runtime": "partial_manifest_evidence" if manifest.get("runtime_dependencies") else "unresolved",
                "behavioral": "linked_to_public_behavior_ids",
            },
            "gold_completeness": {
                "file": "complete" if selected else "unresolved",
                "symbol": "unresolved",
                "resource": "unresolved",
                "runtime_state": "partial" if manifest.get("runtime_dependencies") else "unresolved",
                "third_party": "partial" if third_party else "unresolved",
                "adapter": "unresolved",
            },
            "review": {
                "status": "ai_assisted_reviewed",
                "reviewer_1": "codex_manifest_normalization_pass",
                "reviewer_1_type": "ai_assisted_author",
                "reviewer_2": "codex_static_entrypoint_closure_pass",
                "reviewer_2_type": "ai_assisted_second_pass_not_independent_human",
                "disagreements": sorted(set(static_values) - set(manifest_values)) if manifest_values else [],
                "adjudicator": "",
                "formal_human_double_review_pending": True,
            },
            "audit": {
                "selection_source": source,
                "manifest_file_count": len(manifest_values),
                "static_candidate_count": len(static_values),
                "static_candidates_not_in_reference_closure": sorted(set(static_values) - set(selected)),
                "limitation": (
                    "File completeness is provisional reference-closure completeness. Symbol, runtime-state, "
                    "replaceability, and semantic minimality remain unresolved until independent human review "
                    "and executable necessity probes."
                ),
            },
        }
        if not args.check:
            path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        total_requirements += len(file_requirements)
        audit_rows.append(
            {
                "task_id": task_id,
                "subset": "representative20" if task_id in representative else "challenge20",
                "selection_source": source,
                "file_requirement_count": len(file_requirements),
                "static_candidate_count": len(static_values),
                "formal_human_double_review_pending": True,
            }
        )
    audit = {
        "schema_version": "featureliftbench.diagnostic_closure_ai_review_audit.v1",
        "review_boundary": (
            "Two AI-assisted passes are recorded and must not be represented as two independent human reviews."
        ),
        "task_count": len(diagnostic),
        "complete_file_task_count": len(diagnostic) - len(unresolved),
        "unresolved_task_ids": unresolved,
        "file_requirement_count": total_requirements,
        "tasks": audit_rows,
    }
    if not args.check:
        OUTPUT.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: audit[key] for key in ("task_count", "complete_file_task_count", "file_requirement_count", "unresolved_task_ids")}, indent=2))
    return 0 if not unresolved else 1


if __name__ == "__main__":
    raise SystemExit(main())
