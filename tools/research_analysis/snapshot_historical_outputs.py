#!/usr/bin/env python3
"""Create or verify immutable hashes for the 62 historical infra-failure runs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "harness"))

from featureliftbench.freeze import file_manifest, manifest_digest  # noqa: E402


DEFAULT_SOURCE = ROOT / "artifacts/research_analysis/v1_1/infra_reeval_manifest.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("create")
    create.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    create.add_argument("--output", type=Path, required=True)
    verify = sub.add_parser("verify")
    verify.add_argument("snapshot", type=Path)
    verify.add_argument("--output", type=Path)
    return parser.parse_args()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def run_paths(source: dict[str, Any]) -> list[Path]:
    paths = sorted({
        ROOT / str(run["run_id"])
        for suite in source.get("suites", [])
        for run in suite.get("runs", [])
    })
    missing = [path for path in paths if not path.is_dir()]
    if missing:
        raise FileNotFoundError(f"historical run directories missing: {', '.join(map(str, missing[:5]))}")
    return paths


def digest_tree(path: Path) -> dict[str, Any]:
    files = file_manifest([path], root=path)
    return {"sha256": manifest_digest({"files": files}), "file_count": len(files)}


def create(args: argparse.Namespace) -> int:
    source = load(args.source)
    paths = run_paths(source)
    payload = {
        "schema_version": "featureliftbench.historical_output_snapshot.v1",
        "source_manifest": args.source.resolve().relative_to(ROOT).as_posix(),
        "run_count": len(paths),
        "runs": {
            path.relative_to(ROOT).as_posix(): digest_tree(path)
            for path in paths
        },
    }
    payload["snapshot_sha256"] = manifest_digest(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite snapshot: {args.output}")
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"snapshot {len(paths)} runs: {payload['snapshot_sha256']}")
    return 0


def verify(args: argparse.Namespace) -> int:
    payload = load(args.snapshot)
    mismatches = []
    for relative, expected in payload.get("runs", {}).items():
        path = ROOT / relative
        actual = digest_tree(path) if path.is_dir() else {"missing": True}
        if actual != expected:
            mismatches.append({"run_path": relative, "expected": expected, "actual": actual})
    result = {
        "snapshot_sha256": payload.get("snapshot_sha256"),
        "run_count": payload.get("run_count"),
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
    }
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 1 if mismatches else 0


def main() -> int:
    args = parse_args()
    return create(args) if args.command == "create" else verify(args)


if __name__ == "__main__":
    raise SystemExit(main())
