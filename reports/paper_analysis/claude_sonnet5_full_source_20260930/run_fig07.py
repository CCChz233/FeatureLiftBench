#!/usr/bin/env python3
"""Replay Claude Full Source trajectories and re-evaluate submission states.

Uses the existing token-efficiency replay. Does not call the model or edit
the original run directories.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "harness"))

from featureliftbench.token_efficiency.constants import PINNED_EVAL_IMAGE  # noqa: E402
from featureliftbench.token_efficiency.pipeline import run_suite  # noqa: E402
from featureliftbench.token_efficiency.scope import OfficialRun  # noqa: E402

SUITE = ROOT / "experiments/python/openhands/claude-sonnet-5/python150-main-r1"
TABLE = Path(__file__).resolve().parent / "task_results.csv"
OUTPUT = Path(__file__).resolve().parent / "fig07"


def _bool(value: str) -> bool | None:
    if value == "1":
        return True
    if value == "0":
        return False
    return None


def _int(value: str) -> int | None:
    if value in {"", "None"}:
        return None
    return int(float(value))


def load_runs() -> list[OfficialRun]:
    sample = json.loads((SUITE / "cattrs__structure_core__001" / "run.json").read_text())
    freeze_id = str((sample.get("benchmark_freeze") or {}).get("freeze_id") or "")
    image = str(
        ((sample.get("experiment_conditions") or {}).get("evaluator_runtime") or {}).get("image")
        or PINNED_EVAL_IMAGE
    )
    if image != PINNED_EVAL_IMAGE:
        raise SystemExit(f"eval image {image} is not the pinned Fig. 7 image")
    runs: list[OfficialRun] = []
    with TABLE.open(newline="") as handle:
        for row in csv.DictReader(handle):
            task_id = row["task_id"]
            runs.append(
                OfficialRun(
                    run_id=f"claude-sonnet-5/{task_id}",
                    configuration="claude-sonnet-5",
                    display_name="Claude Sonnet 5",
                    short_name="Claude",
                    task_id=task_id,
                    suite_id=SUITE.name,
                    source_run_dir=SUITE.relative_to(ROOT).as_posix() + "/" + task_id,
                    mapped_run_dir=str(SUITE / task_id),
                    final_pass=row["functional_pass"] == "1",
                    lift_type=row["lift_type"],
                    official_tokens=_int(row["total_tokens"]),
                    original_steps=_int(row["assistant_steps"]),
                    usage_source=row["token_source"],
                    usage_unverified=row["usage_unverified"] == "True",
                    eval_docker_image=image,
                    freeze_id=freeze_id,
                    build_pass=_bool(row["build_pass"]),
                    public_pass=_bool(row["public_pass"]),
                    hidden_pass=_bool(row["hidden_pass"]),
                    isolation_pass=_bool(row["isolation_pass"]),
                )
            )
    if len(runs) != 150:
        raise SystemExit(f"expected 150 runs, got {len(runs)}")
    return runs


def main() -> int:
    runs = load_runs()
    print(f"fig07 assigned {len(runs)} passes {sum(run.final_pass for run in runs)}", flush=True)
    run_suite(
        runs,
        output_dir=OUTPUT,
        workers=2,
        resume=True,
        use_docker=True,
        evaluate_states=True,
        root=ROOT,
    )
    print("fig07 suite returned", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
