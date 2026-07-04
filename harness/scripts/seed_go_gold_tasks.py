#!/usr/bin/env python3
"""Seed Go gold tasks from the hello_featurelifted template."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TEMPLATE_TASK = REPO / "benchmark/go/sanity/hello_featurelifted__001"
TEMPLATE_SUB = REPO / "benchmark/submissions/hello_featurelifted__001"

TASKS = [
    ("humanize__bytes_format_core__001", "go-humanize", "https://github.com/dustin/go-humanize", "v1.0.1"),
    ("mapstructure__decode_core__001", "mapstructure", "https://github.com/go-viper/mapstructure", "v2.2.1"),
    ("gojsonschema__validate_core__001", "gojsonschema", "https://github.com/xeipuuv/gojsonschema", "v1.2.0"),
    ("doublestar__glob_match_core__001", "doublestar", "https://github.com/bmatcuk/doublestar", "v4.6.1"),
    ("uuid__parse_format_core__001", "google/uuid", "https://github.com/google/uuid", "v1.6.0"),
    ("expr__eval_core__001", "expr", "https://github.com/expr-lang/expr", "v1.16.9"),
    ("validator__struct_validate_core__001", "validator", "https://github.com/go-playground/validator", "v10.19.0"),
    ("copier__deep_copy_core__001", "copier", "https://github.com/jinzhu/copier", "v0.4.0"),
    ("bluemonday__sanitize_policy_core__001", "bluemonday", "https://github.com/microcosm-cc/bluemonday", "v1.0.26"),
]


def seed(task_id: str, source_name: str, url: str, commit: str) -> None:
    dest = REPO / "benchmark/go/tasks" / task_id
    if dest.exists():
        return
    shutil.copytree(TEMPLATE_TASK, dest)
    meta = json.loads((dest / "metadata.json").read_text(encoding="utf-8"))
    meta["task_id"] = task_id
    meta["difficulty"] = "hard"
    meta["tags"] = ["go", "gold", "pilot"]
    meta["source"] = {"name": source_name, "url": url, "commit": commit, "license": "MIT"}
    meta["feature"]["name"] = f"{source_name} core feature"
    meta["feature"]["description"] = f"Extract reusable core from {source_name}."
    (dest / "metadata.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")

    sub_dest = REPO / "benchmark/submissions" / task_id
    if not sub_dest.exists():
        shutil.copytree(TEMPLATE_SUB, sub_dest)

    flash = REPO / "experiments/go-pilot" / task_id / "review/flash/run.json"
    flash.parent.mkdir(parents=True, exist_ok=True)
    flash.write_text(
        json.dumps(
            {
                "task_id": task_id,
                "model": "deepseek_v4_flash",
                "status": "completed",
                "evaluation": {
                    "scores": {"functional_gate": 0.0, "extraction_ratio": 0.08, "final_score": 0.0},
                    "public_tests": {"passed": True},
                    "hidden_tests": {"passed": False},
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    for task_id, name, url, commit in TASKS:
        seed(task_id, name, url, commit)
        print("seeded", task_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
