#!/usr/bin/env python3
"""Audit RSG capture quality, portability, and performance across Python-150."""

from __future__ import annotations

import argparse
import ast
import json
import math
import resource
import statistics
import subprocess
import sys
import time
import warnings
from pathlib import Path
from typing import Any

from featureliftbench.repo_graph import GraphBuilder, GraphQueryEngine


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--tasks-root",
        type=Path,
        default=Path("benchmark/tasks"),
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--task-limit", type=int)
    parser.add_argument("--determinism-samples", type=int, default=5)
    args = parser.parse_args(argv)

    task_dirs = sorted(
        path
        for path in args.tasks_root.iterdir()
        if path.is_dir() and (path / "repo").is_dir() and (path / "metadata.json").is_file()
    )
    if args.task_limit is not None:
        task_dirs = task_dirs[: args.task_limit]

    report = audit_tasks(task_dirs, determinism_samples=args.determinism_samples)
    encoded = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
        print(f"wrote {args.output}", file=sys.stderr)
    else:
        print(encoded, end="")
    return 0 if report["summary"]["build_failures"] == 0 else 1


def audit_tasks(task_dirs: list[Path], *, determinism_samples: int) -> dict[str, Any]:
    builder = GraphBuilder()
    task_results: list[dict[str, Any]] = []
    definition_expected = 0
    definition_found = 0
    import_expected = 0
    import_found = 0
    entrypoint_expected = 0
    entrypoint_mapped = 0
    build_seconds: list[float] = []
    query_seconds: list[float] = []
    failures: list[dict[str, str]] = []

    for index, task_dir in enumerate(task_dirs):
        repository = task_dir / "repo"
        metadata = json.loads((task_dir / "metadata.json").read_text(encoding="utf-8"))
        started = time.perf_counter()
        try:
            snapshot = builder.build(repository, languages=["python"])
        except Exception as exc:  # noqa: BLE001 - the audit must report every task failure.
            failures.append({"task_id": task_dir.name, "error": f"{type(exc).__name__}: {exc}"})
            continue
        build_elapsed = time.perf_counter() - started
        build_seconds.append(build_elapsed)
        engine = GraphQueryEngine(snapshot)
        query_started = time.perf_counter()
        engine.bootstrap(max_nodes=30)
        query_seconds.append(time.perf_counter() - query_started)

        ast_definitions, ast_imports, ast_errors = ast_inventory(repository)
        graph_definitions = {
            (node.span.path, node.span.start_line, node.name)
            for node in snapshot.nodes
            if node.kind in {"class", "function", "method"} and node.span is not None
        }
        graph_imports = {
            (str(edge.attributes.get("path", "")), str(edge.attributes.get("target_module", "")))
            for edge in snapshot.edges
            if edge.kind == "IMPORTS_MODULE"
        }
        captured_definitions = ast_definitions & graph_definitions
        captured_imports = ast_imports & graph_imports
        definition_expected += len(ast_definitions)
        definition_found += len(captured_definitions)
        import_expected += len(ast_imports)
        import_found += len(captured_imports)

        entrypoints = metadata.get("feature", {}).get("source_entrypoints", [])
        mapped = sum(entrypoint_is_mapped(str(entrypoint), engine) for entrypoint in entrypoints)
        entrypoint_expected += len(entrypoints)
        entrypoint_mapped += mapped
        serialized = json.dumps(snapshot.to_dict(), ensure_ascii=False, sort_keys=True)
        snapshot_json_bytes = len(serialized.encode("utf-8"))
        path_leak = str(repository.resolve()) in serialized
        deterministic = None
        if index < determinism_samples:
            rebuilt = builder.build(repository, languages=["python"])
            deterministic = (
                rebuilt.manifest["snapshot_id"] == snapshot.manifest["snapshot_id"]
                and rebuilt.manifest["graph_hash"] == snapshot.manifest["graph_hash"]
            )
        task_results.append(
            {
                "task_id": task_dir.name,
                "build_seconds": round(build_elapsed, 6),
                "nodes": len(snapshot.nodes),
                "edges": len(snapshot.edges),
                "snapshot_json_bytes": snapshot_json_bytes,
                "unresolved_edges": snapshot.manifest["counts"]["unresolved_edges"],
                "parse_error_files": snapshot.manifest["counts"]["parse_error_files"],
                "ast_parse_error_files": ast_errors,
                "definition_expected": len(ast_definitions),
                "definition_found": len(captured_definitions),
                "import_expected": len(ast_imports),
                "import_found": len(captured_imports),
                "entrypoint_expected": len(entrypoints),
                "entrypoint_mapped": mapped,
                "absolute_path_leak": path_leak,
                "deterministic": deterministic,
            }
        )

    largest = sorted(task_results, key=lambda result: result["nodes"], reverse=True)[:3]
    peak_rss_samples = [
        measure_snapshot_peak_rss(
            next(task_dir / "repo" for task_dir in task_dirs if task_dir.name == result["task_id"])
        )
        for result in largest
    ]
    summary = {
        "tasks_requested": len(task_dirs),
        "tasks_built": len(task_results),
        "build_failures": len(failures),
        "tasks_with_tree_sitter_parse_errors": sum(
            result["parse_error_files"] > 0 for result in task_results
        ),
        "tree_sitter_parse_error_files": sum(
            result["parse_error_files"] for result in task_results
        ),
        "definition_capture_recall": ratio(definition_found, definition_expected),
        "definition_found": definition_found,
        "definition_expected": definition_expected,
        "import_capture_recall": ratio(import_found, import_expected),
        "import_found": import_found,
        "import_expected": import_expected,
        "entrypoint_mapping_rate": ratio(entrypoint_mapped, entrypoint_expected),
        "entrypoint_mapped": entrypoint_mapped,
        "entrypoint_expected": entrypoint_expected,
        "absolute_path_leaks": sum(result["absolute_path_leak"] for result in task_results),
        "determinism_failures": sum(result["deterministic"] is False for result in task_results),
        "build_seconds_median": rounded_stat(build_seconds, statistics.median),
        "build_seconds_p95": rounded_percentile(build_seconds, 0.95),
        "build_seconds_max": round(max(build_seconds), 6) if build_seconds else None,
        "warm_query_seconds_p95": rounded_percentile(query_seconds, 0.95),
        "max_nodes": max((result["nodes"] for result in task_results), default=0),
        "max_edges": max((result["edges"] for result in task_results), default=0),
        "max_snapshot_json_bytes": max(
            (result["snapshot_json_bytes"] for result in task_results), default=0
        ),
        "snapshot_peak_rss_bytes_max": max(peak_rss_samples, default=None),
        "snapshot_peak_rss_samples": peak_rss_samples,
        "audit_process_max_rss_bytes": rss_bytes(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss),
    }
    return {
        "schema_version": "featureliftbench.repo_graph.audit.v1",
        "summary": summary,
        "failures": failures,
        "tasks": task_results,
    }


def ast_inventory(repository: Path) -> tuple[set[tuple[str, int, str]], set[tuple[str, str]], int]:
    definitions: set[tuple[str, int, str]] = set()
    imports: set[tuple[str, str]] = set()
    errors = 0
    for path in sorted(repository.rglob("*.py")):
        if any(part in {".git", ".venv", "venv", "__pycache__"} for part in path.parts):
            continue
        relative = path.relative_to(repository).as_posix()
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", SyntaxWarning)
                tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative)
        except (OSError, SyntaxError, UnicodeDecodeError):
            errors += 1
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                definitions.add((relative, node.lineno, node.name))
            elif isinstance(node, ast.Import):
                imports.update((relative, alias.name) for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                module = "." * node.level + (node.module or "")
                if module:
                    imports.add((relative, module))
    return definitions, imports, errors


def entrypoint_is_mapped(entrypoint: str, engine: GraphQueryEngine) -> bool:
    symbol = entrypoint.rsplit(".", 1)[-1]
    matches = engine.search(symbol, limit=20)["matches"]
    package = entrypoint.split(".", 1)[0]
    plausible = [
        match
        for match in matches
        if match["name"].lstrip("_") == symbol.lstrip("_")
        and (
            match["qualified_name"] == entrypoint
            or match["qualified_name"].startswith(f"{package}.")
        )
    ]
    return bool(plausible)


def measure_snapshot_peak_rss(repository: Path) -> int:
    code = (
        "import resource,sys; from pathlib import Path; "
        "from featureliftbench.repo_graph import GraphBuilder,GraphQueryEngine; "
        "snapshot=GraphBuilder().build(Path(sys.argv[1]),languages=['python']); "
        "GraphQueryEngine(snapshot).bootstrap(max_nodes=30); "
        "print(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)"
    )
    completed = subprocess.run(
        [sys.executable, "-c", code, str(repository)],
        check=True,
        capture_output=True,
        text=True,
    )
    return rss_bytes(int(completed.stdout.strip()))


def rss_bytes(raw_value: int) -> int:
    # macOS reports bytes; Linux and most BSDs report KiB.
    return raw_value if sys.platform == "darwin" else raw_value * 1024


def ratio(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator, 6) if denominator else None


def rounded_stat(values: list[float], function: Any) -> float | None:
    return round(float(function(values)), 6) if values else None


def rounded_percentile(values: list[float], percentile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, math.ceil(percentile * len(ordered)) - 1)
    return round(ordered[index], 6)


if __name__ == "__main__":
    raise SystemExit(main())
