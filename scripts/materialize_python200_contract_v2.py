#!/usr/bin/env python3
"""Materialize a contract-repaired Python-200 candidate without mutating frozen tasks."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "harness"
if str(HARNESS) not in sys.path:
    sys.path.insert(0, str(HARNESS))

from featureliftbench.task_render import render_public_task  # noqa: E402
from featureliftbench.task_spec import sync_spec_hashes, write_metadata  # noqa: E402
from featureliftbench.task_spec_migrate import (  # noqa: E402
    _render_required_api_surface_test,
    _sync_behavior_contract,
    _surface_test_nodeid,
)
from featureliftbench.validate import validate_task  # noqa: E402


BASE_SUITE = ROOT / "benchmark/selection/python200_suite.json"
REPAIRS = ROOT / "benchmark/contract_v2/repairs.json"
CANDIDATES = ROOT / "reports/contract_closure_200/api_patch_candidates.json"
OVERRIDES = ROOT / "benchmark/contract_v2/overrides"
REFERENCE_OVERRIDES = ROOT / "benchmark/contract_v2/reference_overrides"
OUTPUT = ROOT / "benchmark/contract_v2/generated_tasks"
REFERENCE_OUTPUT = ROOT / "benchmark/contract_v2/generated_references"
MANIFEST = ROOT / "benchmark/contract_v2/suite.json"
EXCLUDED = {"repo", "reference_solution", "__pycache__", ".pytest_cache", ".DS_Store"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--reference-output", type=Path, default=REFERENCE_OUTPUT)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--repairs", type=Path, default=REPAIRS)
    parser.add_argument("--candidates", type=Path, default=CANDIDATES)
    return parser.parse_args()


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def flatten(entries: Any) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for entry in entries if isinstance(entries, list) else []:
        if not isinstance(entry, dict):
            continue
        result.append(entry)
        result.extend(flatten(entry.get("members")))
    return result


def entry_map(entries: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        str(entry["path"]): entry
        for entry in flatten(entries)
        if isinstance(entry.get("path"), str)
    }


def remove_api(entries: list[dict[str, Any]], paths: set[str]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for original in entries:
        if not isinstance(original, dict) or str(original.get("path")) in paths:
            continue
        entry = copy.deepcopy(original)
        if isinstance(entry.get("members"), list):
            entry["members"] = remove_api(entry["members"], paths)
            if not entry["members"]:
                entry.pop("members", None)
        result.append(entry)
    return result


def upsert_api(entries: list[dict[str, Any]], new_entry: dict[str, Any]) -> None:
    path = str(new_entry["path"])
    existing = entry_map(entries)
    if path in existing:
        existing[path].update(copy.deepcopy(new_entry))
        return
    owner_path = path.rsplit(".", 1)[0]
    owner = existing.get(owner_path)
    if owner is not None and owner.get("kind") in {"class", "module", "object"}:
        owner.setdefault("members", []).append(copy.deepcopy(new_entry))
    else:
        entries.append(copy.deepcopy(new_entry))


def apply_candidate_operations(metadata: dict[str, Any], operations: list[dict[str, Any]]) -> None:
    required_api = metadata["public_spec"]["required_api"]
    for operation in operations:
        entries = entry_map(required_api)
        path = str(operation.get("api_path", ""))
        op = operation.get("op")
        if op == "replace_kind" and path in entries:
            entries[path]["kind"] = operation["value"]
        elif op == "replace_signature" and path in entries:
            entries[path]["signature"] = operation["value"]
        elif op in {"upsert_required_api", "upsert_required_api_member"}:
            entry = operation.get("entry")
            if isinstance(entry, dict):
                upsert_api(required_api, entry)


def update_mappings(evaluation: dict[str, Any], updates: dict[str, Any]) -> None:
    all_mappings: dict[str, dict[str, Any]] = {}
    for key in ("public_test_mappings", "hidden_test_mappings"):
        for mapping in evaluation.get(key) or []:
            if isinstance(mapping, dict) and isinstance(mapping.get("nodeid"), str):
                all_mappings[str(mapping["nodeid"])] = mapping
    for nodeid, behavior_ids in updates.items():
        mapping = all_mappings.get(nodeid)
        if mapping is None:
            key = "public_test_mappings" if nodeid.startswith("public_tests/") else "hidden_test_mappings"
            mapping = {
                "nodeid": nodeid,
                "mapping_method": "contract_v2_adjudication",
            }
            evaluation.setdefault(key, []).append(mapping)
        mapping["behavior_ids"] = list(behavior_ids)
        mapping["mapping_method"] = "contract_v2_adjudication"


def deep_merge(target: dict[str, Any], updates: dict[str, Any]) -> None:
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            deep_merge(target[key], value)
        else:
            target[key] = copy.deepcopy(value)


def sync_api_coverage(metadata: dict[str, Any], explicit: dict[str, Any]) -> None:
    evaluation = metadata["evaluation_spec"]
    existing = {
        str(item.get("path")): item
        for item in evaluation.get("required_api_coverage") or []
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    }
    coverage = []
    for entry in flatten(metadata["public_spec"]["required_api"]):
        path = str(entry["path"])
        tests = explicit.get(path)
        if tests is None and path in existing:
            tests = existing[path].get("covered_by_tests")
        if not tests:
            tests = [_surface_test_nodeid()]
        coverage.append({"path": path, "covered_by_tests": sorted(set(tests))})
    evaluation["required_api_coverage"] = coverage


def sync_api_surface_behavior(metadata: dict[str, Any]) -> None:
    public = metadata["public_spec"]
    evaluation = metadata["evaluation_spec"]
    api_behavior_ids = {
        str(item.get("behavior_id"))
        for item in evaluation.get("public_clauses") or []
        if isinstance(item, dict) and item.get("clause_kind") == "api_surface"
    }
    paths = [
        f"`{entry['path']}`"
        for entry in flatten(public.get("required_api"))
        if isinstance(entry.get("path"), str)
    ]
    shown = ", ".join(paths[:12])
    if len(paths) > 12:
        shown += f", and {len(paths) - 12} listed members"
    text = (
        "The package exposes the required task API paths "
        f"{shown} with the kinds and callable signatures listed in this contract."
    )
    for behavior in public.get("behaviors") or []:
        if isinstance(behavior, dict) and str(behavior.get("id")) in api_behavior_ids:
            behavior["text"] = text


def apply_repair(
    task_dir: Path,
    repair: dict[str, Any],
    candidate: dict[str, Any] | None,
) -> None:
    metadata_path = task_dir / "metadata.json"
    metadata = load_object(metadata_path)
    public = metadata["public_spec"]
    evaluation = metadata["evaluation_spec"]
    if repair.get("accept_api_candidates") is True and candidate is not None:
        apply_candidate_operations(metadata, candidate.get("operations") or [])

    remove_paths = {str(path) for path in repair.get("api_remove") or []}
    if remove_paths:
        public["required_api"] = remove_api(public["required_api"], remove_paths)
    for entry in repair.get("api_upsert") or []:
        if isinstance(entry, dict) and isinstance(entry.get("path"), str):
            upsert_api(public["required_api"], entry)

    behavior_by_id = {
        str(item.get("id")): item
        for item in public.get("behaviors") or []
        if isinstance(item, dict)
    }
    for behavior_id, text in (repair.get("behavior_text") or {}).items():
        if behavior_id not in behavior_by_id:
            public.setdefault("behaviors", []).append({"id": behavior_id, "text": text})
        else:
            behavior_by_id[behavior_id]["text"] = text
    remove_behaviors = {str(value) for value in repair.get("behavior_remove") or []}
    if remove_behaviors:
        public["behaviors"] = [
            item for item in public.get("behaviors") or []
            if str(item.get("id")) not in remove_behaviors
        ]
    sync_api_surface_behavior(metadata)
    behavior_text = {
        str(item["id"]): str(item["text"])
        for item in public.get("behaviors") or []
        if isinstance(item, dict) and item.get("id") and item.get("text")
    }
    evaluation["public_clauses"] = [
        item for item in evaluation.get("public_clauses") or []
        if str(item.get("behavior_id")) not in remove_behaviors
    ]
    clause_by_id = {
        str(item.get("behavior_id")): item
        for item in evaluation.get("public_clauses") or []
        if isinstance(item, dict)
    }
    for behavior_id, text in behavior_text.items():
        clause = clause_by_id.get(behavior_id)
        if clause is None:
            clause = {"behavior_id": behavior_id, "clause_kind": "included_behavior"}
            evaluation.setdefault("public_clauses", []).append(clause)
        clause["text"] = text

    update_mappings(evaluation, repair.get("mapping_updates") or {})
    if remove_behaviors:
        for key in ("public_test_mappings", "hidden_test_mappings"):
            for mapping in evaluation.get(key) or []:
                mapping["behavior_ids"] = [
                    value for value in mapping.get("behavior_ids") or []
                    if str(value) not in remove_behaviors
                ]
    evaluation["contract_remediation"] = {
        "schema_version": "featureliftbench.contract_remediation.v1",
        "release": "python200-contract-v2",
        "adjudication": str(repair.get("adjudication", "contract closure repair")),
    }

    sync_api_coverage(metadata, repair.get("api_coverage") or {})
    surface = _render_required_api_surface_test(public["required_api"], task_id=task_dir.name)
    (task_dir / "hidden_tests/test_required_api_surface.py").write_text(surface, encoding="utf-8")

    requirement_prefixes = tuple(str(value).lower() for value in repair.get("remove_requirement_prefixes") or [])
    if requirement_prefixes:
        lock = task_dir / "requirements.lock"
        lines = lock.read_text(encoding="utf-8").splitlines()
        lines = [line for line in lines if not line.strip().lower().startswith(requirement_prefixes)]
        lock.write_text("\n".join(lines) + "\n", encoding="utf-8")
        environment = metadata.get("environment")
        allowed = environment.get("allowed_dependencies") if isinstance(environment, dict) else None
        if isinstance(allowed, list):
            environment["allowed_dependencies"] = [
                value for value in allowed
                if not str(value).lower().startswith(requirement_prefixes)
            ]

    manifest_updates = repair.get("oracle_manifest")
    if isinstance(manifest_updates, dict):
        manifest_path = task_dir / "evaluation/oracle_manifest.json"
        oracle_manifest = load_object(manifest_path)
        deep_merge(oracle_manifest, manifest_updates)
        manifest_path.write_text(
            json.dumps(oracle_manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    metadata["task_revision"] = int(metadata.get("task_revision") or 0) + 1
    task_markdown = render_public_task(metadata)
    metadata = sync_spec_hashes(metadata, task_markdown)
    write_metadata(task_dir, metadata)
    (task_dir / "TASK.md").write_text(task_markdown, encoding="utf-8")
    _sync_behavior_contract(task_dir, metadata["evaluation_spec"], task_markdown)
    behavior_path = task_dir / "evaluation/behavior_contract.json"
    behavior_contract = load_object(behavior_path)
    behavior_contract["schema_version"] = "featureliftbench.behavior_contract.v1"
    behavior_contract["review_status"] = "adjudicated"
    behavior_contract["review"] = {
        "protocol_version": "contract_v2_adjudication.v1",
        "reviewer_id": "codex_contract_closure_remediation_20260804",
        "reviewer_type": "ai_assisted_adjudication",
        "conflict_count": 0,
        "formal_human_double_review_pending": True,
    }
    behavior_contract["unmapped_hidden_test_nodeids"] = []
    behavior_contract["unmapped_public_test_nodeids"] = []
    behavior_path.write_text(
        json.dumps(behavior_contract, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def copy_task(source: Path, destination: Path) -> None:
    def ignore(_directory: str, names: list[str]) -> set[str]:
        return {name for name in names if name in EXCLUDED or name.endswith(".pyc")}

    shutil.copytree(source, destination, ignore=ignore)
    marker = destination / "repo/.source-archive-backed"
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(
        "Source is materialized from the immutable Python-200 source registry.\n",
        encoding="utf-8",
    )


def reference_source(task_id: str) -> Path:
    candidates = (
        ROOT / "benchmark/submissions" / task_id / "oracle",
        ROOT / "benchmark/staging" / task_id / "reference_solution",
        ROOT / "benchmark/external50" / task_id / "reference_solution",
    )
    source = next((path for path in candidates if path.is_dir()), None)
    if source is None:
        raise FileNotFoundError(f"missing reference solution for {task_id}")
    return source


def overlay_files(source: Path, destination: Path) -> None:
    if not source.is_dir():
        return
    for path in sorted(source.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(source)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)


def apply_reference_repair(reference_dir: Path, repair: dict[str, Any]) -> None:
    for item in repair.get("reference_replacements") or []:
        if not isinstance(item, dict):
            continue
        path = reference_dir / str(item.get("path", ""))
        old = str(item.get("old", ""))
        new = str(item.get("new", ""))
        expected = int(item.get("count", 1))
        text = path.read_text(encoding="utf-8")
        actual = text.count(old)
        if actual != expected:
            raise ValueError(
                f"{reference_dir.name}: reference replacement {path.name} "
                f"expected {expected} matches, found {actual}"
            )
        path.write_text(text.replace(old, new), encoding="utf-8")


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*"), key=lambda value: value.as_posix()):
        if (
            path.is_file()
            and not path.name.endswith(".pyc")
            and not any(part in EXCLUDED for part in path.parts)
        ):
            relative = path.relative_to(root).as_posix()
            digest.update(b"F\0" + relative.encode() + b"\0" + path.read_bytes())
    return digest.hexdigest()


def replace_tree(source: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    source.rename(destination)


def main() -> int:
    args = parse_args()
    suite = load_object(BASE_SUITE)
    repairs_payload = load_object(args.repairs)
    repairs = repairs_payload.get("tasks") or {}
    candidates_payload = load_object(args.candidates)
    candidates = {
        str(item["task_id"]): item for item in candidates_payload.get("tasks") or []
    }
    selected = [str(value) for value in suite.get("task_ids") or []]
    unknown = set(repairs) - set(selected)
    if unknown:
        raise SystemExit("unknown repaired task ids: " + ", ".join(sorted(unknown)))

    with tempfile.TemporaryDirectory(prefix="flb-contract-v2-") as temporary:
        built = Path(temporary) / "tasks"
        built_references = Path(temporary) / "references"
        built.mkdir()
        built_references.mkdir()
        for task_id in selected:
            destination = built / task_id
            copy_task(ROOT / str(suite["task_root"]) / task_id, destination)
            overlay_files(OVERRIDES / task_id, destination)
            repair = repairs.get(task_id)
            if isinstance(repair, dict):
                apply_repair(destination, repair, candidates.get(task_id))
                reference_destination = built_references / task_id
                shutil.copytree(
                    reference_source(task_id),
                    reference_destination,
                    ignore=lambda _directory, names: {
                        name
                        for name in names
                        if name in EXCLUDED or name.endswith(".pyc")
                    },
                )
                overlay_files(REFERENCE_OVERRIDES / task_id, reference_destination)
                apply_reference_repair(reference_destination, repair)

        failures = []
        for task_id in sorted(repairs):
            result = validate_task(built / task_id)
            failures.extend(f"{task_id}: {error}" for error in result.errors)
        if failures:
            for failure in failures[:100]:
                print(failure, file=sys.stderr)
            raise SystemExit(f"contract-v2 validation failed with {len(failures)} errors")

        digest = tree_digest(built)
        reference_digest = tree_digest(built_references)
        manifest = {
            "schema_version": "featureliftbench.python200_contract_suite.v2",
            "suite_id": "python200-full-repository-no-hint-contract-v2",
            "base_suite_id": suite.get("suite_id"),
            "base_freeze_id": suite.get("baseline_freeze_id"),
            "task_count": len(selected),
            "task_ids": selected,
            "repaired_task_count": len(repairs),
            "repaired_task_ids": sorted(repairs),
            "task_root": str(args.output.relative_to(ROOT)),
            "task_tree_sha256": digest,
            "reference_root": str(args.reference_output.relative_to(ROOT)),
            "reference_tree_sha256": reference_digest,
        }
        rendered_manifest = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
        if args.check:
            stale = (
                not args.output.is_dir()
                or tree_digest(args.output) != digest
                or not args.reference_output.is_dir()
                or tree_digest(args.reference_output) != reference_digest
                or not args.manifest.is_file()
                or args.manifest.read_text(encoding="utf-8") != rendered_manifest
            )
            if stale:
                raise SystemExit("contract-v2 generated suite is stale")
        elif args.apply:
            replace_tree(built, args.output)
            replace_tree(built_references, args.reference_output)
            args.manifest.parent.mkdir(parents=True, exist_ok=True)
            args.manifest.write_text(rendered_manifest, encoding="utf-8")

    mode = "checked" if args.check else "written" if args.apply else "validated"
    print(f"Contract-v2 {mode}: tasks={len(selected)} repaired={len(repairs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
