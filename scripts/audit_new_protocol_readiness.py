#!/usr/bin/env python3
"""Audit task readiness for the test-blind repository extraction protocol."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


GENERIC_BEHAVIOR_PATTERNS = (
    "preserves the corresponding upstream-observable result within the documented scope",
    "every declared required API path and member exists",
    "declared target API remains importable and preserves upstream-observable semantics",
)
TEST_DIR_NAMES = frozenset({"test", "tests", "testing"})
DOC_DIR_NAMES = frozenset({"doc", "docs", "example", "examples"})
CALLABLE_KINDS = frozenset({"class", "function", "method", "callable"})


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Audit FeatureLiftBench tasks for the test-blind Main protocol: complete "
            "contract for experiment readiness, plus independent review for paper readiness."
        )
    )
    parser.add_argument(
        "tasks_root",
        nargs="?",
        type=Path,
        default=Path("benchmark/tasks"),
    )
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--markdown-out", type=Path)
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="print one compact readiness line instead of the full JSON report",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="backward-compatible alias for --strict-paper",
    )
    parser.add_argument(
        "--strict-experiment",
        action="store_true",
        help="exit 1 unless every task has an experiment-ready public contract",
    )
    parser.add_argument(
        "--strict-paper",
        action="store_true",
        help="exit 1 unless every task also has independent human review",
    )
    return parser.parse_args()


def _is_test_like(path: Path) -> bool:
    lowered_parts = tuple(part.lower() for part in path.parts)
    name = path.name.lower()
    return (
        any(part in TEST_DIR_NAMES for part in lowered_parts[:-1])
        or name.startswith("test_")
        or name.endswith("_test.py")
        or name.endswith("_test.go")
    )


def _is_doc_or_example(path: Path) -> bool:
    lowered_parts = tuple(part.lower() for part in path.parts)
    name = path.name.lower()
    return (
        any(part in DOC_DIR_NAMES for part in lowered_parts[:-1])
        or name.startswith(("readme", "example"))
        or name in {"changelog", "changes", "news"}
    )


def _entry_has_callable_signature(entry: dict[str, Any]) -> bool:
    kind = str(entry.get("kind", "")).strip().lower()
    if kind in CALLABLE_KINDS:
        return bool(str(entry.get("signature", "")).strip())
    return True


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


def _audit_task(task_dir: Path) -> dict[str, Any]:
    metadata_path = task_dir / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    public_spec = (
        metadata.get("public_spec")
        if isinstance(metadata.get("public_spec"), dict)
        else {}
    )
    evaluation_spec = (
        metadata.get("evaluation_spec")
        if isinstance(metadata.get("evaluation_spec"), dict)
        else {}
    )
    required_api = [
        item for item in public_spec.get("required_api", []) if isinstance(item, dict)
    ]
    behaviors = [
        item for item in public_spec.get("behaviors", []) if isinstance(item, dict)
    ]
    behavior_texts = [str(item.get("text", "")) for item in behaviors]
    generic_behavior_ids = [
        str(item.get("id", ""))
        for item in behaviors
        if any(
            pattern in str(item.get("text", ""))
            for pattern in GENERIC_BEHAVIOR_PATTERNS
        )
    ]
    missing_callable_signatures = [
        str(item.get("path", ""))
        for item in _flatten_api(required_api)
        if not _entry_has_callable_signature(item)
    ]

    repo_dir = task_dir / "repo"
    repo_files = (
        sorted(path for path in repo_dir.rglob("*") if path.is_file())
        if repo_dir.is_dir()
        else []
    )
    relative_repo_files = [path.relative_to(repo_dir) for path in repo_files]
    upstream_test_files = [
        str(path) for path in relative_repo_files if _is_test_like(path)
    ]
    doc_or_example_files = [
        str(path) for path in relative_repo_files if _is_doc_or_example(path)
    ]

    manual_review = (
        evaluation_spec.get("manual_review")
        if isinstance(evaluation_spec.get("manual_review"), dict)
        else {}
    )
    independent_human_review = (
        manual_review.get("independent_human_review") is True
    )
    source_entrypoints = public_spec.get("source_entrypoints")
    source_entrypoints = (
        [str(item) for item in source_entrypoints if isinstance(item, str) and item]
        if isinstance(source_entrypoints, list)
        else []
    )

    issues: list[str] = []
    if metadata.get("spec_status") != "compliant":
        issues.append("not_engineering_compliant")
    if not repo_files:
        issues.append("missing_repository_snapshot")
    if not source_entrypoints:
        issues.append("missing_source_entrypoints")
    if not required_api:
        issues.append("missing_required_api")
    if not behaviors:
        issues.append("missing_behaviors")
    if generic_behavior_ids:
        issues.append("generic_behavior_contract")
    if missing_callable_signatures:
        issues.append("missing_callable_signatures")
    if not independent_human_review:
        issues.append("independent_human_review_pending")

    engineering_ready = not any(
        issue
        in {
            "not_engineering_compliant",
            "missing_repository_snapshot",
            "missing_source_entrypoints",
            "missing_required_api",
            "missing_behaviors",
        }
        for issue in issues
    )
    contract_ready = not any(
        issue in {"generic_behavior_contract", "missing_callable_signatures"}
        for issue in issues
    )
    repository_discovery_ready = bool(upstream_test_files)
    experiment_ready = engineering_ready and contract_ready
    paper_ready = experiment_ready and independent_human_review
    return {
        "task_id": task_dir.name,
        "spec_status": metadata.get("spec_status"),
        "repo_file_count": len(repo_files),
        "upstream_test_file_count": len(upstream_test_files),
        "upstream_test_files_sample": upstream_test_files[:10],
        "doc_or_example_file_count": len(doc_or_example_files),
        "source_entrypoint_count": len(source_entrypoints),
        "required_api_count": len(required_api),
        "behavior_count": len(behaviors),
        "generic_behavior_ids": generic_behavior_ids,
        "missing_callable_signatures": missing_callable_signatures,
        "independent_human_review": independent_human_review,
        "reviewer_type": manual_review.get("reviewer_type"),
        "engineering_ready": engineering_ready,
        "contract_ready": contract_ready,
        "experiment_ready": experiment_ready,
        "repository_discovery_ready": repository_discovery_ready,
        "paper_ready": paper_ready,
        "issues": issues,
    }


def audit(tasks_root: Path) -> dict[str, Any]:
    task_dirs = sorted(
        path
        for path in tasks_root.iterdir()
        if path.is_dir() and (path / "metadata.json").is_file()
    )
    tasks = [_audit_task(task_dir) for task_dir in task_dirs]
    issue_counts = Counter(
        issue for task in tasks for issue in task.get("issues", [])
    )
    return {
        "schema_version": "featureliftbench.new_protocol_readiness.v2",
        "tasks_root": str(tasks_root.resolve()),
        "protocol": {
            "agent_visible": [
                "generated TASK.md",
                "pinned repo/ including upstream tests/docs/examples when present",
                "dependency lock and redacted runtime metadata",
                "writable submission/",
            ],
            "agent_hidden": [
                "benchmark public_tests/",
                "benchmark hidden_tests/",
                "evaluation/",
                "reference/oracle artifacts",
            ],
            "post_submit": [
                "build/import",
                "benchmark public tier",
                "benchmark hidden tier",
                "isolation/forbidden checks",
                "compactness scoring",
            ],
        },
        "summary": {
            "task_count": len(tasks),
            "engineering_ready": sum(task["engineering_ready"] for task in tasks),
            "contract_ready": sum(task["contract_ready"] for task in tasks),
            "experiment_ready": sum(task["experiment_ready"] for task in tasks),
            "repository_discovery_ready": sum(
                task["repository_discovery_ready"] for task in tasks
            ),
            "independent_human_review": sum(
                task["independent_human_review"] for task in tasks
            ),
            "paper_ready": sum(task["paper_ready"] for task in tasks),
            "issue_counts": dict(sorted(issue_counts.items())),
        },
        "tasks": tasks,
    }


def _markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    task_count = summary["task_count"]
    lines = [
        "# New Protocol Readiness Audit",
        "",
        "Protocol: complete generated TASK + pinned upstream repository context; "
        "all benchmark-authored evaluator tests hidden until one-shot submission.",
        "",
        "## Summary",
        "",
        "| Gate | Ready |",
        "| --- | ---: |",
        f"| Engineering package/spec | {summary['engineering_ready']}/{task_count} |",
        f"| Complete non-generic contract | {summary['contract_ready']}/{task_count} |",
        f"| Experiment-ready content | {summary['experiment_ready']}/{task_count} |",
        f"| Upstream tests available in `repo/` (informational) | {summary['repository_discovery_ready']}/{task_count} |",
        f"| Independent human review | {summary['independent_human_review']}/{task_count} |",
        f"| Paper-ready for new protocol | {summary['paper_ready']}/{task_count} |",
        "",
        "## Issue Counts",
        "",
        "| Issue | Tasks |",
        "| --- | ---: |",
    ]
    for issue, count in summary["issue_counts"].items():
        lines.append(f"| `{issue}` | {count} |")
    lines.extend(
        [
            "",
            "## Per-task Queue",
            "",
            "| Task | Repo files | Upstream tests | Contract | Human | Issues |",
            "| --- | ---: | ---: | --- | --- | --- |",
        ]
    )
    for task in report["tasks"]:
        issues = ", ".join(task["issues"]) or "—"
        lines.append(
            f"| `{task['task_id']}` | {task['repo_file_count']} | "
            f"{task['upstream_test_file_count']} | "
            f"{'ready' if task['contract_ready'] else 'fix'} | "
            f"{'yes' if task['independent_human_review'] else 'no'} | {issues} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = _parse_args()
    report = audit(args.tasks_root)
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(payload, encoding="utf-8")
        print(f"wrote {args.json_out}")
    if args.markdown_out:
        args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_out.write_text(_markdown(report), encoding="utf-8")
        print(f"wrote {args.markdown_out}")
    if args.summary_only:
        summary = report["summary"]
        task_count = summary["task_count"]
        print(
            "New-protocol content audit: "
            f"engineering {summary['engineering_ready']}/{task_count}; "
            f"contract {summary['contract_ready']}/{task_count}; "
            f"experiment-ready {summary['experiment_ready']}/{task_count}; "
            "upstream-tests "
            f"{summary['repository_discovery_ready']}/{task_count}; "
            f"human {summary['independent_human_review']}/{task_count}; "
            f"paper-ready {summary['paper_ready']}/{task_count}"
        )
    elif not args.json_out and not args.markdown_out:
        print(payload, end="")
    task_count = report["summary"]["task_count"]
    if (
        args.strict_experiment
        and report["summary"]["experiment_ready"] != task_count
    ):
        return 1
    if (
        (args.strict or args.strict_paper)
        and report["summary"]["paper_ready"] != task_count
    ):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
