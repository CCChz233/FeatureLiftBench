#!/usr/bin/env python3
"""Sync task requirements.lock files from metadata allowed_dependencies."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "harness") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "harness"))

from featureliftbench.benchmark_wheels import (  # noqa: E402
    expand_with_transitive_deps,
    load_benchmark_wheel_specs,
    resolve_wheel_spec,
)
from featureliftbench.dependency_audit import dependency_alias, list_task_dirs, normalized_allowed_set  # noqa: E402
from featureliftbench.metrics import dependency_name  # noqa: E402
from featureliftbench.paths import BENCHMARK_ROOT, TASKS_DIR  # noqa: E402


def lock_text_for_metadata(metadata: dict) -> tuple[str, list[str]]:
    environment = metadata.get("environment")
    if not isinstance(environment, dict):
        return "", []

    allowed_raw = environment.get("allowed_dependencies")
    if not isinstance(allowed_raw, list) or not allowed_raw:
        return "", []

    base_packages = [
        dependency_alias(item)
        for item in allowed_raw
        if isinstance(item, str) and dependency_name(item)
    ]
    expanded_packages = expand_with_transitive_deps(base_packages)

    specs = load_benchmark_wheel_specs()
    lines: list[str] = []
    for package in expanded_packages:
        spec = resolve_wheel_spec(package) or specs.get(package)
        if not spec:
            raise ValueError(f"no benchmark wheel pin for dependency: {package}")
        lines.append(spec)
    return "\n".join(sorted(set(lines), key=str.lower)) + "\n", expanded_packages


def sync_task_lock(task_dir: Path, *, dry_run: bool = False, update_metadata: bool = True) -> bool:
    metadata_path = task_dir / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata.get("language") == "go":
        return False

    allowed = normalized_allowed_set(metadata)
    if not allowed:
        return False

    lock_path = task_dir / "requirements.lock"
    new_text, expanded_packages = lock_text_for_metadata(metadata)
    old_text = lock_path.read_text(encoding="utf-8") if lock_path.is_file() else ""

    metadata_changed = False
    if update_metadata:
        environment = metadata.setdefault("environment", {})
        if isinstance(environment, dict):
            current_allowed = sorted(
                {
                    dependency_alias(item)
                    for item in environment.get("allowed_dependencies", [])
                    if isinstance(item, str)
                }
            )
            target_allowed = sorted(set(expanded_packages))
            if current_allowed != target_allowed:
                environment["allowed_dependencies"] = target_allowed
                metadata_changed = True

    if old_text == new_text and not metadata_changed:
        return False

    if dry_run:
        print(f"would update {task_dir.name}")
    else:
        lock_path.write_text(new_text, encoding="utf-8")
        if metadata_changed:
            metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"updated {task_dir.name}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=TASKS_DIR,
        help="task dataset root (default: benchmark/tasks)",
    )
    parser.add_argument(
        "--staging",
        action="store_true",
        help="also sync benchmark/staging tasks that exist under --root sibling staging/",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    roots = [args.root.resolve()]
    if args.staging:
        staging_root = BENCHMARK_ROOT / "staging"
        if staging_root.is_dir():
            roots.append(staging_root)

    updated = 0
    for root in roots:
        for task_dir in list_task_dirs(root):
            try:
                if sync_task_lock(task_dir, dry_run=args.dry_run):
                    updated += 1
            except ValueError as exc:
                print(f"ERROR {task_dir.name}: {exc}", file=sys.stderr)
                return 1

    print(f"{'would update' if args.dry_run else 'updated'} {updated} task lock files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
