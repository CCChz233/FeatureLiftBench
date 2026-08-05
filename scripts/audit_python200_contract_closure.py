#!/usr/bin/env python3
"""Build and verify the assertion-level Python-200 contract-closure ledger."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "harness"
if str(HARNESS) not in sys.path:
    sys.path.insert(0, str(HARNESS))

from featureliftbench.contract_closure_audit import (  # noqa: E402
    AUDIT_SCHEMA,
    audit_task,
    review_template,
    validate_review,
    write_summary_csv,
)


DEFAULT_OUTPUT = ROOT / "reports" / "contract_closure_200"
DEFAULT_SUITE = ROOT / "benchmark/selection/python200_suite.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--suite", type=Path, default=DEFAULT_SUITE)
    parser.add_argument("--task-id", action="append", dest="task_ids")
    parser.add_argument(
        "--task-list",
        type=Path,
        help="newline-delimited task IDs to audit in addition to --task-id",
    )
    parser.add_argument("--write-templates", action="store_true")
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"expected JSON object: {path}")
    return value


def labels() -> dict[str, dict[str, str]]:
    policy = load_json(ROOT / "benchmark/selection/python200_balance_policy.json")
    expansion = load_json(ROOT / "benchmark/selection/external50_expansion_20260731.json")
    result: dict[str, dict[str, str]] = {}
    for row in expansion.get("rows") or []:
        if isinstance(row, dict) and row.get("disposition") == "selected":
            result[str(row["task_id"])] = {
                "lift_type": str(row.get("final_lift_type") or row.get("lift_type") or ""),
                "primary_coupling": str(row.get("entanglement") or ""),
            }
    taxonomy = ROOT / "reports/lift_taxonomy/LIFT_LABELS.jsonl"
    if taxonomy.is_file():
        for line in taxonomy.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            result.setdefault(str(row["task_id"]), {})["lift_type"] = str(row.get("lift_type") or "")
    baseline = policy.get("baseline") if isinstance(policy.get("baseline"), dict) else {}
    _ = baseline  # Policy loading is also a schema/existence gate for the audit.
    return result


def main() -> int:
    args = parse_args()
    suite_path = args.suite if args.suite.is_absolute() else ROOT / args.suite
    suite = load_json(suite_path)
    root = ROOT / str(suite["task_root"])
    selected = [str(value) for value in suite.get("task_ids") or []]
    requested_ids = list(args.task_ids or [])
    if args.task_list:
        task_list_path = args.task_list if args.task_list.is_absolute() else ROOT / args.task_list
        requested_ids.extend(
            line.strip()
            for line in task_list_path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        )
    if requested_ids:
        requested = set(requested_ids)
        unknown = requested - set(selected)
        if unknown:
            raise SystemExit(f"unknown task ids: {', '.join(sorted(unknown))}")
        selected = [value for value in selected if value in requested]
    task_labels = labels()
    external = {
        path.name
        for path in (ROOT / "benchmark/external50").iterdir()
        if path.is_dir()
    }
    tasks = []
    for task_id in selected:
        label = task_labels.get(task_id, {})
        tasks.append(
            audit_task(
                root / task_id,
                release_group="external50" if task_id in external else "frozen_python150",
                lift_type=label.get("lift_type"),
                primary_coupling=label.get("primary_coupling"),
            )
        )

    output = args.output if args.output.is_absolute() else ROOT / args.output
    reviews_dir = output / "reviews"
    if not args.check:
        output.mkdir(parents=True, exist_ok=True)
        reviews_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": AUDIT_SCHEMA,
            "suite_id": suite.get("suite_id"),
            "task_set_sha256": suite.get("task_set_sha256"),
            "generated_at": datetime.now(UTC).isoformat(),
            "task_count": len(tasks),
            "tasks": tasks,
        }
        (output / "machine_audit.json").write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        write_summary_csv(output / "summary.csv", tasks)
        if args.write_templates:
            for task in tasks:
                path = reviews_dir / f"{task['task_id']}.json"
                if not path.exists():
                    path.write_text(
                        json.dumps(review_template(task), indent=2, sort_keys=True) + "\n",
                        encoding="utf-8",
                    )

    review_errors: dict[str, list[str]] = {}
    review_verdicts: Counter[str] = Counter()
    for task in tasks:
        path = reviews_dir / f"{task['task_id']}.json"
        if not path.is_file():
            review_errors[task["task_id"]] = ["review file missing"]
            continue
        try:
            review = load_json(path)
        except (json.JSONDecodeError, SystemExit) as exc:
            review_errors[task["task_id"]] = [f"invalid review JSON: {exc}"]
            continue
        errors = validate_review(review, task)
        if errors:
            review_errors[task["task_id"]] = errors
        else:
            review_verdicts[str(review["overall_verdict"])] += 1

    strict_invalid = [task for task in tasks if not task["strict_validation"]["valid"]]
    mapping_invalid = [task for task in tasks if task["mapping_issues"]]
    contract_invalid = [task for task in tasks if task["behavior_contract_issues"]]
    print(f"Machine audit: {len(tasks)} tasks")
    print(f"Strict validation: {len(tasks) - len(strict_invalid)}/{len(tasks)}")
    print(f"Mapping clean: {len(tasks) - len(mapping_invalid)}/{len(tasks)}")
    print(f"Behavior-contract metadata clean: {len(tasks) - len(contract_invalid)}/{len(tasks)}")
    print(f"Completed reviews: {len(tasks) - len(review_errors)}/{len(tasks)}")
    if review_verdicts:
        print("Review verdicts: " + ", ".join(f"{key}={value}" for key, value in sorted(review_verdicts.items())))

    if args.check:
        failures: list[str] = []
        failures.extend(f"{task['task_id']}: strict validation failed" for task in strict_invalid)
        failures.extend(f"{task['task_id']}: mapping issues" for task in mapping_invalid)
        failures.extend(f"{task['task_id']}: behavior-contract issues" for task in contract_invalid)
        failures.extend(
            f"{task_id}: {'; '.join(errors[:3])}"
            for task_id, errors in sorted(review_errors.items())
        )
        non_closed = sum(value for key, value in review_verdicts.items() if key != "closed")
        if non_closed:
            failures.append(f"{non_closed} completed reviews are not closed")
        if failures:
            print("Contract-closure check failed:", file=sys.stderr)
            for failure in failures[:80]:
                print(f"- {failure}", file=sys.stderr)
            if len(failures) > 80:
                print(f"- ... {len(failures) - 80} more", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
