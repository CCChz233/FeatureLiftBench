#!/usr/bin/env python3
"""Run one observation-only probe against repair oracle targets."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


HARNESS = Path(__file__).resolve().parents[1]
if str(HARNESS) not in sys.path:
    sys.path.insert(0, str(HARNESS))

from featureliftbench.differential_probe import (  # noqa: E402
    ProbeValidationError,
)
from featureliftbench.differential_probe import run_differential_probe  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run the same observation-only Python probe against repo/, an "
            "optional immutable baseline, and submission/."
        )
    )
    parser.add_argument("probe", type=Path)
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument("--timeout", type=int, default=60)
    args = parser.parse_args()

    try:
        result = run_differential_probe(
            args.workspace,
            args.probe,
            timeout_seconds=args.timeout,
        )
    except ProbeValidationError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        return 2

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["observations_comparable"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
