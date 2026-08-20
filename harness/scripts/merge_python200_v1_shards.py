#!/usr/bin/env python3
"""Merge four 50-task V1 shard suites into one Python-200 suite.json."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "harness") not in sys.path:
    sys.path.insert(0, str(ROOT / "harness"))

from featureliftbench.agent_runner import _sum_agent_usage  # noqa: E402
from featureliftbench.suite_utils import compact_suite_run_entry  # noqa: E402
from featureliftbench.suite_utils import rebuild_suite_summary  # noqa: E402

SUITE_JSON = ROOT / "benchmark/selection/python200_suite.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def merge_shards(output_dir: Path, shard_dirs: list[Path]) -> dict[str, Any]:
    expected = _load(SUITE_JSON)["task_ids"]
    if len(expected) != 200:
        raise SystemExit(f"python200 suite has {len(expected)} tasks, expected 200")

    by_task: dict[str, tuple[Path, dict[str, Any]]] = {}
    sources: list[dict[str, Any]] = []
    template: dict[str, Any] | None = None
    for shard_dir in shard_dirs:
        suite_path = shard_dir / "suite.json"
        if not suite_path.is_file():
            raise SystemExit(f"missing {suite_path}")
        suite = _load(suite_path)
        if template is None:
            template = suite
        runs = [row for row in suite.get("runs") or [] if isinstance(row, dict)]
        sources.append(
            {
                "suite_dir": str(shard_dir),
                "profile": ((suite.get("agent_config") or {}).get("profile")),
                "n_runs": len(runs),
            }
        )
        for row in runs:
            task_id = row.get("task_id")
            if not isinstance(task_id, str) or not task_id:
                continue
            if task_id in by_task:
                raise SystemExit(f"duplicate task {task_id} in {shard_dir}")
            by_task[task_id] = (shard_dir, row)

    missing = [tid for tid in expected if tid not in by_task]
    extra = sorted(set(by_task) - set(expected))
    if missing or extra:
        raise SystemExit(
            f"merge mismatch missing={len(missing)} extra={len(extra)} "
            f"missing_head={missing[:5]} extra_head={extra[:5]}"
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    full_runs: list[dict[str, Any]] = []
    for task_id in expected:
        shard_dir, row = by_task[task_id]
        src = (shard_dir / task_id).resolve()
        dest = output_dir / task_id
        if not src.is_dir():
            raise SystemExit(f"missing task dir {src}")
        if dest.is_symlink():
            dest.unlink()
        elif dest.exists():
            raise SystemExit(f"refusing to replace existing path {dest}")
        dest.symlink_to(src)
        run_path = src / "run.json"
        full_runs.append(_load(run_path) if run_path.is_file() else row)

    assert template is not None
    compact_runs = [
        compact_suite_run_entry(run) if "evaluation" in run else run for run in full_runs
    ]
    payload = dict(template)
    payload.update(
        {
            "mode": "suite",
            "checkpoint": False,
            "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "output_dir": str(output_dir),
            "merged_from_shards": sources,
            "method_label": "v1",
            "summary": rebuild_suite_summary(full_runs),
            "agent_usage_totals": _sum_agent_usage(full_runs),
            "runs": compact_runs,
        }
    )
    payload.pop("checkpoint_progress", None)
    (output_dir / "suite.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "SHARD_MANIFEST.json").write_text(
        json.dumps(
            {
                "schema_version": "featureliftbench.python200_v1_shard_merge.v1",
                "n_tasks": len(compact_runs),
                "shards": sources,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("shards", nargs="+", type=Path)
    args = parser.parse_args()
    if len(args.shards) != 4:
        raise SystemExit("expected exactly 4 shard directories")
    payload = merge_shards(args.output, args.shards)
    summary = payload.get("summary") or {}
    print(
        json.dumps(
            {
                "output": str(args.output),
                "total": summary.get("total"),
                "passed": summary.get("passed"),
                "functional_passed": summary.get("functional_passed"),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
