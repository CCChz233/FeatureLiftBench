#!/usr/bin/env python3
"""Deprecated wrapper. Use scripts/list_tasks.py instead."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> None:
    script = Path(__file__).resolve().parents[1] / "list_tasks.py"
    args = ["--tag", "extreme", *sys.argv[1:]]
    raise SystemExit(subprocess.call([sys.executable, str(script), *args]))


if __name__ == "__main__":
    main()
