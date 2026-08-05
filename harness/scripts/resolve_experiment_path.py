#!/usr/bin/env python3
"""Resolve an old or current repository experiment path."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "harness"))

from featureliftbench.experiment_paths import resolve_experiment_path  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path")
    args = parser.parse_args()
    print(resolve_experiment_path(args.path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
