#!/usr/bin/env python3
"""Deprecated wrapper. Use scripts/analyze_benchmark_suite.py instead."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

if __name__ == "__main__":
    target = Path(__file__).resolve().parents[1] / "analyze_benchmark_suite.py"
    sys.argv[0] = str(target)
    runpy.run_path(str(target), run_name="__main__")
