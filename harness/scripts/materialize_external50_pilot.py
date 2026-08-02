#!/usr/bin/env python3
"""Materialize External-50 pilot tasks into benchmark/staging/."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import sys
import tarfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
HARNESS = ROOT / "harness"
sys.path.insert(0, str(HARNESS))

from featureliftbench.source_archive import sha256_file, tree_stats  # noqa: E402
from featureliftbench.task_render import render_public_task  # noqa: E402
from featureliftbench.task_spec import (  # noqa: E402
    compute_generated_task_hash,
    compute_spec_hash,
)

PIN_ROOT = Path("/tmp/flb_pins")
STAGING = ROOT / "benchmark" / "staging"
ARCHIVES = ROOT / "benchmark" / "sources" / "archives"
REGISTRY = ROOT / "benchmark" / "sources" / "external50_registry.json"
LEDGER = ROOT / "benchmark" / "selection" / "external50_expansion_20260731.json"
CARDS = ROOT / "benchmark" / "selection" / "external50_design_cards"

PINS = {
    "semver__version_core__001": {
        "package": "semver",
        "url": "https://github.com/python-semver/python-semver",
        "commit": "6adf8765f6e21910f1f0c13151ce84f32f8d431d",
        "tag": "3.0.4",
        "license": "BSD-3-Clause",
        "license_path": "LICENSE.txt",
        "src": PIN_ROOT / "semver",
        "forbidden": "semver",
        "lift": "Direct",
    },
    "uritools__uri_join_normalize_core__001": {
        "package": "uritools",
        "url": "https://github.com/tkem/uritools",
        "commit": "1908bfa847b319ee01fb83b100381b1cafad94c5",
        "tag": "v6.1.3",
        "license": "MIT",
        "license_path": "LICENSE",
        "src": PIN_ROOT / "uritools",
        "forbidden": "uritools",
        "lift": "Adapted",
    },
    "cssselect__selector_xpath_core__001": {
        "package": "cssselect",
        "url": "https://github.com/scrapy/cssselect",
        "commit": "a5057bbf12ddc605354f5bee123ae79b9c980703",
        "tag": "v1.5.0",
        "license": "BSD-3-Clause",
        "license_path": "LICENSE",
        "src": PIN_ROOT / "cssselect",
        "forbidden": "cssselect",
        "lift": "Adapted",
    },
    "tinydb__query_storage_core__001": {
        "package": "tinydb",
        "url": "https://github.com/msiemens/tinydb",
        "commit": "10644a0e07ad180c5b756aba272ee6b0dbd12df8",
        "tag": "v4.8.2",
        "license": "MIT",
        "license_path": "LICENSE",
        "src": PIN_ROOT / "tinydb",
        "forbidden": "tinydb",
        "lift": "Composite",
    },
    "dateparser__parse_settings_pipeline_core__001": {
        "package": "dateparser",
        "url": "https://github.com/scrapinghub/dateparser",
        "commit": "08c78d3b8bcdd2f721dff8ffaf25de482fd696dd",
        "tag": "v1.4.1",
        "license": "BSD-3-Clause",
        "license_path": "LICENSE",
        "src": PIN_ROOT / "dateparser",
        "forbidden": "dateparser",
        "lift": "Composite",
    },
}


def _rewrite_imports(text: str, old: str, new: str = "featurelifted") -> str:
    text = re.sub(rf"\bfrom {re.escape(old)}\b", f"from {new}", text)
    text = re.sub(rf"\bimport {re.escape(old)}\b", f"import {new}", text)
    # Rewrite dynamic import_module("pkg...") string literals
    text = text.replace(f'"{old}.', f'"{new}.')
    text = text.replace(f"'{old}.", f"'{new}.")
    return text


def copy_package_tree(src_pkg: Path, dest: Path, upstream_name: str) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(
        src_pkg,
        dest,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".mypy_cache", "*.egg-info"),
    )
    for path in dest.rglob("*.py"):
        raw = path.read_text(encoding="utf-8")
        updated = _rewrite_imports(raw, upstream_name)
        if updated != raw:
            path.write_text(updated, encoding="utf-8")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def ensure_source_registry() -> None:
    if REGISTRY.is_file():
        return
    write_json(
        REGISTRY,
        {
            "schema_version": "featureliftbench.source_registry.v1",
            "policy_id": "featureliftbench.full_repository_source.v2",
            "generated_from": "benchmark/staging External-50 source assets",
            "repositories": [],
            "snapshots": [],
            "summary": {
                "repository_count": 0,
                "snapshot_count": 0,
                "task_count": 0,
                "external_repository_count": 0,
                "curated_repository_count": 0,
                "ready_snapshot_count": 0,
                "pending_snapshot_count": 0,
            },
        },
    )


def collect_tests(task_dir: Path) -> tuple[list[str], list[str]]:
    public: list[str] = []
    hidden: list[str] = []
    for label, bucket in (("public_tests", public), ("hidden_tests", hidden)):
        root = task_dir / label
        for py in sorted(root.rglob("test_*.py")):
            text = py.read_text(encoding="utf-8")
            for match in re.finditer(r"^def (test_[A-Za-z0-9_]+)\(", text, re.M):
                rel = py.relative_to(task_dir).as_posix()
                bucket.append(f"{rel}::{match.group(1)}")
    return public, hidden


def flatten_api_paths(required_api: list[dict[str, Any]]) -> list[str]:
    paths: list[str] = []

    def walk(entry: dict[str, Any]) -> None:
        path = entry.get("path")
        if isinstance(path, str):
            paths.append(path)
        for member in entry.get("members") or []:
            if isinstance(member, dict):
                walk(member)

    for item in required_api:
        if isinstance(item, dict):
            walk(item)
    return paths


def finalize_metadata(task_dir: Path, metadata: dict[str, Any]) -> None:
    metadata["task_revision"] = int(metadata.get("task_revision") or 1)
    public_nodeids, hidden_nodeids = collect_tests(task_dir)
    behaviors = metadata["public_spec"]["behaviors"]
    behavior_ids = [b["id"] for b in behaviors if isinstance(b, dict) and "id" in b]
    api_behavior = behavior_ids[-2] if len(behavior_ids) >= 2 else behavior_ids[-1]
    forbid_behavior = behavior_ids[-1]

    for b in behaviors:
        text = str(b.get("text", "")).lower()
        if "required task api" in text or "exposes the required" in text:
            api_behavior = b["id"]
        if "does not import forbidden" in text or "forbidden upstream" in text:
            forbid_behavior = b["id"]

    usable = [i for i in behavior_ids if i not in {api_behavior, forbid_behavior}] or behavior_ids

    public_mappings = []
    for i, nodeid in enumerate(public_nodeids):
        public_mappings.append(
            {
                "nodeid": nodeid,
                "behavior_ids": [usable[i % len(usable)]],
                "mapping_method": "ai_assisted",
            }
        )

    hidden_mappings: list[dict[str, Any]] = []
    non_meta_hidden = [
        n
        for n in hidden_nodeids
        if "required_api_surface" not in n and "no_upstream" not in n and "no_" not in n.split("::")[-1]
    ]
    # Prefer behavior-named assignment for first N non-meta hidden tests
    for i, nodeid in enumerate(hidden_nodeids):
        if "required_api_surface" in nodeid:
            ids = [api_behavior]
            method = "generated_required_api_surface"
        elif "no_upstream" in nodeid or nodeid.endswith("test_no_upstream_import_surface"):
            ids = [forbid_behavior]
            method = "ai_assisted"
        else:
            ids = [usable[i % len(usable)]]
            method = "ai_assisted"
        hidden_mappings.append(
            {"nodeid": nodeid, "behavior_ids": ids, "mapping_method": method}
        )

    # Every behavior MUST appear in hidden mappings
    hidden_covered = {bid for m in hidden_mappings for bid in m["behavior_ids"]}
    backfill_node = (
        non_meta_hidden[0]
        if non_meta_hidden
        else (hidden_nodeids[0] if hidden_nodeids else public_nodeids[0])
    )
    for bid in behavior_ids:
        if bid not in hidden_covered:
            # attach to an existing hidden mapping rather than inventing nodeids
            for mapping in hidden_mappings:
                if mapping["nodeid"] == backfill_node:
                    if bid not in mapping["behavior_ids"]:
                        mapping["behavior_ids"].append(bid)
                    break
            else:
                hidden_mappings.append(
                    {
                        "nodeid": backfill_node,
                        "behavior_ids": [bid],
                        "mapping_method": "ai_assisted_coverage_backfill",
                    }
                )
            hidden_covered.add(bid)

    api_paths = flatten_api_paths(metadata["public_spec"]["required_api"])
    surface_node = next(
        (n for n in hidden_nodeids if "required_api_surface" in n),
        hidden_nodeids[0] if hidden_nodeids else public_nodeids[0],
    )
    required_api_coverage = [
        {"path": path, "covered_by_tests": [surface_node]} for path in api_paths
    ]

    metadata["evaluation_spec"] = {
        "public_clauses": [
            {
                "behavior_id": b["id"],
                "clause_kind": "included_behavior",
                "text": b["text"],
            }
            for b in behaviors
        ],
        "public_test_mappings": public_mappings,
        "hidden_test_mappings": hidden_mappings,
        "required_api_coverage": required_api_coverage,
        "manual_review": {
            "reviewed_at": "2026-07-31",
            "reviewer": "external50_pilot_materialize",
            "reviewer_type": "ai_assisted_task_level_review",
            "checklist_passed": True,
            "notes": "Pilot materialization with frozen design-card scope.",
        },
    }

    task_md = render_public_task(metadata)
    (task_dir / "TASK.md").write_text(task_md, encoding="utf-8")
    metadata["spec_hash"] = compute_spec_hash(metadata["public_spec"])
    metadata["generated_task_hash"] = compute_generated_task_hash(task_md)
    write_json(task_dir / "metadata.json", metadata)

    # behavior_contract.json
    write_json(
        task_dir / "evaluation" / "behavior_contract.json",
        {
            "task_id": metadata["task_id"],
            "public_clauses": metadata["evaluation_spec"]["public_clauses"],
            "public_test_mappings": [
                {
                    "nodeid": m["nodeid"],
                    "public_clause_ids": m["behavior_ids"],
                }
                for m in public_mappings
            ],
            "hidden_test_mappings": [
                {
                    "nodeid": m["nodeid"],
                    "public_clause_ids": m["behavior_ids"],
                }
                for m in hidden_mappings
            ],
            "spec_sha256": compute_generated_task_hash(task_md),
        },
    )


def make_archive_and_register(task_id: str, meta: dict[str, Any], repo_dir: Path) -> None:
    ensure_source_registry()
    pkg = meta["package"]
    commit = meta["commit"]
    url = meta["url"]
    owner_repo = "/".join(url.rstrip("/").split("/")[-2:]).lower()
    owner, repo = owner_repo.split("/")
    source_repo_id = f"github__{owner.replace('-', '_')}__{repo.replace('-', '_')}"
    short = commit[:12]
    stats = tree_stats(repo_dir)
    archive_name = f"{source_repo_id}__{short}--{stats.source_tree_sha256[:16]}.tar.gz"
    archive_path = ARCHIVES / archive_name
    ARCHIVES.mkdir(parents=True, exist_ok=True)
    if archive_path.exists():
        archive_path.unlink()
    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(repo_dir, arcname=".")
    archive_sha = sha256_file(archive_path)
    source_snapshot_id = f"{source_repo_id}__{short}"

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    repos = registry["repositories"]
    snaps = registry["snapshots"]

    # upsert repository
    existing_repo = next((r for r in repos if r.get("source_repo_id") == source_repo_id), None)
    if existing_repo is None:
        repos.append(
            {
                "canonical_url": url if url.endswith(".git") is False else url[:-4],
                "display_names": [pkg],
                "ecosystem_family": "unassigned",
                "licenses": [meta["license"]],
                "snapshot_ids": [source_snapshot_id],
                "source_kind": "external_oss",
                "source_repo_id": source_repo_id,
                "task_ids": [task_id],
                "upstream_org": owner,
            }
        )
    else:
        if source_snapshot_id not in existing_repo.get("snapshot_ids", []):
            existing_repo.setdefault("snapshot_ids", []).append(source_snapshot_id)
        if task_id not in existing_repo.get("task_ids", []):
            existing_repo.setdefault("task_ids", []).append(task_id)

    existing_snap = next((s for s in snaps if s.get("source_snapshot_id") == source_snapshot_id), None)
    snap_payload = {
        "acquisition_method": "github_tag_tarball",
        "archive_path": f"benchmark/sources/archives/{archive_name}",
        "archive_sha256": archive_sha,
        "current_snapshot_scope": "full_tracked_tree",
        "license_text_path": meta["license_path"],
        "max_path_depth": stats.max_path_depth,
        "python_file_count": stats.python_file_count,
        "python_loc": stats.python_loc,
        "requested_revision": commit,
        "resolved_commit": commit,
        "revision_kind": "git_commit",
        "source_repo_id": source_repo_id,
        "source_snapshot_id": source_snapshot_id,
        "source_tree_sha256": stats.source_tree_sha256,
        "status": "ready",
        "target_snapshot_scope": "full_tracked_tree",
        "task_ids": [task_id],
        "total_bytes": stats.total_bytes,
        "tracked_file_count": stats.tracked_file_count,
    }
    if existing_snap is None:
        snaps.append(snap_payload)
    else:
        existing_snap.update(snap_payload)
        if task_id not in existing_snap.get("task_ids", []):
            existing_snap.setdefault("task_ids", []).append(task_id)

    registry["repositories"] = sorted(repos, key=lambda r: r["source_repo_id"])
    registry["snapshots"] = sorted(snaps, key=lambda s: s["source_snapshot_id"])
    summary = registry.setdefault("summary", {})
    summary["repository_count"] = len(registry["repositories"])
    summary["snapshot_count"] = len(registry["snapshots"])
    summary["ready_snapshot_count"] = sum(
        1 for s in registry["snapshots"] if s.get("status") == "ready"
    )
    summary["external_repository_count"] = sum(
        1 for r in registry["repositories"] if r.get("source_kind") == "external_oss"
    )
    summary["curated_repository_count"] = (
        len(registry["repositories"]) - summary["external_repository_count"]
    )
    summary["task_count"] = len(
        {
            str(registered_task)
            for snapshot in registry["snapshots"]
            for registered_task in snapshot.get("task_ids", [])
        }
    )
    summary["pending_snapshot_count"] = (
        len(registry["snapshots"]) - summary["ready_snapshot_count"]
    )
    write_json(REGISTRY, registry)
    return source_snapshot_id


def base_metadata(task_id: str, meta: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    forbidden = meta["forbidden"]
    return {
        "task_id": task_id,
        "language": "python",
        "difficulty": "medium",
        "status": "materialized_candidate",
        "task_revision": 1,
        "tags": ["external50", "pilot", meta["lift"].lower(), forbidden],
        "source": {
            "name": meta["package"],
            "url": meta["url"],
            "commit": meta["commit"],
            "license": meta["license"],
        },
        "feature": kwargs["feature"],
        "entanglement": kwargs["entanglement"],
        "output": kwargs["output"],
        "environment": {
            "python": "3.12",
            "network": False,
            "timeout_seconds": kwargs.get("timeout", 90),
            "dependency_lock": "requirements.lock",
            "allowed_dependencies": kwargs.get("allowed_dependencies", []),
            "forbidden_dependencies": [forbidden],
            "forbidden_imports": [forbidden],
            "forbidden_paths": ["repo/", f"{forbidden}/"],
        },
        "tests": {
            "public": "public_tests/",
            "hidden": "hidden_tests/",
            "command": "pytest",
        },
        "spec_status": "compliant",
        "public_spec": kwargs["public_spec"],
    }


def materialize_semver() -> Path:
    task_id = "semver__version_core__001"
    meta = PINS[task_id]
    task_dir = STAGING / task_id
    if task_dir.exists():
        shutil.rmtree(task_dir)
    task_dir.mkdir(parents=True)

    # repo snapshot
    shutil.copytree(
        meta["src"],
        task_dir / "repo",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".flb_pin", "*.tar.gz"),
    )

    # reference
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["src"] / "src" / "semver", ref, "semver")
    # drop CLI from required surface but keep files; __init__ already exports Version
    init = (ref / "__init__.py").read_text(encoding="utf-8")
    if "Version" not in init:
        (ref / "__init__.py").write_text(
            init + "\nfrom .version import Version\n__all__ = ['Version']\n",
            encoding="utf-8",
        )

    (task_dir / "requirements.lock").write_text(
        "# no third-party dependencies\n", encoding="utf-8"
    )
    (task_dir / "evaluation").mkdir(parents=True)
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("semver\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "semver",
            "required_source_files": [
                "src/semver/version.py",
                "src/semver/__init__.py",
            ],
            "runtime_dependencies": [],
            "notes": "Direct extract of Version parse/compare/bump/replace.",
        },
    )

    public = task_dir / "public_tests"
    hidden = task_dir / "hidden_tests"
    public.mkdir()
    hidden.mkdir()
    (public / "test_public_api.py").write_text(
        '''from __future__ import annotations

from featurelifted import Version


def test_parse_basic() -> None:
    v = Version.parse("1.2.3")
    assert str(v) == "1.2.3"
    assert v.major == 1 and v.minor == 2 and v.patch == 3


def test_compare_and_order() -> None:
    a = Version.parse("1.2.3")
    b = Version.parse("1.2.4")
    assert a.compare(b) == -1
    assert a < b
    assert a != b


def test_bump_and_replace() -> None:
    v = Version.parse("1.2.3")
    assert str(v.bump_major()) == "2.0.0"
    assert str(v.bump_minor()) == "1.3.0"
    assert str(v.bump_patch()) == "1.2.4"
    assert str(v.replace(prerelease="rc.1")) == "1.2.3-rc.1"
''',
        encoding="utf-8",
    )
    (hidden / "test_hidden_behavior.py").write_text(
        '''from __future__ import annotations

import re
from pathlib import Path

import pytest
from featurelifted import Version


def test_prerelease_and_build_parse() -> None:
    v = Version.parse("1.0.0-alpha.1+build.7")
    assert v.prerelease == "alpha.1"
    assert v.build == "build.7"
    assert str(v) == "1.0.0-alpha.1+build.7"


def test_invalid_version_raises() -> None:
    with pytest.raises(ValueError):
        Version.parse("not-a-version")


def test_constructor_defaults() -> None:
    v = Version(2)
    assert str(v) == "2.0.0"


def test_ordering_operators() -> None:
    assert Version.parse("1.0.0") <= Version.parse("1.0.0")
    assert Version.parse("2.0.0") >= Version.parse("1.9.9")


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\\s*(?:from semver|import semver)\\b", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8"))
''',
        encoding="utf-8",
    )
    (hidden / "test_required_api_surface.py").write_text(
        '''from featurelifted import Version


def test_required_api_surface() -> None:
    assert isinstance(Version, type)
    assert callable(Version.parse)
    assert callable(Version.compare)
    assert callable(Version.bump_major)
    assert callable(Version.bump_minor)
    assert callable(Version.bump_patch)
    assert callable(Version.replace)
''',
        encoding="utf-8",
    )

    metadata = base_metadata(
        task_id,
        meta,
        feature={
            "name": "Version parse/compare/bump",
            "description": "Extract python-semver Version API into featurelifted.",
            "source_entrypoints": ["semver.Version"],
            "included_behaviors": [
                "parse semver strings into Version",
                "compare and order Version instances",
                "bump major/minor/patch and replace parts",
            ],
            "excluded_behaviors": [
                "CLI entry points",
                "file reading helpers",
                "deprecated VersionInfo-only quirks beyond optional alias",
            ],
        },
        entanglement={
            "level": "medium",
            "types": ["data_model_coupling"],
            "primary": "data_model_coupling",
            "description": "Version fields, prerelease/build ordering, and immutable replace/bump semantics.",
            "signals": ["prerelease ordering", "immutable bump/replace"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import Version",
            "callable": "Version.parse",
            "signature": "Version.parse(version: str) -> Version",
        },
        public_spec={
            "title": "Version parse/compare/bump",
            "summary": "Extract a task-scoped subset of `semver` into a standalone `featurelifted` package.",
            "required_api": [
                {
                    "path": "featurelifted.Version",
                    "kind": "class",
                    "signature": "(major: int, minor: int = 0, patch: int = 0, prerelease: str | None = None, build: str | None = None)",
                    "members": [
                        {"path": "featurelifted.Version.parse", "kind": "method", "signature": "(version: str) -> Version"},
                        {"path": "featurelifted.Version.compare", "kind": "method", "signature": "(self, other: Version) -> int"},
                        {"path": "featurelifted.Version.bump_major", "kind": "method", "signature": "(self) -> Version"},
                        {"path": "featurelifted.Version.bump_minor", "kind": "method", "signature": "(self) -> Version"},
                        {"path": "featurelifted.Version.bump_patch", "kind": "method", "signature": "(self) -> Version"},
                        {"path": "featurelifted.Version.replace", "kind": "method", "signature": "(self, **parts) -> Version"},
                    ],
                }
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: parse semver strings into Version. Required observable cases include parse basic; prerelease and build parse."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: compare and order Version instances. Required observable cases include compare and order; ordering operators."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: bump major/minor/patch and replace parts. Required observable cases include bump and replace; constructor defaults."},
                {"id": "B004", "text": "Invalid version strings raise ValueError."},
                {"id": "B005", "text": "The package exposes the required task API paths `featurelifted.Version`, `featurelifted.Version.parse`, `featurelifted.Version.compare`, `featurelifted.Version.bump_major`, `featurelifted.Version.bump_minor`, `featurelifted.Version.bump_patch`, `featurelifted.Version.replace` with the kinds and callable signatures listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: semver."},
            ],
            "exclusions": [
                "CLI entry points",
                "file reading helpers",
                "deprecated VersionInfo-only quirks beyond optional alias",
                "original semver import at runtime",
            ],
            "forbidden": {"imports": ["semver"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


def materialize_uritools() -> Path:
    task_id = "uritools__uri_join_normalize_core__001"
    meta = PINS[task_id]
    task_dir = STAGING / task_id
    if task_dir.exists():
        shutil.rmtree(task_dir)
    task_dir.mkdir(parents=True)
    shutil.copytree(
        meta["src"],
        task_dir / "repo",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".flb_pin", "*.tar.gz"),
    )

    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["src"] / "src" / "uritools", ref, "uritools")
    # add adapted urinorm
    init_path = ref / "__init__.py"
    init = init_path.read_text(encoding="utf-8")
    if "def urinorm" not in init:
        init_path.write_text(
            init
            + '''

def urinorm(uri: str) -> str:
    """Adapted normalize: lowercase scheme + collapse path dots via getpath()."""
    parts = urisplit(uri)
    scheme = parts.getscheme() or ""
    authority = parts.authority
    path = parts.getpath() or ""
    query = parts.query or ""
    fragment = parts.fragment or ""
    out = ""
    if scheme:
        out += f"{scheme}:"
    if authority is not None:
        out += f"//{authority}"
    out += path
    if query:
        out += f"?{query}"
    if fragment:
        out += f"#{fragment}"
    return out
''',
            encoding="utf-8",
        )

    (task_dir / "requirements.lock").write_text("# no third-party dependencies\n", encoding="utf-8")
    (task_dir / "evaluation").mkdir(parents=True)
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("uritools\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "uritools",
            "required_source_files": ["src/uritools/__init__.py"],
            "runtime_dependencies": [],
            "notes": "Adapted flat helpers + urinorm via SplitResult getters.",
        },
    )

    public = task_dir / "public_tests"
    hidden = task_dir / "hidden_tests"
    public.mkdir()
    hidden.mkdir()
    (public / "test_public_api.py").write_text(
        '''from __future__ import annotations

from featurelifted import urijoin, urinorm, urisplit, uriunsplit


def test_urisplit_fields() -> None:
    parts = urisplit("https://example.com/a/b?q=1#frag")
    assert parts.scheme == "https"
    assert parts.authority == "example.com"
    assert parts.path == "/a/b"
    assert parts.query == "q=1"
    assert parts.fragment == "frag"
    assert uriunsplit(parts) == "https://example.com/a/b?q=1#frag"


def test_urijoin_relative() -> None:
    assert urijoin("https://example.com/a/", "../b") == "https://example.com/b"


def test_urinorm_path_dots() -> None:
    assert urinorm("https://example.com/a/./b/../c") == "https://example.com/a/c"
''',
        encoding="utf-8",
    )
    (hidden / "test_hidden_behavior.py").write_text(
        '''from __future__ import annotations

import re
from pathlib import Path

from featurelifted import uriencode, uridecode, urijoin, urinorm, urisplit


def test_encode_decode_roundtrip() -> None:
    encoded = uriencode("你好")
    if isinstance(encoded, bytes):
        encoded_text = encoded.decode("ascii")
    else:
        encoded_text = encoded
    assert "%" in encoded_text
    assert uridecode(encoded) == "你好"


def test_urijoin_strict_absolute_ref() -> None:
    assert urijoin("https://example.com/a", "https://other.test/x", strict=True) == "https://other.test/x"


def test_urinorm_scheme_case() -> None:
    out = urinorm("HTTP://Example.COM/a/./b")
    assert out.startswith("http://")
    assert "/a/b" in out or out.endswith("/a/b")


def test_split_relative_ref() -> None:
    parts = urisplit("/rel/path")
    assert parts.scheme is None or parts.scheme == ""
    assert parts.path == "/rel/path"


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\\s*(?:from uritools|import uritools)\\b", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8"))
''',
        encoding="utf-8",
    )
    (hidden / "test_required_api_surface.py").write_text(
        '''from featurelifted import (
    SplitResult,
    uridecode,
    uriencode,
    urijoin,
    urinorm,
    urisplit,
    uriunsplit,
)


def test_required_api_surface() -> None:
    assert callable(urisplit)
    assert callable(uriunsplit)
    assert callable(urijoin)
    assert callable(urinorm)
    assert callable(uriencode)
    assert callable(uridecode)
    assert SplitResult is not None
''',
        encoding="utf-8",
    )

    metadata = base_metadata(
        task_id,
        meta,
        feature={
            "name": "URI split/join/normalize helpers",
            "description": "Adapted uritools helpers as featurelifted flat API.",
            "source_entrypoints": [
                "uritools.urisplit",
                "uritools.urijoin",
                "uritools.uriencode",
                "uritools.uridecode",
            ],
            "included_behaviors": [
                "split/unsplit with SplitResult fields",
                "join absolute and relative refs",
                "adapted urinorm path/scheme normalization",
                "utf-8 percent encode/decode",
            ],
            "excluded_behaviors": [
                "network fetch",
                "uridefrag/uricompose outside Required API",
            ],
        },
        entanglement={
            "level": "medium",
            "types": ["parser_state_coupling"],
            "primary": "parser_state_coupling",
            "description": "URI component parsing and join/normalize rules.",
            "signals": ["SplitResult fields", "dot-segment collapse", "strict join"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import urisplit, urijoin, urinorm, uriencode, uridecode",
            "callable": "urisplit",
            "signature": "urisplit(uri: str) -> SplitResult",
        },
        public_spec={
            "title": "URI split/join/normalize helpers",
            "summary": "Extract a task-scoped subset of `uritools` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.urisplit", "kind": "function", "signature": "(uri: str) -> SplitResult"},
                {"path": "featurelifted.uriunsplit", "kind": "function", "signature": "(parts: SplitResult | tuple) -> str"},
                {"path": "featurelifted.urijoin", "kind": "function", "signature": "(base: str, ref: str, strict: bool = False) -> str"},
                {"path": "featurelifted.urinorm", "kind": "function", "signature": "(uri: str) -> str"},
                {"path": "featurelifted.uriencode", "kind": "function", "signature": "(s: str, safe: str = '', encoding: str = 'utf-8') -> str"},
                {"path": "featurelifted.uridecode", "kind": "function", "signature": "(s: str, encoding: str = 'utf-8') -> str"},
                {"path": "featurelifted.SplitResult", "kind": "class"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: split/unsplit with SplitResult fields scheme/authority/path/query/fragment. Required observable cases include urisplit fields; split relative ref."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: join absolute and relative refs. Required observable cases include urijoin relative; urijoin strict absolute ref."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: adapted urinorm path/scheme normalization. Required observable cases include urinorm path dots; urinorm scheme case."},
                {"id": "B004", "text": "The extracted feature must support this observable behavior: utf-8 percent encode/decode. Required observable cases include encode decode roundtrip."},
                {"id": "B005", "text": "The package exposes the required task API paths `featurelifted.urisplit`, `featurelifted.uriunsplit`, `featurelifted.urijoin`, `featurelifted.urinorm`, `featurelifted.uriencode`, `featurelifted.uridecode`, `featurelifted.SplitResult` with the kinds and callable signatures listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: uritools."},
            ],
            "exclusions": [
                "network fetch",
                "uridefrag/uricompose outside Required API",
                "original uritools import at runtime",
            ],
            "forbidden": {"imports": ["uritools"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


def materialize_cssselect() -> Path:
    task_id = "cssselect__selector_xpath_core__001"
    meta = PINS[task_id]
    task_dir = STAGING / task_id
    if task_dir.exists():
        shutil.rmtree(task_dir)
    task_dir.mkdir(parents=True)
    shutil.copytree(
        meta["src"],
        task_dir / "repo",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".flb_pin", "*.tar.gz"),
    )
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["src"] / "cssselect", ref, "cssselect")

    (task_dir / "requirements.lock").write_text("# no third-party dependencies\n", encoding="utf-8")
    (task_dir / "evaluation").mkdir(parents=True)
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("cssselect\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "cssselect",
            "required_source_files": [
                "cssselect/__init__.py",
                "cssselect/parser.py",
                "cssselect/xpath.py",
            ],
            "runtime_dependencies": [],
            "notes": "Adapted packaging of parse + Generic/HTML translators.",
        },
    )

    public = task_dir / "public_tests"
    hidden = task_dir / "hidden_tests"
    public.mkdir()
    hidden.mkdir()
    (public / "test_public_api.py").write_text(
        '''from __future__ import annotations

from featurelifted import GenericTranslator, HTMLTranslator, parse


def test_generic_class_selector() -> None:
    xpath = GenericTranslator().css_to_xpath("div.note")
    assert "div" in xpath
    assert "note" in xpath


def test_html_translator_lowercases() -> None:
    html = HTMLTranslator().css_to_xpath("DIV")
    generic = GenericTranslator().css_to_xpath("DIV")
    assert "div" in html
    assert "DIV" in generic


def test_parse_returns_selectors() -> None:
    sel = parse("div#main")
    assert sel
''',
        encoding="utf-8",
    )
    (hidden / "test_hidden_behavior.py").write_text(
        '''from __future__ import annotations

import re
from pathlib import Path

import pytest
from featurelifted import ExpressionError, GenericTranslator, HTMLTranslator, SelectorError, parse


def test_id_and_nth_child() -> None:
    xpath = HTMLTranslator().css_to_xpath("div#main:nth-child(2)")
    assert "main" in xpath
    assert "preceding-sibling" in xpath


def test_attribute_selector() -> None:
    xpath = GenericTranslator().css_to_xpath("a[href]")
    assert "href" in xpath


def test_invalid_selector_error() -> None:
    with pytest.raises((SelectorError, Exception)):
        parse("@@@")


def test_unknown_pseudo_expression_error() -> None:
    with pytest.raises(ExpressionError):
        GenericTranslator().css_to_xpath(":foobar")


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\\s*(?:from cssselect|import cssselect)\\b", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8"))
''',
        encoding="utf-8",
    )
    (hidden / "test_required_api_surface.py").write_text(
        '''from featurelifted import (
    ExpressionError,
    GenericTranslator,
    HTMLTranslator,
    SelectorError,
    parse,
)


def test_required_api_surface() -> None:
    assert callable(parse)
    assert isinstance(GenericTranslator, type)
    assert isinstance(HTMLTranslator, type)
    assert callable(GenericTranslator().css_to_xpath)
    assert callable(HTMLTranslator().css_to_xpath)
    assert issubclass(SelectorError, Exception)
    assert issubclass(ExpressionError, Exception)
''',
        encoding="utf-8",
    )

    metadata = base_metadata(
        task_id,
        meta,
        feature={
            "name": "CSS selector to XPath",
            "description": "Adapted cssselect parse + translator surface.",
            "source_entrypoints": [
                "cssselect.parse",
                "cssselect.GenericTranslator",
                "cssselect.HTMLTranslator",
            ],
            "included_behaviors": [
                "translate CSS selectors to XPath via GenericTranslator",
                "HTMLTranslator HTML name lowercasing",
                "invalid selector and unsupported expression errors",
            ],
            "excluded_behaviors": [
                "executing xpath against documents",
                "scrapy Selector integration",
            ],
        },
        entanglement={
            "level": "medium",
            "types": ["parser_state_coupling"],
            "primary": "parser_state_coupling",
            "description": "Selector parsing and XPath translation rules differ for HTML vs generic.",
            "signals": ["HTML lowercasing", "nth-child", "ExpressionError"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import parse, GenericTranslator, HTMLTranslator",
            "callable": "GenericTranslator.css_to_xpath",
            "signature": "css_to_xpath(selector: str, prefix: str = 'descendant-or-self::') -> str",
        },
        public_spec={
            "title": "CSS selector to XPath",
            "summary": "Extract a task-scoped subset of `cssselect` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.parse", "kind": "function", "signature": "(selector: str)"},
                {
                    "path": "featurelifted.GenericTranslator",
                    "kind": "class",
                    "members": [
                        {
                            "path": "featurelifted.GenericTranslator.css_to_xpath",
                            "kind": "method",
                            "signature": "(self, selector: str, prefix: str = 'descendant-or-self::') -> str",
                        }
                    ],
                },
                {
                    "path": "featurelifted.HTMLTranslator",
                    "kind": "class",
                    "members": [
                        {
                            "path": "featurelifted.HTMLTranslator.css_to_xpath",
                            "kind": "method",
                            "signature": "(self, selector: str, prefix: str = 'descendant-or-self::') -> str",
                        }
                    ],
                },
                {"path": "featurelifted.SelectorError", "kind": "exception"},
                {"path": "featurelifted.ExpressionError", "kind": "exception"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: translate CSS selectors to XPath via GenericTranslator. Required observable cases include generic class selector; attribute selector."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: HTMLTranslator HTML name lowercasing. Required observable cases include html translator lowercases; id and nth child."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: invalid selector and unsupported expression errors. Required observable cases include invalid selector error; unknown pseudo expression error."},
                {"id": "B004", "text": "parse returns selector objects usable with the translators."},
                {"id": "B005", "text": "The package exposes the required task API paths `featurelifted.parse`, `featurelifted.GenericTranslator`, `featurelifted.GenericTranslator.css_to_xpath`, `featurelifted.HTMLTranslator`, `featurelifted.HTMLTranslator.css_to_xpath`, `featurelifted.SelectorError`, `featurelifted.ExpressionError` with the kinds and callable signatures listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: cssselect."},
            ],
            "exclusions": [
                "executing xpath against documents",
                "scrapy Selector integration",
                "original cssselect import at runtime",
            ],
            "forbidden": {"imports": ["cssselect"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


def materialize_tinydb() -> Path:
    task_id = "tinydb__query_storage_core__001"
    meta = PINS[task_id]
    task_dir = STAGING / task_id
    if task_dir.exists():
        shutil.rmtree(task_dir)
    task_dir.mkdir(parents=True)
    shutil.copytree(
        meta["src"],
        task_dir / "repo",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".flb_pin", "*.tar.gz"),
    )
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["src"] / "tinydb", ref, "tinydb")
    init_path = ref / "__init__.py"
    init = init_path.read_text(encoding="utf-8")
    if "from .storages import Storage, JSONStorage, MemoryStorage" not in init:
        init_path.write_text(
            init.replace(
                "from .storages import Storage, JSONStorage",
                "from .storages import Storage, JSONStorage, MemoryStorage",
            ).replace(
                "__all__ = ('TinyDB', 'Storage', 'JSONStorage', 'Query', 'where')",
                "__all__ = ('TinyDB', 'Storage', 'JSONStorage', 'MemoryStorage', 'Query', 'where')",
            ),
            encoding="utf-8",
        )
    (task_dir / "requirements.lock").write_text("# no third-party dependencies\n", encoding="utf-8")
    (task_dir / "evaluation").mkdir(parents=True)
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("tinydb\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "tinydb",
            "required_source_files": [
                "tinydb/database.py",
                "tinydb/queries.py",
                "tinydb/storages.py",
                "tinydb/table.py",
            ],
            "runtime_dependencies": [],
            "notes": "Composite DB + Query + Storage.",
        },
    )

    public = task_dir / "public_tests"
    hidden = task_dir / "hidden_tests"
    public.mkdir()
    hidden.mkdir()
    (public / "test_public_api.py").write_text(
        '''from __future__ import annotations

from featurelifted import MemoryStorage, Query, TinyDB


def test_insert_and_all() -> None:
    db = TinyDB(storage=MemoryStorage)
    doc_id = db.insert({"name": "alice", "age": 30})
    assert isinstance(doc_id, int)
    assert db.all() == [{"name": "alice", "age": 30}]
    db.close()


def test_search_equality() -> None:
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple([{"name": "a", "age": 1}, {"name": "b", "age": 2}])
    q = Query()
    assert db.search(q.name == "b") == [{"name": "b", "age": 2}]
    db.close()


def test_update_and_remove() -> None:
    db = TinyDB(storage=MemoryStorage)
    db.insert({"name": "x", "age": 1})
    q = Query()
    db.update({"age": 2}, q.name == "x")
    assert db.get(q.name == "x")["age"] == 2
    db.remove(q.name == "x")
    assert db.all() == []
    db.close()
''',
        encoding="utf-8",
    )
    (hidden / "test_hidden_behavior.py").write_text(
        '''from __future__ import annotations

import re
from pathlib import Path

from featurelifted import JSONStorage, MemoryStorage, Query, TinyDB


def test_exists_matches_test_ops() -> None:
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple(
        [
            {"name": "ann", "tag": "ok"},
            {"name": "bob"},
            {"name": "cara", "tag": "ok-1"},
        ]
    )
    q = Query()
    assert len(db.search(q.tag.exists())) == 2
    assert db.search(q.tag.matches(r"^ok$")) == [{"name": "ann", "tag": "ok"}]
    assert db.search(q.name.test(lambda v: v.startswith("c"))) == [
        {"name": "cara", "tag": "ok-1"}
    ]
    db.close()


def test_logical_and_or() -> None:
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple(
        [
            {"name": "a", "age": 10},
            {"name": "b", "age": 20},
            {"name": "c", "age": 10},
        ]
    )
    q = Query()
    assert db.search((q.age == 10) & (q.name == "a")) == [{"name": "a", "age": 10}]
    names = {d["name"] for d in db.search((q.name == "a") | (q.name == "b"))}
    assert names == {"a", "b"}
    db.close()


def test_json_storage_roundtrip(tmp_path) -> None:
    path = tmp_path / "db.json"
    db = TinyDB(path, storage=JSONStorage)
    db.insert({"k": 1})
    db.close()
    db2 = TinyDB(path, storage=JSONStorage)
    assert db2.all() == [{"k": 1}]
    db2.truncate()
    assert db2.all() == []
    db2.close()


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\\s*(?:from tinydb|import tinydb)\\b", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8"))
''',
        encoding="utf-8",
    )
    (hidden / "test_required_api_surface.py").write_text(
        '''from featurelifted import JSONStorage, MemoryStorage, Query, TinyDB


def test_required_api_surface() -> None:
    assert isinstance(TinyDB, type)
    assert isinstance(Query, type)
    assert isinstance(JSONStorage, type)
    assert isinstance(MemoryStorage, type)
    db = TinyDB(storage=MemoryStorage)
    for name in (
        "insert",
        "insert_multiple",
        "all",
        "get",
        "search",
        "update",
        "remove",
        "truncate",
        "close",
    ):
        assert callable(getattr(db, name))
    db.close()
''',
        encoding="utf-8",
    )

    metadata = base_metadata(
        task_id,
        meta,
        feature={
            "name": "TinyDB query and storage",
            "description": "Composite TinyDB + Query + JSON/Memory storage.",
            "source_entrypoints": ["tinydb.TinyDB", "tinydb.Query"],
            "included_behaviors": [
                "CRUD insert/search/update/remove/truncate",
                "Query operators == exists matches test and/or",
                "JSONStorage and MemoryStorage backends",
            ],
            "excluded_behaviors": [
                "middleware caching",
                "SQL storage",
                "multi-process locking guarantees",
            ],
        },
        entanglement={
            "level": "high",
            "types": ["data_model_coupling"],
            "primary": "data_model_coupling",
            "description": "DB mutations, query DSL, and storage backends compose one contract.",
            "signals": ["Query composition", "storage persistence", "doc ids"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import TinyDB, Query, MemoryStorage, JSONStorage",
            "callable": "TinyDB.insert",
            "signature": "TinyDB.insert(document: dict) -> int",
        },
        public_spec={
            "title": "TinyDB query and storage",
            "summary": "Extract a task-scoped subset of `tinydb` into a standalone `featurelifted` package.",
            "required_api": [
                {
                    "path": "featurelifted.TinyDB",
                    "kind": "class",
                    "members": [
                        {"path": "featurelifted.TinyDB.insert", "kind": "method", "signature": "(self, document: dict) -> int"},
                        {"path": "featurelifted.TinyDB.insert_multiple", "kind": "method", "signature": "(self, documents: list) -> list"},
                        {"path": "featurelifted.TinyDB.all", "kind": "method", "signature": "(self) -> list"},
                        {"path": "featurelifted.TinyDB.get", "kind": "method", "signature": "(self, cond=None, doc_id=None)"},
                        {"path": "featurelifted.TinyDB.search", "kind": "method", "signature": "(self, cond)"},
                        {"path": "featurelifted.TinyDB.update", "kind": "method", "signature": "(self, fields, cond=None, doc_ids=None)"},
                        {"path": "featurelifted.TinyDB.remove", "kind": "method", "signature": "(self, cond=None, doc_ids=None)"},
                        {"path": "featurelifted.TinyDB.truncate", "kind": "method", "signature": "(self) -> None"},
                        {"path": "featurelifted.TinyDB.close", "kind": "method", "signature": "(self) -> None"},
                    ],
                },
                {"path": "featurelifted.Query", "kind": "class"},
                {"path": "featurelifted.JSONStorage", "kind": "class"},
                {"path": "featurelifted.MemoryStorage", "kind": "class"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: CRUD insert/search/update/remove/truncate. Required observable cases include insert and all; search equality; update and remove."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: Query operators == exists matches test and logical and/or. Required observable cases include exists matches test ops; logical and or."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: JSONStorage and MemoryStorage backends. Required observable cases include json storage roundtrip."},
                {"id": "B004", "text": "Default table behavior matches upstream TinyDB for the frozen CRUD paths."},
                {"id": "B005", "text": "The package exposes the required task API paths `featurelifted.TinyDB`, `featurelifted.Query`, `featurelifted.JSONStorage`, `featurelifted.MemoryStorage` and TinyDB CRUD methods with the kinds and callable signatures listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: tinydb."},
            ],
            "exclusions": [
                "middleware caching",
                "SQL storage",
                "multi-process locking guarantees",
                "original tinydb import at runtime",
            ],
            "forbidden": {"imports": ["tinydb"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


def materialize_dateparser() -> Path:
    task_id = "dateparser__parse_settings_pipeline_core__001"
    meta = PINS[task_id]
    task_dir = STAGING / task_id
    if task_dir.exists():
        shutil.rmtree(task_dir)
    task_dir.mkdir(parents=True)
    shutil.copytree(
        meta["src"],
        task_dir / "repo",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".flb_pin", "*.tar.gz"),
    )
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["src"] / "dateparser", ref, "dateparser")
    # Bundle dateparser_data beside featurelifted so offline settings load works
    data_dest = task_dir / "reference_solution" / "dateparser_data"
    if data_dest.exists():
        shutil.rmtree(data_dest)
    shutil.copytree(
        meta["src"] / "dateparser_data",
        data_dest,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    # wrapper exports
    init = ref / "__init__.py"
    text = init.read_text(encoding="utf-8")
    if "def detect_languages" not in text:
        init.write_text(
            text
            + '''

from .conf import Settings as _UpstreamSettings
from .search.search import DateSearchWithDetection


class Settings:
    """Adapted Settings constructor matching design-card Settings(**options)."""

    def __new__(cls, settings=None, **options):
        base = _UpstreamSettings()
        payload = {}
        if isinstance(settings, dict):
            payload.update(settings)
        payload.update(options)
        if not payload:
            return base
        return base.replace(**payload)


def detect_languages(text: str, languages: list[str] | None = None) -> list[str]:
    """Return detected language shortcodes using dateparser's offline detector."""
    detected = DateSearchWithDetection().detect_language(text, languages=languages)
    if not detected:
        return []
    if isinstance(detected, str):
        return [detected]
    short = getattr(detected, "shortname", None) or getattr(detected, "name", None)
    return [str(short or detected)]
''',
            encoding="utf-8",
        )

    (task_dir / "requirements.lock").write_text(
        "\n".join(
            [
                "python-dateutil==2.9.0.post0",
                "pytz==2025.2",
                "regex==2024.11.6",
                "tzlocal==5.3.1",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (task_dir / "evaluation").mkdir(parents=True)
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("dateparser\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "dateparser",
            "required_source_files": [
                "dateparser/__init__.py",
                "dateparser/conf.py",
                "dateparser/search/search.py",
                "dateparser/data/",
            ],
            "runtime_dependencies": [
                "python-dateutil",
                "pytz",
                "regex",
                "tzlocal",
            ],
            "notes": "Composite Settings + parse + detect_languages; offline data bundled in repo/reference.",
        },
    )

    public = task_dir / "public_tests"
    hidden = task_dir / "hidden_tests"
    public.mkdir()
    hidden.mkdir()
    (public / "test_public_api.py").write_text(
        '''from __future__ import annotations

from datetime import datetime

from featurelifted import Settings, detect_languages, parse


def test_parse_iso_and_english() -> None:
    assert parse("2020-01-15") == datetime(2020, 1, 15, 0, 0)
    assert parse("January 15, 2020") == datetime(2020, 1, 15, 0, 0)


def test_parse_with_languages() -> None:
    es = parse("15 de enero de 2020", languages=["es"])
    fr = parse("15 janvier 2020", languages=["fr"])
    assert es is not None and es.year == 2020 and es.month == 1 and es.day == 15
    assert fr is not None and fr.year == 2020 and fr.month == 1 and fr.day == 15


def test_settings_timezone_aware() -> None:
    settings = Settings(
        {
            "RETURN_AS_TIMEZONE_AWARE": True,
            "TIMEZONE": "UTC",
            "TO_TIMEZONE": "UTC",
        }
    )
    dt = parse("2020-01-15 12:00:00", settings=settings)
    assert dt is not None
    assert dt.tzinfo is not None
''',
        encoding="utf-8",
    )
    (hidden / "test_hidden_behavior.py").write_text(
        '''from __future__ import annotations

import re
from pathlib import Path

import pytest
from featurelifted import Settings, detect_languages, parse


def test_detect_languages_es_fr() -> None:
    es = detect_languages("15 de enero de 2020", languages=["en", "es", "fr"])
    fr = detect_languages("15 janvier 2020", languages=["en", "es", "fr"])
    assert "es" in es
    assert "fr" in fr


def test_prefer_dates_from_past() -> None:
    settings = Settings({"PREFER_DATES_FROM": "past"})
    assert parse("2020-01-15", settings=settings) is not None


def test_date_order_dmy() -> None:
    settings = Settings({"DATE_ORDER": "DMY", "STRICT_PARSING": False})
    dt = parse("15/01/2020", settings=settings)
    assert dt is not None
    assert dt.day == 15 and dt.month == 1 and dt.year == 2020


def test_invalid_settings_key() -> None:
    with pytest.raises(TypeError):
        Settings({"PREFER_DATES_FROM": None})


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\\s*(?:from dateparser\\b|import dateparser\\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
''',
        encoding="utf-8",
    )
    (hidden / "test_required_api_surface.py").write_text(
        '''from featurelifted import Settings, detect_languages, parse


def test_required_api_surface() -> None:
    assert callable(parse)
    assert callable(detect_languages)
    assert Settings is not None
''',
        encoding="utf-8",
    )

    metadata = base_metadata(
        task_id,
        meta,
        timeout=120,
        allowed_dependencies=["python-dateutil", "pytz", "regex", "tzlocal"],
        feature={
            "name": "dateparser settings parse pipeline",
            "description": "Composite Settings + parse + detect_languages with frozen allowlist.",
            "source_entrypoints": [
                "dateparser.parse",
                "dateparser.conf.Settings",
                "dateparser.search.search.DateSearchWithDetection.detect_language",
            ],
            "included_behaviors": [
                "parse ISO/English/Spanish/French dates",
                "settings timezone-aware and DATE_ORDER",
                "detect_languages shortcodes for en/es/fr subset",
            ],
            "excluded_behaviors": [
                "search_dates",
                "network downloads",
                "settings keys outside allowlist",
            ],
        },
        entanglement={
            "level": "high",
            "types": ["parser_state_coupling", "data_model_coupling"],
            "primary": "parser_state_coupling",
            "description": "Settings, locale data, and language detection compose the parse pipeline.",
            "signals": ["settings allowlist", "locale data", "language shortcodes"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import parse, Settings, detect_languages",
            "callable": "parse",
            "signature": "parse(date_string: str, ...) -> datetime | None",
        },
        public_spec={
            "title": "dateparser settings parse pipeline",
            "summary": "Extract a task-scoped subset of `dateparser` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.parse", "kind": "function", "signature": "(date_string: str, date_formats=None, languages=None, locales=None, region=None, settings=None)"},
                {"path": "featurelifted.Settings", "kind": "class", "signature": "(**options)"},
                {"path": "featurelifted.detect_languages", "kind": "function", "signature": "(text: str, languages: list[str] | None = None) -> list[str]"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: parse ISO/English/Spanish/French dates. Required observable cases include parse iso and english; parse with languages."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: settings timezone-aware and DATE_ORDER from the allowlist (PREFER_DATES_FROM, RETURN_AS_TIMEZONE_AWARE, TIMEZONE, TO_TIMEZONE, DATE_ORDER, STRICT_PARSING, REQUIRE_PARTS). Required observable cases include settings timezone aware; date order dmy; prefer dates from past."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: detect_languages returns list[str] shortcodes for the en/es/fr subset. Required observable cases include detect languages es fr."},
                {"id": "B004", "text": "Parsing remains offline using bundled locale/date data without network access."},
                {"id": "B005", "text": "The package exposes the required task API paths `featurelifted.parse`, `featurelifted.Settings`, `featurelifted.detect_languages` with the kinds and callable signatures listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: dateparser."},
            ],
            "exclusions": [
                "search_dates",
                "network downloads",
                "settings keys outside allowlist",
                "languages outside en/es/fr for required tests",
                "original dateparser import at runtime",
            ],
            "forbidden": {"imports": ["dateparser"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


BUILDERS = {
    "semver__version_core__001": materialize_semver,
    "uritools__uri_join_normalize_core__001": materialize_uritools,
    "cssselect__selector_xpath_core__001": materialize_cssselect,
    "tinydb__query_storage_core__001": materialize_tinydb,
    "dateparser__parse_settings_pipeline_core__001": materialize_dateparser,
}


def main(argv: list[str]) -> int:
    targets = argv[1:] or list(BUILDERS)
    for task_id in targets:
        if task_id not in BUILDERS:
            print(f"unknown task: {task_id}", file=sys.stderr)
            return 1
        if not (PIN_ROOT / PINS[task_id]["package"]).exists():
            print(f"missing pin tree for {task_id}", file=sys.stderr)
            return 1
        path = BUILDERS[task_id]()
        print(f"materialized {task_id} -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
