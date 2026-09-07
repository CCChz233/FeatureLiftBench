#!/usr/bin/env python3
"""L0 screen: public tests vs metadata required_api / public clauses."""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TASK_ROOTS = [
    ROOT / "benchmark/python200_hard_tasks",
    ROOT / "benchmark/tasks",
    ROOT / "benchmark/hard50",
]

SKIP_NAMES = {
    "True",
    "False",
    "None",
    "len",
    "set",
    "list",
    "dict",
    "str",
    "int",
    "bool",
    "tuple",
    "type",
    "isinstance",
    "hasattr",
    "getattr",
    "setattr",
    "print",
    "range",
    "enumerate",
    "zip",
    "sorted",
    "all",
    "any",
    "min",
    "max",
    "sum",
    "open",
    "Path",
    "pytest",
    "raises",
    "warns",
    "approx",
    "tmp_path",
    "monkeypatch",
    "featurelifted",
}


def find_task(task_id: str) -> Path:
    for root in TASK_ROOTS:
        path = root / task_id
        if (path / "metadata.json").is_file():
            return path
    raise FileNotFoundError(f"task not found: {task_id}")


def required_leaves(meta: dict) -> list[str]:
    return sorted({path.rsplit(".", 1)[-1] for path in required_paths(meta)})


def required_paths(meta: dict) -> list[str]:
    out: list[str] = []

    def walk(items: object) -> None:
        if not items:
            return
        if isinstance(items, list):
            for item in items:
                walk(item)
            return
        if isinstance(items, dict):
            path = items.get("path")
            if path:
                out.append(str(path))
            walk(items.get("members"))
            return
        if isinstance(items, str):
            out.append(items)

    walk((meta.get("public_spec") or {}).get("required_api") or [])
    return out


def clause_texts(task_dir: Path) -> list[dict[str, str]]:
    path = task_dir / "evaluation" / "behavior_contract.json"
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for clause in data.get("public_clauses") or []:
        if isinstance(clause, dict):
            rows.append(
                {
                    "id": str(clause.get("behavior_id") or ""),
                    "text": str(clause.get("text") or "")[:240],
                }
            )
    return rows


def function_names(src: str, func_name: str | None) -> dict[str, list[str]]:
    try:
        tree = ast.parse(src)
    except SyntaxError as exc:
        return {"__syntax_error__": [str(exc)]}
    found: dict[str, list[str]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        if func_name and node.name != func_name:
            continue
        names: list[str] = []
        for child in ast.walk(node):
            if isinstance(child, ast.Attribute):
                names.append(child.attr)
            elif isinstance(child, ast.Name):
                names.append(child.id)
        found[node.name] = sorted(set(names))
        if func_name:
            break
    return found


def extra_vs_required(used: list[str], leaves: set[str]) -> list[str]:
    extra = []
    for name in used:
        if name in leaves or name in SKIP_NAMES:
            continue
        if name.startswith("test_") or name.startswith("_"):
            continue
        extra.append(name)
    return extra


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task_id")
    parser.add_argument("--test-name", default="")
    parser.add_argument("--tasks-root", type=Path)
    args = parser.parse_args()
    task_dir = args.tasks_root / args.task_id if args.tasks_root else find_task(args.task_id)
    meta = json.loads((task_dir / "metadata.json").read_text(encoding="utf-8"))
    leaves = required_leaves(meta)
    leaf_set = set(leaves)
    public_dir = task_dir / "public_tests"
    tests: dict[str, object] = {}
    undeclared: dict[str, list[str]] = {}
    if public_dir.is_dir():
        src = "\n".join(
            path.read_text(encoding="utf-8", errors="replace")
            for path in sorted(public_dir.rglob("*.py"))
        )
        used = function_names(src, args.test_name or None)
        tests = used
        for name, names in used.items():
            extra = extra_vs_required(names, leaf_set)
            if extra:
                undeclared[name] = extra
    report = {
        "task_id": args.task_id,
        "task_dir": str(task_dir.relative_to(ROOT)) if ROOT in task_dir.parents else str(task_dir),
        "required_api": required_paths(meta),
        "required_leaves": leaves,
        "public_clauses": clause_texts(task_dir),
        "public_test_names_used": tests,
        "names_not_in_required_api": undeclared,
        "note": (
            "names_not_in_required_api is a heuristic. Confirm against the first "
            "failing test: locals and helper names are not undeclared APIs. "
            "A real defect is a public test calling a method/attribute/output "
            "marker that is absent from required_api and public clauses."
        ),
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
