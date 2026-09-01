#!/usr/bin/env python3
"""Aggregate Flash-33 tool-agent audit records from multiple reviewers."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO / "harness") not in sys.path:
    sys.path.insert(0, str(_REPO / "harness"))

from featureliftbench.agentic_evidence.flash33_aggregate import (
    aggregate_reviewer_runs,
)
from featureliftbench.agentic_evidence.flash33_aggregate import write_aggregate


DEFAULT_OUTPUT = (
    _REPO
    / "artifacts/research_analysis/hidden_provenance"
    / "flash33_agent_labels_consensus.json"
)
DEFAULT_AGREEMENT = (
    _REPO
    / "artifacts/research_analysis/hidden_provenance"
    / "flash33_agreement.json"
)
DEFAULT_MANIFEST = (
    _REPO
    / "experiments/validation/agentic_evidence/flash33_suite_v1"
    / "suite_manifest.json"
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "run_dirs",
        nargs="*",
        type=Path,
        help="Reviewer run directories (legacy positional form).",
    )
    parser.add_argument(
        "--run-dir",
        action="append",
        dest="run_dir_flags",
        type=Path,
        default=[],
        help="Reviewer run directory; repeat once per reviewer.",
    )
    parser.add_argument(
        "--reviewer",
        action="append",
        dest="reviewers",
        default=[],
        help="Reviewer id aligned with --run-dir / positional run dirs.",
    )
    parser.add_argument("--suite-manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--agreement-output", type=Path, default=DEFAULT_AGREEMENT)
    return parser


def main() -> int:
    args = _parser().parse_args()
    run_dirs = [path.resolve() for path in [*args.run_dirs, *args.run_dir_flags]]
    if not run_dirs:
        print("pass one or more reviewer run directories", file=sys.stderr)
        return 2
    reviewers = list(args.reviewers)
    if reviewers and len(reviewers) != len(run_dirs):
        print("--reviewer count must match run directory count", file=sys.stderr)
        return 2
    if not reviewers:
        reviewers = [f"reviewer_{index + 1}" for index in range(len(run_dirs))]
    for run_dir in run_dirs:
        if not run_dir.is_dir():
            print(f"missing run directory: {run_dir}", file=sys.stderr)
            return 2
    result = aggregate_reviewer_runs(
        zip(reviewers, run_dirs),
        suite_manifest=args.suite_manifest.resolve()
        if args.suite_manifest
        else None,
    )
    write_aggregate(
        result,
        output=args.output.resolve(),
        agreement_output=args.agreement_output.resolve(),
    )
    agreement = result["agreement"]
    print(
        f"wrote {args.output} n_tasks={result['consensus']['n']} "
        f"agreement={agreement['agreement']}/{agreement['n_cases']} "
        f"conflict={agreement['conflict']} "
        f"coverage_failure={agreement['coverage_failure']} "
        f"valid_rate={agreement['valid_rate']}"
    )
    print(f"wrote {args.agreement_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
