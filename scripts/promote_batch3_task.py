#!/usr/bin/env python3
"""Promote a batch3_pilot task into benchmark/tasks/ with normalized metadata."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "benchmark" / "batch3_pilot"
TASKS = ROOT / "benchmark" / "tasks"
SUBMISSIONS = ROOT / "benchmark" / "submissions"

EXCLUDE_NAMES = {
    ".pytest_cache",
    "__pycache__",
    "evaluator_config.yaml",
    "reference_solution",
}


def normalize_metadata(meta: dict) -> dict:
    """Convert pilot metadata to main-split schema (legacy tasks omit status)."""
    source = meta.get("source") or {}
    if not source.get("name"):
        repo_url = str(meta.get("repo", ""))
        source = {
            "name": source.get("name") or meta.get("feature_name", "").split()[0],
            "url": source.get("url") or repo_url,
            "commit": source.get("commit") or meta.get("commit", ""),
            "license": source.get("license") or meta.get("license", ""),
        }
    feature = meta.get("feature") or {}
    if not feature.get("name"):
        feature = {
            "name": meta.get("feature_name", ""),
            "description": feature.get("description", meta.get("hard_reason", "")),
            "source_entrypoints": feature.get("source_entrypoints", []),
            "included_behaviors": feature.get("included_behaviors", []),
            "excluded_behaviors": feature.get("excluded_behaviors", []),
        }
    entanglement = meta.get("entanglement") or {}
    output = meta.get("output") or {}
    environment = meta.get("environment") or {}
    tests = meta.get("tests") or {
        "public": "public_tests/",
        "hidden": "hidden_tests/",
        "command": "pytest",
    }

    tags = [t for t in meta.get("tags", []) if t not in {"pilot", "materialized"}]
    if "batch-3" not in tags:
        tags.insert(0, "batch-3")
    primary = entanglement.get("primary") or meta.get("feature_type", "")
    if primary and primary not in tags:
        tags.append(primary)

    # Fix output.import for audit gate: include symbols used in tests.
    task_id = meta["task_id"]
    if task_id.startswith("stevedore__"):
        output["import"] = (
            "from featurelifted import EntryPointSpec, ExtensionManager, NamedExtensionManager, "
            "NoMatches, MultipleMatches, error_on_conflict, ignore_conflicts"
        )
    elif task_id.startswith("tenacity__"):
        output["import"] = (
            "from featurelifted import Retrying, RetryError, retry_if_exception_type, "
            "retry_if_result, stop_after_attempt, wait_fixed, wait_chain, wait_exponential"
        )

    return {
        "task_id": meta["task_id"],
        "language": meta.get("language", "python"),
        "status": "main",
        "difficulty": meta.get("difficulty") or meta.get("difficulty_initial", "hard"),
        "tags": tags,
        "source": source,
        "feature": feature,
        "entanglement": entanglement,
        "output": output,
        "environment": environment,
        "tests": tests,
    }


def copy_task_tree(task_id: str) -> Path:
    src = PILOT / task_id
    dst = TASKS / task_id
    if not src.is_dir():
        raise FileNotFoundError(src)
    if dst.exists():
        raise FileExistsError(f"already exists: {dst}")

    def ignore(_dir: str, names: list[str]) -> set[str]:
        return {n for n in names if n in EXCLUDE_NAMES}

    shutil.copytree(src, dst, ignore=ignore)
    meta = json.loads((src / "metadata.json").read_text(encoding="utf-8"))
    normalized = normalize_metadata(meta)
    (dst / "metadata.json").write_text(json.dumps(normalized, indent=2) + "\n", encoding="utf-8")
    return dst


def install_oracle(task_id: str) -> None:
    ref = PILOT / task_id / "reference_solution" / "featurelifted"
    out = SUBMISSIONS / task_id / "oracle" / "featurelifted"
    if out.exists():
        shutil.rmtree(out.parent)
    shutil.copytree(ref, out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task_id")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    task_id = args.task_id
    if task_id == "py_hard3_pkginfo_metadata_001":
        print("refusing blocked task", file=sys.stderr)
        return 1
    if (TASKS / task_id).exists():
        print(f"already in main split: {task_id}", file=sys.stderr)
        return 1

    if args.dry_run:
        meta = json.loads((PILOT / task_id / "metadata.json").read_text())
        print(json.dumps(normalize_metadata(meta), indent=2))
        return 0

    dst = copy_task_tree(task_id)
    install_oracle(task_id)
    print(f"promoted task tree: {dst}")
    print(f"installed oracle: {SUBMISSIONS / task_id / 'oracle'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
