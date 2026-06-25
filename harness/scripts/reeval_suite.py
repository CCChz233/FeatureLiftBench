#!/usr/bin/env python3
"""Re-evaluate existing suite submissions without re-running agents."""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "harness") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "harness"))

from featureliftbench.docker_eval import evaluate_submission_docker  # noqa: E402
from featureliftbench.evaluator import evaluate_submission  # noqa: E402
from featureliftbench.paths import TASKS_DIR  # noqa: E402
from featureliftbench.suite_utils import compact_suite_run_entry  # noqa: E402
from featureliftbench.suite_utils import evaluation_payload  # noqa: E402
from featureliftbench.suite_utils import rebuild_suite_summary  # noqa: E402
from featureliftbench.suite_utils import run_status  # noqa: E402
from featureliftbench.suite_utils import utc_now  # noqa: E402


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def resolve_task_dir(task_id: str, tasks_root: Path | None) -> Path:
    root = tasks_root or TASKS_DIR
    task_dir = root / task_id
    if not task_dir.is_dir():
        raise FileNotFoundError(f"task directory not found: {task_dir}")
    return task_dir


def reeval_task(
    *,
    suite_dir: Path,
    task_id: str,
    tasks_root: Path | None,
    use_docker: bool,
    docker_image: str,
    dry_run: bool,
) -> dict[str, Any]:
    task_run_dir = suite_dir / task_id
    run_json_path = task_run_dir / "run.json"
    if not run_json_path.is_file():
        raise FileNotFoundError(f"missing run.json: {run_json_path}")

    run_data = load_json(run_json_path)
    submission_dir = task_run_dir / "submission"
    if not submission_dir.is_dir():
        raise FileNotFoundError(f"missing submission dir: {submission_dir}")

    task_dir = resolve_task_dir(task_id, tasks_root)
    eval_output_dir = task_run_dir / "eval"

    if dry_run:
        return {
            "task_id": task_id,
            "status": run_data.get("status", "failed"),
            "dry_run": True,
        }

    if use_docker:
        eval_result = evaluate_submission_docker(
            task_dir=task_dir,
            submission_dir=submission_dir,
            output_dir=eval_output_dir,
            image=docker_image,
            use_docker=True,
        )
    else:
        eval_result = evaluate_submission(task_dir, submission_dir, eval_output_dir)

    agent = run_data.get("agent") if isinstance(run_data.get("agent"), dict) else {}
    submission = run_data.get("submission") if isinstance(run_data.get("submission"), dict) else {}
    agent_passed = bool(agent.get("passed", False))
    submission_exists = submission.get("exists", submission_dir.is_dir())

    run_data["generated_at"] = utc_now()
    run_data["evaluation"] = evaluation_payload(eval_result, eval_output_dir)
    run_data["status"] = run_status(
        validation_ok=True,
        agent_passed=agent_passed,
        submission_exists=bool(submission_exists),
        eval_result=eval_result,
    )
    write_json(run_json_path, run_data)

    return {
        "task_id": task_id,
        "status": run_data["status"],
        "eval_status": eval_result.get("status", "failed"),
        "final_score": eval_result.get("scores", {}).get("final_score", 0.0),
    }


def update_suite_json(suite_dir: Path) -> dict[str, Any]:
    suite_path = suite_dir / "suite.json"
    if not suite_path.is_file():
        raise FileNotFoundError(f"missing suite.json: {suite_path}")

    suite = load_json(suite_path)
    runs: list[dict[str, Any]] = []
    for entry in suite.get("runs") or []:
        task_id = entry.get("task_id")
        if not isinstance(task_id, str) or not task_id:
            continue
        run_json_path = suite_dir / task_id / "run.json"
        if not run_json_path.is_file():
            continue
        runs.append(load_json(run_json_path))

    suite["generated_at"] = utc_now()
    suite["summary"] = rebuild_suite_summary(runs)
    suite["runs"] = [compact_suite_run_entry(run) for run in runs]
    write_json(suite_path, suite)
    return suite


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("suite_dir", type=Path, help="Existing run-agent suite directory")
    parser.add_argument("--tasks-root", type=Path, default=None, help="Override benchmark tasks root")
    parser.add_argument("--workers", type=int, default=4, help="Parallel re-eval workers")
    parser.add_argument("--task-id", action="append", dest="task_ids", help="Limit to specific task IDs")
    parser.add_argument("--dry-run", action="store_true", help="List tasks without re-evaluating")
    parser.add_argument("--docker", action="store_true", help="Run evaluation inside Docker image")
    parser.add_argument(
        "--docker-image",
        default="featureliftbench-eval:latest",
        help="Docker image for --docker (default: featureliftbench-eval:latest)",
    )
    args = parser.parse_args()

    suite_dir = args.suite_dir.resolve()
    suite_path = suite_dir / "suite.json"
    if not suite_path.is_file():
        raise SystemExit(f"missing suite.json: {suite_path}")

    suite = load_json(suite_path)
    task_ids = args.task_ids or [run.get("task_id") for run in suite.get("runs") or []]
    task_ids = [task_id for task_id in task_ids if isinstance(task_id, str) and task_id]
    if not task_ids:
        raise SystemExit("no tasks to re-evaluate")

    results: list[dict[str, Any]] = []
    worker_count = max(1, int(args.workers))

    if worker_count == 1:
        for task_id in task_ids:
            results.append(
                reeval_task(
                    suite_dir=suite_dir,
                    task_id=task_id,
                    tasks_root=args.tasks_root,
                    use_docker=args.docker,
                    docker_image=args.docker_image,
                    dry_run=args.dry_run,
                )
            )
    else:
        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            futures = {
                executor.submit(
                    reeval_task,
                    suite_dir=suite_dir,
                    task_id=task_id,
                    tasks_root=args.tasks_root,
                    use_docker=args.docker,
                    docker_image=args.docker_image,
                    dry_run=args.dry_run,
                ): task_id
                for task_id in task_ids
            }
            for future in as_completed(futures):
                results.append(future.result())

    if not args.dry_run:
        updated = update_suite_json(suite_dir)
        summary = updated.get("summary", {})
        print(
            f"Re-evaluated {len(results)} tasks: "
            f"{summary.get('passed', 0)}/{summary.get('total', 0)} passed, "
            f"avg final_score={summary.get('average_final_score', 0.0)}"
        )
    else:
        print(f"Dry run: would re-evaluate {len(results)} tasks in {suite_dir}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
