#!/usr/bin/env python3
"""Download offline vendor wheels for benchmark task requirements.lock files."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "harness") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "harness"))

from featureliftbench.benchmark_wheels import (  # noqa: E402
    all_benchmark_wheel_specs,
    load_source_build_packages,
    resolve_wheel_spec,
)
from featureliftbench.dependency_install import SANITY_VENDOR_WHEELS  # noqa: E402
from featureliftbench.dependency_install import dependency_name, vendor_wheel_present  # noqa: E402
from featureliftbench.paths import TASKS_DIR, VENDOR_WHEELS_DIR  # noqa: E402

DEFAULT_PLATFORMS = (
    "manylinux_2_28_x86_64",
    "manylinux2014_x86_64",
)
DEFAULT_PYTHON_VERSION = "311"


def _download_package(
    package_spec: str,
    *,
    output_dir: Path,
    platforms: tuple[str, ...],
    python_version: str,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    source_build_packages = load_source_build_packages()
    failures: list[str] = []
    for platform in platforms:
        command = [
            sys.executable,
            "-m",
            "pip",
            "download",
            "--only-binary",
            ":all:",
            "--no-deps",
            "--platform",
            platform,
            "--python-version",
            python_version,
            "--implementation",
            "cp",
            "--dest",
            str(output_dir),
            package_spec,
        ]
        completed = subprocess.run(command, text=True, capture_output=True, check=False)
        if completed.returncode == 0:
            return
        detail = (completed.stderr or completed.stdout or "").strip()
        failures.append(f"{platform}: {detail}")

    package_name = dependency_name(package_spec)
    if package_name in source_build_packages:
        build_command = [
            sys.executable,
            "-m",
            "pip",
            "wheel",
            "--no-deps",
            "--wheel-dir",
            str(output_dir),
            package_spec,
        ]
        built = subprocess.run(build_command, text=True, capture_output=True, check=False)
        normalized = package_name.replace("-", "_")
        universal = [
            path
            for path in output_dir.glob("*.whl")
            if path.name.lower().replace("-", "_").startswith(normalized)
            and path.name.endswith("-none-any.whl")
        ]
        if built.returncode == 0 and universal:
            return
        detail = (built.stderr or built.stdout or "").strip()
        raise RuntimeError(f"universal wheel build failed for {package_spec}: {detail}")

    raise RuntimeError(
        f"pip download failed for {package_spec} on compatible platforms: "
        + " | ".join(failures)
    )


def _collect_specs(*, include_tasks: bool) -> list[str]:
    specs = set(all_benchmark_wheel_specs())
    for package_name in SANITY_VENDOR_WHEELS:
        spec = resolve_wheel_spec(package_name)
        if spec:
            specs.add(spec)
    if include_tasks:
        for task_dir in sorted(TASKS_DIR.iterdir()):
            lock_path = task_dir / "requirements.lock"
            if not lock_path.is_file():
                continue
            for line in lock_path.read_text(encoding="utf-8", errors="ignore").splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    specs.add(line)
    return sorted(specs, key=str.lower)


def _collect_selection_specs(selection_path: Path) -> list[str]:
    payload = json.loads(selection_path.read_text(encoding="utf-8"))
    specs: set[str] = set()
    for row in payload.get("rows", []):
        if row.get("disposition") != "selected" or not row.get("task_id"):
            continue
        released = _REPO_ROOT / "benchmark/external50" / row["task_id"]
        task_dir = (
            released
            if (released / "requirements.lock").is_file()
            else _REPO_ROOT / "benchmark/staging" / row["task_id"]
        )
        lock_path = task_dir / "requirements.lock"
        if not lock_path.is_file():
            raise RuntimeError(f"selected task lock missing: {lock_path}")
        for line in lock_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                specs.add(line)
    return sorted(specs, key=str.lower)


def bootstrap_vendor_wheels(
    *,
    force: bool = False,
    platforms: tuple[str, ...] = DEFAULT_PLATFORMS,
    python_version: str = DEFAULT_PYTHON_VERSION,
    include_tasks: bool = True,
    package_specs: list[str] | None = None,
) -> list[str]:
    downloaded: list[str] = []
    specs = package_specs or _collect_specs(include_tasks=include_tasks)
    for package_spec in specs:
        package_name = dependency_name(package_spec)
        if not package_name:
            continue
        if not force and vendor_wheel_present(package_name):
            continue
        _download_package(
            package_spec,
            output_dir=VENDOR_WHEELS_DIR,
            platforms=platforms,
            python_version=python_version,
        )
        downloaded.append(package_name)
    return downloaded


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force",
        action="store_true",
        help="re-download wheels even when matching files already exist",
    )
    parser.add_argument(
        "--platform",
        action="append",
        dest="platforms",
        help=(
            "compatible target wheel platform in preference order (repeatable; "
            "default: manylinux_2_28_x86_64 then manylinux2014_x86_64)"
        ),
    )
    parser.add_argument(
        "--python-version",
        default=DEFAULT_PYTHON_VERSION,
        help=f"target CPython ABI tag without dot (default: {DEFAULT_PYTHON_VERSION})",
    )
    parser.add_argument(
        "--manifest-only",
        action="store_true",
        help="download only harness/config/benchmark_wheels.toml specs (skip task locks)",
    )
    parser.add_argument(
        "--selection",
        type=Path,
        help="download only lock specs for selected rows in an expansion ledger",
    )
    args = parser.parse_args()

    if args.manifest_only and args.selection:
        parser.error("--manifest-only and --selection are mutually exclusive")

    platforms = tuple(args.platforms) if args.platforms else DEFAULT_PLATFORMS
    try:
        downloaded = bootstrap_vendor_wheels(
            force=args.force,
            platforms=platforms,
            python_version=args.python_version,
            include_tasks=not args.manifest_only,
            package_specs=(
                _collect_selection_specs(args.selection.resolve())
                if args.selection
                else None
            ),
        )
    except RuntimeError as exc:
        print(f"bootstrap_vendor_wheels: {exc}", file=sys.stderr)
        return 1

    if downloaded:
        print(f"downloaded vendor wheels: {', '.join(sorted(set(downloaded)))}")
    else:
        print(f"vendor wheels already present under {VENDOR_WHEELS_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
