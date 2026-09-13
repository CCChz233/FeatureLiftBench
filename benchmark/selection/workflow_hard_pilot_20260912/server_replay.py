"""Verify an overlay, replay Linux Docker references, then calibrate candidates.

Requires the existing FeatureLiftBench checkout/runtime, images and wheel cache.
The overlay is a private maintainer artifact, never an agent workspace.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "harness"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["verify", "reference", "calibrate"])
    parser.add_argument("--lock", type=Path, default=HERE / "INPUT_LOCK.json")
    parser.add_argument("--agent-profile")
    parser.add_argument("--agent-config", type=Path, default=ROOT / "harness/config/agents.toml")
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env")
    parser.add_argument("--reference-evidence", type=Path)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--timeout-seconds", type=int, default=3600)
    args = parser.parse_args()
    lock = json.loads(args.lock.read_text(encoding="utf-8"))
    failures = [p for p, sha in lock["files"].items() if not (ROOT / p).is_file() or digest(ROOT / p) != sha]
    # Reject additional candidate code/test files as well as changed locked files.
    for task_id in lock["task_ids"]:
        task = ROOT / "benchmark/staging" / task_id
        for part in ("reference_solution", "public_tests", "hidden_tests", "evaluation"):
            for path in (task / part).rglob("*"):
                if path.is_file() and not any(p in {"__pycache__", ".pytest_cache"} for p in path.parts) and path.suffix not in {".pyc", ".pyo"}:
                    if path.relative_to(ROOT).as_posix() not in lock["files"]:
                        failures.append("unexpected: " + str(path))
    if failures:
        raise ValueError("Input lock mismatch: " + ", ".join(failures[:10]))
    print(f"Verified {len(lock['files'])} locked files", flush=True)
    if args.mode == "verify":
        return 0
    if sys.platform != "linux":
        raise RuntimeError("Official replay requires Linux; use replay.py for Windows development checks")
    if args.repeats < 1 or args.timeout_seconds < 1:
        parser.error("repeats and timeout must be positive")
    if args.mode == "calibrate":
        if not args.agent_profile or not args.reference_evidence:
            parser.error("calibrate requires --agent-profile and --reference-evidence")
        prior = json.loads(args.reference_evidence.read_text(encoding="utf-8"))
        if prior.get("mode") != "reference" or not prior.get("all_passed") or prior.get("input_lock_sha256") != digest(args.lock):
            raise ValueError("Matching successful Docker reference evidence required")
        if not args.agent_config.is_file() or not args.env_file.is_file():
            raise FileNotFoundError("Provide the server agent configuration and credential file")
    subprocess.run(["docker", "info", "--format", "{{.OSType}}"], check=True)
    from featureliftbench.source_archive import materialize_task_source, tree_stats, load_source_registry, source_indexes
    registry_path = ROOT / "benchmark/sources/workflow_hard_pilot_registry.json"
    _, snapshots = source_indexes(load_source_registry(registry_path))
    for task_id in lock["task_ids"]:
        repo = ROOT / "benchmark/staging" / task_id / "repo"
        if not repo.exists():
            materialize_task_source(task_id, repo, registry_path=registry_path, root=ROOT, require_registered=True)
        elif tree_stats(repo).source_tree_sha256 != snapshots[task_id]["source_tree_sha256"]:
            raise ValueError(f"Existing source tree mismatch: {task_id}; use a clean overlay checkout")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = ROOT / "experiments/calibration/workflow_hard_pilot" / (args.mode + "-" + stamp)
    output.mkdir(parents=True, exist_ok=False)
    env = {**os.environ, "PYTHONPATH": str(ROOT / "harness"), "PYTHONDONTWRITEBYTECODE": "1", "FEATURELIFTBENCH_SOURCE_REGISTRY": str(registry_path)}
    cli = [sys.executable, "-B", "-m", "featureliftbench.cli"]
    report = dict(mode=args.mode, input_lock_sha256=digest(args.lock), agent_profile=args.agent_profile, agent_config_sha256=digest(args.agent_config) if args.mode == "calibrate" else None, timeout_seconds=args.timeout_seconds, repetitions=args.repeats, runs=[], all_passed=False)
    report_path = output / "summary.json"
    def save():
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    save()
    for repeat in range(args.repeats):
        ids = lock["task_ids"] if args.mode == "reference" else lock["hard_candidates"]
        for task_id in ids:
            task = ROOT / "benchmark/staging" / task_id
            run_output = output / (f"r{repeat + 1}-" + task_id)
            if args.mode == "reference":
                command = cli + ["eval", str(task), str(task / "reference_solution"), "--docker", "--output", str(run_output)]
            else:
                command = cli + ["run-agent", str(task), "--agent", "openhands", "--agent-profile", args.agent_profile, "--agent-config", str(args.agent_config.resolve()), "--env-file", str(args.env_file.resolve()), "--eval-docker", "--agent-docker", "--source-context", "full_repository", "--no-agent-source-hints", "--no-agent-public-tests", "--extra-agent-passes", "0", "--retry-rate-limit", "1", "--retry-transient-api", "1", "--timeout-seconds", str(args.timeout_seconds), "--output", str(run_output)]
            print("Running " + task_id + f" repeat {repeat + 1}", flush=True)
            with (output / (run_output.name + ".log")).open("w", encoding="utf-8") as log:
                process = subprocess.run(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
            record = dict(task_id=task_id, repeat=repeat + 1, returncode=process.returncode, command=command, output=str(run_output))
            if args.mode == "reference":
                result_path = run_output / "result.json"
                result = json.loads(result_path.read_text()) if result_path.is_file() else {}
                record["passed"] = process.returncode == 0 and result.get("status") == "passed" and result.get("isolation_pass") is True
            report["runs"].append(record)
            save()
    report["all_passed"] = args.mode == "reference" and all(r.get("passed") for r in report["runs"])
    report["calibration_note"] = "Analyze all independent runs and infrastructure failures separately; process completion is not a functional pass. No post-result test tuning."
    save()
    print(report_path)
    return 0 if args.mode == "calibrate" or report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
