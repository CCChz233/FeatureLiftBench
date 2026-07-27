#!/usr/bin/env python3
"""Populate task-local pruned snapshots from verified full source archives."""

from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

from featureliftbench.source_archive import safe_extract_archive
from featureliftbench.source_archive import tree_stats


ROOT = Path(__file__).resolve().parents[1]
STAGING = ROOT / "benchmark" / "staging"
ARCHIVES = ROOT / "benchmark" / "sources" / "archives"

SOURCES = {
    "itsdangerous__timed_serializer_core__001": {
        "commit": "096c8d42545d3b68ea21a4f890fb2b2d8979c0bd",
        "archive": "github__pallets__itsdangerous__6d151186bb78--12e8bc9c7d546afb.tar.gz",
        "paths": ["src/itsdangerous", "LICENSE.txt", "README.md", "pyproject.toml"],
    },
    "flask__route_dispatch_core__001": {
        "commit": "c12a5d874c5a014495eb2db8a73f40037bc813ac",
        "archive": "github__pallets__flask__53e48a1d6ede--fb145dcd8d68fab8.tar.gz",
        "paths": ["src/flask", "LICENSE.txt", "README.md", "pyproject.toml"],
    },
    "parse__format_parser_core__001": {
        "commit": "334db144c2813e9029cb890bbd49edd30f67ab9b",
        "archive": "github__r1chardj0n3s__parse__bc0424a5126f--78db819312a60fdf.tar.gz",
        "paths": ["parse.py", "LICENSE", "README.rst", "pyproject.toml"],
    },
    "filelock__reentrant_lock_core__001": {
        "commit": "141f5d8c21be2830a9d93ad4ad822acf4b0f8a12",
        "archive": "github__tox_dev__filelock__e053d110cc3c--f39d6186b5fc3931.tar.gz",
        "paths": ["src/filelock", "LICENSE", "README.md", "pyproject.toml"],
    },
    "blinker__signal_registry_core__001": {
        "commit": "876a12a1988c1789799a1d6919abdce38a62a0ff",
        "archive": "github__pallets_eco__blinker__a8512e545418--412cc94895314af3.tar.gz",
        "paths": ["src/blinker", "LICENSE.rst", "README.rst", "pyproject.toml"],
    },
    "python_decouple__config_repository_core__001": {
        "commit": "860969c0bc7ea9f6815447b498cbaf206813865b",
        "archive": "github__hbnetwork__python_decouple__b89bface0a8b--98e12ab5f18a7472.tar.gz",
        "paths": ["decouple.py", "LICENSE", "README.rst", "setup.py"],
    },
    "decorator__signature_preserving_core__001": {
        "commit": "ad013a2c1ad7969963acf3dea948632be387f5a0",
        "archive": "github__micheles__decorator__b8543f0c0f23--bbbfca1166c63e92.tar.gz",
        "paths": ["src/decorator.py", "LICENSE.txt", "README.rst", "setup.py"],
    },
}


def main() -> int:
    for task_id, source in SOURCES.items():
        task = STAGING / task_id
        metadata_path = task / "metadata.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata["source"]["requested_tag"] = metadata["source"]["commit"]
        metadata["source"]["commit"] = source["commit"]
        metadata["source"]["resolved_commit"] = source["commit"]
        metadata_path.write_text(
            json.dumps(metadata, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        archive = ARCHIVES / source["archive"]
        with tempfile.TemporaryDirectory(prefix=f"flb-pruned-{task_id}-") as tmp:
            extracted = Path(tmp) / "full"
            safe_extract_archive(archive, extracted)
            destination = task / "repo"
            if destination.exists():
                shutil.rmtree(destination)
            destination.mkdir(parents=True)
            for relative in source["paths"]:
                origin = extracted / relative
                target = destination / relative
                if origin.is_dir():
                    shutil.copytree(origin, target, symlinks=True)
                elif origin.is_file():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(origin, target)
                else:
                    raise ValueError(f"{task_id}: missing selected source path {relative}")
        stats = tree_stats(destination)
        print(
            f"{task_id}: {stats.tracked_file_count} files, "
            f"{stats.python_loc} Python LOC, {stats.source_tree_sha256}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
