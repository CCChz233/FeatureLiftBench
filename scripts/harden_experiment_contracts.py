#!/usr/bin/env python3
"""Harden Python-main public contracts for evaluator-test-blind experiments.

The script does not invent new evaluator behavior.  It rewrites migrated generic
clauses using the task's existing included-behavior labels and public/hidden test
mapping names, fills callable signatures from the already-verified oracle
submission, regenerates TASK/spec hashes, and re-runs constitution validation
before writing.
"""

from __future__ import annotations

import argparse
import ast
import copy
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "harness"
if str(HARNESS) not in sys.path:
    sys.path.insert(0, str(HARNESS))

from featureliftbench.constitution_validate import validate_constitution
from featureliftbench.task_render import render_public_task
from featureliftbench.task_spec import sync_spec_hashes, write_metadata
from featureliftbench.task_spec_migrate import (
    _render_required_api_surface_test,
    _surface_test_nodeid,
    _sync_behavior_contract,
)


GENERIC_BEHAVIOR_MARKERS = (
    "preserves the corresponding upstream-observable result within the documented scope",
    "every declared required API path and member exists",
    "declared target API remains importable and preserves upstream-observable semantics",
)
CALLABLE_KINDS = frozenset({"class", "function", "method", "callable"})
IGNORED_TEST_NAME_PARTS = (
    "required api surface",
    "no import surface",
    "no upstream import surface",
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "tasks_root",
        nargs="?",
        type=Path,
        default=Path("benchmark/tasks"),
    )
    parser.add_argument(
        "--task-id",
        action="append",
        dest="task_ids",
        help="limit to a task id; repeatable",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="write validated metadata/TASK/behavior-contract changes",
    )
    parser.add_argument("--report", type=Path)
    return parser.parse_args()


def _flatten_api(entries: Any) -> list[dict[str, Any]]:
    flattened: list[dict[str, Any]] = []
    if not isinstance(entries, list):
        return flattened
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        flattened.append(entry)
        flattened.extend(_flatten_api(entry.get("members")))
    return flattened


def _oracle_dir(task_dir: Path) -> Path:
    candidates = (
        ROOT / "benchmark" / "submissions" / task_dir.name / "oracle",
        ROOT / "benchmark" / "staging" / task_dir.name / "reference_solution",
        ROOT / "benchmark" / "external50" / task_dir.name / "reference_solution",
    )
    return next((path for path in candidates if path.is_dir()), candidates[0])


def _stable_signature(value: str) -> str:
    value = re.sub(r" at 0x[0-9A-Fa-f]+", "", value)
    value = re.sub(r"<module '([^']+)' from '[^']+'>", r"<module '\1'>", value)
    value = re.sub(r"\bfeaturelifted(?:\.[A-Za-z_][A-Za-z0-9_]*)*\.", "", value)
    return value


def _oracle_signatures(
    task_dir: Path,
    paths: list[str],
) -> tuple[dict[str, Any], str | None]:
    oracle_dir = _oracle_dir(task_dir)
    if not oracle_dir.is_dir():
        return {}, f"missing oracle: {oracle_dir}"
    child = r'''
import importlib
import inspect
import json
import featurelifted

result = {}
for path in json.loads(__import__("os").environ["FLB_API_PATHS"]):
    suffix = path.removeprefix("featurelifted.")
    parts = suffix.split(".")
    try:
        value = featurelifted
        runtime_bound = False
        consumed = 0
        try:
            for part in parts:
                value = getattr(value, part)
            consumed = len(parts)
        except AttributeError:
            value = featurelifted
        if consumed != len(parts):
            for index in range(len(parts), 0, -1):
                module_name = "featurelifted." + ".".join(parts[:index])
                try:
                    value = importlib.import_module(module_name)
                    consumed = index
                    break
                except ModuleNotFoundError as exc:
                    if not isinstance(exc.name, str) or not module_name.startswith(exc.name):
                        raise
        remaining = parts[consumed:]
        for offset, part in enumerate(remaining):
            try:
                value = getattr(value, part)
            except AttributeError:
                if isinstance(value, type) and offset == len(remaining) - 1:
                    value = getattr(value(), part)
                    runtime_bound = True
                else:
                    raise
        is_exception = isinstance(value, type) and issubclass(value, BaseException)
        is_class = isinstance(value, type) and not is_exception
        is_module = inspect.ismodule(value)
        is_callable = callable(value)
        is_function = inspect.isfunction(value) or inspect.ismethod(value) or inspect.isbuiltin(value)
        try:
            signature = str(inspect.signature(value))
        except (TypeError, ValueError):
            if isinstance(value, type) and not is_exception:
                signature = str(inspect.signature(value.__new__))
            else:
                signature = None
        result[path] = {
            "signature": signature,
            "is_exception": is_exception,
            "is_class": is_class,
            "is_module": is_module,
            "is_callable": is_callable,
            "is_function": is_function,
            "runtime_bound": runtime_bound,
        }
    except Exception as exc:
        result[path] = {"error": f"{type(exc).__name__}: {exc}"}
print(json.dumps(result, sort_keys=True))
'''
    env = os.environ.copy()
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = (
        str(oracle_dir) if not existing else os.pathsep.join((str(oracle_dir), existing))
    )
    env["PYTHONHASHSEED"] = "0"
    env["FLB_API_PATHS"] = json.dumps(paths)
    completed = subprocess.run(
        [sys.executable, "-B", "-c", child],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=60,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        return {}, f"oracle introspection failed: {detail}"
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        return {}, f"oracle introspection returned invalid JSON: {exc}"
    signatures: dict[str, str] = {}
    exceptions: set[str] = set()
    classes: set[str] = set()
    modules: set[str] = set()
    callables: set[str] = set()
    functions: set[str] = set()
    runtime_bound: set[str] = set()
    for path, value in payload.items():
        if not isinstance(value, dict):
            continue
        if value.get("is_exception") is True:
            exceptions.add(path)
        if value.get("is_class") is True:
            classes.add(path)
        if value.get("is_module") is True:
            modules.add(path)
        if value.get("is_callable") is True:
            callables.add(path)
        if value.get("is_function") is True:
            functions.add(path)
        if value.get("runtime_bound") is True:
            runtime_bound.add(path)
        signature = value.get("signature")
        if isinstance(signature, str):
            signatures[path] = _stable_signature(signature)
    return {
        "signatures": signatures,
        "exceptions": sorted(exceptions),
        "classes": sorted(classes),
        "modules": sorted(modules),
        "callables": sorted(callables),
        "functions": sorted(functions),
        "runtime_bound": sorted(runtime_bound),
    }, None


def _test_name(nodeid: str) -> str | None:
    name = nodeid.rsplit("::", 1)[-1]
    if name.startswith("test_"):
        name = name[5:]
    phrase = name.replace("_", " ").strip()
    if not phrase or any(part in phrase for part in IGNORED_TEST_NAME_PARTS):
        return None
    phrase = re.sub(r"\bhidden\b|\bpublic\b", "", phrase)
    return re.sub(r"\s+", " ", phrase).strip()


def _mapped_observable_phrases(
    evaluation_spec: dict[str, Any],
) -> dict[str, list[str]]:
    by_behavior: dict[str, list[str]] = defaultdict(list)
    for key in ("public_test_mappings", "hidden_test_mappings"):
        for mapping in evaluation_spec.get(key) or []:
            if not isinstance(mapping, dict):
                continue
            phrase = _test_name(str(mapping.get("nodeid", "")))
            if phrase is None:
                continue
            for behavior_id in mapping.get("behavior_ids") or []:
                behavior_id = str(behavior_id)
                if phrase not in by_behavior[behavior_id]:
                    by_behavior[behavior_id].append(phrase)
    return dict(by_behavior)


def _explicit_surface_text(required_api: list[dict[str, Any]]) -> str:
    paths = [
        f"`{entry['path']}`"
        for entry in _flatten_api(required_api)
        if isinstance(entry.get("path"), str)
    ]
    if len(paths) > 12:
        shown = ", ".join(paths[:12]) + f", and {len(paths) - 12} listed members"
    else:
        shown = ", ".join(paths)
    return (
        "The package exposes the required task API paths "
        f"{shown} with the kinds and callable signatures listed in this contract."
    )


def _entry_by_path(required_api: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        str(entry["path"]): entry
        for entry in _flatten_api(required_api)
        if isinstance(entry.get("path"), str)
    }


def _expression_path(node: ast.expr, imported: dict[str, str]) -> str | None:
    if isinstance(node, ast.Name):
        return imported.get(node.id)
    if isinstance(node, ast.Attribute):
        prefix = _expression_path(node.value, imported)
        if prefix:
            return f"{prefix}.{node.attr}"
    return None


def _return_class_path(
    signature: str | None,
    class_by_leaf: dict[str, str],
) -> str | None:
    if not signature or "->" not in signature:
        return None
    annotation = signature.rsplit("->", 1)[1]
    for token in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", annotation):
        if token in class_by_leaf:
            return class_by_leaf[token]
    return None


def _hidden_member_usage(
    task_dir: Path,
    required_api: list[dict[str, Any]],
    *,
    include_public: bool = False,
) -> dict[str, dict[str, Any]]:
    entries = _entry_by_path(required_api)
    class_paths = {
        path for path, entry in entries.items() if entry.get("kind") == "class"
    }
    class_by_leaf = {path.rsplit(".", 1)[-1]: path for path in class_paths}
    callable_returns = {
        path: _return_class_path(
            str(entry.get("signature", "")),
            class_by_leaf,
        )
        for path, entry in entries.items()
        if entry.get("kind") in CALLABLE_KINDS
    }
    usage: dict[str, dict[str, Any]] = {}

    roots = [task_dir / "hidden_tests"]
    if include_public:
        roots.insert(0, task_dir / "public_tests")
    paths = sorted(
        path
        for root in roots
        if root.is_dir()
        for path in root.rglob("*.py")
    )
    for path in paths:
        if path.name == "test_required_api_surface.py":
            continue
        source = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        imported: dict[str, str] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and isinstance(node.module, str):
                if node.module == "featurelifted" or node.module.startswith(
                    "featurelifted."
                ):
                    for alias in node.names:
                        imported[alias.asname or alias.name] = (
                            f"{node.module}.{alias.name}"
                        )
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "featurelifted" or alias.name.startswith(
                        "featurelifted."
                    ):
                        imported[alias.asname or alias.name.split(".", 1)[0]] = (
                            alias.name
                        )

        tests: list[ast.FunctionDef | ast.AsyncFunctionDef] = []
        for node in tree.body:
            if isinstance(
                node,
                (ast.FunctionDef, ast.AsyncFunctionDef),
            ) and node.name.startswith("test_"):
                tests.append(node)
            elif isinstance(node, ast.ClassDef):
                tests.extend(
                    child
                    for child in node.body
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and child.name.startswith("test_")
                )
        relative = path.relative_to(task_dir).as_posix()
        for test in tests:
            nodeid = f"{relative}::{test.name}"
            local_types: dict[str, str] = {}
            assignments = [
                node
                for node in ast.walk(test)
                if isinstance(node, (ast.Assign, ast.AnnAssign))
            ]
            for _ in range(3):
                changed = False
                for assignment in assignments:
                    value = assignment.value
                    targets = (
                        assignment.targets
                        if isinstance(assignment, ast.Assign)
                        else [assignment.target]
                    )
                    inferred: str | None = None
                    if isinstance(value, ast.Call):
                        called_path = _expression_path(value.func, imported)
                        if called_path in class_paths:
                            inferred = called_path
                        elif called_path:
                            inferred = callable_returns.get(called_path)
                    elif isinstance(value, ast.Name):
                        inferred = local_types.get(value.id)
                    if inferred:
                        for target in targets:
                            if isinstance(target, ast.Name) and local_types.get(
                                target.id
                            ) != inferred:
                                local_types[target.id] = inferred
                                changed = True
                if not changed:
                    break
            for node in ast.walk(test):
                if (
                    isinstance(node, ast.Assert)
                    and isinstance(node.test, ast.Call)
                    and isinstance(node.test.func, ast.Name)
                    and node.test.func.id == "isinstance"
                    and len(node.test.args) == 2
                    and isinstance(node.test.args[0], ast.Name)
                ):
                    narrowed = _expression_path(node.test.args[1], imported)
                    if narrowed in class_paths:
                        local_types[node.test.args[0].id] = narrowed

            parents = {
                child: parent
                for parent in ast.walk(test)
                for child in ast.iter_child_nodes(parent)
            }
            for node in ast.walk(test):
                if not isinstance(node, ast.Attribute):
                    continue
                owner: str | None = None
                if isinstance(node.value, ast.Name):
                    owner = local_types.get(node.value.id)
                    imported_path = imported.get(node.value.id)
                    if imported_path in class_paths:
                        owner = imported_path
                elif isinstance(node.value, ast.Call):
                    constructed = _expression_path(node.value.func, imported)
                    if constructed in class_paths:
                        owner = constructed
                if owner not in class_paths:
                    continue
                member_path = f"{owner}.{node.attr}"
                called = (
                    isinstance(parents.get(node), ast.Call)
                    and parents[node].func is node
                )
                current = usage.setdefault(
                    member_path,
                    {
                        "owner": owner,
                        "kind": "method" if called else "attribute",
                        "nodeids": [],
                    },
                )
                if called:
                    current["kind"] = "method"
                if nodeid not in current["nodeids"]:
                    current["nodeids"].append(nodeid)
    return usage


def _add_hidden_members(
    required_api: list[dict[str, Any]],
    usage: dict[str, dict[str, Any]],
) -> list[str]:
    entries = _entry_by_path(required_api)
    added: list[str] = []
    for path, evidence in sorted(usage.items()):
        if path in entries:
            continue
        owner = entries.get(str(evidence.get("owner")))
        if owner is None or owner.get("kind") != "class":
            continue
        member = {
            "path": path,
            "kind": str(evidence.get("kind", "attribute")),
        }
        owner.setdefault("members", []).append(member)
        entries[path] = member
        added.append(path)
    return added


def _sync_api_coverage(
    evaluation_spec: dict[str, Any],
    required_api: list[dict[str, Any]],
    member_usage: dict[str, dict[str, Any]],
) -> None:
    existing = {
        str(item.get("path")): item
        for item in evaluation_spec.get("required_api_coverage") or []
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    }
    coverage: list[dict[str, Any]] = []
    for entry in _flatten_api(required_api):
        path = str(entry.get("path", ""))
        current = existing.get(path)
        evidence = member_usage.get(path, {}).get("nodeids") or []
        tests = list(evidence)
        if not tests and current is not None:
            tests = [
                str(nodeid)
                for nodeid in current.get("covered_by_tests") or []
                if isinstance(nodeid, str)
            ]
        if not tests:
            tests = [_surface_test_nodeid()]
        coverage.append({"path": path, "covered_by_tests": sorted(set(tests))})
    evaluation_spec["required_api_coverage"] = coverage


def _harden_behavior_texts(
    metadata: dict[str, Any],
) -> dict[str, str]:
    public_spec = metadata["public_spec"]
    evaluation_spec = metadata["evaluation_spec"]
    included = (
        metadata.get("feature", {}).get("included_behaviors", [])
        if isinstance(metadata.get("feature"), dict)
        else []
    )
    included = [str(item).strip().rstrip(".") for item in included if str(item).strip()]
    phrases = _mapped_observable_phrases(evaluation_spec)
    clause_kind_by_id = {
        str(item.get("behavior_id")): str(item.get("clause_kind", "included_behavior"))
        for item in evaluation_spec.get("public_clauses") or []
        if isinstance(item, dict)
    }
    required_api = [
        item
        for item in public_spec.get("required_api") or []
        if isinstance(item, dict)
    ]
    hardened: dict[str, str] = {}
    included_index = 0
    for behavior in public_spec.get("behaviors") or []:
        if not isinstance(behavior, dict):
            continue
        behavior_id = str(behavior.get("id", ""))
        text = str(behavior.get("text", "")).strip()
        kind = clause_kind_by_id.get(behavior_id, "included_behavior")
        if kind == "api_surface":
            hardened[behavior_id] = _explicit_surface_text(required_api)
            continue
        base = included[included_index] if included_index < len(included) else text
        included_index += 1
        is_generic = any(marker in text for marker in GENERIC_BEHAVIOR_MARKERS)
        if not is_generic:
            continue
        sentence = (
            "The extracted feature must support this observable behavior: "
            f"{base}."
        )
        observed = phrases.get(behavior_id, [])
        if observed:
            sentence += " Required observable cases include " + "; ".join(observed) + "."
        hardened[behavior_id] = sentence
    return hardened


def harden_task(task_dir: Path, *, write: bool) -> dict[str, Any]:
    metadata_path = task_dir / "metadata.json"
    original = json.loads(metadata_path.read_text(encoding="utf-8"))
    if original.get("spec_status") != "compliant":
        return {
            "task_id": task_dir.name,
            "status": "skipped",
            "reason": "spec_status is not compliant",
        }
    metadata = copy.deepcopy(original)
    public_spec = metadata.get("public_spec")
    evaluation_spec = metadata.get("evaluation_spec")
    if not isinstance(public_spec, dict) or not isinstance(evaluation_spec, dict):
        return {
            "task_id": task_dir.name,
            "status": "failed",
            "reason": "missing public_spec/evaluation_spec",
        }

    api_entries = _flatten_api(public_spec.get("required_api"))
    callable_paths = [
        str(entry["path"])
        for entry in api_entries
        if entry.get("kind") in CALLABLE_KINDS
        and isinstance(entry.get("path"), str)
    ]
    introspection, introspection_error = _oracle_signatures(task_dir, callable_paths)
    signatures = introspection.get("signatures", {})
    exception_paths = set(introspection.get("exceptions", []))
    runtime_bound_paths = set(introspection.get("runtime_bound", []))
    signature_updates = 0
    unresolved_callables: list[str] = []
    for entry in api_entries:
        path = str(entry.get("path", ""))
        if entry.get("kind") not in CALLABLE_KINDS:
            continue
        if path in exception_paths:
            entry["kind"] = "exception"
            entry.pop("signature", None)
            continue
        signature = signatures.get(path)
        if signature:
            if entry.get("signature") != signature:
                entry["signature"] = signature
                signature_updates += 1
            if path in runtime_bound_paths:
                entry["runtime_bound"] = True
        elif not str(entry.get("signature", "")).strip():
            unresolved_callables.append(path)

    required_api = [
        item
        for item in public_spec.get("required_api") or []
        if isinstance(item, dict)
    ]
    member_usage = _hidden_member_usage(task_dir, required_api)
    added_members = _add_hidden_members(required_api, member_usage)
    if added_members:
        member_introspection, member_error = _oracle_signatures(
            task_dir,
            [
                path
                for path in added_members
                if member_usage.get(path, {}).get("kind") == "method"
            ],
        )
        if member_error and not introspection_error:
            introspection_error = member_error
        member_signatures = member_introspection.get("signatures", {})
        member_runtime_bound = set(member_introspection.get("runtime_bound", []))
        entries = _entry_by_path(required_api)
        for path in added_members:
            signature = member_signatures.get(path)
            if signature:
                entries[path]["signature"] = signature
                signature_updates += 1
                if path in member_runtime_bound:
                    entries[path]["runtime_bound"] = True
            elif entries[path].get("kind") == "method":
                unresolved_callables.append(path)
    _sync_api_coverage(evaluation_spec, required_api, member_usage)

    text_updates = _harden_behavior_texts(metadata)
    for behavior in public_spec.get("behaviors") or []:
        if isinstance(behavior, dict) and str(behavior.get("id")) in text_updates:
            behavior["text"] = text_updates[str(behavior["id"])]
    for clause in evaluation_spec.get("public_clauses") or []:
        if isinstance(clause, dict) and str(clause.get("behavior_id")) in text_updates:
            clause["text"] = text_updates[str(clause["behavior_id"])]

    public_spec["public_vs_hidden_note"] = (
        "Benchmark evaluator tests remain private. Each evaluator test maps to the "
        "public behaviors above and only deepens examples, boundaries, or combinations "
        "within those declared behaviors."
    )
    evaluation_spec["experiment_contract_hardening"] = {
        "method": "existing_contract_and_test_mapping_review",
        "oracle_signature_source": "benchmark/submissions/<task_id>/oracle",
    }

    surface_source = _render_required_api_surface_test(
        required_api,
        task_id=task_dir.name,
    )
    surface_path = task_dir / "hidden_tests" / "test_required_api_surface.py"
    surface_changed = (
        not surface_path.is_file()
        or surface_path.read_text(encoding="utf-8") != surface_source
    )
    task_markdown = render_public_task(metadata)
    task_path = task_dir / "TASK.md"
    task_changed = (
        not task_path.is_file()
        or task_path.read_text(encoding="utf-8") != task_markdown
    )
    changed = metadata != original or surface_changed or task_changed
    if changed:
        metadata["task_revision"] = int(original.get("task_revision", 0) or 0) + 1
        task_markdown = render_public_task(metadata)
    metadata = sync_spec_hashes(metadata, task_markdown)
    changed = changed or metadata != original
    errors = validate_constitution(
        task_dir,
        metadata,
        task_markdown=task_markdown,
        test_source_overrides={
            "hidden_tests/test_required_api_surface.py": surface_source,
        },
    )
    if errors:
        return {
            "task_id": task_dir.name,
            "status": "failed",
            "reason": "constitution validation failed",
            "errors": errors,
            "introspection_error": introspection_error,
            "unresolved_callables": unresolved_callables,
        }
    if write and changed:
        write_metadata(task_dir, metadata)
        task_path.write_text(task_markdown, encoding="utf-8")
        surface_path.write_text(
            surface_source,
            encoding="utf-8",
        )
        _sync_behavior_contract(task_dir, evaluation_spec, task_markdown)
    return {
        "task_id": task_dir.name,
        "status": "changed" if changed else "unchanged",
        "written": bool(write and changed),
        "signature_updates": signature_updates,
        "behavior_updates": len(text_updates),
        "member_updates": len(added_members),
        "added_members": added_members,
        "surface_updated": surface_changed,
        "introspection_error": introspection_error,
        "unresolved_callables": unresolved_callables,
        "spec_hash": metadata.get("spec_hash"),
        "task_revision": metadata.get("task_revision"),
    }


def main() -> int:
    args = _parse_args()
    selected = set(args.task_ids or [])
    task_dirs = sorted(
        path
        for path in args.tasks_root.iterdir()
        if path.is_dir()
        and (path / "metadata.json").is_file()
        and (not selected or path.name in selected)
    )
    reports = [harden_task(task_dir, write=args.write) for task_dir in task_dirs]
    summary = {
        "total": len(reports),
        "changed": sum(item["status"] == "changed" for item in reports),
        "unchanged": sum(item["status"] == "unchanged" for item in reports),
        "failed": sum(item["status"] == "failed" for item in reports),
        "skipped": sum(item["status"] == "skipped" for item in reports),
        "written": sum(item.get("written") is True for item in reports),
        "signature_updates": sum(int(item.get("signature_updates", 0)) for item in reports),
        "behavior_updates": sum(int(item.get("behavior_updates", 0)) for item in reports),
        "member_updates": sum(int(item.get("member_updates", 0)) for item in reports),
        "unresolved_callables": sum(
            len(item.get("unresolved_callables") or []) for item in reports
        ),
        "introspection_errors": sum(
            bool(item.get("introspection_error")) for item in reports
        ),
    }
    payload = {
        "schema_version": "featureliftbench.contract_hardening.v1",
        "write": args.write,
        "summary": summary,
        "tasks": reports,
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"wrote {args.report}")
    print(json.dumps(summary, sort_keys=True))
    return 1 if summary["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
