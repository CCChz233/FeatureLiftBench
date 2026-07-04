#!/usr/bin/env python3
"""Cross-platform preflight for Go OpenHands experiments."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def _ok(msg: str) -> None:
    print(f"[OK] {msg}")


def _warn(msg: str) -> None:
    print(f"[WARN] {msg}")


def _fail(msg: str, failures: list[str]) -> None:
    print(f"[FAIL] {msg}")
    failures.append(msg)


def main() -> int:
    failures: list[str] = []
    print("=== Go OpenHands preflight (python) ===")

    openhands = shutil.which("openhands")
    if openhands:
        try:
            version = subprocess.run(
                ["openhands", "--version"],
                capture_output=True,
                text=True,
                check=False,
                timeout=15,
            )
            ver = (version.stdout or version.stderr or "").strip() or "version_unknown"
        except (OSError, subprocess.TimeoutExpired):
            ver = "version_unknown"
        _ok(f"openhands: {openhands} ({ver})")
    else:
        _fail("openhands not in PATH", failures)

    go_bin = shutil.which("go")
    if go_bin:
        try:
            out = subprocess.run(["go", "version"], capture_output=True, text=True, check=False, timeout=10)
            _ok((out.stdout or out.stderr).strip())
        except (OSError, subprocess.TimeoutExpired):
            _warn("go found but version check timed out")
    else:
        _warn("go not on host PATH (agent may fail go test; Docker eval still works)")

    docker = shutil.which("docker")
    if not docker:
        _fail("docker not in PATH", failures)
    else:
        probe = subprocess.run(
            ["docker", "image", "inspect", "featureliftbench-eval:latest"],
            capture_output=True,
            text=True,
            check=False,
        )
        if probe.returncode == 0:
            _ok("docker image featureliftbench-eval:latest")
            go_probe = subprocess.run(
                [
                    "docker",
                    "run",
                    "--rm",
                    "--entrypoint",
                    "go",
                    "featureliftbench-eval:latest",
                    "version",
                ],
                capture_output=True,
                text=True,
                check=False,
                timeout=60,
            )
            if go_probe.returncode == 0:
                _ok(f"eval image go: {(go_probe.stdout or '').strip()}")
            else:
                _fail(
                    "eval image missing go toolchain (rebuild: docker/build_eval_image.sh)",
                    failures,
                )
        else:
            _fail("missing featureliftbench-eval:latest (run docker/build_eval_image.sh)", failures)

    env_path = REPO / ".env"
    if env_path.is_file():
        _ok(".env present")
    else:
        _warn(".env missing (need LLM_API_KEY / API base for --override-with-envs)")

    gold: list[str] = []
    tasks_root = REPO / "benchmark" / "go" / "tasks"
    for task_dir in sorted(tasks_root.iterdir()):
        if not task_dir.is_dir():
            continue
        repo = task_dir / "repo"
        if not repo.is_dir():
            continue
        go_files = list(repo.glob("*.go"))
        if len(go_files) == 1 and (repo / "add.go").is_file():
            continue
        gold.append(task_dir.name)
        _ok(f"gold-ready task: {task_dir.name}")
    if not gold:
        _fail("no gold-ready Go tasks found", failures)

    model = os.environ.get("LLM_MODEL", "deepseek/deepseek-v4-flash")
    _ok(f"LLM_MODEL default/target: {model}")

    if os.environ.get("SKIP_GATE", "").strip() in {"1", "true", "yes"}:
        _warn("SKIP_GATE=1: skipping semver gate spot-check")
    elif docker:
        review = REPO / "experiments" / "go-pilot" / "semver__version_parse_core__001" / "review"
        gate = review / "gate_report.json"
        if gate.is_file():
            data = json.loads(gate.read_text(encoding="utf-8"))
            if data.get("decision") == "promote":
                _ok("semver gate_report.json promote (cached)")
            else:
                _warn(f"semver gate decision={data.get('decision')} — rerun run_go_pilot_review.sh")
        else:
            _warn("semver gate_report.json missing — run run_go_pilot_review.sh semver__version_parse_core__001 --docker")

    if failures:
        print("Preflight FAILED")
        return 1
    print("Preflight PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
