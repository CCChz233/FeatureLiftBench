#!/usr/bin/env python3
"""Generate reviewable API-contract patch candidates from evaluator usage and oracles."""

from __future__ import annotations

import argparse
import ast
import copy
import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "harness"
if str(HARNESS) not in sys.path:
    sys.path.insert(0, str(HARNESS))

from featureliftbench.constitution_validate import STANDARD_MODULE_METADATA_REFS  # noqa: E402


HARDENER_PATH = ROOT / "scripts/archive/harden_experiment_contracts.py"
SPEC = importlib.util.spec_from_file_location("flb_contract_hardener", HARDENER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load {HARDENER_PATH}")
HARDENER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HARDENER)

DEFAULT_AUDIT = ROOT / "reports/contract_closure_200/machine_audit.json"
DEFAULT_DECISIONS = ROOT / "reports/contract_closure_200/decisions.jsonl"
DEFAULT_OUTPUT = ROOT / "reports/contract_closure_200/api_patch_candidates.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument("--decisions", type=Path, default=DEFAULT_DECISIONS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--task-id", action="append", dest="task_ids")
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def load_decisions(path: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict) or not isinstance(value.get("task_id"), str):
            raise ValueError(f"{path}:{number}: invalid decision")
        rows[str(value["task_id"])] = value
    return rows


def flatten(entries: Any) -> list[dict[str, Any]]:
    return HARDENER._flatten_api(entries)


def imported_paths(tree: ast.AST) -> dict[str, str]:
    result: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and isinstance(node.module, str):
            if node.module == "featurelifted" or node.module.startswith("featurelifted."):
                for alias in node.names:
                    result[alias.asname or alias.name] = f"{node.module}.{alias.name}"
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "featurelifted" or alias.name.startswith("featurelifted."):
                    result[alias.asname or alias.name.split(".", 1)[0]] = alias.name
    return result


def expression_path(node: ast.expr, imported: dict[str, str]) -> str | None:
    if isinstance(node, ast.Name):
        return imported.get(node.id)
    if isinstance(node, ast.Attribute):
        prefix = expression_path(node.value, imported)
        return f"{prefix}.{node.attr}" if prefix else None
    return None


def ast_usage(task_dir: Path) -> dict[str, dict[str, Any]]:
    usage: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"called": False, "class_checked": False, "exception_checked": False, "evidence": []}
    )
    for directory in ("public_tests", "hidden_tests"):
        root = task_dir / directory
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*.py")):
            source = path.read_text(encoding="utf-8")
            try:
                tree = ast.parse(source)
            except SyntaxError:
                continue
            imported = imported_paths(tree)
            relative = path.relative_to(task_dir).as_posix()
            for node in ast.walk(tree):
                api_path: str | None = None
                signal: str | None = None
                if isinstance(node, ast.Call):
                    api_path = expression_path(node.func, imported)
                    signal = "called"
                    if (
                        isinstance(node.func, ast.Name)
                        and node.func.id in {"isinstance", "issubclass"}
                        and len(node.args) >= 2
                    ):
                        checked = expression_path(node.args[1], imported)
                        if checked:
                            api_path = checked
                            signal = "class_checked"
                if api_path is None or not api_path.startswith("featurelifted."):
                    continue
                item = usage[api_path]
                item[signal or "called"] = True
                evidence = f"{relative}:{getattr(node, 'lineno', 0)}"
                if evidence not in item["evidence"]:
                    item["evidence"].append(evidence)
    return dict(usage)


def oracle_kind(
    path: str,
    facts: dict[str, Any],
    entries: dict[str, dict[str, Any]] | None = None,
) -> str | None:
    if path in set(facts.get("exceptions") or []):
        return "exception"
    if path in set(facts.get("classes") or []):
        return "class"
    if path in set(facts.get("modules") or []):
        return "module"
    if path in set(facts.get("functions") or []):
        owner_path = path.rsplit(".", 1)[0]
        owner = (entries or {}).get(owner_path)
        if isinstance(owner, dict) and owner.get("kind") == "class":
            return "method"
        return "function"
    return None


def inferred_kind(path: str, usage: dict[str, dict[str, Any]]) -> str:
    item = usage.get(path) or {}
    if item.get("class_checked"):
        return "class"
    if item.get("called"):
        return "callable"
    return "object"


def api_component_verdict(decision: dict[str, Any]) -> str:
    value = (decision.get("components") or {}).get("api_surface")
    return str(value.get("verdict")) if isinstance(value, dict) else str(value)


def task_candidates(
    task: dict[str, Any],
    decision: dict[str, Any],
    task_dir: Path,
) -> dict[str, Any]:
    metadata = load_json(task_dir / "metadata.json")
    required_api = copy.deepcopy((metadata.get("public_spec") or {}).get("required_api") or [])
    entries = {str(item["path"]): item for item in flatten(required_api) if isinstance(item.get("path"), str)}
    usage = ast_usage(task_dir)
    undeclared = {
        str(path)
        for path in task.get("undeclared_api_ids") or []
        if path not in STANDARD_MODULE_METADATA_REFS
    }
    inspect_paths = sorted(set(entries) | undeclared)
    oracle, oracle_error = HARDENER._oracle_signatures(task_dir, inspect_paths)
    signatures = oracle.get("signatures") or {}

    operations: list[dict[str, Any]] = []
    adjusted = copy.deepcopy(required_api)
    adjusted_entries = {
        str(item["path"]): item for item in flatten(adjusted) if isinstance(item.get("path"), str)
    }
    for path, entry in sorted(entries.items()):
        actual = oracle_kind(path, oracle, adjusted_entries)
        if actual and actual != entry.get("kind"):
            operations.append(
                {
                    "op": "replace_kind",
                    "api_path": path,
                    "old": entry.get("kind"),
                    "value": actual,
                    "confidence": "high",
                    "evidence": ["reference_solution_introspection"],
                }
            )
            adjusted_entries[path]["kind"] = actual
        signature = signatures.get(path)
        effective_kind = actual or entry.get("kind")
        if signature and effective_kind in {"class", "function", "method", "callable"}:
            if entry.get("signature") != signature:
                operations.append(
                    {
                        "op": "replace_signature",
                        "api_path": path,
                        "old": entry.get("signature"),
                        "value": signature,
                        "confidence": "high",
                        "evidence": ["reference_solution_introspection"],
                    }
                )

    for path in sorted(undeclared):
        kind = oracle_kind(path, oracle, adjusted_entries) or inferred_kind(path, usage)
        entry: dict[str, Any] = {"path": path, "kind": kind}
        if signatures.get(path) and kind in {"class", "function", "method", "callable"}:
            entry["signature"] = signatures[path]
        operations.append(
            {
                "op": "upsert_required_api",
                "api_path": path,
                "entry": entry,
                "confidence": "high" if oracle_kind(path, oracle, adjusted_entries) else "medium",
                "evidence": usage.get(path, {}).get("evidence") or ["machine_audit"],
            }
        )

    member_usage = HARDENER._hidden_member_usage(
        task_dir,
        adjusted,
        include_public=True,
    )
    for path, evidence in sorted(member_usage.items()):
        if path in entries or path in undeclared:
            continue
        operations.append(
            {
                "op": "upsert_required_api_member",
                "api_path": path,
                "owner": evidence.get("owner"),
                "entry": {"path": path, "kind": evidence.get("kind", "attribute")},
                "confidence": "medium",
                "evidence": evidence.get("nodeids") or [],
            }
        )

    deduped: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for operation in operations:
        key = (str(operation.get("op")), str(operation.get("api_path")))
        if key not in seen:
            deduped.append(operation)
            seen.add(key)
    return {
        "task_id": task["task_id"],
        "current_api_verdict": api_component_verdict(decision),
        "review_required": True,
        "oracle_error": oracle_error,
        "operations": deduped,
    }


def main() -> int:
    args = parse_args()
    audit = load_json(args.audit)
    decisions = load_decisions(args.decisions)
    suite = load_json(ROOT / "benchmark/selection/python200_suite.json")
    root = ROOT / str(suite["task_root"])
    requested = set(args.task_ids or [])
    tasks = []
    for task in audit.get("tasks") or []:
        task_id = str(task["task_id"])
        decision = decisions.get(task_id)
        if decision is None or api_component_verdict(decision) == "closed":
            continue
        if requested and task_id not in requested:
            continue
        tasks.append(task_candidates(task, decision, root / task_id))
    payload = {
        "schema_version": "featureliftbench.api_contract_patch_candidates.v1",
        "suite_id": suite.get("suite_id"),
        "generated_from_audit_at": audit.get("generated_at"),
        "task_count": len(tasks),
        "operation_count": sum(len(task["operations"]) for task in tasks),
        "tasks": tasks,
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != rendered:
            raise SystemExit("API patch candidates are stale")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(
        f"API patch candidates: tasks={payload['task_count']} "
        f"operations={payload['operation_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
