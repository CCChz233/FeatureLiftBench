#!/usr/bin/env python3
"""Freeze and run the v1.1 Oracle canary/full reproducibility gates."""

from __future__ import annotations

import argparse
import json
import locale
import os
import platform
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
HARNESS_ROOT = REPO_ROOT / "harness"
if str(HARNESS_ROOT) not in sys.path:
    sys.path.insert(0, str(HARNESS_ROOT))

from featureliftbench.docker_eval import DEFAULT_EVAL_IMAGE  # noqa: E402
from featureliftbench.docker_eval import evaluate_submission_docker  # noqa: E402
from featureliftbench.freeze import file_manifest, manifest_digest, sha256_file  # noqa: E402

from build_v11_diagnostic_subset import CANARY_5  # noqa: E402


TASKS_ROOT = REPO_ROOT / "benchmark/tasks"
SUBMISSIONS_ROOT = REPO_ROOT / "benchmark/submissions"
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "experiments/v1_1_oracle_validation"
CURRENT_FREEZE_POINTER = REPO_ROOT / "artifacts/research_analysis/v1_1/current_oracle_freeze.json"
EVALUATOR_PATHS = (
    REPO_ROOT / "harness/featureliftbench/evaluator.py",
    REPO_ROOT / "harness/featureliftbench/docker_eval.py",
    REPO_ROOT / "harness/featureliftbench/dependency_install.py",
    REPO_ROOT / "harness/featureliftbench/dependency_audit.py",
    REPO_ROOT / "harness/featureliftbench/benchmark_wheels.py",
    REPO_ROOT / "harness/featureliftbench/metrics.py",
    REPO_ROOT / "harness/featureliftbench/scoring.py",
    REPO_ROOT / "harness/featureliftbench/validate.py",
    REPO_ROOT / "harness/featureliftbench/closure_gold.py",
    REPO_ROOT / "harness/featureliftbench/schemas",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    freeze = subparsers.add_parser("freeze", help="create an evaluator/task freeze manifest")
    freeze.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    freeze.add_argument("--docker-image", default=DEFAULT_EVAL_IMAGE)

    for name in ("verify", "canary", "full", "summarize"):
        sub = subparsers.add_parser(name)
        sub.add_argument("freeze_manifest", type=Path)
        if name in {"canary", "full"}:
            sub.add_argument("--workers", type=int, default=1)
            sub.add_argument("--resume", action="store_true")
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def task_ids() -> list[str]:
    return sorted(
        path.name for path in TASKS_ROOT.iterdir() if (path / "metadata.json").is_file()
    )


def tree_digest(path: Path) -> dict[str, Any]:
    files = file_manifest([path], root=path)
    return {
        "sha256": manifest_digest({"files": files}),
        "file_count": len(files),
    }


def docker_identity(image: str) -> dict[str, Any]:
    command = ["docker", "image", "inspect", image]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        message = completed.stderr.strip() or completed.stdout.strip() or "docker inspect failed"
        raise RuntimeError(f"cannot freeze Docker image {image}: {message}")
    values = json.loads(completed.stdout)
    if not isinstance(values, list) or not values:
        raise RuntimeError(f"docker inspect returned no image: {image}")
    value = values[0]
    digests = value.get("RepoDigests") if isinstance(value.get("RepoDigests"), list) else []
    image_id = str(value.get("Id") or "")
    immutable_ref = str(digests[0]) if digests else image_id
    if not immutable_ref:
        raise RuntimeError(f"Docker image lacks immutable identity: {image}")
    return {
        "requested_ref": image,
        "image_id": image_id,
        "repo_digests": [str(item) for item in digests],
        "immutable_ref": immutable_ref,
    }


def build_freeze(image: str) -> dict[str, Any]:
    ids = task_ids()
    if len(ids) != 150:
        raise ValueError(f"expected 150 Python tasks, found {len(ids)}")
    missing_oracles = [task_id for task_id in ids if not (SUBMISSIONS_ROOT / task_id / "oracle").is_dir()]
    if missing_oracles:
        raise ValueError(f"missing Oracle submissions: {', '.join(missing_oracles)}")
    evaluator_files = file_manifest(EVALUATOR_PATHS, root=REPO_ROOT)
    wheel_files = file_manifest([REPO_ROOT / "benchmark/vendor-wheels"], root=REPO_ROOT)
    payload: dict[str, Any] = {
        "schema_version": "featureliftbench.evaluator_freeze.v1",
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "task_count": len(ids),
        "task_ids": ids,
        "canary_task_ids": list(CANARY_5),
        "task_trees": {task_id: tree_digest(TASKS_ROOT / task_id) for task_id in ids},
        "oracle_trees": {task_id: tree_digest(SUBMISSIONS_ROOT / task_id / "oracle") for task_id in ids},
        "evaluator_files": evaluator_files,
        "vendor_wheels": wheel_files,
        "docker": docker_identity(image),
        "environment": {
            "python": sys.version,
            "python_executable": sys.executable,
            "platform": platform.platform(),
            "locale": locale.setlocale(locale.LC_ALL, None),
            "timezone": os.environ.get("TZ", "system-default"),
            "pythonhashseed": os.environ.get("PYTHONHASHSEED", "not-set-on-host"),
            "network_for_evaluator": "none",
            "docker_memory": os.environ.get("FEATURELIFTBENCH_DOCKER_MEMORY", "4g"),
            "docker_cpus": os.environ.get("FEATURELIFTBENCH_DOCKER_CPUS", "2"),
            "docker_pids": os.environ.get("FEATURELIFTBENCH_DOCKER_PIDS", "256"),
        },
        "policy": {
            "canary_repetitions": 3,
            "full_repetitions": 3,
            "canary_counts_toward_full": False,
            "historical_outputs_mutable": False,
        },
    }
    payload["freeze_id"] = manifest_digest(payload)[:16]
    return payload


def freeze_command(args: argparse.Namespace) -> int:
    payload = build_freeze(args.docker_image)
    root = args.output_root / payload["freeze_id"]
    path = root / "freeze_manifest.json"
    if path.exists():
        existing = load_json(path)
        if existing.get("freeze_id") != payload["freeze_id"]:
            raise RuntimeError(f"refusing to overwrite different freeze: {path}")
    write_json(path, payload)
    write_json(root / "quarantine_manifest.json", {
        "schema_version": "featureliftbench.quarantine.v1",
        "freeze_id": payload["freeze_id"],
        "tasks": [],
    })
    write_json(
        CURRENT_FREEZE_POINTER,
        {
            "schema_version": "featureliftbench.current_oracle_freeze.v1",
            "freeze_id": payload["freeze_id"],
            "freeze_manifest": str(path.relative_to(REPO_ROOT)),
            "generated_at": payload["generated_at"],
        },
    )
    print(path)
    return 0


def verify_freeze(manifest: dict[str, Any]) -> list[dict[str, str]]:
    mismatches: list[dict[str, str]] = []
    for task_id, expected in manifest["task_trees"].items():
        actual = tree_digest(TASKS_ROOT / task_id)
        if actual != expected:
            mismatches.append({"scope": "task", "id": task_id, "expected": str(expected), "actual": str(actual)})
    for task_id, expected in manifest["oracle_trees"].items():
        actual = tree_digest(SUBMISSIONS_ROOT / task_id / "oracle")
        if actual != expected:
            mismatches.append({"scope": "oracle", "id": task_id, "expected": str(expected), "actual": str(actual)})
    actual_eval = file_manifest(EVALUATOR_PATHS, root=REPO_ROOT)
    if actual_eval != manifest["evaluator_files"]:
        mismatches.append({"scope": "evaluator", "id": "global", "expected": manifest_digest({"files": manifest["evaluator_files"]}), "actual": manifest_digest({"files": actual_eval})})
    actual_wheels = file_manifest([REPO_ROOT / "benchmark/vendor-wheels"], root=REPO_ROOT)
    if actual_wheels != manifest["vendor_wheels"]:
        mismatches.append({"scope": "vendor_wheels", "id": "global", "expected": manifest_digest({"files": manifest["vendor_wheels"]}), "actual": manifest_digest({"files": actual_wheels})})
    current_docker = docker_identity(str(manifest["docker"]["immutable_ref"]))
    if current_docker["image_id"] != manifest["docker"]["image_id"]:
        mismatches.append({"scope": "docker", "id": "global", "expected": str(manifest["docker"]["image_id"]), "actual": str(current_docker["image_id"])})
    return mismatches


def verify_command(args: argparse.Namespace) -> int:
    manifest = load_json(args.freeze_manifest)
    mismatches = verify_freeze(manifest)
    print(json.dumps({"freeze_id": manifest.get("freeze_id"), "mismatches": mismatches}, indent=2, sort_keys=True))
    return 1 if mismatches else 0


def phase_root(path: Path, manifest: dict[str, Any], phase: str) -> Path:
    return path.resolve().parent / phase


def command_state(result: dict[str, Any], key: str) -> bool | None:
    value = result.get(key)
    if not isinstance(value, dict) or value.get("skipped") is True:
        return None
    passed = value.get("passed")
    return passed if isinstance(passed, bool) else None


def classify_failure(result: dict[str, Any]) -> str:
    sandbox = result.get("sandbox") if isinstance(result.get("sandbox"), dict) else {}
    if sandbox.get("docker_sandbox_error") is True:
        return "environment_docker"
    for key in ("dependency_install", "eval_tooling", "submission_install"):
        value = result.get(key) if isinstance(result.get(key), dict) else {}
        if value.get("timed_out") is True:
            return "timeout"
        if value.get("skipped") is not True and value.get("passed") is False:
            return "dependency" if key == "dependency_install" else "environment_tooling"
    for key in ("build", "public_tests", "hidden_tests"):
        value = result.get(key) if isinstance(result.get(key), dict) else {}
        if value.get("timed_out") is True:
            return "timeout"
    if result.get("status") != "passed":
        # The Oracle is part of the task definition. Once dependency install,
        # tooling, Docker, and timeout have been excluded, an Oracle failure is
        # classified as a task-asset failure (often relocation/closure/resource
        # incompleteness), not as an Agent failure.
        return "task"
    return ""


def result_row(task_id: str, repetition: int, output_dir: Path, result: dict[str, Any]) -> dict[str, Any]:
    required_result_keys = {
        "status", "build_pass", "test_pass", "original_import_pass", "environment",
        "dependency_install", "eval_tooling", "submission_install", "build",
        "public_tests", "hidden_tests", "metrics", "scores", "logs",
    }
    required_log_phases = {"venv"}
    for result_key, log_phase in (
        ("dependency_install", "dependency_install"),
        ("eval_tooling", "eval_tooling"),
        ("submission_install", "submission_install"),
        ("build", "build"),
        ("public_tests", "public"),
        ("hidden_tests", "hidden"),
    ):
        command = result.get(result_key) if isinstance(result.get(result_key), dict) else {}
        # The evaluator's not-reached placeholders use returncode=None even
        # though older result schemas left skipped=false. Require logs only for
        # phases that actually produced a command result.
        if command.get("returncode") is not None:
            required_log_phases.add(log_phase)
    required_log_names = {
        f"{phase}.{stream}"
        for phase in required_log_phases
        for stream in ("stdout", "stderr")
    }
    log_dir = output_dir / "logs"
    actual_log_names = {path.name for path in log_dir.iterdir()} if log_dir.is_dir() else set()
    environment = result.get("environment") if isinstance(result.get("environment"), dict) else {}
    return {
        "task_id": task_id,
        "repetition": repetition,
        "status": result.get("status"),
        "build_pass": result.get("build_pass"),
        "public_pass": command_state(result, "public_tests"),
        "hidden_pass": command_state(result, "hidden_tests"),
        "original_import_pass": result.get("original_import_pass"),
        "failure_class": classify_failure(result),
        "result_schema_complete": not (required_result_keys - set(result)),
        "missing_result_keys": sorted(required_result_keys - set(result)),
        "environment_record_complete": all(environment.get(key) for key in ("python", "venv_dir", "install_mode")),
        "logs_complete": required_log_names <= actual_log_names,
        "missing_log_files": sorted(required_log_names - actual_log_names),
        "result_path": str(output_dir / "result.json"),
        "result_sha256": sha256_file(output_dir / "result.json") if (output_dir / "result.json").is_file() else "",
    }


def evaluate_one(
    task_id: str,
    repetition: int,
    output: Path,
    image: str,
    resume: bool,
) -> dict[str, Any]:
    result_path = output / "result.json"
    if resume and result_path.is_file():
        result = load_json(result_path)
    else:
        result = evaluate_submission_docker(
            TASKS_ROOT / task_id,
            SUBMISSIONS_ROOT / task_id / "oracle",
            output,
            image=image,
            use_docker=True,
        )
    return result_row(task_id, repetition, output, result)


def run_phase(args: argparse.Namespace, phase: str) -> int:
    manifest = load_json(args.freeze_manifest)
    mismatches = verify_freeze(manifest)
    if mismatches:
        write_json(args.freeze_manifest.parent / f"{phase}_freeze_mismatches.json", mismatches)
        raise RuntimeError(f"freeze verification failed with {len(mismatches)} mismatches")
    if phase == "full":
        canary_summary = phase_root(args.freeze_manifest, manifest, "canary") / "summary.json"
        if not canary_summary.is_file() or load_json(canary_summary).get("gate_pass") is not True:
            raise RuntimeError("full run refused: passing canary summary is required for this freeze")
    ids = list(manifest["canary_task_ids"] if phase == "canary" else manifest["task_ids"])
    root = phase_root(args.freeze_manifest, manifest, phase)
    work = [
        (task_id, repetition, root / f"rep-{repetition}" / task_id)
        for task_id in ids
        for repetition in range(1, 4)
    ]
    rows: list[dict[str, Any]] = []
    workers = max(1, int(args.workers))
    image = str(manifest["docker"]["immutable_ref"])
    if workers == 1:
        for task_id, repetition, output in work:
            rows.append(evaluate_one(task_id, repetition, output, image, args.resume))
            if not args.resume:
                print(f"{phase}: {task_id} rep-{repetition}: {rows[-1]['status']} {rows[-1]['failure_class']}", flush=True)
    else:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {
                pool.submit(evaluate_one, task_id, repetition, output, image, args.resume): (task_id, repetition)
                for task_id, repetition, output in work
            }
            for future in as_completed(futures):
                row = future.result()
                rows.append(row)
                if not args.resume:
                    print(f"{phase}: {row['task_id']} rep-{row['repetition']}: {row['status']} {row['failure_class']}", flush=True)
    rows.sort(key=lambda item: (item["task_id"], item["repetition"]))
    write_json(root / "ledger.json", {
        "schema_version": "featureliftbench.oracle_revalidation_ledger.v1",
        "freeze_id": manifest["freeze_id"],
        "phase": phase,
        "workers": workers,
        "docker_image_id": manifest["docker"]["image_id"],
        "docker_immutable_ref": manifest["docker"]["immutable_ref"],
        "rows": rows,
    })
    summary = summarize_rows(rows, manifest=manifest, phase=phase)
    write_json(root / "summary.json", summary)
    update_quarantine(args.freeze_manifest, summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["gate_pass"] else 1


def summarize_rows(rows: list[dict[str, Any]], *, manifest: dict[str, Any], phase: str) -> dict[str, Any]:
    expected_tasks = manifest["canary_task_ids"] if phase == "canary" else manifest["task_ids"]
    grouped: dict[str, list[dict[str, Any]]] = {task_id: [] for task_id in expected_tasks}
    for row in rows:
        grouped.setdefault(str(row["task_id"]), []).append(row)
    unstable: list[str] = []
    failed: list[str] = []
    incomplete: list[str] = []
    invalid_artifacts: list[str] = []
    failure_classes: dict[str, int] = {}
    for task_id, task_rows in grouped.items():
        if len(task_rows) != 3:
            incomplete.append(task_id)
            continue
        if any(
            not row.get("result_schema_complete")
            or not row.get("environment_record_complete")
            or not row.get("logs_complete")
            for row in task_rows
        ):
            invalid_artifacts.append(task_id)
        signatures = {
            (
                row["status"], row["build_pass"], row["public_pass"],
                row["hidden_pass"], row["original_import_pass"], row["failure_class"],
            )
            for row in task_rows
        }
        if len(signatures) != 1:
            unstable.append(task_id)
        if any(row["status"] != "passed" or row["failure_class"] for row in task_rows):
            failed.append(task_id)
        for row in task_rows:
            value = str(row["failure_class"] or "")
            if value:
                failure_classes[value] = failure_classes.get(value, 0) + 1
    gate_pass = (
        not unstable
        and not failed
        and not incomplete
        and not invalid_artifacts
        and len(rows) == len(expected_tasks) * 3
    )
    return {
        "schema_version": "featureliftbench.oracle_revalidation_summary.v1",
        "freeze_id": manifest["freeze_id"],
        "phase": phase,
        "task_count": len(expected_tasks),
        "run_count": len(rows),
        "expected_run_count": len(expected_tasks) * 3,
        "gate_pass": gate_pass,
        "unstable_task_ids": sorted(unstable),
        "failed_task_ids": sorted(failed),
        "incomplete_task_ids": sorted(incomplete),
        "invalid_artifact_task_ids": sorted(invalid_artifacts),
        "failure_class_counts": dict(sorted(failure_classes.items())),
    }


def update_quarantine(freeze_path: Path, summary: dict[str, Any]) -> None:
    path = freeze_path.parent / "quarantine_manifest.json"
    payload = load_json(path) if path.is_file() else {
        "schema_version": "featureliftbench.quarantine.v1",
        "freeze_id": summary["freeze_id"],
        "tasks": [],
    }
    entries = {item["task_id"]: item for item in payload.get("tasks") or [] if isinstance(item, dict)}
    for task_id in summary["failed_task_ids"]:
        entries[task_id] = {"task_id": task_id, "reason": "oracle_failed", "phase": summary["phase"]}
    for task_id in summary["unstable_task_ids"]:
        entries[task_id] = {"task_id": task_id, "reason": "flaky_or_nondeterministic", "phase": summary["phase"]}
    payload["tasks"] = [entries[key] for key in sorted(entries)]
    write_json(path, payload)


def summarize_command(args: argparse.Namespace) -> int:
    manifest = load_json(args.freeze_manifest)
    summaries = {}
    for phase in ("canary", "full"):
        path = phase_root(args.freeze_manifest, manifest, phase) / "summary.json"
        summaries[phase] = load_json(path) if path.is_file() else {"status": "missing"}
    print(json.dumps({"freeze_id": manifest["freeze_id"], "summaries": summaries}, indent=2, sort_keys=True))
    return 0


def main() -> int:
    args = parse_args()
    if args.command == "freeze":
        return freeze_command(args)
    if args.command == "verify":
        return verify_command(args)
    if args.command == "canary":
        return run_phase(args, "canary")
    if args.command == "full":
        return run_phase(args, "full")
    if args.command == "summarize":
        return summarize_command(args)
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
