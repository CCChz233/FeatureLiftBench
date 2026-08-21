#!/usr/bin/env python3
"""Generate or validate programmatic calibration cases for evidence Agents."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO / "harness") not in sys.path:
    sys.path.insert(0, str(_REPO / "harness"))

from featureliftbench.agentic_evidence.canaries import generate_canary_suite
from featureliftbench.agentic_evidence.canaries import validate_canary_suite


DEFAULT_OUTPUT = (
    _REPO / "artifacts/research_analysis/agentic_evidence/canaries_v1"
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--per-class", type=int, default=10)
    parser.add_argument("--seed", type=int, default=20260820)
    parser.add_argument("--check", action="store_true")
    return parser


def main() -> int:
    args = _parser().parse_args()
    output = args.output.resolve()
    if args.check:
        errors = validate_canary_suite(output)
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            return 1
        print(f"valid agentic evidence canary suite: {output}")
        return 0
    if output.exists() and any(output.iterdir()):
        print(
            f"output already exists and is not empty: {output}; choose a new path",
            file=sys.stderr,
        )
        return 2
    manifest = generate_canary_suite(
        output,
        per_class=args.per_class,
        seed=args.seed,
    )
    errors = validate_canary_suite(output)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(
        f"wrote {manifest['case_count']} agentic evidence canaries to {output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
