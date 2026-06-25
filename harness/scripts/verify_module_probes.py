#!/usr/bin/env python3
"""Audit and optionally verify module probe tables from task design notes."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
from fnmatch import fnmatch
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "harness") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "harness"))

from featureliftbench.evaluator import evaluate_submission
from featureliftbench.paths import SUBMISSIONS_DIR, TASKS_DIR

DESIGNS_DIR = _REPO_ROOT / "docs" / "task_designs"
_PROBE_SECTION = re.compile(r"## Module Probes\s*\n(\|.*?\n(?:\|.*\n)+)", re.MULTILINE)
_TEST_NAME = re.compile(r"`(test_[\w]+)`")
_REMOVE_PATH = re.compile(r"`([^`]+)`")


def parse_module_probes(design_path: Path) -> list[dict[str, object]]:
    if not design_path.is_file():
        return []
    text = design_path.read_text(encoding="utf-8")
    match = _PROBE_SECTION.search(text)
    if not match:
        return []
    table = match.group(1)
    rows = [line for line in table.splitlines() if line.startswith("|") and not re.match(r"^\|\s*-+", line)]
    probes: list[dict[str, object]] = []
    for row in rows[1:]:
        cells = [cell.strip() for cell in row.strip("|").split("|")]
        if len(cells) < 3:
            continue
        label, remove_cell, tests_cell = cells[0], cells[1], cells[2]
        remove_paths = []
        for token in _REMOVE_PATH.findall(remove_cell):
            token = token.strip()
            if token.endswith(".py") or "/" in token:
                remove_paths.append(token)
        must_fail = _TEST_NAME.findall(tests_cell)
        if not must_fail:
            for token in _TEST_NAME.findall(remove_cell):
                must_fail.append(token)
        probes.append(
            {
                "label": label,
                "remove_paths": remove_paths,
                "must_fail_tests": must_fail,
            }
        )
    return probes


def _submission_files(submission_dir: Path) -> list[Path]:
    pkg_root = submission_dir
    for candidate in submission_dir.iterdir():
        if candidate.is_dir() and (candidate / "__init__.py").is_file():
            pkg_root = candidate
            break
    return [path for path in pkg_root.rglob("*.py") if path.is_file()]


def _matches_remove_path(rel_path: str, pattern: str) -> bool:
    normalized = rel_path.replace("\\", "/")
    pattern = pattern.replace("\\", "/")
    if normalized == pattern or normalized.endswith("/" + pattern):
        return True
    if fnmatch(normalized, pattern):
        return True
    return fnmatch(normalized, f"*/{pattern}")


def apply_probe_removal(submission_dir: Path, remove_paths: list[str]) -> list[str]:
    removed: list[str] = []
    if not remove_paths:
        return removed
    for path in _submission_files(submission_dir):
        rel = path.relative_to(submission_dir).as_posix()
        if any(_matches_remove_path(rel, pattern) for pattern in remove_paths):
            path.unlink()
            removed.append(rel)
    return removed


def audit_design_coverage(task_dirs: list[Path], *, min_probes: int) -> list[dict[str, object]]:
    reports: list[dict[str, object]] = []
    for task_dir in task_dirs:
        task_id = task_dir.name
        design = DESIGNS_DIR / f"{task_id}.md"
        probes = parse_module_probes(design)
        reports.append(
            {
                "task_id": task_id,
                "design": str(design),
                "design_present": design.is_file(),
                "probe_count": len(probes),
                "ok": design.is_file() and len(probes) >= min_probes,
                "probes": probes,
            }
        )
    return reports


def verify_oracle_probes(task_dir: Path, probes: list[dict[str, object]]) -> dict[str, object]:
    task_id = task_dir.name
    oracle_dir = SUBMISSIONS_DIR / task_id / "oracle"
    report: dict[str, object] = {
        "task_id": task_id,
        "oracle_present": oracle_dir.is_dir(),
        "baseline_passed": False,
        "probe_results": [],
    }
    if not oracle_dir.is_dir():
        report["status"] = "skipped"
        report["reason"] = "oracle submission not found"
        return report

    with tempfile.TemporaryDirectory(prefix="flb-probe-verify-") as tmp:
        output_root = Path(tmp)
        baseline_out = output_root / "baseline"
        baseline_out.mkdir()
        baseline = evaluate_submission(task_dir, oracle_dir, baseline_out)
        report["baseline_passed"] = baseline.get("status") == "passed"
        if not report["baseline_passed"]:
            report["status"] = "failed"
            report["reason"] = "oracle baseline eval failed"
            return report

        probe_results: list[dict[str, object]] = []
        for probe in probes:
            probe_out = output_root / f"probe-{len(probe_results)}"
            probe_out.mkdir()
            submission_copy = probe_out / "submission"
            shutil.copytree(oracle_dir, submission_copy)
            removed = apply_probe_removal(
                submission_copy,
                list(probe.get("remove_paths") or []),
            )
            eval_out = probe_out / "eval"
            eval_out.mkdir()
            result = evaluate_submission(task_dir, submission_copy, eval_out)
            hidden = result.get("hidden_tests") or {}
            hidden_passed = hidden.get("passed")
            stdout_path = eval_out / "logs" / "hidden.stdout"
            stdout = stdout_path.read_text(encoding="utf-8") if stdout_path.is_file() else ""
            must_fail = list(probe.get("must_fail_tests") or [])
            matched_tests = [name for name in must_fail if name in stdout and "FAILED" in stdout]
            probe_results.append(
                {
                    "label": probe.get("label"),
                    "remove_paths": probe.get("remove_paths"),
                    "removed_files": removed,
                    "must_fail_tests": must_fail,
                    "hidden_passed": hidden_passed,
                    "matched_failures": matched_tests,
                    "passed": hidden_passed is False and (not must_fail or bool(matched_tests)),
                }
            )

        report["probe_results"] = probe_results
        report["status"] = "passed" if all(item["passed"] for item in probe_results) else "failed"
        return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task_dirs", nargs="*", type=Path, help="Task directories")
    parser.add_argument("--min-probes", type=int, default=3, help="Minimum probes per design note")
    parser.add_argument(
        "--verify-oracle",
        action="store_true",
        help="Run oracle baseline + probe removal checks (requires local oracle submissions)",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.task_dirs:
        task_dirs = [path.resolve() for path in args.task_dirs]
    else:
        task_dirs = sorted(
            path for path in TASKS_DIR.iterdir() if path.is_dir() and (path / "metadata.json").is_file()
        )

    audit = audit_design_coverage(task_dirs, min_probes=args.min_probes)
    gaps = [item for item in audit if not item["ok"]]

    oracle_reports: list[dict[str, object]] = []
    if args.verify_oracle:
        for item in audit:
            task_dir = TASKS_DIR / str(item["task_id"])
            probes = list(item.get("probes") or [])
            if probes:
                oracle_reports.append(verify_oracle_probes(task_dir, probes))

    payload = {"audit": audit, "oracle_verification": oracle_reports}
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"{'task_id':<45} {'design':>6} {'probes':>6} {'status':>8}")
        for item in audit:
            status = "OK" if item["ok"] else "GAP"
            print(
                f"{item['task_id']:<45} "
                f"{str(item['design_present']):>6} "
                f"{item['probe_count']:>6} "
                f"{status:>8}"
            )
        print()
        print(f"Audited {len(audit)} tasks; {len(gaps)} below min_probes={args.min_probes}.")
        if args.verify_oracle:
            verified = [item for item in oracle_reports if item.get("status") == "passed"]
            skipped = [item for item in oracle_reports if item.get("status") == "skipped"]
            failed = [item for item in oracle_reports if item.get("status") == "failed"]
            print(
                f"Oracle probe verification: {len(verified)} passed, "
                f"{len(failed)} failed, {len(skipped)} skipped."
            )

    exit_code = len(gaps)
    if args.verify_oracle:
        exit_code += sum(1 for item in oracle_reports if item.get("status") == "failed")
    if exit_code:
        raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
