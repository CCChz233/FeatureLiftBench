#!/usr/bin/env python3
"""CLI wrapper: flb_test_first freeze|verify."""

from __future__ import annotations

import sys
from pathlib import Path

HARNESS = Path(__file__).resolve().parents[1]
if str(HARNESS) not in sys.path:
    sys.path.insert(0, str(HARNESS))

from featureliftbench.test_first_lift.__main__ import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
