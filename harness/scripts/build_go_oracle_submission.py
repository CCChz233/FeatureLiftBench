#!/usr/bin/env python3
"""Build Go oracle/copy_all submissions from task repo snapshots."""

from __future__ import annotations

import shutil
from pathlib import Path

from featureliftbench.paths import SUBMISSIONS_DIR

_SOURCE_PACKAGES = (
    "package originalpkg",
    "package semver",
    "package humanize",
    "package mapstructure",
)
_ORACLE_EXCLUDED = (
    "bulk_excluded.go",
    "bulk2_excluded.go",
    "bulk3_excluded.go",
    "more_excluded.go",
    "constraints.go",
    "times.go",
    "comma.go",
    "cache_excluded.go",
)


def build_go_submission(task_dir: Path, *, variant: str = "oracle") -> Path:
    task_id = task_dir.name
    repo_dir = task_dir / "repo"
    out_dir = SUBMISSIONS_DIR / task_id / variant
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for path in sorted(repo_dir.glob("*.go")):
        text = path.read_text(encoding="utf-8")
        for src_pkg in _SOURCE_PACKAGES:
            text = text.replace(src_pkg, "package featurelifted")
        (out_dir / path.name).write_text(text, encoding="utf-8")

    if variant == "oracle":
        for name in _ORACLE_EXCLUDED:
            extra = out_dir / name
            if extra.is_file():
                extra.unlink()

    (out_dir / "go.mod").write_text("module featurelifted\n\ngo 1.22\n", encoding="utf-8")
    return out_dir


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", type=Path, required=True, help="Task directory")
    parser.add_argument(
        "--variant",
        choices=("oracle", "copy_all"),
        default="oracle",
        help="Submission variant to build",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output directory (default: benchmark/submissions/<task_id>/<variant>)",
    )
    args = parser.parse_args()
    out = build_go_submission(args.task.resolve(), variant=args.variant)
    if args.output:
        import shutil

        args.output = args.output.resolve()
        if args.output.exists():
            shutil.rmtree(args.output)
        shutil.copytree(out, args.output)
        out = args.output
    print(f"built {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
