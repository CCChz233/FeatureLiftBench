#!/usr/bin/env python3
"""Lightweight read-only gate audit for one FeatureLiftBench task."""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
from typing import Any, Optional


def find_repo_root() -> Path:
    cwd = Path.cwd().resolve()
    for candidate in (cwd, *cwd.parents):
        if (candidate / "benchmark" / "manifest.json").is_file():
            return candidate
    return cwd


ROOT = find_repo_root()


def load_json(path: Path) -> tuple[Optional[dict[str, Any]], Optional[str]]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except FileNotFoundError:
        return None, f"missing {path.name}"
    except json.JSONDecodeError as exc:
        return None, f"invalid JSON in {path}: {exc}"


def nonempty_dir(path: Path) -> bool:
    return path.is_dir() and any(path.rglob("*"))


def source_info(meta: dict[str, Any]) -> dict[str, Any]:
    source = meta.get("source")
    if isinstance(source, dict):
        return source
    return {
        "name": meta.get("source_name") or meta.get("feature_name") or "",
        "url": meta.get("repo") or meta.get("source_url") or "",
        "commit": meta.get("commit") or "",
        "license": meta.get("license") or "",
    }


def feature_info(meta: dict[str, Any]) -> dict[str, Any]:
    feature = meta.get("feature")
    if isinstance(feature, dict):
        return feature
    return {
        "name": meta.get("feature_name") or "",
        "included_behaviors": meta.get("included_behaviors") or [],
        "excluded_behaviors": meta.get("excluded_behaviors") or [],
    }


def output_info(meta: dict[str, Any]) -> dict[str, Any]:
    output = meta.get("output")
    return output if isinstance(output, dict) else {}


def metadata_forbidden_imports(meta: dict[str, Any]) -> list[str]:
    values: list[str] = []
    for key in ("forbidden_imports",):
        raw = meta.get(key)
        if isinstance(raw, list):
            values.extend(str(v) for v in raw if v)
    env = meta.get("environment")
    if isinstance(env, dict):
        raw = env.get("forbidden_imports")
        if isinstance(raw, list):
            values.extend(str(v) for v in raw if v)
    return sorted(set(values))


def file_forbidden_imports(path: Path) -> list[str]:
    if not path.is_file():
        return []
    return sorted(
        {
            line.strip()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        }
    )


def import_roots(py_file: Path) -> set[str]:
    try:
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
    except (SyntaxError, UnicodeDecodeError):
        return set()
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".", 1)[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".", 1)[0])
    return roots


def scan_tests(task_dir: Path, forbidden: set[str]) -> tuple[list[str], list[str]]:
    issues: list[str] = []
    warnings: list[str] = []
    for rel in ("public_tests", "hidden_tests"):
        root = task_dir / rel
        imports_featurelifted = False
        for py_file in root.rglob("*.py"):
            roots = import_roots(py_file)
            if "featurelifted" in roots:
                imports_featurelifted = True
            if "submission" in roots:
                issues.append(f"{py_file.relative_to(task_dir)} imports submission")
            blocked = sorted(forbidden.intersection(roots))
            if blocked:
                issues.append(f"{py_file.relative_to(task_dir)} imports forbidden upstream roots: {blocked}")
        if root.is_dir() and not imports_featurelifted:
            warnings.append(f"{rel}/ has no direct featurelifted import")
    return issues, warnings


def evidence_paths(task_id: str, limit: int = 12) -> list[str]:
    hits: list[str] = []
    for base in (ROOT / "experiments", ROOT / "evidence", ROOT / "reports"):
        if not base.exists():
            continue
        for path in base.rglob(task_id):
            hits.append(str(path.relative_to(ROOT)))
            if len(hits) >= limit:
                return hits
    return hits


def audit(task_dir: Path) -> dict[str, Any]:
    task_dir = task_dir.resolve()
    issues: list[str] = []
    warnings: list[str] = []
    reject_reasons: list[str] = []

    if not task_dir.is_dir():
        return {
            "task_dir": str(task_dir),
            "verdict": "reject",
            "reject_reasons": ["task directory does not exist"],
            "issues": [],
            "warnings": [],
        }

    meta, error = load_json(task_dir / "metadata.json")
    if error:
        return {
            "task_dir": str(task_dir),
            "verdict": "reject",
            "reject_reasons": [error],
            "issues": [],
            "warnings": [],
        }
    assert meta is not None

    task_id = str(meta.get("task_id") or task_dir.name)
    status = str(meta.get("status") or "")
    if task_id != task_dir.name:
        issues.append(f"task_id mismatch: metadata={task_id!r}, dirname={task_dir.name!r}")
    if status == "blocked":
        reject_reasons.append("task status is blocked")

    required_paths = {
        "requirements.lock": (task_dir / "requirements.lock").is_file(),
        "TASK.md": (task_dir / "TASK.md").is_file(),
        "repo/": (task_dir / "repo").is_dir(),
        "public_tests/": nonempty_dir(task_dir / "public_tests"),
        "hidden_tests/": nonempty_dir(task_dir / "hidden_tests"),
        "evaluation/": (task_dir / "evaluation").is_dir(),
    }
    for label, ok in required_paths.items():
        if not ok:
            issues.append(f"missing or empty {label}")

    source = source_info(meta)
    for key in ("name", "url", "commit", "license"):
        if not source.get(key):
            issues.append(f"missing source.{key}")

    feature = feature_info(meta)
    if not feature.get("name"):
        issues.append("missing feature.name or feature_name")
    output = output_info(meta)
    if output.get("package") != "featurelifted":
        issues.append(f"output.package must be featurelifted, got {output.get('package')!r}")
    if not meta.get("tests"):
        issues.append("missing metadata.tests")
    if not meta.get("environment"):
        issues.append("missing metadata.environment")
    if not meta.get("difficulty"):
        issues.append("missing metadata.difficulty")
    if "batch3_pilot" in task_dir.parts and not status:
        issues.append("new pilot task should have explicit lifecycle status")

    oracle_manifest = task_dir / "evaluation" / "oracle_manifest.json"
    forbidden_imports_path = task_dir / "evaluation" / "forbidden_imports.txt"
    if not oracle_manifest.is_file():
        issues.append("missing evaluation/oracle_manifest.json")
    if not forbidden_imports_path.is_file():
        issues.append("missing evaluation/forbidden_imports.txt")

    forbidden = set(metadata_forbidden_imports(meta))
    forbidden.update(file_forbidden_imports(forbidden_imports_path))
    if not forbidden:
        issues.append("no forbidden upstream imports recorded")

    test_issues, test_warnings = scan_tests(task_dir, {item.split(".", 1)[0] for item in forbidden})
    issues.extend(test_issues)
    warnings.extend(test_warnings)

    inline_ref = task_dir / "reference_solution" / "featurelifted"
    oracle_ref = ROOT / "benchmark" / "submissions" / task_id / "oracle" / "featurelifted"
    if not inline_ref.is_dir() and not oracle_ref.is_dir():
        issues.append("no inline reference_solution/featurelifted or benchmark/submissions oracle found")

    if meta.get("difficulty") == "hard":
        if not meta.get("hard_reason") and not meta.get("entanglement"):
            issues.append("hard task lacks hard_reason or entanglement metadata")
        hits = evidence_paths(task_id)
        if not hits:
            warnings.append("no experiment/evidence/report path named after task_id found")
    else:
        hits = []

    if reject_reasons:
        verdict = "reject"
    elif issues:
        verdict = "fix_required"
    else:
        verdict = "pass"

    return {
        "task_dir": str(task_dir),
        "task_id": task_id,
        "status": status or "implicit",
        "verdict": verdict,
        "reject_reasons": reject_reasons,
        "issues": issues,
        "warnings": warnings,
        "evidence_path_hits": hits,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task_dir", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = audit(args.task_dir)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"task: {result.get('task_id', args.task_dir.name)}")
        print(f"status: {result.get('status', 'unknown')}")
        print(f"verdict: {result['verdict']}")
        for key in ("reject_reasons", "issues", "warnings", "evidence_path_hits"):
            values = result.get(key) or []
            if values:
                print(f"{key}:")
                for value in values:
                    print(f"  - {value}")
    return 0 if result["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
