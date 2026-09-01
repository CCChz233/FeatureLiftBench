#!/usr/bin/env python3
"""Build or verify a checksummed Python-200 evaluator overlay.

The public Git repository intentionally excludes unreleased Hard-50 hidden
tests, reference solutions, Oracle submissions, and newly collected wheels.
This command packages those local assets for direct delivery to an experiment
server without putting them in Git history.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import tarfile
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any, BinaryIO


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CANDIDATE = (
    ROOT
    / "artifacts"
    / "research_analysis"
    / "python200_prime"
    / "current_candidate_freeze.json"
)
DEFAULT_FINAL = (
    ROOT
    / "artifacts"
    / "research_analysis"
    / "python200_prime"
    / "current_benchmark_freeze.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "exports" / "server-overlays"
MANIFEST_NAME = "SERVER_OVERLAY_MANIFEST.json"
SCHEMA_VERSION = "featureliftbench.python200_server_overlay.v1"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, default=DEFAULT_CANDIDATE)
    parser.add_argument("--final-freeze", type=Path, default=DEFAULT_FINAL)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--include-source-archives",
        action="store_true",
        help="include pinned source archives for an offline server",
    )
    parser.add_argument("--verify", type=Path, help="verify an existing overlay")
    return parser.parse_args()


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_relative(path: Path) -> str:
    relative = path.resolve().relative_to(ROOT).as_posix()
    pure = PurePosixPath(relative)
    if pure.is_absolute() or ".." in pure.parts:
        raise ValueError(f"unsafe overlay path: {relative}")
    return relative


def _files_under(path: Path) -> list[Path]:
    if not path.is_dir():
        raise ValueError(f"required overlay directory missing: {path}")
    return sorted(item for item in path.rglob("*") if item.is_file())


def _collect_assets(
    candidate: dict[str, Any], *, include_source_archives: bool
) -> tuple[dict[str, Path], dict[str, dict[str, int]]]:
    tasks = candidate.get("tasks")
    if not isinstance(tasks, dict) or len(tasks) != 200:
        raise ValueError("candidate must contain exactly 200 task records")
    baseline_ids = sorted(
        task_id
        for task_id, record in tasks.items()
        if isinstance(record, dict) and record.get("stratum") == "python150"
    )
    hard50_ids = sorted(
        task_id
        for task_id, record in tasks.items()
        if isinstance(record, dict) and record.get("stratum") == "hard50"
    )
    if len(baseline_ids) != 150 or len(hard50_ids) != 50:
        raise ValueError("candidate strata must be Python-150 + Hard-50")

    groups: dict[str, list[Path]] = {
        "hard50_hidden_tests": [],
        "hard50_oracle_manifests": [],
        "hard50_reference_solutions": [],
        "python150_oracle_submissions": [],
        "vendor_wheels": [],
        "source_archives": [],
    }
    for task_id in hard50_ids:
        task_dir = ROOT / "benchmark" / "hard50" / task_id
        groups["hard50_hidden_tests"].extend(_files_under(task_dir / "hidden_tests"))
        oracle_manifest = task_dir / "evaluation" / "oracle_manifest.json"
        if not oracle_manifest.is_file():
            raise ValueError(f"{task_id}: Oracle manifest missing")
        groups["hard50_oracle_manifests"].append(oracle_manifest)
        groups["hard50_reference_solutions"].extend(
            _files_under(
                ROOT
                / "benchmark"
                / "hard50_pilot"
                / task_id
                / "reference_solution"
            )
        )
    for task_id in baseline_ids:
        groups["python150_oracle_submissions"].extend(
            _files_under(ROOT / "benchmark" / "submissions" / task_id / "oracle")
        )
    groups["vendor_wheels"] = sorted(
        path for path in (ROOT / "benchmark" / "vendor-wheels").glob("*.whl") if path.is_file()
    )
    if not groups["vendor_wheels"]:
        raise ValueError("vendor wheel directory is empty")
    if include_source_archives:
        groups["source_archives"] = sorted(
            path
            for path in (ROOT / "benchmark" / "sources" / "archives").glob("*.tar.gz")
            if path.is_file()
        )
        if not groups["source_archives"]:
            raise ValueError("source archives requested but none were found")

    assets: dict[str, Path] = {}
    summaries: dict[str, dict[str, int]] = {}
    for group, paths in groups.items():
        total_bytes = 0
        for path in paths:
            relative = _safe_relative(path)
            if relative in assets:
                raise ValueError(f"duplicate overlay path: {relative}")
            assets[relative] = path
            total_bytes += path.stat().st_size
        summaries[group] = {"file_count": len(paths), "size_bytes": total_bytes}
    return dict(sorted(assets.items())), summaries


def _manifest(
    candidate: dict[str, Any],
    final_freeze: dict[str, Any],
    assets: dict[str, Path],
    groups: dict[str, dict[str, int]],
    *,
    include_source_archives: bool,
) -> dict[str, Any]:
    candidate_id = candidate.get("candidate_id")
    if not isinstance(candidate_id, str) or len(candidate_id) != 64:
        raise ValueError("candidate id is missing")
    if (
        final_freeze.get("candidate_id") != candidate_id
        or final_freeze.get("gate_pass") is not True
    ):
        raise ValueError("final freeze does not match the candidate")
    entries = {
        relative: {
            "sha256": _sha256_file(path),
            "size_bytes": path.stat().st_size,
        }
        for relative, path in assets.items()
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "candidate_id": candidate_id,
        "final_freeze_id": final_freeze.get("freeze_id"),
        "include_source_archives": include_source_archives,
        "groups": groups,
        "summary": {
            "file_count": len(entries),
            "size_bytes": sum(item["size_bytes"] for item in entries.values()),
        },
        "entries": entries,
        "application": {
            "root": "FeatureLiftBench repository root",
            "policy": "extract only after archive verification",
        },
    }


def _tar_info(name: str, size: int, *, mode: int = 0o644) -> tarfile.TarInfo:
    info = tarfile.TarInfo(name=name)
    info.size = size
    info.mode = mode
    info.mtime = 0
    info.uid = 0
    info.gid = 0
    info.uname = ""
    info.gname = ""
    return info


def _add_bytes(archive: tarfile.TarFile, name: str, data: bytes) -> None:
    archive.addfile(_tar_info(name, len(data)), io.BytesIO(data))


def _add_file(archive: tarfile.TarFile, name: str, path: Path) -> None:
    with path.open("rb") as handle:
        archive.addfile(_tar_info(name, path.stat().st_size), handle)


def _write_archive(
    output: Path,
    manifest: dict[str, Any],
    assets: dict[str, Path],
) -> None:
    manifest_bytes = (
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", filename="", mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w") as archive:
                _add_bytes(archive, MANIFEST_NAME, manifest_bytes)
                for relative, path in assets.items():
                    _add_file(archive, relative, path)


def verify_archive(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"overlay archive missing: {path}")
    with tarfile.open(path, mode="r:gz") as archive:
        members = archive.getmembers()
        by_name: dict[str, tarfile.TarInfo] = {}
        for member in members:
            pure = PurePosixPath(member.name)
            if (
                pure.is_absolute()
                or ".." in pure.parts
                or not member.isfile()
                or member.issym()
                or member.islnk()
            ):
                raise ValueError(f"unsafe archive member: {member.name}")
            if member.name in by_name:
                raise ValueError(f"duplicate archive member: {member.name}")
            by_name[member.name] = member
        manifest_member = by_name.pop(MANIFEST_NAME, None)
        if manifest_member is None:
            raise ValueError("overlay manifest missing from archive")
        manifest_handle = archive.extractfile(manifest_member)
        if manifest_handle is None:
            raise ValueError("overlay manifest cannot be read")
        manifest = json.loads(manifest_handle.read().decode("utf-8"))
        if manifest.get("schema_version") != SCHEMA_VERSION:
            raise ValueError("unexpected overlay schema")
        entries = manifest.get("entries")
        if not isinstance(entries, dict) or set(entries) != set(by_name):
            raise ValueError("archive membership differs from overlay manifest")
        for name, expected in entries.items():
            handle: BinaryIO | None = archive.extractfile(by_name[name])
            if handle is None:
                raise ValueError(f"cannot read archive member: {name}")
            digest = hashlib.sha256()
            size = 0
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
                size += len(chunk)
            if size != expected.get("size_bytes") or digest.hexdigest() != expected.get(
                "sha256"
            ):
                raise ValueError(f"overlay member failed verification: {name}")
    return manifest


def main() -> int:
    args = _parse_args()
    if args.verify:
        archive = args.verify.resolve()
        manifest = verify_archive(archive)
        checksum_path = archive.with_suffix(archive.suffix + ".sha256")
        if checksum_path.is_file():
            expected = checksum_path.read_text(encoding="utf-8").split()[0]
            if expected != _sha256_file(archive):
                raise ValueError("overlay archive checksum file does not match")
        print(
            "Verified Python-200 server overlay: "
            f"{manifest['summary']['file_count']} files, "
            f"candidate={manifest['candidate_id']}"
        )
        return 0

    candidate = _load(args.candidate.resolve())
    final_freeze = _load(args.final_freeze.resolve())
    assets, groups = _collect_assets(
        candidate, include_source_archives=args.include_source_archives
    )
    manifest = _manifest(
        candidate,
        final_freeze,
        assets,
        groups,
        include_source_archives=args.include_source_archives,
    )
    suffix = "-offline" if args.include_source_archives else ""
    output = (
        args.output_dir.resolve()
        / f"python200-prime-server-overlay-{candidate['candidate_id'][:12]}{suffix}.tar.gz"
    )
    _write_archive(output, manifest, assets)
    checksum = _sha256_file(output)
    checksum_path = output.with_suffix(output.suffix + ".sha256")
    checksum_path.write_text(f"{checksum}  {output.name}\n", encoding="utf-8")
    verify_archive(output)
    print(f"Wrote {output}")
    print(f"Wrote {checksum_path}")
    print(
        f"Overlay: {manifest['summary']['file_count']} files, "
        f"{manifest['summary']['size_bytes']} bytes"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
