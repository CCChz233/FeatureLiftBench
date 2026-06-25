#!/usr/bin/env python3
"""Audit metadata.output.import against featurelifted imports in task tests."""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "harness") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "harness"))

from featureliftbench.paths import TASKS_DIR


def _collect_imports_from_file(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    found: set[str] = set()
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return found

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "featurelifted" or alias.name.startswith("featurelifted."):
                    found.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module and (
                node.module == "featurelifted" or node.module.startswith("featurelifted.")
            ):
                module = node.module
                for alias in node.names:
                    if alias.name == "*":
                        found.add(f"{module}.*")
                    else:
                        name = alias.name
                        if module == "featurelifted":
                            found.add(name)
                        else:
                            found.add(f"{module}.{name}")
    return found


def _collect_test_imports(task_dir: Path) -> set[str]:
    imports: set[str] = set()
    for subdir in ("public_tests", "hidden_tests"):
        tests_root = task_dir / subdir
        if not tests_root.is_dir():
            continue
        for path in tests_root.rglob("*.py"):
            imports.update(_collect_imports_from_file(path))
    return imports


def _parse_output_import(import_line: str) -> set[str]:
    """Best-effort parse of metadata output.import into referenced symbols."""
    symbols: set[str] = set()
    if not import_line.strip():
        return symbols

    for part in re.split(r";|\n", import_line):
        part = part.strip()
        if not part:
            continue
        if part.startswith("import featurelifted"):
            match_as = re.match(r"^import featurelifted(?:\s+as\s+(\w+))?", part)
            symbols.add("featurelifted")
            if match_as and match_as.group(1):
                symbols.add(match_as.group(1))
            continue
        match = re.match(r"^from\s+(featurelifted(?:\.[\w.]+)?)\s+import\s+(.+)$", part)
        if not match:
            continue
        module, names = match.group(1), match.group(2)
        for chunk in names.split(","):
            chunk = chunk.strip()
            if not chunk:
                continue
            if chunk == "*":
                symbols.add(f"{module}.*")
                continue
            name = chunk.split(" as ")[0].strip()
            alias = chunk.split(" as ")[1].strip() if " as " in chunk else None
            if module == "featurelifted":
                symbols.add(name)
                if alias:
                    symbols.add(alias)
            else:
                symbols.add(f"{module}.{name}")
                if alias:
                    symbols.add(alias)
    return symbols


def _missing_in_output(test_imports: set[str], output_imports: set[str]) -> list[str]:
    missing: list[str] = []
    for symbol in sorted(test_imports):
        if symbol in output_imports:
            continue
        if symbol == "featurelifted" and "featurelifted" in output_imports:
            continue
        if symbol.startswith("featurelifted.") and symbol.split(".", 1)[1] in output_imports:
            continue
        module_prefix = ".".join(symbol.split(".")[:-1]) if "." in symbol else ""
        if module_prefix and f"{module_prefix}.*" in output_imports:
            continue
        # Module alias used in tests (e.g. expr_mod for featurelifted.expression).
        if "." not in symbol and f"featurelifted.{symbol}" in output_imports:
            continue
        missing.append(symbol)
    return missing


def audit_task(task_dir: Path) -> dict[str, object]:
    metadata_path = task_dir / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    output = metadata.get("output", {})
    import_line = output.get("import", "") if isinstance(output, dict) else ""

    test_imports = _collect_test_imports(task_dir)
    output_imports = _parse_output_import(str(import_line))
    missing = _missing_in_output(test_imports, output_imports)

    return {
        "task_id": task_dir.name,
        "test_imports": sorted(test_imports),
        "output_imports": sorted(output_imports),
        "missing_in_output": missing,
        "ok": not missing,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "task_dirs",
        nargs="*",
        type=Path,
        help="Task directories (default: all under benchmark/tasks/)",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON report")
    parser.add_argument(
        "--fail-on-gap",
        action="store_true",
        help="Exit with code equal to number of tasks with L1 gaps",
    )
    args = parser.parse_args()

    if args.task_dirs:
        task_dirs = [path.resolve() for path in args.task_dirs]
    else:
        task_dirs = sorted(
            path
            for path in TASKS_DIR.iterdir()
            if path.is_dir() and (path / "metadata.json").is_file()
        )

    reports = [audit_task(task_dir) for task_dir in task_dirs]
    gaps = [report for report in reports if report["missing_in_output"]]

    if args.json:
        print(json.dumps(reports, indent=2))
    else:
        for report in reports:
            status = "OK" if report["ok"] else "GAP"
            print(f"[{status}] {report['task_id']}")
            if report["missing_in_output"]:
                for item in report["missing_in_output"]:
                    print(f"  missing in output.import: {item}")

        print()
        print(f"Audited {len(reports)} tasks; {len(gaps)} with L1 gaps.")

    if args.fail_on_gap and gaps:
        raise SystemExit(len(gaps))


if __name__ == "__main__":
    main()
