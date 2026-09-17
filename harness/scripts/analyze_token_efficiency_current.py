#!/usr/bin/env python3
"""Offline token-efficiency analysis for the official Python-150 comparison.

Does not rerun agents, mutate original experiment records, or edit the paper.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "harness") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "harness"))

from featureliftbench.token_efficiency.constants import ANALYSIS_SEED, DEFAULT_WORKERS  # noqa: E402
from featureliftbench.token_efficiency.inventory import inventory_official_runs  # noqa: E402
from featureliftbench.token_efficiency.package import package_delivery  # noqa: E402
from featureliftbench.token_efficiency.pipeline import (  # noqa: E402
    collect_run_metrics,
    parse_spotcheck_runs,
    progress_counts,
    run_suite,
    sample_other_config_spotchecks,
    sample_pilot_runs,
    write_pilot_manifest,
    _write_metrics_table,
)
from featureliftbench.token_efficiency.scope import load_official_runs, repo_root  # noqa: E402
from featureliftbench.token_efficiency.summarize import summarize_suite  # noqa: E402
from featureliftbench.token_efficiency.util import write_json  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    inv = sub.add_parser("inventory", help="Phase A read-only coverage inventory")
    inv.add_argument("--manifest", default="docs/paper/paper_sources.json")
    inv.add_argument(
        "--output",
        default="reports/paper_analysis/token_efficiency_current/inventory",
    )

    pilot = sub.add_parser("pilot", help="Fix then replay the 20 Pro/Flash pilots")
    pilot.add_argument("--seed", type=int, default=ANALYSIS_SEED)
    pilot.add_argument(
        "--output",
        default="reports/paper_analysis/token_efficiency_current/pilot",
    )
    _add_exec_flags(pilot)

    run = sub.add_parser("run", help="Replay and evaluate assigned runs")
    run.add_argument("--scope", choices=["paper150", "pilot"], default="paper150")
    run.add_argument(
        "--output",
        default="reports/paper_analysis/token_efficiency_current/full",
    )
    run.add_argument("--pilot-manifest", default="")
    run.add_argument("--run-id", action="append", default=[], help="Restrict to these run_id values")
    _add_exec_flags(run)

    summ = sub.add_parser("summarize", help="Write summaries and paper_ready drafts")
    summ.add_argument(
        "--input",
        default="reports/paper_analysis/token_efficiency_current/full",
    )

    pack = sub.add_parser("package", help="Build delivery and evidence tarballs")
    pack.add_argument(
        "--input",
        default="reports/paper_analysis/token_efficiency_current/full",
    )
    pack.add_argument(
        "--inventory",
        default="reports/paper_analysis/token_efficiency_current/inventory",
    )
    pack.add_argument(
        "--pilot",
        default="reports/paper_analysis/token_efficiency_current/pilot",
    )
    pack.add_argument(
        "--output",
        default="reports/paper_analysis/token_efficiency_current",
    )

    spot = sub.add_parser("parse-spotcheck", help="Parse Luna/GLM/Qwen/OSS spotchecks without Docker")
    spot.add_argument(
        "--output",
        default="reports/paper_analysis/token_efficiency_current/spotcheck_parse",
    )

    prog = sub.add_parser("progress", help="Count completed full-run metrics")
    prog.add_argument(
        "--input",
        default="reports/paper_analysis/token_efficiency_current/full",
    )

    args = parser.parse_args(argv)
    root = repo_root()
    if args.command == "inventory":
        summary = inventory_official_runs(output_dir=root / args.output, root=root)
        print(f"inventory n={summary['n_runs']} -> {args.output}")
        return 0
    if args.command == "pilot":
        runs = load_official_runs(root)
        selected, report = sample_pilot_runs(runs, seed=args.seed)
        output = root / args.output
        output.mkdir(parents=True, exist_ok=True)
        manifest_path = output / "pilot_manifest.csv"
        if manifest_path.is_file() and not args.force_resample:
            print(f"using existing {manifest_path}")
        else:
            write_pilot_manifest(manifest_path, selected, report)
            print(f"wrote {manifest_path} n={len(selected)}")
        spot, spot_report = sample_other_config_spotchecks(runs)
        write_json(output / "other_config_spotcheck.json", {"runs": [item.run_id for item in spot], "report": spot_report})
        if args.sample_only:
            return 0
        run_suite(
            selected,
            output_dir=output,
            workers=args.workers,
            resume=args.resume,
            use_docker=not args.no_docker,
            evaluate_states=not args.skip_eval,
            root=root,
        )
        return 0
    if args.command == "run":
        runs = load_official_runs(root)
        if args.scope == "pilot":
            from featureliftbench.token_efficiency.util import read_csv

            manifest = root / (args.pilot_manifest or "reports/paper_analysis/token_efficiency_current/pilot/pilot_manifest.csv")
            wanted = {(row["configuration"], row["task_id"]) for row in read_csv(manifest)}
            runs = [run for run in runs if (run.configuration, run.task_id) in wanted]
        if args.run_id:
            wanted_ids = set(args.run_id)
            runs = [run for run in runs if run.run_id in wanted_ids]
        output = root / args.output
        run_suite(
            runs,
            output_dir=output,
            workers=args.workers,
            resume=args.resume,
            use_docker=not args.no_docker,
            evaluate_states=not args.skip_eval,
            root=root,
        )
        print(f"run n={len(runs)} -> {output}")
        return 0
    if args.command == "summarize":
        full = root / args.input
        runs = load_official_runs(root)
        rows = collect_run_metrics(full, runs)
        _write_metrics_table(full, rows, runs)
        summarize_suite(metrics_rows=rows, runs=runs, output_dir=full)
        print(f"summarized {len(rows)} rows in {full}")
        return 0
    if args.command == "package":
        checksums = package_delivery(
            inventory_dir=root / args.inventory,
            pilot_dir=root / args.pilot,
            full_dir=root / args.input,
            output_dir=root / args.output,
            root=root,
        )
        print(checksums)
        return 0
    if args.command == "parse-spotcheck":
        runs = load_official_runs(root)
        selected, report = sample_other_config_spotchecks(runs)
        write_json(root / args.output / "selection.json", {"runs": [item.run_id for item in selected], "report": report})
        rows = parse_spotcheck_runs(selected, output_dir=root / args.output, root=root)
        print(f"parsed {len(rows)} spotchecks -> {args.output}")
        return 0
    if args.command == "progress":
        payload = progress_counts(root / args.input)
        print(payload)
        return 0
    return 2


def _add_exec_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    parser.add_argument("--resume", action="store_true", default=True)
    parser.add_argument("--no-resume", action="store_false", dest="resume")
    parser.add_argument("--no-docker", action="store_true")
    parser.add_argument("--skip-eval", action="store_true")
    parser.add_argument("--sample-only", action="store_true")
    parser.add_argument("--force-resample", action="store_true")


if __name__ == "__main__":
    raise SystemExit(main())
