#!/usr/bin/env python3
"""Repository entrypoint for the FeatureLiftBench validation gate."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "harness"))

from featureliftbench.cli import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main(["validate-benchmark", *sys.argv[1:]]))
