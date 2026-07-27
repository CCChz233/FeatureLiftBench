#!/usr/bin/env python3
"""Revalidate all Python-150 Oracle submissions under the frozen v2 protocol."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "harness"
if str(HARNESS) not in sys.path:
    sys.path.insert(0, str(HARNESS))

from featureliftbench.docker_eval import DEFAULT_EVAL_IMAGE, evaluate_submission_docker
from featureliftbench.evaluator import evaluate_submission


POLICY_ID = "featureliftbench.full_repository_no_hint_main.v2"
SCHEMA_VERSION = "featureliftbench.v2_oracle_revalidation.v1"
DEFAULT_OUTPUT = ROOT / "reports" / "audits" / "v2_oracle_revalidation"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--backend", choices=("docker", "local"), default="docker")
    parser.add_argument("--image", default=DEFAULT_EVAL_IMAGE)
    parser.add_argument(
        "--keep-passing-outputs",
        action="store_true",
        help="retain verbose evaluator output for successful repetitions",
    )
    parser.add_argument(
        "--task-id",
        action="append",
        dest="task_ids",
        help="limit to a task id; repeatable (development only)",
    )
    return parser.parse_args()


def _task_dirs(task_ids: list[str] | None) -> list[Path]:
    root = ROOT / "benchmark" / "tasks"
    if task_ids:
        paths = [root / task_id for task_id in task_ids]
    else:
        paths = sorted(
            path
            for path in root.iterdir()
            if path.is_dir() and (path / "metadata.json").is_file()
        )
    missing = [path.name for path in paths if not (path / "metadata.json").is_file()]
    if missing:
        raise ValueError(f"unknown task ids: {', '.join(missing)}")
    return paths


def _stable_result(result: dict[str, Any]) -> dict[str, Any]:
    compactness = result.get("compactness")
    if not isinstance(compactness, dict):
        compactness = {}
    provenance = compactness.get("source_provenance")
    if not isinstance(provenance, dict):
        provenance = {}
    return {
        "status": result.get("status"),
        "build_pass": result.get("build_pass"),
        "test_pass": result.get("test_pass"),
        "original_import_pass": result.get("original_import_pass"),
        "public_pass": (result.get("public_tests") or {}).get("passed"),
        "hidden_pass": (result.get("hidden_tests") or {}).get("passed"),
        "scores": result.get("scores") or {},
        "metrics": {
            key: (result.get("metrics") or {}).get(key)
            for key in (
                "file_count",
                "loc",
                "reference_loc",
                "dependency_count",
                "suspicious_file_count",
            )
        },
        "compactness": {
            key: compactness.get(key)
            for key in (
                "status",
                "reference_loc",
                "submitted_loc",
                "reference_file_count",
                "submitted_file_count",
                "copied_loc",
                "copied_fraction",
                "extraction_ratio_to_reference",
                "runtime_dependency_count",
                "unapproved_external_dependency_count",
                "path_leakage",
                "forbidden_source_import",
                "compactness_class",
            )
        },
        "source": {
            key: provenance.get(key)
            for key in (
                "policy_id",
                "source_repo_id",
                "source_snapshot_id",
                "archive_sha256",
                "source_digest",
                "resolved_commit",
                "snapshot_scope",
                "status",
            )
        },
        "errors": result.get("errors") or [],
    }


def _fingerprint(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _run_one(
    *,
    task_dir: Path,
    repetition: int,
    output_root: Path,
    backend: str,
    image: str,
    keep_passing_outputs: bool,
) -> dict[str, Any]:
    task_id = task_dir.name
    oracle = ROOT / "benchmark" / "submissions" / task_id / "oracle"
    output = output_root / "work" / f"repeat-{repetition}" / task_id
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    try:
        if backend == "docker":
            result = evaluate_submission_docker(
                task_dir,
                oracle,
                output,
                image=image,
            )
        else:
            result = evaluate_submission(task_dir, oracle, output)
        stable = _stable_result(result)
        passed = (
            stable["status"] == "passed"
            and stable["build_pass"] is True
            and stable["test_pass"] is True
            and stable["original_import_pass"] is True
            and stable["public_pass"] is True
            and stable["hidden_pass"] is True
            and stable["scores"].get("functional_gate") == 1.0
            and stable["source"].get("status") == "ready"
            and stable["source"].get("snapshot_scope")
            in {"full_tracked_tree", "curated_source_tree"}
            and stable["compactness"].get("status") == "ok"
            and isinstance(stable["compactness"].get("reference_loc"), int)
        )
        record = {
            "task_id": task_id,
            "repetition": repetition,
            "backend": backend,
            "passed": passed,
            "fingerprint": _fingerprint(stable),
            "result": stable,
        }
    except Exception as exc:  # noqa: BLE001 - preserve every task failure
        record = {
            "task_id": task_id,
            "repetition": repetition,
            "backend": backend,
            "passed": False,
            "fingerprint": "",
            "exception": f"{type(exc).__name__}: {exc}",
        }
    if record["passed"] and not keep_passing_outputs:
        shutil.rmtree(output, ignore_errors=True)
    return record


def _image_identity(image: str, backend: str) -> dict[str, str]:
    if backend != "docker":
        return {"name": "", "id": "", "backend": "local"}
    completed = subprocess.run(
        ["docker", "image", "inspect", image, "--format", "{{.Id}}"],
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "name": image,
        "id": completed.stdout.strip(),
        "backend": "docker",
    }


def _write_markdown(payload: dict[str, Any], path: Path) -> None:
    summary = payload["summary"]
    failed = payload["failed_task_ids"]
    unstable = payload["unstable_task_ids"]
    lines = [
        "# FeatureLiftBench v2 Oracle Revalidation",
        "",
        f"- Gate: **{'PASS' if payload['gate_pass'] else 'FAIL'}**",
        f"- Backend: `{payload['environment']['backend']}`",
        f"- Tasks: {summary['task_count']}",
        f"- Repetitions per task: {summary['repetitions']}",
        f"- Passing runs: {summary['passed_runs']}/{summary['expected_runs']}",
        f"- Stable tasks: {summary['stable_tasks']}/{summary['task_count']}",
        f"- Failed tasks: {len(failed)}",
        f"- Unstable tasks: {len(unstable)}",
        "",
    ]
    if failed:
        lines.extend(["## Failed tasks", "", *[f"- `{item}`" for item in failed], ""])
    if unstable:
        lines.extend(
            ["## Unstable tasks", "", *[f"- `{item}`" for item in unstable], ""]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = _parse_args()
    if args.repetitions < 1:
        raise ValueError("--repetitions must be positive")
    if args.workers < 1:
        raise ValueError("--workers must be positive")
    tasks = _task_dirs(args.task_ids)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)

    jobs = [
        (task_dir, repetition)
        for repetition in range(1, args.repetitions + 1)
        for task_dir in tasks
    ]
    records: list[dict[str, Any]] = []
    completed_count = 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(
                _run_one,
                task_dir=task_dir,
                repetition=repetition,
                output_root=output,
                backend=args.backend,
                image=args.image,
                keep_passing_outputs=args.keep_passing_outputs,
            ): (task_dir.name, repetition)
            for task_dir, repetition in jobs
        }
        for future in as_completed(futures):
            record = future.result()
            records.append(record)
            completed_count += 1
            mark = "PASS" if record["passed"] else "FAIL"
            print(
                f"[{completed_count:03d}/{len(jobs):03d}] {mark} "
                f"r{record['repetition']} {record['task_id']}",
                flush=True,
            )

    records.sort(key=lambda item: (item["task_id"], item["repetition"]))
    by_task: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        by_task.setdefault(str(record["task_id"]), []).append(record)
    failed_task_ids = sorted(
        task_id
        for task_id, task_records in by_task.items()
        if not all(record["passed"] for record in task_records)
    )
    unstable_task_ids = sorted(
        task_id
        for task_id, task_records in by_task.items()
        if len({record["fingerprint"] for record in task_records}) != 1
    )
    expected_runs = len(tasks) * args.repetitions
    passed_runs = sum(bool(record["passed"]) for record in records)
    gate_pass = (
        len(tasks) == 150
        and args.repetitions >= 3
        and passed_runs == expected_runs
        and not failed_task_ids
        and not unstable_task_ids
    )
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "policy_id": POLICY_ID,
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "gate_pass": gate_pass,
        "environment": {
            **_image_identity(args.image, args.backend),
            "python": sys.version,
        },
        "summary": {
            "task_count": len(tasks),
            "repetitions": args.repetitions,
            "expected_runs": expected_runs,
            "passed_runs": passed_runs,
            "stable_tasks": len(tasks) - len(unstable_task_ids),
        },
        "failed_task_ids": failed_task_ids,
        "unstable_task_ids": unstable_task_ids,
        "runs": records,
    }
    (output / "summary.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    _write_markdown(payload, output / "summary.md")
    work = output / "work"
    if work.is_dir() and not any(work.rglob("result.json")):
        shutil.rmtree(work)
    print(
        f"Oracle v2 gate: {'PASS' if gate_pass else 'FAIL'}; "
        f"{passed_runs}/{expected_runs} runs; "
        f"{len(unstable_task_ids)} unstable tasks.",
        flush=True,
    )
    return 0 if gate_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
