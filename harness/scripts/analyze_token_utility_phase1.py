#!/usr/bin/env python3
"""Phase-1 token-utility gold labels: replay unique submission trees and eval.

Offline analysis only. Does not modify original suite eval/result.json.
Last tree is trusted when its hash matches the on-disk package; earlier
unique trees are evaluated with the official Docker evaluator.
"""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "harness") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "harness"))

from featureliftbench.docker_eval import evaluate_submission_docker  # noqa: E402
from featureliftbench.token_utility_replay import (  # noqa: E402
    attach_disk_hash,
    earliest_pass,
    original_scores,
    replay_events,
    resolve_replay_repo,
    sample_unique,
    score_tuple,
)

DEFAULT_TASKS_ROOT = _REPO_ROOT / "benchmark" / "python200_tasks"
DEFAULT_IMAGE = "featureliftbench-eval:latest"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def iter_suite_tasks(suite_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in suite_dir.iterdir()
        if path.is_dir() and (path / "agent").is_dir()
    )


def replay_task(task_dir: Path, tasks_root: Path, *, all_unique: bool = False) -> dict[str, Any]:
    events = task_dir / "agent" / "openhands_events.jsonl"
    audit = task_dir / "agent" / "context_audit.jsonl"
    repo = resolve_replay_repo(task_dir, tasks_root)
    result = replay_events(
        events_path=events,
        repo_src=repo,
        audit_path=audit if audit.is_file() else None,
        keep_files=False,
    )
    attach_disk_hash(result, task_dir / "submission" / "featurelifted")
    orig = original_scores(task_dir)
    unique = [
        {
            "index": item.index,
            "tree_hash": item.tree_hash,
            "tokens": item.tokens,
            "n_files": item.n_files,
            "n_bytes": item.n_bytes,
            "source": item.source,
        }
        for item in result.unique
    ]
    sampled = list(result.unique) if all_unique else sample_unique(result.unique)
    return {
        "task_id": task_dir.name,
        "replay_ok": result.last_matches_disk,
        "last_hash": result.last_hash,
        "disk_hash": result.disk_hash,
        "total_tokens": result.total_tokens,
        "editor_writes": result.editor_writes,
        "terminal_runs": result.terminal_runs,
        "terminal_errors": result.terminal_errors,
        "n_unique": len(result.unique),
        "unique": unique,
        "sampled_hashes": [item.tree_hash for item in sampled],
        "original": orig,
        "error": result.error,
    }


def materialize_samples(
    task_dir: Path,
    tasks_root: Path,
    hashes: set[str],
    dest_root: Path,
) -> None:
    if not hashes:
        return
    replay_events(
        events_path=task_dir / "agent" / "openhands_events.jsonl",
        repo_src=resolve_replay_repo(task_dir, tasks_root),
        audit_path=task_dir / "agent" / "context_audit.jsonl",
        keep_files=False,
        save_hashes=hashes,
        save_root=dest_root,
    )


def eval_snapshot(
    *,
    task_id: str,
    tree_hash: str,
    submission_dir: Path,
    output_dir: Path,
    tasks_root: Path,
    image: str,
) -> dict[str, Any]:
    existing = output_dir / "result.json"
    if existing.is_file():
        try:
            result = json.loads(existing.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            result = {}
        else:
            payload = score_tuple(result)
            payload["task_id"] = task_id
            payload["tree_hash"] = tree_hash
            payload["eval_status"] = result.get("status")
            payload["cached"] = True
            return payload
    output_dir.mkdir(parents=True, exist_ok=True)
    try:
        result = evaluate_submission_docker(
            task_dir=tasks_root / task_id,
            submission_dir=submission_dir,
            output_dir=output_dir,
            image=image,
            use_docker=True,
        )
    except Exception as exc:  # noqa: BLE001
        return {
            "task_id": task_id,
            "tree_hash": tree_hash,
            "functional_gate": None,
            "eval_status": "error",
            "error": f"{type(exc).__name__}: {exc}",
        }
    payload = score_tuple(result)
    payload["task_id"] = task_id
    payload["tree_hash"] = tree_hash
    payload["eval_status"] = result.get("status")
    return payload


def summarize_task(row: dict[str, Any]) -> dict[str, Any]:
    snapshots = row.get("snapshots") or []
    orig_gate = (row.get("original") or {}).get("functional_gate")
    gold = earliest_pass(snapshots)
    total = row.get("total_tokens") or 0
    out = {
        "task_id": row["task_id"],
        "replay_ok": row.get("replay_ok"),
        "original_functional_gate": orig_gate,
        "total_tokens": total,
        "n_unique": row.get("n_unique"),
        "n_evaled": sum(1 for item in snapshots if item.get("evaled")),
        "earliest_pass_tokens": gold.get("tokens") if gold else None,
        "earliest_pass_frac": (
            gold["tokens"] / total if gold and gold.get("tokens") is not None and total else None
        ),
        "earliest_pass_hash": gold.get("tree_hash") if gold else None,
        "gate_at_2m": None,
        "passed_before_2m": None,
        "late_pass": None,
    }
    at_2m = None
    for item in snapshots:
        tokens = item.get("tokens")
        if tokens is None:
            continue
        if tokens <= 2_000_000:
            at_2m = item
        else:
            break
    if at_2m is not None:
        out["gate_at_2m"] = at_2m.get("functional_gate")
        out["passed_before_2m"] = at_2m.get("functional_gate") == 1.0
    if orig_gate == 1.0:
        out["late_pass"] = bool(
            gold
            and gold.get("tokens") is not None
            and gold["tokens"] >= 2_000_000
        )
    return out


def run_check(
    suite_dir: Path,
    tasks_root: Path,
    task_ids: list[str] | None,
    *,
    all_unique: bool = False,
) -> list[dict[str, Any]]:
    rows = []
    tasks = iter_suite_tasks(suite_dir)
    if task_ids:
        wanted = set(task_ids)
        tasks = [path for path in tasks if path.name in wanted]
    for task_dir in tasks:
        row = replay_task(task_dir, tasks_root, all_unique=all_unique)
        print(
            f"{row['task_id']:48} match={row['replay_ok']} "
            f"uniq={row['n_unique']:3} gate={row['original'].get('functional_gate')} "
            f"term_err={row['terminal_errors']}"
        )
        rows.append(row)
    matched = sum(1 for row in rows if row["replay_ok"])
    print(f"replay_ok {matched}/{len(rows)}")
    return rows


def run_eval(
    *,
    suite_dir: Path,
    tasks_root: Path,
    work_root: Path,
    image: str,
    workers: int,
    task_ids: list[str] | None,
    check_rows: list[dict[str, Any]] | None = None,
    all_unique: bool = False,
) -> dict[str, Any]:
    if check_rows is None:
        check_rows = run_check(suite_dir, tasks_root, task_ids, all_unique=all_unique)
    trees_root = work_root / "trees"
    eval_root = work_root / "evals"
    jobs: list[dict[str, Any]] = []
    reports: list[dict[str, Any]] = []
    for row in check_rows:
        task_dir = suite_dir / row["task_id"]
        unique_by_hash = {item["tree_hash"]: item for item in row["unique"]}
        snapshots: list[dict[str, Any]] = []
        hashes_to_eval: set[str] = set()
        if not row["replay_ok"]:
            row["snapshots"] = []
            row["summary"] = summarize_task(row)
            reports.append(row)
            continue
        for tree_hash in row["sampled_hashes"]:
            meta = dict(unique_by_hash[tree_hash])
            meta["evaled"] = False
            if tree_hash == row["last_hash"]:
                meta.update(row["original"])
                meta["evaled"] = True
                meta["source"] = "original_eval"
            else:
                hashes_to_eval.add(tree_hash)
                meta["source"] = "docker_eval"
            snapshots.append(meta)
        if hashes_to_eval:
            materialize_samples(task_dir, tasks_root, hashes_to_eval, trees_root / row["task_id"])
        for snap in snapshots:
            if snap.get("source") == "docker_eval":
                jobs.append(
                    {
                        "task_id": row["task_id"],
                        "tree_hash": snap["tree_hash"],
                        "submission_dir": trees_root / row["task_id"] / snap["tree_hash"],
                        "output_dir": eval_root / row["task_id"] / snap["tree_hash"],
                    }
                )
        row["snapshots"] = snapshots
        reports.append(row)

    def _run(job: dict[str, Any]) -> dict[str, Any]:
        return eval_snapshot(
            task_id=job["task_id"],
            tree_hash=job["tree_hash"],
            submission_dir=job["submission_dir"],
            output_dir=job["output_dir"],
            tasks_root=tasks_root,
            image=image,
        )

    print(f"eval jobs={len(jobs)} workers={workers}")
    results: dict[tuple[str, str], dict[str, Any]] = {}
    if jobs:
        if workers <= 1:
            for job in jobs:
                payload = _run(job)
                results[(payload["task_id"], payload["tree_hash"])] = payload
                print(
                    f"  eval {payload['task_id']} {payload['tree_hash'][:8]} "
                    f"gate={payload.get('functional_gate')}"
                )
        else:
            with ThreadPoolExecutor(max_workers=workers) as pool:
                futures = [pool.submit(_run, job) for job in jobs]
                for future in as_completed(futures):
                    try:
                        payload = future.result()
                    except Exception as exc:  # noqa: BLE001
                        print(f"  eval worker failed: {type(exc).__name__}: {exc}")
                        continue
                    results[(payload["task_id"], payload["tree_hash"])] = payload
                    print(
                        f"  eval {payload['task_id']} {payload['tree_hash'][:8]} "
                        f"gate={payload.get('functional_gate')}"
                    )
    for row in reports:
        for snap in row.get("snapshots") or []:
            if snap.get("source") != "docker_eval":
                continue
            payload = results.get((row["task_id"], snap["tree_hash"]))
            if payload:
                snap.update(
                    {
                        "functional_gate": payload.get("functional_gate"),
                        "build_pass": payload.get("build_pass"),
                        "public_tests_pass": payload.get("public_tests_pass"),
                        "hidden_tests_pass": payload.get("hidden_tests_pass"),
                        "isolation_pass": payload.get("isolation_pass"),
                        "evaled": True,
                    }
                )
        row["snapshots"] = sorted(
            row.get("snapshots") or [],
            key=lambda item: (item.get("tokens") is None, item.get("tokens") or 0, item.get("index") or 0),
        )
        row["summary"] = summarize_task(row)
    return {
        "suite": str(suite_dir),
        "tasks_root": str(tasks_root),
        "n_tasks": len(reports),
        "n_replay_ok": sum(1 for row in reports if row.get("replay_ok")),
        "n_eval_jobs": len(jobs),
        "reports": reports,
    }


def suite_rollup(payload: dict[str, Any]) -> dict[str, Any]:
    summaries = [row["summary"] for row in payload["reports"] if row.get("replay_ok")]
    passes = [row for row in summaries if row.get("original_functional_gate") == 1.0]
    fracs = [row["earliest_pass_frac"] for row in passes if row.get("earliest_pass_frac") is not None]
    late = [row for row in passes if row.get("late_pass")]
    known_2m = [row for row in passes if row.get("gate_at_2m") is not None]
    lost_at_2m = [row for row in known_2m if row.get("passed_before_2m") is False]
    def _median(values: list[float]) -> float | None:
        if not values:
            return None
        ordered = sorted(values)
        mid = len(ordered) // 2
        if len(ordered) % 2:
            return ordered[mid]
        return (ordered[mid - 1] + ordered[mid]) / 2
    return {
        "replay_ok": payload["n_replay_ok"],
        "assigned": payload["n_tasks"],
        "pass_with_gold": len(passes),
        "earliest_pass_frac_median": _median(fracs),
        "late_pass_n": len(late),
        "pass_with_2m_snapshot": len(known_2m),
        "would_fail_at_2m": len(lost_at_2m),
        "eval_jobs": payload["n_eval_jobs"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("check", "eval"))
    parser.add_argument("suites", nargs="+", type=Path)
    parser.add_argument("--tasks-root", type=Path, default=DEFAULT_TASKS_ROOT)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, default=None)
    parser.add_argument("--task-id", action="append", dest="task_ids")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--docker-image", default=DEFAULT_IMAGE)
    parser.add_argument(
        "--all-unique",
        action="store_true",
        help="Evaluate every unique tree instead of the default sample",
    )
    args = parser.parse_args()
    work_root = args.work_root or args.output.parent / "token_utility_phase1_work"
    reports = []
    for suite in args.suites:
        suite_dir = suite.resolve()
        if args.mode == "check":
            rows = run_check(
                suite_dir,
                args.tasks_root.resolve(),
                args.task_ids,
                all_unique=args.all_unique,
            )
            reports.append({"suite": str(suite_dir), "rows": rows})
        else:
            payload = run_eval(
                suite_dir=suite_dir,
                tasks_root=args.tasks_root.resolve(),
                work_root=work_root / suite_dir.name,
                image=args.docker_image,
                workers=args.workers,
                task_ids=args.task_ids,
                all_unique=args.all_unique,
            )
            payload["rollup"] = suite_rollup(payload)
            print("rollup", payload["rollup"])
            reports.append(payload)
    _write_json(args.output, {"mode": args.mode, "reports": reports})
    print("wrote", args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
