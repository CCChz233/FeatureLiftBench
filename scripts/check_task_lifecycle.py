#!/usr/bin/env python3
"""Read-only lifecycle and package structure audit for FeatureLiftBench tasks.

Writes:
  reports/audits/task_lifecycle_report.md
  reports/audits/task_lifecycle_report.csv

Does not modify benchmark data, evaluator code, or experiment artifacts.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "benchmark" / "manifest.json"
REPORTS_DIR = ROOT / "reports" / "audits"
CSV_PATH = REPORTS_DIR / "task_lifecycle_report.csv"
MD_PATH = REPORTS_DIR / "task_lifecycle_report.md"

BATCH3_ALLOWED_STATUSES = {
    "design_only",
    "design_only_source_snapshot_missing",
    "blocked",
    "needs_review",
    "materialized_candidate",
}

MAIN_IMPLICIT_STATUSES = {"", "main", "legacy_main_implicit", "unknown", "MISSING_STATUS"}


@dataclass
class TaskFinding:
    split_id: str
    split_root: str
    task_id: str
    task_path: str
    language: str
    lifecycle_status: str
    has_metadata: bool
    has_lock: bool
    has_repo: bool
    has_public_tests: bool
    has_hidden_tests: bool
    has_evaluation: bool
    has_task_md: bool
    spec_status: str
    metadata_fields_ok: bool
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def main() -> int:
    manifest = load_manifest()
    splits = manifest.get("splits") or {}
    exclude_map = manifest.get("exclude_task_ids") or {}
    excluded_by_split: dict[str, set[str]] = defaultdict(set)
    for split_id, ids in exclude_map.items():
        if split_id == "notes":
            continue
        if isinstance(ids, list):
            excluded_by_split[split_id].update(ids)

    findings: list[TaskFinding] = []
    global_issues: list[str] = []

    for split_id, split in splits.items():
        root = ROOT / split["root"]
        if not root.is_dir():
            global_issues.append(f"{split_id}: missing split root {split['root']}")
            continue
        excluded = excluded_by_split.get(split_id, set())
        task_dirs = sorted(p for p in root.iterdir() if p.is_dir())
        for task_dir in task_dirs:
            if task_dir.name in excluded:
                continue
            findings.append(audit_task(split_id, split, task_dir))

    overlap = detect_cross_split_overlaps(splits, exclude_map)
    for issue in overlap:
        global_issues.append(issue)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(findings)
    write_markdown(findings, manifest, global_issues)

    error_count = sum(1 for f in findings if f.issues) + len(global_issues)
    print(f"wrote {CSV_PATH.relative_to(ROOT)}")
    print(f"wrote {MD_PATH.relative_to(ROOT)}")
    print(f"tasks_checked: {len(findings)}")
    print(f"tasks_with_errors: {sum(1 for f in findings if f.issues)}")
    print(f"global_issues: {len(global_issues)}")
    return 1 if error_count else 0


def load_manifest() -> dict[str, Any]:
    if not MANIFEST_PATH.is_file():
        raise SystemExit(f"missing manifest: {MANIFEST_PATH}")
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def audit_task(split_id: str, split: dict[str, Any], task_dir: Path) -> TaskFinding:
    language = str(split.get("language") or "unknown")
    meta_path = task_dir / "metadata.json"
    has_metadata = meta_path.is_file()
    metadata: dict[str, Any] = {}
    if has_metadata:
        try:
            metadata = json.loads(meta_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            return TaskFinding(
                split_id=split_id,
                split_root=split["root"],
                task_id=task_dir.name,
                task_path=task_dir.as_posix(),
                language=language,
                lifecycle_status="parse_error",
                has_metadata=True,
                has_lock=False,
                has_repo=False,
                has_public_tests=False,
                has_hidden_tests=False,
                has_evaluation=False,
                has_task_md=False,
                spec_status="unknown",
                metadata_fields_ok=False,
                issues=[f"metadata.json parse error: {exc}"],
            )

    task_id = str(metadata.get("task_id") or task_dir.name)
    lang = str(metadata.get("language") or language)
    status = infer_lifecycle_status(split_id, split, metadata)

    has_repo = (task_dir / "repo").is_dir()
    has_public = (task_dir / "public_tests").is_dir() and any((task_dir / "public_tests").rglob("*"))
    has_hidden = (task_dir / "hidden_tests").is_dir() and any((task_dir / "hidden_tests").rglob("*"))
    has_eval = (task_dir / "evaluation").is_dir()
    has_task_md = (task_dir / "TASK.md").is_file()
    has_lock = has_dependency_lock(task_dir, lang, split_id)

    spec_status = str(metadata.get("spec_status") or "")
    if not spec_status:
        spec_status = "compliant" if isinstance(metadata.get("public_spec"), dict) else "legacy"

    finding = TaskFinding(
        split_id=split_id,
        split_root=split["root"],
        task_id=task_id,
        task_path=task_dir.relative_to(ROOT).as_posix(),
        language=lang,
        lifecycle_status=status,
        has_metadata=has_metadata,
        has_lock=has_lock,
        has_repo=has_repo,
        has_public_tests=has_public,
        has_hidden_tests=has_hidden,
        has_evaluation=has_eval,
        has_task_md=has_task_md,
        spec_status=spec_status,
        metadata_fields_ok=False,
    )

    if not has_metadata:
        finding.issues.append("missing metadata.json")
        return finding

    if task_id != task_dir.name:
        finding.issues.append(f"task_id mismatch: metadata={task_id!r} dirname={task_dir.name!r}")

    if not has_repo:
        finding.issues.append("missing repo/")
    if not has_public:
        finding.issues.append("missing or empty public_tests/")
    if not has_hidden:
        finding.issues.append("missing or empty hidden_tests/")
    if not has_eval:
        finding.issues.append("missing evaluation/")
    if not has_lock:
        finding.issues.append(dependency_lock_label(lang))

    field_issues, field_warnings = check_metadata_fields(metadata, lang)
    finding.issues.extend(field_issues)
    finding.warnings.extend(field_warnings)
    finding.metadata_fields_ok = not field_issues

    finding.issues.extend(check_split_specific_rules(split_id, split, task_dir, metadata, status))
    finding.warnings.extend(check_test_import_warnings(task_dir, lang))

    if split_id == "python_main_candidate" and spec_status == "legacy":
        finding.warnings.append("spec_status=legacy (constitution migration pending)")
    if spec_status == "compliant" and not isinstance(metadata.get("public_spec"), dict):
        finding.issues.append("spec_status=compliant but metadata.public_spec is missing")

    return finding


def infer_lifecycle_status(split_id: str, split: dict[str, Any], metadata: dict[str, Any]) -> str:
    raw = metadata.get("status")
    if isinstance(raw, str) and raw.strip():
        return raw.strip()
    lifecycle = split.get("lifecycle_status")
    if split_id == "python_main_candidate":
        return "legacy_main_implicit"
    if lifecycle:
        return f"implicit_{lifecycle}"
    return "MISSING_STATUS"


def has_dependency_lock(task_dir: Path, language: str, split_id: str) -> bool:
    if language == "go":
        if (task_dir / "environment" / "go.mod").is_file():
            return True
        return split_id == "go_legacy_pilot" and (task_dir / "repo" / "go.mod").is_file()
    return (task_dir / "requirements.lock").is_file()


def dependency_lock_label(language: str) -> str:
    if language == "go":
        return "missing environment/go.mod"
    return "missing requirements.lock"


def check_metadata_fields(metadata: dict[str, Any], language: str) -> tuple[list[str], list[str]]:
    issues: list[str] = []
    warnings: list[str] = []

    if not metadata.get("task_id"):
        warnings.append("metadata.task_id missing (dirname used)")

    if metadata.get("language") not in {language, "python", "go"}:
        if metadata.get("language") is None:
            issues.append("metadata.language missing")
        elif metadata.get("language") != language:
            warnings.append(f"metadata.language={metadata.get('language')!r} differs from split default {language!r}")

    if not has_source_info(metadata):
        issues.append("missing source info (source.* or repo+commit)")

    if not has_feature_info(metadata):
        issues.append("missing feature info (feature.* or feature_name)")

    if not has_output_info(metadata):
        issues.append("missing output info (output.package or output.module)")

    if not metadata.get("tests"):
        warnings.append("metadata.tests missing (default paths assumed)")

    if not metadata.get("environment"):
        warnings.append("metadata.environment missing")

    if language == "python":
        package = (metadata.get("output") or {}).get("package")
        if package and package != "featurelifted":
            issues.append(f"output.package must be featurelifted, got {package!r}")

    return issues, warnings


def has_source_info(metadata: dict[str, Any]) -> bool:
    source = metadata.get("source") or {}
    if source.get("name") and source.get("url") and source.get("commit"):
        return True
    if metadata.get("repo") and metadata.get("commit"):
        return True
    return False


def has_feature_info(metadata: dict[str, Any]) -> bool:
    feature = metadata.get("feature") or {}
    if feature.get("name"):
        return True
    return bool(metadata.get("feature_name"))


def has_output_info(metadata: dict[str, Any]) -> bool:
    output = metadata.get("output") or {}
    return bool(output.get("package") or output.get("module"))


def check_split_specific_rules(
    split_id: str,
    split: dict[str, Any],
    task_dir: Path,
    metadata: dict[str, Any],
    status: str,
) -> list[str]:
    issues: list[str] = []

    if split_id == "python_main_candidate":
        if status not in MAIN_IMPLICIT_STATUSES and status not in {
            "validated_candidate",
            "hard_candidate",
            "main",
            "materialized_candidate",
        }:
            issues.append(f"unexpected status in main candidate pool: {status!r}")
        if status in {"design_only", "design_only_source_snapshot_missing", "blocked", "needs_review"}:
            issues.append(f"pre-main lifecycle status {status!r} must not remain in benchmark/tasks")

    if split_id == "python_batch3_pilot":
        if status not in BATCH3_ALLOWED_STATUSES:
            issues.append(f"batch3_pilot status not allowed: {status!r}")
        if status == "blocked" and not metadata.get("blocked_reason"):
            issues.append("blocked task missing blocked_reason")
        if status == "materialized_candidate":
            commit = str(metadata.get("commit") or metadata.get("source", {}).get("commit") or "")
            if commit in {"", "TODO-pin"} or commit.startswith("blocked"):
                issues.append("materialized_candidate must pin a real commit")
            ref_init = task_dir / "reference_solution" / "featurelifted" / "__init__.py"
            if not ref_init.is_file():
                issues.append("materialized_candidate missing reference_solution/featurelifted/__init__.py")

    if split_id == "python_staging":
        if status in {"design_only", "design_only_source_snapshot_missing", "blocked"}:
            issues.append(f"staging should not retain status {status!r}")

    return issues


def check_test_import_warnings(task_dir: Path, language: str) -> list[str]:
    if language != "python":
        return []
    warnings: list[str] = []
    for label in ("public_tests", "hidden_tests"):
        test_dir = task_dir / label
        if not test_dir.is_dir():
            continue
        for py_file in test_dir.rglob("*.py"):
            text = py_file.read_text(encoding="utf-8", errors="replace")
            if re.search(r"(?:^|\n)\s*(?:from|import)\s+submission\b", text):
                warnings.append(f"{py_file.relative_to(task_dir)} imports submission (prefer featurelifted)")
            if "import featurelifted" not in text and "from featurelifted" not in text:
                if "test_" in py_file.name:
                    warnings.append(f"{py_file.relative_to(task_dir)} does not import featurelifted")
    return warnings


def detect_cross_split_overlaps(splits: dict[str, Any], exclude_map: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    excluded_all: set[str] = set()
    for key, val in exclude_map.items():
        if key == "notes" or not isinstance(val, list):
            continue
        excluded_all.update(val)

    by_id: dict[str, list[str]] = defaultdict(list)
    for split_id, split in splits.items():
        if split.get("paper_use") in {"smoke_only", "legacy_pilot"}:
            continue
        root = ROOT / split["root"]
        if not root.is_dir():
            continue
        for task_dir in root.iterdir():
            if not task_dir.is_dir() or task_dir.name in excluded_all:
                continue
            by_id[task_dir.name].append(split_id)

    for task_id, split_ids in sorted(by_id.items()):
        if len(split_ids) > 1:
            issues.append(f"task_id {task_id!r} appears in multiple splits: {', '.join(split_ids)}")
    return issues


def write_csv(findings: list[TaskFinding]) -> None:
    with CSV_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(
            [
                "split_id",
                "task_id",
                "task_path",
                "language",
                "lifecycle_status",
                "has_metadata",
                "has_lock",
                "has_repo",
                "has_public_tests",
                "has_hidden_tests",
                "has_evaluation",
                "has_task_md",
                "spec_status",
                "metadata_fields_ok",
                "issue_count",
                "warning_count",
                "issues",
                "warnings",
            ]
        )
        for row in findings:
            writer.writerow(
                [
                    row.split_id,
                    row.task_id,
                    row.task_path,
                    row.language,
                    row.lifecycle_status,
                    row.has_metadata,
                    row.has_lock,
                    row.has_repo,
                    row.has_public_tests,
                    row.has_hidden_tests,
                    row.has_evaluation,
                    row.has_task_md,
                    row.spec_status,
                    row.metadata_fields_ok,
                    len(row.issues),
                    len(row.warnings),
                    "; ".join(row.issues),
                    "; ".join(row.warnings),
                ]
            )


def write_markdown(findings: list[TaskFinding], manifest: dict[str, Any], global_issues: list[str]) -> None:
    today = date.today().isoformat()
    by_split: dict[str, list[TaskFinding]] = defaultdict(list)
    for f in findings:
        by_split[f.split_id].append(f)

    status_counts = Counter(f.lifecycle_status for f in findings)
    issue_rows = [f for f in findings if f.issues]
    warning_rows = [f for f in findings if f.warnings]

    lines: list[str] = [
        "# Task Lifecycle Report",
        "",
        f"Generated: {today}",
        "",
        "Read-only audit from `scripts/check_task_lifecycle.py`. No files were modified.",
        "",
        "## Summary",
        "",
        f"- Tasks checked: {len(findings)}",
        f"- Tasks with errors: {len(issue_rows)}",
        f"- Tasks with warnings: {len(warning_rows)}",
        f"- Global issues: {len(global_issues)}",
        "",
        "### Lifecycle status counts",
        "",
        "| Status | Count |",
        "|---|---:|",
    ]
    for status, count in sorted(status_counts.items()):
        lines.append(f"| {status} | {count} |")

    lines.extend(["", "## Manifest splits", ""])
    for split_id, split in (manifest.get("splits") or {}).items():
        checked = by_split.get(split_id, [])
        err = sum(1 for f in checked if f.issues)
        lines.append(
            f"- **{split_id}** (`{split.get('root')}`): checked {len(checked)} tasks, errors {err}"
        )

    if global_issues:
        lines.extend(["", "## Global issues", ""])
        for issue in global_issues:
            lines.append(f"- {issue}")

    if issue_rows:
        lines.extend(["", "## Tasks with errors", ""])
        lines.append("| Split | Task | Status | Issues |")
        lines.append("|---|---|---|---|")
        for row in sorted(issue_rows, key=lambda r: (r.split_id, r.task_id)):
            lines.append(
                f"| {row.split_id} | `{row.task_id}` | {row.lifecycle_status} | {'; '.join(row.issues)} |"
            )

    if warning_rows:
        lines.extend(["", "## Tasks with warnings (non-blocking)", ""])
        lines.append("| Split | Task | Warnings |")
        lines.append("|---|---|---|")
        for row in sorted(warning_rows, key=lambda r: (r.split_id, r.task_id))[:50]:
            lines.append(f"| {row.split_id} | `{row.task_id}` | {'; '.join(row.warnings)} |")
        if len(warning_rows) > 50:
            lines.append(f"| ... | ... | ({len(warning_rows) - 50} more warnings in CSV) |")

    lines.extend(
        [
            "",
            "## Full data",
            "",
            f"See `{CSV_PATH.relative_to(ROOT)}` for the complete per-task matrix.",
            "",
        ]
    )

    MD_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
