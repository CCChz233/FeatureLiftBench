#!/usr/bin/env python3
"""Freeze, prewarm, plan, or execute the OpenHands RSG small-repeat Pilot."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "harness") not in sys.path:
    sys.path.insert(0, str(ROOT / "harness"))

from featureliftbench.repo_graph.pilot import freeze_experiment
from featureliftbench.repo_graph.pilot import load_pilot_spec
from featureliftbench.repo_graph.pilot import prewarm_graphs
from featureliftbench.repo_graph.pilot import run_pilot


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--spec",
        type=Path,
        default=ROOT / "harness/config/experiments/rsg_openhands_pilot_v1.toml",
    )
    parser.add_argument("--experiment-id", default="")
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--execute", action="store_true", help="authorize paid API runs")
    parser.add_argument("--skip-prewarm", action="store_true")
    args = parser.parse_args()

    spec_path = args.spec.resolve()
    spec = load_pilot_spec(spec_path)
    experiment_id = args.experiment_id or (
        f"rsg-pilot-v1-{datetime.now().astimezone().strftime('%Y%m%d-%H%M%S')}"
    )
    experiment_dir = (
        args.output.resolve()
        if args.output is not None
        else ROOT
        / "experiments/methods/rsg_pilot/openhands/deepseek-v4-flash"
        / experiment_id
    )
    experiment_dir.mkdir(parents=True, exist_ok=True)
    freeze_experiment(
        spec,
        spec_path=spec_path,
        experiment_dir=experiment_dir,
        root=ROOT,
    )
    if not args.skip_prewarm:
        prewarm_graphs(spec, experiment_dir=experiment_dir, root=ROOT)
    state = run_pilot(spec, experiment_dir=experiment_dir, root=ROOT, execute=args.execute)
    print(f"Pilot {state['status']}: {experiment_dir}")
    if state.get("stop_reason"):
        print(f"Stop reason: {state['stop_reason']}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
