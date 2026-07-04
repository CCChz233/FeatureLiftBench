#!/usr/bin/env python3
"""Copy naive submission into agent workspace (pipeline smoke only)."""
from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

from featureliftbench.paths import SUBMISSIONS_DIR


def main() -> int:
    workspace = Path(os.environ["FEATURELIFTBENCH_WORKSPACE"])
    submission_dir = Path(os.environ["FEATURELIFTBENCH_SUBMISSION_DIR"])
    metadata = json.loads((workspace / "metadata.json").read_text(encoding="utf-8"))
    task_id = str(metadata.get("task_id", "")).strip()
    if not task_id:
        raise SystemExit("metadata.json missing task_id")
    src = SUBMISSIONS_DIR / task_id / "naive"
    if not src.is_dir():
        raise SystemExit(f"naive submission not found: {src}")
    submission_dir.mkdir(parents=True, exist_ok=True)
    for path in src.iterdir():
        dest = submission_dir / path.name
        if path.is_dir():
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(path, dest)
        else:
            shutil.copy2(path, dest)
    print(f"pipeline-smoke: copied naive submission for {task_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
