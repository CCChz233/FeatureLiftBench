#!/usr/bin/env python3
"""Close the offline dependency contract for the selected External-50 tasks."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "harness"))

from featureliftbench.benchmark_wheels import (  # noqa: E402
    expand_with_transitive_deps,
    resolve_wheel_spec,
)
from featureliftbench.dependency_audit import dependency_alias  # noqa: E402
from featureliftbench.metrics import dependency_name  # noqa: E402
from featureliftbench.task_render import render_public_task  # noqa: E402
from featureliftbench.task_spec import (  # noqa: E402
    compute_generated_task_hash,
    compute_spec_hash,
)


SELECTION_PATH = ROOT / "benchmark/selection/external50_expansion_20260731.json"
CLOSURE_ID = "python200-offline-dependency-closure-20260801-v1"
RELEASE_ROOT = ROOT / "benchmark/external50"
STAGING_ROOT = ROOT / "benchmark/staging"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def selected_task_dir(task_id: str) -> Path:
    released = RELEASE_ROOT / task_id
    if (released / "metadata.json").is_file():
        return released
    return STAGING_ROOT / task_id


def selected_task_ids() -> list[str]:
    selection = load_json(SELECTION_PATH)
    return sorted(
        row["task_id"]
        for row in selection["rows"]
        if row.get("disposition") == "selected"
    )


def closure_for(metadata: dict[str, Any]) -> list[str]:
    allowed = metadata.get("environment", {}).get("allowed_dependencies", [])
    roots = [
        dependency_alias(value)
        for value in allowed
        if isinstance(value, str) and dependency_name(value)
    ]
    return sorted(set(expand_with_transitive_deps(roots)))


def lock_text(packages: list[str]) -> str:
    if not packages:
        return "# no third-party dependencies\n"
    lines: list[str] = []
    for package in packages:
        spec = resolve_wheel_spec(package)
        if spec is None:
            raise ValueError(f"no canonical wheel pin for {package}")
        lines.append(spec)
    return "\n".join(sorted(set(lines), key=str.lower)) + "\n"


def expected_files(task_dir: Path) -> tuple[dict[str, Any], str, dict[str, Any] | None]:
    metadata = load_json(task_dir / "metadata.json")
    packages = closure_for(metadata)
    metadata["environment"]["allowed_dependencies"] = packages
    if packages:
        if metadata.get("dependency_closure_id") != CLOSURE_ID:
            metadata["task_revision"] = int(metadata.get("task_revision") or 1) + 1
        metadata["dependency_closure_id"] = CLOSURE_ID
        tags = metadata.setdefault("tags", [])
        if "offline-dependency-closed" not in tags:
            tags.append("offline-dependency-closed")

    task_md = render_public_task(metadata)
    metadata["spec_hash"] = compute_spec_hash(metadata["public_spec"])
    metadata["generated_task_hash"] = compute_generated_task_hash(task_md)

    manifest_path = task_dir / "evaluation/oracle_manifest.json"
    manifest = load_json(manifest_path) if manifest_path.is_file() else None
    if manifest is not None:
        manifest["runtime_dependencies"] = packages
    return metadata, task_md, manifest


def process(task_id: str, *, check: bool) -> bool:
    task_dir = selected_task_dir(task_id)
    metadata, task_md, manifest = expected_files(task_dir)
    lock = lock_text(metadata["environment"]["allowed_dependencies"])
    expected = {
        task_dir / "metadata.json": json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        task_dir / "TASK.md": task_md,
        task_dir / "requirements.lock": lock,
    }
    if manifest is not None:
        expected[task_dir / "evaluation/oracle_manifest.json"] = (
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
        )
    contract_path = task_dir / "evaluation/behavior_contract.json"
    if contract_path.is_file():
        contract = load_json(contract_path)
        contract["spec_sha256"] = compute_generated_task_hash(task_md)
        expected[contract_path] = json.dumps(contract, indent=2, ensure_ascii=False) + "\n"

    stale = [
        path
        for path, content in expected.items()
        if not path.is_file() or path.read_text(encoding="utf-8") != content
    ]
    if check:
        if stale:
            print(f"STALE {task_id}: {', '.join(path.name for path in stale)}")
        return bool(stale)
    for path in stale:
        path.write_text(expected[path], encoding="utf-8")
    if stale:
        print(f"closed {task_id}")
    return bool(stale)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    task_ids = selected_task_ids()
    if len(task_ids) != 50:
        raise SystemExit(f"expected 50 selected tasks, found {len(task_ids)}")
    changed = sum(process(task_id, check=args.check) for task_id in task_ids)
    if args.check:
        print(f"dependency closure check: {len(task_ids) - changed}/50 current")
        return 1 if changed else 0
    print(f"dependency closure updated {changed}/50 tasks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
