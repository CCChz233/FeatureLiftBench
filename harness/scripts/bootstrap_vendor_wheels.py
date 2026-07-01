#!/usr/bin/env python3
"""Download offline vendor wheels required by sanity smoke tasks."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "harness") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "harness"))

from featureliftbench.dependency_install import SANITY_VENDOR_WHEELS  # noqa: E402
from featureliftbench.dependency_install import sanity_vendor_wheels_ready  # noqa: E402
from featureliftbench.dependency_install import vendor_wheel_present  # noqa: E402
from featureliftbench.paths import VENDOR_WHEELS_DIR  # noqa: E402

SANITY_LOCK_PACKAGES = {
    "text-unidecode": "text-unidecode==1.3",
}


def _download_package(package_spec: str, *, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        "-m",
        "pip",
        "download",
        "--only-binary",
        ":all:",
        "--dest",
        str(output_dir),
        package_spec,
    ]
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "").strip()
        raise RuntimeError(f"pip download failed for {package_spec}: {detail}")


def bootstrap_vendor_wheels(*, force: bool = False) -> list[str]:
    downloaded: list[str] = []
    for package_name in SANITY_VENDOR_WHEELS:
        package_spec = SANITY_LOCK_PACKAGES.get(package_name, package_name)
        if not force and vendor_wheel_present(package_name):
            continue
        _download_package(package_spec, output_dir=VENDOR_WHEELS_DIR)
        downloaded.append(package_name)
    return downloaded


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force",
        action="store_true",
        help="re-download wheels even when matching files already exist",
    )
    args = parser.parse_args()

    try:
        downloaded = bootstrap_vendor_wheels(force=args.force)
    except RuntimeError as exc:
        print(f"bootstrap_vendor_wheels: {exc}", file=sys.stderr)
        return 1

    ready, missing = sanity_vendor_wheels_ready()
    if downloaded:
        print(f"downloaded vendor wheels: {', '.join(downloaded)}")
    if ready:
        print(f"vendor wheels ready under {VENDOR_WHEELS_DIR}")
        return 0

    print(
        f"bootstrap_vendor_wheels: still missing wheels for: {', '.join(missing)}",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
