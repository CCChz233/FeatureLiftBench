#!/usr/bin/env python3
"""Stratified provenance audit for non-structural exact RSG edges."""

from __future__ import annotations

import argparse
import ast
import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Any

from featureliftbench.repo_graph import GraphBuilder


DEFAULT_TASKS = (
    "sqlparse__token_tree_core__001",
    "pydantic_settings__env_source_core__001",
    "stevedore__extension_manager_core__hard3_001",
    "jinja2__loader_inheritance_core__001",
    "pytest__marker_registry_core__hard3_001",
    "tomlkit__roundtrip_document__001",
    "click__option_parser__001",
    "marshmallow__schema_core__001",
    "distlib__wheel_metadata_core__hard3_001",
    "configobj__roundtrip_config_core__001",
)

SAMPLE_QUOTAS = {
    "IMPORTS_MODULE": 34,
    "MUTABLE_GLOBAL": 23,
    "LOADS_RESOURCE": 20,
    "READS_ENV": 15,
    "READS_CWD": 8,
    "WRITES_CWD": 4,
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks-root", type=Path, default=Path("benchmark/tasks"))
    parser.add_argument("--task-id", action="append")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--seed", type=int, default=20260722)
    args = parser.parse_args(argv)
    task_ids = tuple(args.task_id) if args.task_id else DEFAULT_TASKS
    report = audit_exact_edges(args.tasks_root, task_ids, seed=args.seed)
    encoded = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")
    precision = report["summary"]["validated_precision"]
    return 0 if precision is not None and precision >= 0.95 else 1


def audit_exact_edges(tasks_root: Path, task_ids: tuple[str, ...], *, seed: int) -> dict[str, Any]:
    candidates: dict[str, list[dict[str, Any]]] = defaultdict(list)
    population: dict[str, int] = defaultdict(int)
    builder = GraphBuilder()
    for task_id in task_ids:
        repository = tasks_root / task_id / "repo"
        snapshot = builder.build(repository, languages=["python"])
        nodes = {node.id: node for node in snapshot.nodes}
        inventory = SourceInventory(repository)
        for edge in snapshot.edges:
            if edge.resolution != "exact" or edge.kind in {"CONTAINS", "DEFINES"}:
                continue
            population[edge.kind] += 1
            source = nodes[edge.source]
            target = nodes.get(edge.target) if edge.target is not None else None
            verdict, reason, excerpt = inventory.validate(edge, source, target)
            evidence_span = target.span if edge.kind == "MUTABLE_GLOBAL" and target else source.span
            evidence_path = str(edge.attributes.get("path") or (evidence_span.path if evidence_span else ""))
            evidence_line = edge.attributes.get("line") or (
                evidence_span.start_line if evidence_span else None
            )
            candidates[edge.kind].append(
                {
                    "task_id": task_id,
                    "edge_id": edge.id,
                    "kind": edge.kind,
                    "source": source.stable_id,
                    "target": target.stable_id if target else None,
                    "path": evidence_path,
                    "line": evidence_line,
                    "expression": edge.attributes.get("target_expression")
                    or edge.attributes.get("target_module"),
                    "excerpt": excerpt,
                    "validated": verdict,
                    "reason": reason,
                }
            )

    randomizer = random.Random(seed)
    samples: list[dict[str, Any]] = []
    for kind, quota in SAMPLE_QUOTAS.items():
        pool = sorted(
            candidates.get(kind, []),
            key=lambda item: (item["task_id"], item["path"], item.get("line") or 0, item["edge_id"]),
        )
        randomizer.shuffle(pool)
        samples.extend(pool[:quota])
    samples.sort(key=lambda item: (item["kind"], item["task_id"], item["edge_id"]))
    validated = sum(bool(sample["validated"]) for sample in samples)
    precision = round(validated / len(samples), 6) if samples else None
    by_kind: dict[str, dict[str, Any]] = {}
    for kind in SAMPLE_QUOTAS:
        selected = [sample for sample in samples if sample["kind"] == kind]
        passed = sum(bool(sample["validated"]) for sample in selected)
        by_kind[kind] = {
            "population": population.get(kind, 0),
            "sampled": len(selected),
            "validated": passed,
            "precision": round(passed / len(selected), 6) if selected else None,
        }
    return {
        "schema_version": "featureliftbench.repo_graph.exact_edge_audit.v1",
        "method": {
            "tasks": list(task_ids),
            "seed": seed,
            "scope": "non-structural exact edges",
            "note": (
                "Validation uses an independent Python AST inventory for imports and module "
                "assignments, plus source excerpts for explicit environment/CWD/resource cues. "
                "It verifies source provenance, not runtime causal necessity."
            ),
        },
        "summary": {
            "population": sum(population.values()),
            "sampled": len(samples),
            "validated": validated,
            "validated_precision": precision,
            "by_kind": by_kind,
            "unsupported_exact_kinds": sorted(set(population) - set(SAMPLE_QUOTAS)),
        },
        "samples": samples,
    }


class SourceInventory:
    def __init__(self, repository: Path) -> None:
        self.repository = repository
        self.imports: set[tuple[str, str]] = set()
        self.module_globals: set[tuple[str, str]] = set()
        self.mutable_globals: set[tuple[str, str]] = set()
        self.sources: dict[str, str] = {}
        for path in sorted(repository.rglob("*.py")):
            relative = path.relative_to(repository).as_posix()
            try:
                source = path.read_text(encoding="utf-8")
                tree = ast.parse(source, filename=relative)
            except (OSError, SyntaxError, UnicodeDecodeError):
                continue
            self.sources[relative] = source
            for statement in tree.body:
                if isinstance(statement, ast.Import):
                    self.imports.update((relative, alias.name) for alias in statement.names)
                elif isinstance(statement, ast.ImportFrom):
                    module = "." * statement.level + (statement.module or "")
                    if module:
                        self.imports.add((relative, module))
                elif isinstance(statement, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                    for name in assignment_names(statement):
                        self.module_globals.add((relative, name))
                        if assignment_is_mutable_literal(statement):
                            self.mutable_globals.add((relative, name))
            for statement in ast.walk(tree):
                if isinstance(statement, ast.Import):
                    self.imports.update((relative, alias.name) for alias in statement.names)
                elif isinstance(statement, ast.ImportFrom):
                    module = "." * statement.level + (statement.module or "")
                    if module:
                        self.imports.add((relative, module))

    def validate(self, edge: Any, source: Any, target: Any) -> tuple[bool, str, str]:
        evidence_span = target.span if edge.kind == "MUTABLE_GLOBAL" and target else source.span
        path = str(edge.attributes.get("path") or (evidence_span.path if evidence_span else ""))
        line = int(edge.attributes.get("line") or (evidence_span.start_line if evidence_span else 1))
        excerpt = self.excerpt(path, line)
        if edge.kind == "IMPORTS_MODULE":
            module = str(edge.attributes.get("target_module", ""))
            valid = (path, module) in self.imports
            return valid, "AST import target matches" if valid else "AST import target missing", excerpt
        if edge.kind == "MUTABLE_GLOBAL":
            valid = target is not None and (target.span.path, target.name) in self.mutable_globals
            return valid, "AST mutable literal assignment matches" if valid else "mutable assignment missing", excerpt
        if edge.kind == "READS_ENV":
            valid = target is not None and (
                "os.getenv" in excerpt or "os.environ" in excerpt
            ) and target.name in excerpt
            return valid, "explicit environment key matches" if valid else "environment key not proven", excerpt
        if edge.kind in {"READS_CWD", "WRITES_CWD"}:
            expected = "getcwd" if edge.kind == "READS_CWD" else "chdir"
            if edge.kind == "READS_CWD" and "Path.cwd" in excerpt:
                expected = "Path.cwd"
            valid = target is not None and target.kind == "working_directory" and expected in excerpt
            return valid, "explicit CWD operation matches" if valid else "CWD operation not proven", excerpt
        if edge.kind == "LOADS_RESOURCE":
            valid = target is not None and target.kind == "resource" and "__file__" in excerpt
            return valid, "explicit __file__ resource matches" if valid else "resource cue not proven", excerpt
        return False, f"unsupported exact kind: {edge.kind}", excerpt

    def excerpt(self, path: str, line: int) -> str:
        source = self.sources.get(path, "")
        lines = source.splitlines()
        if not lines:
            return ""
        start = max(0, line - 2)
        end = min(len(lines), line + 1)
        return " ".join(part.strip() for part in lines[start:end])[:500]


def assignment_names(statement: ast.Assign | ast.AnnAssign | ast.AugAssign) -> set[str]:
    targets: list[ast.expr]
    if isinstance(statement, ast.Assign):
        targets = list(statement.targets)
    else:
        targets = [statement.target]
    names: set[str] = set()
    stack = targets[:]
    while stack:
        target = stack.pop()
        if isinstance(target, ast.Name):
            names.add(target.id)
        elif isinstance(target, (ast.Tuple, ast.List)):
            stack.extend(target.elts)
    return names


def assignment_is_mutable_literal(statement: ast.Assign | ast.AnnAssign | ast.AugAssign) -> bool:
    if isinstance(statement, ast.Assign):
        value = statement.value
    elif isinstance(statement, ast.AnnAssign):
        value = statement.value
    else:
        return False
    return isinstance(
        value,
        (
            ast.Dict,
            ast.DictComp,
            ast.List,
            ast.ListComp,
            ast.Set,
            ast.SetComp,
        ),
    )


if __name__ == "__main__":
    raise SystemExit(main())
