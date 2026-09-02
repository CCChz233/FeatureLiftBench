#!/usr/bin/env python3
"""Render compact per-task dossiers for the Python-200 closure review."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AUDIT = ROOT / "reports/contract_closure_200/machine_audit.json"
DEFAULT_OUTPUT = ROOT / "reports/contract_closure_200/dossiers"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--task-id", action="append", dest="task_ids")
    parser.add_argument("--title-prefix", default="")
    return parser.parse_args()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def flatten_api(entries: Any) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for entry in entries or []:
        if not isinstance(entry, dict):
            continue
        result.append(entry)
        result.extend(flatten_api(entry.get("members")))
    return result


def render(task: dict[str, Any], *, title_prefix: str = "") -> str:
    task_dir = ROOT / task["task_path"]
    metadata = load(task_dir / "metadata.json")
    public_spec = metadata.get("public_spec") if isinstance(metadata.get("public_spec"), dict) else {}
    oracle = load(task_dir / "evaluation/oracle_manifest.json")
    lines = [
        f"# {title_prefix}{task['task_id']}",
        "",
        f"- release: `{task['release_group']}`",
        f"- lift: `{task.get('lift_type') or 'unknown'}`",
        f"- coupling: `{task.get('primary_coupling') or 'unknown'}`",
        f"- strict validation: `{'PASS' if task['strict_validation']['valid'] else 'FAIL'}`",
        f"- tests/assertions: `{task['test_count']}/{task['assertion_count']}`",
        "",
        "## Required API",
        "",
    ]
    for entry in flatten_api(public_spec.get("required_api")):
        signature = entry.get("signature")
        suffix = f" `{signature}`" if signature else ""
        lines.append(f"- `{entry.get('path')}` ({entry.get('kind')}){suffix}")
    lines.extend(["", "## Public Behaviors", ""])
    for behavior in public_spec.get("behaviors") or []:
        if isinstance(behavior, dict):
            lines.append(f"- **{behavior.get('id')}**: {behavior.get('text')}")
    lines.extend(["", "## Tests", ""])
    for test in task.get("tests") or []:
        mapping = ", ".join(test.get("behavior_ids") or []) or "UNMAPPED"
        api_ids = ", ".join(test.get("api_ids") or []) or "none detected"
        risks = ", ".join(test.get("risk_tags") or []) or "none"
        lines.extend(
            [
                f"### `{test['nodeid']}`",
                "",
                f"- mapping: `{mapping}`",
                f"- API: `{api_ids}`",
                f"- risk: `{risks}`",
            ]
        )
        for assertion in test.get("assertions") or []:
            lines.append(
                f"- {assertion['assertion_id']} `{assertion['kind']}` L{assertion['line']}: "
                f"`{assertion['expression']}`"
            )
        if not test.get("assertions"):
            lines.append("- assertion: implicit successful execution")
        lines.append("")
    lines.extend(["## Dependency / Oracle Evidence", ""])
    environment = metadata.get("environment") if isinstance(metadata.get("environment"), dict) else {}
    lines.append(f"- allowed dependencies: `{', '.join(environment.get('allowed_dependencies') or []) or 'none'}`")
    lines.append(f"- forbidden imports: `{', '.join(environment.get('forbidden_imports') or []) or 'none'}`")
    lines.append(f"- source entrypoints: `{', '.join(public_spec.get('source_entrypoints') or []) or 'none'}`")
    lines.append(f"- oracle source files: `{', '.join(oracle.get('required_source_files') or []) or 'none'}`")
    lines.append(f"- runtime dependencies: `{', '.join(oracle.get('runtime_dependencies') or []) or 'none'}`")
    if oracle.get("notes"):
        lines.append(f"- oracle notes: {oracle['notes']}")
    if task["strict_validation"]["errors"]:
        lines.extend(["", "## Machine Issues", ""])
        lines.extend(f"- {value}" for value in task["strict_validation"]["errors"])
    if task["behavior_contract_issues"]:
        lines.extend(f"- {value}" for value in task["behavior_contract_issues"])
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    audit_path = args.audit if args.audit.is_absolute() else ROOT / args.audit
    output = args.output if args.output.is_absolute() else ROOT / args.output
    payload = load(audit_path)
    selected = set(args.task_ids or [])
    output.mkdir(parents=True, exist_ok=True)
    count = 0
    for task in payload.get("tasks") or []:
        if selected and task["task_id"] not in selected:
            continue
        (output / f"{task['task_id']}.md").write_text(
            render(task, title_prefix=args.title_prefix), encoding="utf-8"
        )
        count += 1
    print(f"Rendered {count} contract-review dossiers in {output.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
