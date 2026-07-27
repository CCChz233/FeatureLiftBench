#!/usr/bin/env python3
"""Build the canonical FeatureLiftBench source repository/snapshot registry."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TASKS_ROOT = ROOT / "benchmark" / "tasks"
DEFAULT_OUTPUT = ROOT / "benchmark" / "sources" / "registry.json"
EXACT_COMMIT_RE = re.compile(r"^[0-9a-fA-F]{40}$")
SLUG_RE = re.compile(r"[^a-z0-9]+")
SOURCE_POLICY_ID = "featureliftbench.full_repository_source.v2"
REPOSITORY_ENRICHMENT_FIELDS = ("upstream_org", "ecosystem_family")
SNAPSHOT_EVIDENCE_FIELDS = (
    "resolved_commit",
    "acquisition_method",
    "current_snapshot_scope",
    "status",
    "archive_path",
    "archive_sha256",
    "source_tree_sha256",
    "license_text_path",
    "tracked_file_count",
    "python_file_count",
    "python_loc",
    "total_bytes",
    "max_path_depth",
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tasks-root", type=Path, default=DEFAULT_TASKS_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the tracked registry exactly matches generated task metadata",
    )
    return parser.parse_args()


def _slug(value: str) -> str:
    return SLUG_RE.sub("_", value.strip().lower()).strip("_") or "source"


def canonicalize_url(raw_url: str) -> tuple[str, str, str | None]:
    """Return canonical URL, source kind, and upstream organization."""

    text = raw_url.strip()
    if not text:
        raise ValueError("source.url must be non-empty")
    parsed = urlparse(text)
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        host = parsed.netloc.lower()
        path = parsed.path.rstrip("/")
        if path.lower().endswith(".git"):
            path = path[:-4]
        path = "/" + "/".join(part for part in path.split("/") if part)
        if host == "github.com":
            parts = path.strip("/").split("/")
            if len(parts) < 2:
                raise ValueError(f"GitHub repository URL lacks owner/repo: {raw_url}")
            owner, repo = parts[:2]
            return (
                f"https://github.com/{owner.lower()}/{repo.lower()}",
                "external_oss",
                owner.lower(),
            )
        return f"https://{host}{path}", "external_oss", None
    local = Path(text.rstrip("/")).as_posix()
    return local, "curated", None


def source_repo_id(canonical_url: str, source_kind: str) -> str:
    if source_kind == "curated":
        return f"local__{_slug(Path(canonical_url).name)}"
    parsed = urlparse(canonical_url)
    if parsed.netloc == "github.com":
        owner, repo = parsed.path.strip("/").split("/")[:2]
        return f"github__{_slug(owner)}__{_slug(repo)}"
    digest = hashlib.sha256(canonical_url.encode("utf-8")).hexdigest()[:12]
    return f"source__{_slug(parsed.netloc or canonical_url)}__{digest}"


def _revision_fields(
    requested_revision: str,
    source_kind: str,
) -> tuple[str, str | None, str, str, str, str]:
    if source_kind == "curated":
        return (
            "curated",
            None,
            "local_curated",
            "curated_source_tree",
            "curated_source_tree",
            "pending_curated_audit",
        )
    if EXACT_COMMIT_RE.fullmatch(requested_revision):
        return (
            "git_commit",
            requested_revision.lower(),
            "git_checkout",
            "legacy_task_local_mixed",
            "full_tracked_tree",
            "pending_full_materialization",
        )
    if requested_revision.endswith("-installed-snapshot"):
        return (
            "installed_snapshot",
            None,
            "pending_revision_resolution",
            "legacy_task_local_mixed",
            "full_tracked_tree",
            "pending_revision_resolution",
        )
    return (
        "tag_or_version",
        None,
        "pending_revision_resolution",
        "legacy_task_local_mixed",
        "full_tracked_tree",
        "pending_revision_resolution",
    )


def build_registry(tasks_root: Path) -> dict[str, Any]:
    task_dirs = sorted(
        path
        for path in tasks_root.iterdir()
        if path.is_dir() and (path / "metadata.json").is_file()
    )
    repositories: dict[str, dict[str, Any]] = {}
    snapshots: dict[tuple[str, str], dict[str, Any]] = {}
    repo_urls: dict[str, str] = {}

    for task_dir in task_dirs:
        metadata = json.loads((task_dir / "metadata.json").read_text(encoding="utf-8"))
        task_id = str(metadata.get("task_id") or task_dir.name)
        source = metadata.get("source")
        if not isinstance(source, dict):
            raise ValueError(f"{task_id}: source metadata must be an object")
        raw_url = str(source.get("url", "")).strip()
        requested_revision = str(source.get("commit", "")).strip()
        display_name = str(source.get("name", "")).strip() or task_id.split("__", 1)[0]
        license_id = str(source.get("license", "")).strip() or "UNKNOWN"
        if not requested_revision:
            raise ValueError(f"{task_id}: source.commit must be non-empty")

        canonical_url, source_kind, upstream_org = canonicalize_url(raw_url)
        repo_id = source_repo_id(canonical_url, source_kind)
        previous_url = repo_urls.setdefault(repo_id, canonical_url)
        if previous_url != canonical_url:
            raise ValueError(
                f"source_repo_id collision for {repo_id}: {previous_url} vs {canonical_url}"
            )
        repository = repositories.setdefault(
            repo_id,
            {
                "source_repo_id": repo_id,
                "canonical_url": canonical_url,
                "source_kind": source_kind,
                "display_names": set(),
                "upstream_org": upstream_org,
                "ecosystem_family": "unassigned",
                "licenses": set(),
                "snapshot_ids": set(),
                "task_ids": set(),
            },
        )
        repository["display_names"].add(display_name)
        repository["licenses"].add(license_id)
        repository["task_ids"].add(task_id)

        snapshot_key = (repo_id, requested_revision)
        revision_hash = hashlib.sha256(
            f"{canonical_url}\0{requested_revision}".encode("utf-8")
        ).hexdigest()[:12]
        snapshot_id = f"{repo_id}__{revision_hash}"
        (
            revision_kind,
            resolved_commit,
            acquisition_method,
            current_scope,
            target_scope,
            status,
        ) = _revision_fields(requested_revision, source_kind)
        snapshot = snapshots.setdefault(
            snapshot_key,
            {
                "source_snapshot_id": snapshot_id,
                "source_repo_id": repo_id,
                "requested_revision": requested_revision,
                "revision_kind": revision_kind,
                "resolved_commit": resolved_commit,
                "acquisition_method": acquisition_method,
                "current_snapshot_scope": current_scope,
                "target_snapshot_scope": target_scope,
                "status": status,
                "archive_path": None,
                "archive_sha256": None,
                "source_tree_sha256": None,
                "license_text_path": None,
                "tracked_file_count": None,
                "python_file_count": None,
                "python_loc": None,
                "total_bytes": None,
                "max_path_depth": None,
                "task_ids": set(),
            },
        )
        snapshot["task_ids"].add(task_id)
        repository["snapshot_ids"].add(snapshot_id)

    repository_rows = []
    for repository in repositories.values():
        row = dict(repository)
        for key in ("display_names", "licenses", "snapshot_ids", "task_ids"):
            row[key] = sorted(row[key])
        repository_rows.append(row)
    repository_rows.sort(key=lambda item: item["source_repo_id"])

    snapshot_rows = []
    for snapshot in snapshots.values():
        row = dict(snapshot)
        row["task_ids"] = sorted(row["task_ids"])
        snapshot_rows.append(row)
    snapshot_rows.sort(key=lambda item: item["source_snapshot_id"])

    ready_count = sum(item["status"] == "ready" for item in snapshot_rows)
    external_count = sum(
        item["source_kind"] == "external_oss" for item in repository_rows
    )
    return {
        "schema_version": "featureliftbench.source_registry.v1",
        "policy_id": SOURCE_POLICY_ID,
        "generated_from": "benchmark/tasks/*/metadata.json",
        "repositories": repository_rows,
        "snapshots": snapshot_rows,
        "summary": {
            "repository_count": len(repository_rows),
            "snapshot_count": len(snapshot_rows),
            "task_count": len(task_dirs),
            "external_repository_count": external_count,
            "curated_repository_count": len(repository_rows) - external_count,
            "ready_snapshot_count": ready_count,
            "pending_snapshot_count": len(snapshot_rows) - ready_count,
        },
    }


def merge_existing_evidence(
    generated: dict[str, Any],
    existing: dict[str, Any],
) -> dict[str, Any]:
    """Preserve audited registry enrichment while regenerating task-derived fields."""

    existing_repositories = {
        str(item.get("source_repo_id")): item
        for item in existing.get("repositories", [])
        if isinstance(item, dict) and item.get("source_repo_id")
    }
    for repository in generated["repositories"]:
        previous = existing_repositories.get(repository["source_repo_id"])
        if not isinstance(previous, dict):
            continue
        if previous.get("canonical_url") != repository["canonical_url"]:
            raise ValueError(
                f"{repository['source_repo_id']}: canonical_url changed in existing registry"
            )
        for key in REPOSITORY_ENRICHMENT_FIELDS:
            if previous.get(key) not in (None, "", "unassigned"):
                repository[key] = previous[key]

    existing_snapshots = {
        str(item.get("source_snapshot_id")): item
        for item in existing.get("snapshots", [])
        if isinstance(item, dict) and item.get("source_snapshot_id")
    }
    for snapshot in generated["snapshots"]:
        previous = existing_snapshots.get(snapshot["source_snapshot_id"])
        if not isinstance(previous, dict):
            continue
        identity_fields = (
            "source_repo_id",
            "requested_revision",
            "revision_kind",
            "target_snapshot_scope",
        )
        changed = [
            key for key in identity_fields if previous.get(key) != snapshot.get(key)
        ]
        if changed:
            raise ValueError(
                f"{snapshot['source_snapshot_id']}: immutable identity changed: "
                + ", ".join(changed)
            )
        for key in SNAPSHOT_EVIDENCE_FIELDS:
            if key in previous:
                snapshot[key] = previous[key]

    ready_count = sum(
        item["status"] == "ready" for item in generated["snapshots"]
    )
    generated["summary"]["ready_snapshot_count"] = ready_count
    generated["summary"]["pending_snapshot_count"] = (
        len(generated["snapshots"]) - ready_count
    )
    return generated


def validate_registry(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    repositories = payload.get("repositories")
    snapshots = payload.get("snapshots")
    if not isinstance(repositories, list) or not isinstance(snapshots, list):
        return ["repositories and snapshots must be arrays"]
    repo_ids = [item.get("source_repo_id") for item in repositories]
    snapshot_ids = [item.get("source_snapshot_id") for item in snapshots]
    if len(repo_ids) != len(set(repo_ids)):
        errors.append("duplicate source_repo_id")
    if len(snapshot_ids) != len(set(snapshot_ids)):
        errors.append("duplicate source_snapshot_id")
    known_repos = set(repo_ids)
    known_snapshots = set(snapshot_ids)
    task_to_snapshot: dict[str, list[str]] = defaultdict(list)
    for snapshot in snapshots:
        if snapshot.get("source_repo_id") not in known_repos:
            errors.append(
                f"{snapshot.get('source_snapshot_id')}: unknown source_repo_id"
            )
        for task_id in snapshot.get("task_ids", []):
            task_to_snapshot[str(task_id)].append(
                str(snapshot.get("source_snapshot_id"))
            )
        if snapshot.get("status") == "ready":
            required = (
                "archive_path",
                "archive_sha256",
                "source_tree_sha256",
                "license_text_path",
                "tracked_file_count",
                "python_file_count",
                "python_loc",
                "total_bytes",
                "max_path_depth",
            )
            missing = [key for key in required if snapshot.get(key) is None]
            if missing:
                errors.append(
                    f"{snapshot.get('source_snapshot_id')}: ready but missing "
                    + ", ".join(missing)
                )
            resolved_commit = str(snapshot.get("resolved_commit") or "")
            if (
                snapshot.get("target_snapshot_scope") == "full_tracked_tree"
                and not EXACT_COMMIT_RE.fullmatch(resolved_commit)
            ):
                errors.append(
                    f"{snapshot.get('source_snapshot_id')}: ready external snapshot "
                    "lacks an exact resolved commit"
                )
    for repository in repositories:
        unknown = set(repository.get("snapshot_ids", [])) - known_snapshots
        if unknown:
            errors.append(
                f"{repository.get('source_repo_id')}: unknown snapshots {sorted(unknown)}"
            )
    multi_snapshot_tasks = sorted(
        task_id for task_id, ids in task_to_snapshot.items() if len(ids) != 1
    )
    if multi_snapshot_tasks:
        errors.append(
            "tasks must map to exactly one snapshot: "
            + ", ".join(multi_snapshot_tasks[:10])
        )
    summary = payload.get("summary", {})
    if summary.get("repository_count") != len(repositories):
        errors.append("summary.repository_count mismatch")
    if summary.get("snapshot_count") != len(snapshots):
        errors.append("summary.snapshot_count mismatch")
    if summary.get("task_count") != len(task_to_snapshot):
        errors.append("summary.task_count mismatch")
    return errors


def main() -> int:
    args = _parse_args()
    tasks_root = args.tasks_root.resolve()
    output = args.output.resolve()
    payload = build_registry(tasks_root)
    if output.is_file():
        try:
            existing = json.loads(output.read_text(encoding="utf-8"))
            payload = merge_existing_evidence(payload, existing)
        except (json.JSONDecodeError, ValueError) as exc:
            print(f"invalid existing source registry: {exc}", file=sys.stderr)
            return 1
    errors = validate_registry(payload)
    if errors:
        print("source registry validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not output.is_file():
            print(f"missing source registry: {output}", file=sys.stderr)
            return 1
        if output.read_text(encoding="utf-8") != rendered:
            print(
                "source registry is stale; run scripts/build_source_registry.py",
                file=sys.stderr,
            )
            return 1
        print(
            f"source registry verified: {payload['summary']['repository_count']} "
            f"repositories, {payload['summary']['snapshot_count']} snapshots, "
            f"{payload['summary']['task_count']} tasks"
        )
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8")
    print(output)
    print(
        f"registered {payload['summary']['repository_count']} repositories and "
        f"{payload['summary']['snapshot_count']} snapshots for "
        f"{payload['summary']['task_count']} tasks; "
        f"{payload['summary']['ready_snapshot_count']} snapshots ready"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
