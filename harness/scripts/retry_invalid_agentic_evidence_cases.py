#!/usr/bin/env python3
"""Re-run only invalid Flash-33 audit cases into the same output directory."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("suite", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--agent-profile", default="deepseek_v4_flash")
    parser.add_argument("--env-file", type=Path, default=Path(".env"))
    parser.add_argument(
        "--agent-bin",
        default="/Users/chz/anaconda3/envs/miniswe/bin/mini",
    )
    parser.add_argument("--agent-id", default="deepseek-v4-flash-provenance-r2")
    parser.add_argument("--timeout-seconds", type=int, default=900)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()

    suite = args.suite.resolve()
    output = args.output.resolve()
    invalid: list[str] = []
    for validation_path in sorted(output.glob("*/validation.json")):
        payload = json.loads(validation_path.read_text(encoding="utf-8"))
        if not payload.get("valid"):
            invalid.append(validation_path.parent.name)
    if args.limit is not None:
        invalid = invalid[: max(0, args.limit)]
    if not invalid:
        print("no invalid cases to retry")
        return 0

    staging = output.parent / f"{output.name}_retry_staging"
    if staging.exists():
        shutil.rmtree(staging)
    (staging / "cases").mkdir(parents=True)
    for case_id in invalid:
        src = suite / "cases" / case_id
        if not src.is_dir():
            print(f"missing suite case: {case_id}", file=sys.stderr)
            return 2
        shutil.copytree(src, staging / "cases" / case_id)
        # Force re-run even under --resume by clearing prior validation.
        case_out = output / case_id
        if case_out.exists():
            shutil.rmtree(case_out)

    cmd = [
        sys.executable,
        "-u",
        str(Path(__file__).resolve().parent / "run_agentic_evidence_canaries.py"),
        str(staging),
        str(output),
        "--agent-profile",
        args.agent_profile,
        "--env-file",
        str(args.env_file),
        "--agent-bin",
        args.agent_bin,
        "--agent-id",
        args.agent_id,
        "--timeout-seconds",
        str(args.timeout_seconds),
        "--resume",
    ]
    env = dict(**{k: v for k, v in __import__("os").environ.items()})
    env.setdefault("FEATURELIFTBENCH_LIVE_TRAJECTORY", "0")
    print(f"retrying {len(invalid)} cases: {invalid}")
    completed = subprocess.run(cmd, check=False, env=env)
    shutil.rmtree(staging, ignore_errors=True)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
