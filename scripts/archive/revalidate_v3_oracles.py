#!/usr/bin/env python3
"""Run the External-150 references three times in the hardened evaluator."""

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


POLICY_ID = "featureliftbench.full_repository_no_hint_main.v3"
SCHEMA_VERSION = "featureliftbench.v3_oracle_revalidation.v1"
DEFAULT_OUTPUT = ROOT / "reports" / "audits" / "v3_oracle_revalidation"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--image", default=DEFAULT_EVAL_IMAGE)
    parser.add_argument("--keep-passing-outputs", action="store_true")
    parser.add_argument(
        "--task-id",
        action="append",
        dest="task_ids",
        help="limit to a task id; repeatable (development only)",
    )
    return parser.parse_args()


def _task_dirs(task_ids: list[str] | None) -> list[Path]:
    tasks_root = ROOT / "benchmark" / "tasks"
    task_dirs = (
        [tasks_root / task_id for task_id in task_ids]
        if task_ids
        else sorted(
            path
            for path in tasks_root.iterdir()
            if path.is_dir() and (path / "metadata.json").is_file()
        )
    )
    missing = [path.name for path in task_dirs if not (path / "metadata.json").is_file()]
    if missing:
        raise ValueError(f"unknown task ids: {', '.join(missing)}")
    return task_dirs


def _stable_result(result: dict[str, Any]) -> dict[str, Any]:
    compactness = result.get("compactness")
    if not isinstance(compactness, dict):
        compactness = {}
    provenance = compactness.get("source_provenance")
    if not isinstance(provenance, dict):
        provenance = {}
    isolation = result.get("isolation")
    if not isinstance(isolation, dict):
        isolation = {}
    scores = result.get("scores")
    if not isinstance(scores, dict):
        scores = {}
    sandbox = result.get("sandbox")
    if not isinstance(sandbox, dict):
        sandbox = {}
    return {
        "status": result.get("status"),
        "build_pass": result.get("build_pass"),
        "public_tests_pass": result.get("public_tests_pass"),
        "hidden_tests_pass": result.get("hidden_tests_pass"),
        "isolation_pass": result.get("isolation_pass"),
        "test_pass": result.get("test_pass"),
        "original_import_pass": result.get("original_import_pass"),
        "functional_gate": scores.get("functional_gate"),
        "final_score": scores.get("final_score"),
        "evaluation_capsule_digest": result.get("evaluation_capsule_digest"),
        "isolation": {
            key: isolation.get(key)
            for key in (
                "pass",
                "forbidden_imports_pass",
                "forbidden_dependencies_pass",
                "forbidden_runtime_capabilities_pass",
                "runtime_import_origin_pass",
                "source_filesystem_absent",
                "network_disabled",
                "submission_location_pass",
                "mount_allowlist_pass",
                "verification_mode",
            )
        },
        "compactness_status": result.get("compactness_status"),
        "compactness": {
            key: compactness.get(key)
            for key in (
                "status",
                "execution_policy",
                "reference_loc",
                "submitted_loc",
                "reference_file_count",
                "submitted_file_count",
                "copied_loc",
                "copied_fraction",
                "extraction_ratio_to_reference",
                "runtime_dependency_count",
                "unapproved_external_dependency_count",
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
        "sandbox": {
            "backend": sandbox.get("backend"),
            "returncode": sandbox.get("docker_returncode"),
            "network": sandbox.get("network"),
            "read_only_rootfs": sandbox.get("read_only"),
            "cap_drop": sandbox.get("cap_drop"),
        },
        "errors": result.get("errors") or [],
    }


def _fingerprint(payload: dict[str, Any]) -> str:
    data = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(data).hexdigest()


def _passes(stable: dict[str, Any]) -> bool:
    isolation = stable["isolation"]
    required_isolation = (
        "forbidden_imports_pass",
        "forbidden_dependencies_pass",
        "forbidden_runtime_capabilities_pass",
        "runtime_import_origin_pass",
        "source_filesystem_absent",
        "network_disabled",
        "submission_location_pass",
        "mount_allowlist_pass",
    )
    capsule_digest = stable.get("evaluation_capsule_digest")
    compactness = stable["compactness"]
    source = stable["source"]
    sandbox = stable["sandbox"]
    return (
        stable["status"] == "passed"
        and stable["build_pass"] is True
        and stable["public_tests_pass"] is True
        and stable["hidden_tests_pass"] is True
        and stable["isolation_pass"] is True
        and stable["test_pass"] is True
        and stable["original_import_pass"] is True
        and stable["functional_gate"] == 1.0
        and stable["final_score"] == 1.0
        and isolation.get("verification_mode") == "docker_functional_capsule_v1"
        and all(isolation.get(key) is True for key in required_isolation)
        and isinstance(capsule_digest, str)
        and len(capsule_digest) == 64
        and stable["compactness_status"] == "ok"
        and compactness.get("status") == "ok"
        and compactness.get("execution_policy")
        == "static_read_only_no_submission_execution"
        and isinstance(compactness.get("reference_loc"), int)
        and source.get("policy_id") == "featureliftbench.full_repository_source.v2"
        and source.get("status") == "ready"
        and source.get("snapshot_scope") == "full_tracked_tree"
        and sandbox.get("backend") == "docker"
        and sandbox.get("returncode") == 0
        and sandbox.get("network") == "none"
        and sandbox.get("read_only_rootfs") is True
        and sandbox.get("cap_drop") == "ALL"
    )


def _run_one(
    task_dir: Path,
    repetition: int,
    output_root: Path,
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
        result = evaluate_submission_docker(task_dir, oracle, output, image=image)
        stable = _stable_result(result)
        passed = _passes(stable)
        record: dict[str, Any] = {
            "task_id": task_id,
            "repetition": repetition,
            "backend": "docker",
            "passed": passed,
            "fingerprint": _fingerprint(stable),
            "result": stable,
        }
    except Exception as exc:  # noqa: BLE001 - every failure belongs in evidence
        record = {
            "task_id": task_id,
            "repetition": repetition,
            "backend": "docker",
            "passed": False,
            "fingerprint": "",
            "exception": f"{type(exc).__name__}: {exc}",
        }
    if record["passed"] and not keep_passing_outputs:
        shutil.rmtree(output, ignore_errors=True)
    return record


def _image_identity(image: str) -> dict[str, str]:
    completed = subprocess.run(
        ["docker", "image", "inspect", image, "--format", "{{.Id}}"],
        capture_output=True,
        text=True,
        check=False,
    )
    return {"name": image, "id": completed.stdout.strip(), "backend": "docker"}


def _write_markdown(payload: dict[str, Any], path: Path) -> None:
    summary = payload["summary"]
    lines = [
        "# FeatureLiftBench v3 Oracle Revalidation",
        "",
        f"- Gate: **{'PASS' if payload['gate_pass'] else 'FAIL'}**",
        "- Evaluator: source-free Docker functional capsule + static metrics stage",
        f"- Tasks: {summary['task_count']}",
        f"- Repetitions: {summary['repetitions']}",
        f"- Passing runs: {summary['passed_runs']}/{summary['expected_runs']}",
        f"- Stable tasks: {summary['stable_tasks']}/{summary['task_count']}",
        f"- Failed tasks: {len(payload['failed_task_ids'])}",
        f"- Unstable tasks: {len(payload['unstable_task_ids'])}",
        "",
    ]
    if payload["failed_task_ids"]:
        lines.extend(
            ["## Failed tasks", ""]
            + [f"- `{task_id}`" for task_id in payload["failed_task_ids"]]
            + [""]
        )
    if payload["unstable_task_ids"]:
        lines.extend(
            ["## Unstable tasks", ""]
            + [f"- `{task_id}`" for task_id in payload["unstable_task_ids"]]
            + [""]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = _parse_args()
    if args.repetitions < 1 or args.workers < 1:
        raise ValueError("--repetitions and --workers must be positive")
    tasks = _task_dirs(args.task_ids)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    jobs = [
        (task_dir, repetition)
        for repetition in range(1, args.repetitions + 1)
        for task_dir in tasks
    ]
    records: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(
                _run_one,
                task_dir,
                repetition,
                output,
                args.image,
                args.keep_passing_outputs,
            ): (task_dir.name, repetition)
            for task_dir, repetition in jobs
        }
        for index, future in enumerate(as_completed(futures), start=1):
            record = future.result()
            records.append(record)
            print(
                f"[{index:03d}/{len(jobs):03d}] "
                f"{'PASS' if record['passed'] else 'FAIL'} "
                f"r{record['repetition']} {record['task_id']}",
                flush=True,
            )

    records.sort(key=lambda item: (item["task_id"], item["repetition"]))
    by_task: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        by_task.setdefault(str(record["task_id"]), []).append(record)
    failed = sorted(
        task_id
        for task_id, task_records in by_task.items()
        if not all(record["passed"] for record in task_records)
    )
    unstable = sorted(
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
        and not failed
        and not unstable
    )
    payload = {
        "schema_version": SCHEMA_VERSION,
        "policy_id": POLICY_ID,
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "gate_pass": gate_pass,
        "environment": {**_image_identity(args.image), "python": sys.version},
        "summary": {
            "task_count": len(tasks),
            "repetitions": args.repetitions,
            "expected_runs": expected_runs,
            "passed_runs": passed_runs,
            "stable_tasks": len(tasks) - len(unstable),
        },
        "failed_task_ids": failed,
        "unstable_task_ids": unstable,
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
        f"Oracle v3 gate: {'PASS' if gate_pass else 'FAIL'}; "
        f"{passed_runs}/{expected_runs} runs; {len(unstable)} unstable tasks.",
        flush=True,
    )
    return 0 if gate_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
