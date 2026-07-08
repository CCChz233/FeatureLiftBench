#!/usr/bin/env python3
"""Read-only preflight for promoting one FeatureLiftBench task to Python main."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def find_repo_root() -> Path:
    cwd = Path.cwd().resolve()
    for candidate in (cwd, *cwd.parents):
        if (candidate / "benchmark" / "manifest.json").is_file():
            return candidate
    return cwd


ROOT = find_repo_root()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main_task_ids() -> set[str]:
    root = ROOT / "benchmark" / "tasks"
    if not root.is_dir():
        return set()
    return {path.name for path in root.iterdir() if path.is_dir() and (path / "metadata.json").is_file()}


def preflight(task_id: str, source_root: Path, target_root: Path) -> dict[str, Any]:
    issues: list[str] = []
    warnings: list[str] = []
    reject_reasons: list[str] = []

    source = source_root / task_id
    target = target_root / task_id
    if not source.is_dir():
        reject_reasons.append(f"missing source task directory: {source}")
        meta: dict[str, Any] = {}
    else:
        try:
            meta = load_json(source / "metadata.json")
        except FileNotFoundError:
            reject_reasons.append("missing metadata.json")
            meta = {}
        except json.JSONDecodeError as exc:
            reject_reasons.append(f"invalid metadata.json: {exc}")
            meta = {}

    if target.exists():
        reject_reasons.append(f"target already exists: {target}")
    if task_id in main_task_ids():
        reject_reasons.append(f"task_id already present in benchmark/tasks: {task_id}")

    status = str(meta.get("status") or "")
    if status == "blocked":
        reject_reasons.append("blocked tasks cannot be promoted")
    elif status not in {"validated_candidate", "hard_candidate", "main"}:
        issues.append(
            f"status is {status or 'implicit'}; promotion requires gate evidence before main membership"
        )

    if meta.get("task_id") and meta.get("task_id") != task_id:
        issues.append(f"metadata.task_id={meta.get('task_id')!r} does not match requested task_id")
    if meta.get("difficulty") == "hard" and not (meta.get("hard_reason") or meta.get("entanglement")):
        issues.append("hard task lacks hard_reason or entanglement metadata")

    required = ["repo", "public_tests", "hidden_tests", "evaluation", "TASK.md", "requirements.lock"]
    for name in required:
        path = source / name
        ok = path.is_dir() if name in {"repo", "public_tests", "hidden_tests", "evaluation"} else path.is_file()
        if source.exists() and not ok:
            issues.append(f"missing {name}")

    inline_ref = source / "reference_solution" / "featurelifted"
    if source.exists() and not inline_ref.is_dir():
        warnings.append("no inline reference_solution/featurelifted found; ensure benchmark/submissions oracle exists")

    promote_script = ROOT / "scripts" / "promote_batch3_task.py"
    commands = []
    if source_root.name == "batch3_pilot" and promote_script.is_file():
        commands.append(f"python3 scripts/promote_batch3_task.py {task_id}")
    else:
        commands.append(f"copy {source} to {target} after gates pass")
    commands.extend(
        [
            "python3 scripts/check_task_lifecycle.py",
            f"PYTHONPATH=harness python3 -B -m featureliftbench.cli validate-task benchmark/tasks/{task_id} --json",
        ]
    )

    if reject_reasons:
        verdict = "reject"
    elif issues:
        verdict = "fix_required"
    else:
        verdict = "pass"

    return {
        "task_id": task_id,
        "source": str(source),
        "target": str(target),
        "status": status or "implicit",
        "verdict": verdict,
        "reject_reasons": reject_reasons,
        "issues": issues,
        "warnings": warnings,
        "next_commands": commands,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task_id")
    parser.add_argument("--source-root", type=Path, default=ROOT / "benchmark" / "batch3_pilot")
    parser.add_argument("--target-root", type=Path, default=ROOT / "benchmark" / "tasks")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = preflight(args.task_id, args.source_root, args.target_root)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"task: {result['task_id']}")
        print(f"status: {result['status']}")
        print(f"verdict: {result['verdict']}")
        for key in ("reject_reasons", "issues", "warnings", "next_commands"):
            values = result.get(key) or []
            if values:
                print(f"{key}:")
                for value in values:
                    print(f"  - {value}")
    return 0 if result["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
