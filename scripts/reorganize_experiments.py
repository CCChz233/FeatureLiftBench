#!/usr/bin/env python3
"""Safely migrate the local experiments store into its canonical layout."""

from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
import tarfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
REGISTRY = EXPERIMENTS / "registry"
ALIAS_PATH = REGISTRY / "path_aliases.json"
LEDGER_PATH = REGISTRY / "bundle_ledger.json"

METHOD_DIRS = (
    "ablation",
    "cgcc_lite_pilot",
    "dpr_pilot",
    "ecsm_pilot",
    "fcec_dev6_20260731",
    "pdr_clean6_20260730",
    "rsg_pilot",
    "td_cognition_pilot",
    "test_first_lift_pilot",
)
BATCH3_DIRS = (
    "batch3-main-reference-eval-20260708-next8",
    "batch3-main-reference-eval-20260708-promotion-candidates",
    "batch3-main-reference-eval-20260708-public-only-promotions",
    "batch3-main-reference-eval-20260708-ready20",
    "batch3-main-reference-eval-20260708-whitespace-rerun",
    "batch3-main-reference-eval-20260711",
    "batch3-main-reference-sweep-20260708-191558",
    "batch3-pilot-reference-docker-eval-20260707-111608",
    "batch3-pilot-reference-docker-eval-20260708-next8",
    "batch3-pilot-reference-docker-eval-20260708-promotion-candidates",
    "batch3-pilot-reference-docker-eval-20260708-ready20",
    "batch3-pilot-reference-docker-eval-20260711-final6",
    "batch3-pilot-reference-eval-20260707-111308",
    "batch3-pilot-reference-eval-20260707-111355",
    "batch3-pilot-reference-eval-20260708-final6",
    "batch3-pilot-reference-eval-20260708-next8",
    "batch3-pilot-reference-eval-20260708-promotion-candidates",
    "batch3-pilot-reference-eval-20260708-remaining26",
)
EXTERNAL_DIRS = (
    "external50_reference_audit_20260801",
    "external50_reference_audit_20260801_full",
)
V11_DIRS = (
    "v1_1_control_preflight",
    "v1_1_infra_reevaluation",
    "v1_1_oracle_validation",
    "v1_1_repair_preflight",
)
HARD50_VALIDATION_DIRS = (
    "hard50_copyheavy_swap_flash_20260828",
    "hard50_copyheavy_swaps_20260827",
    "hard50_pilot_flash_20260827",
    "hard50_pilot_flash_swaps_20260827",
    "hard50_pilot_gates_20260827",
    "hard50_remaining40_flash_20260827",
)
ALLOWED_TOP_LEVEL = {
    "README.md",
    "python",
    "GO",
    "smoke",
    "methods",
    "validation",
    "bundles",
    "registry",
}


@dataclass(frozen=True)
class Move:
    source: str
    destination: str
    kind: str


@dataclass(frozen=True)
class RetiredBundle:
    filename: str
    sha256: str
    reason: str
    evidence_groups: tuple[tuple[str, ...], ...] = ()
    require_oracles: int = 0
    replacement_bundle: str = ""


def _moves() -> list[Move]:
    moves = [
        Move(f"experiments/{name}", f"experiments/methods/{name}", "method")
        for name in METHOD_DIRS
    ]
    moves.extend(
        Move(f"experiments/{name}", f"experiments/validation/batch3/{name}", "validation")
        for name in BATCH3_DIRS
    )
    moves.extend(
        Move(
            f"experiments/{name}",
            f"experiments/validation/external50/{name}",
            "validation",
        )
        for name in EXTERNAL_DIRS
    )
    moves.extend(
        Move(f"experiments/{name}", f"experiments/validation/v1_1/{name}", "validation")
        for name in V11_DIRS
    )
    moves.extend(
        Move(
            f"experiments/{name}",
            f"experiments/validation/hard50/{name}",
            "validation",
        )
        for name in HARD50_VALIDATION_DIRS
    )
    moves.extend(
        [
            Move(
                "experiments/configs/rsg_smoke_20260723.toml",
                "experiments/methods/rsg_pilot/configs/rsg_smoke_20260723.toml",
                "method_config",
            ),
            Move(
                "experiments/logs/hard50-qwen3.6-27b-fp8-20260720-023500.log",
                "experiments/python/openhands/qwen3.6-27b-fp8/"
                "hard50-qwen3.6-27b-fp8-20260720-023500/suite.log",
                "suite_log",
            ),
            Move(
                "experiments/logs/hard50-qwen3.6-35b-a3b-fp8-20260720-022800.log",
                "experiments/python/openhands/qwen3.6-35b-a3b-fp8/"
                "hard50-qwen3.6-35b-a3b-fp8-20260720-022800/suite.log",
                "suite_log",
            ),
            Move(
                "experiments/FeatureLiftBench-python150-results-20260803.tar.gz",
                "experiments/bundles/incoming/frozen-results/"
                "FeatureLiftBench-python150-results-20260803.tar.gz",
                "bundle_keep",
            ),
            Move(
                "experiments/FeatureLiftBench-python150-results-20260803.tar.gz.sha256",
                "experiments/bundles/incoming/frozen-results/"
                "FeatureLiftBench-python150-results-20260803.tar.gz.sha256",
                "bundle_keep",
            ),
            Move(
                "experiments/FeatureLiftBench-deepseek-v4-flash-150-20260805.tar.gz",
                "experiments/bundles/incoming/frozen-results/"
                "FeatureLiftBench-deepseek-v4-flash-150-20260805.tar.gz",
                "bundle_keep",
            ),
            Move(
                "experiments/python200-deepseek-v4-flash-lite-v1-vllm-local-0813-001-results-latest.tar.gz",
                "experiments/bundles/incoming/frozen-results/"
                "python200-deepseek-v4-flash-lite-v1-vllm-local-0813-001-results-latest.tar.gz",
                "bundle_keep",
            ),
            Move(
                "experiments/python200-hard-main-20260829.tar.gz",
                "experiments/bundles/incoming/frozen-results/"
                "python200-hard-main-20260829.tar.gz",
                "bundle_keep",
            ),
            Move(
                "experiments/python200-hard-main-20260829.tar.gz.sha256",
                "experiments/bundles/incoming/frozen-results/"
                "python200-hard-main-20260829.tar.gz.sha256",
                "bundle_keep",
            ),
            Move(
                "experiments/flb-useful-focus-expts-20260730-144258.tar.gz",
                "experiments/bundles/archive/methods/"
                "flb-useful-focus-expts-20260730-144258.tar.gz",
                "bundle_keep",
            ),
            Move(
                "experiments/bundles/outgoing/FeatureLiftBench-runnable-python200-5f9c495-20260802.tar.gz",
                "experiments/bundles/outgoing/current/FeatureLiftBench-runnable-python200-5f9c495-20260802.tar.gz",
                "bundle_keep",
            ),
            Move(
                "experiments/bundles/outgoing/FeatureLiftBench-runnable-python200-5f9c495-20260802.tar.gz.sha256",
                "experiments/bundles/outgoing/current/FeatureLiftBench-runnable-python200-5f9c495-20260802.tar.gz.sha256",
                "bundle_keep",
            ),
            Move(
                "experiments/bundles/outgoing/FeatureLiftBench-v3-846-20260801-ready.tar.gz",
                "experiments/bundles/archive/releases/FeatureLiftBench-v3-846-20260801-ready.tar.gz",
                "bundle_keep",
            ),
            Move(
                "experiments/bundles/outgoing/FeatureLiftBench-v3-846-20260801-ready.tar.gz.sha256",
                "experiments/bundles/archive/releases/FeatureLiftBench-v3-846-20260801-ready.tar.gz.sha256",
                "bundle_keep",
            ),
        ]
    )
    retired = (
        "flb_python150_fullproof_excl27b_20260726.tar.gz",
        "flb_python150_results_5models_20260726.tar.gz",
    )
    moves.extend(
        Move(f"experiments/{name}", f"experiments/bundles/retired/{name}", "bundle_retired")
        for name in retired
    )
    for name in (
        "flb_python150_results_excl27b_20260726.tar.gz",
        "flb_python150_results_excl27b_20260726.tar.gz.sha256",
        "hard50-qwen36-27b-35b-20260720-131139.tar.gz",
        "hard50-qwen36-27b-35b-20260720-131139.tar.gz.sha256",
    ):
        moves.append(
            Move(
                f"experiments/bundles/incoming/{name}",
                f"experiments/bundles/retired/{name}",
                "bundle_retired",
            )
        )
    for name in (
        "FeatureLiftBench-runnable-20260728-114056.tar.gz",
        "FeatureLiftBench-runnable-20260728-114056.tar.gz.sha256",
        "flb_python150_oracles_20260727.tar.gz",
        "flb_python150_oracles_20260727.tar.gz.sha256",
    ):
        moves.append(
            Move(
                f"experiments/bundles/outgoing/{name}",
                f"experiments/bundles/retired/{name}",
                "bundle_retired",
            )
        )
    return moves


COMMON_150 = (
    "experiments/python/openhands/deepseek-v4-flash-dspark/compliant150-flash-dspark-main-001",
    "experiments/python/openhands/gpt-oss-120b/compliant150-gptoss120b-main-002",
    "experiments/python/openhands/qwen3.5-122b-a10b-fp8/compliant150-qwen122b-main-001",
    "experiments/python/openhands/qwen3.6-35b-a3b-fp8/compliant150-qwen35b-main-001",
)
RETIRED_BUNDLES = (
    RetiredBundle(
        "flb_python150_fullproof_excl27b_20260726.tar.gz",
        "d5a827e3cad715f5ebfd4934da9478e313a4eed0308596d3dd90d088874fbf00",
        "superseded four-model full export; canonical suites are present",
        tuple((path,) for path in COMMON_150),
    ),
    RetiredBundle(
        "flb_python150_results_5models_20260726.tar.gz",
        "340369f6fa3319ee7ca4f707fc22ee03462a314c6c240ddd5fbd8d630ea90a19",
        "superseded mixed-snapshot export; canonical component suites are present",
        tuple((path,) for path in COMMON_150)
        + ((
            "experiments/python/openhands/qwen3.6-27b-fp8/qwen36-27b-fp8-main-20260704-001328",
            "experiments/python/openhands/qwen3.6-27b-fp8/hard50-qwen3.6-27b-fp8-20260720-023500",
        ),),
    ),
    RetiredBundle(
        "flb_python150_results_excl27b_20260726.tar.gz",
        "17b97f24a4ce2651aa28b3580b2fee1d6ed921b307d8a9f559dbbb227db07c6f",
        "incoming result package imported into canonical suites",
        tuple((path,) for path in COMMON_150),
    ),
    RetiredBundle(
        "hard50-qwen36-27b-35b-20260720-131139.tar.gz",
        "ea148ff7d6dbe2e829cb6a7f001dabc792e89f093718876f0ead97830cfa0ae4",
        "incoming hard50 package imported into canonical suites",
        (
            ("experiments/python/openhands/qwen3.6-27b-fp8/hard50-qwen3.6-27b-fp8-20260720-023500",),
            ("experiments/python/openhands/qwen3.6-35b-a3b-fp8/hard50-qwen3.6-35b-a3b-fp8-20260720-022800",),
        ),
    ),
    RetiredBundle(
        "FeatureLiftBench-runnable-20260728-114056.tar.gz",
        "37f97a95201306fa34d057d4756bd6a83949c3e56bfa8ac03943f85746d1ede6",
        "superseded runnable package",
        replacement_bundle="experiments/bundles/outgoing/current/FeatureLiftBench-runnable-python200-5f9c495-20260802.tar.gz",
    ),
    RetiredBundle(
        "flb_python150_oracles_20260727.tar.gz",
        "c11f973657b732118a7c476940dc79342f03b27b5116e279f3b06bc94dde77cb",
        "oracle-only package replaced by canonical oracle trees and v3 release package",
        require_oracles=150,
        replacement_bundle="experiments/bundles/archive/releases/FeatureLiftBench-v3-846-20260801-ready.tar.gz",
    ),
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tree_fingerprint(path: Path) -> str:
    digest = hashlib.sha256()
    if path.is_file():
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
    for child in sorted(item for item in path.rglob("*") if item.is_file()):
        digest.update(child.relative_to(path).as_posix().encode())
        digest.update(b"\0")
        with child.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    return digest.hexdigest()


def safe_tar(path: Path) -> tuple[bool, str]:
    try:
        with tarfile.open(path, "r:gz") as archive:
            for member in archive.getmembers():
                name = PurePosixPath(member.name)
                if name.is_absolute() or ".." in name.parts:
                    return False, f"unsafe member: {member.name}"
                if member.issym() or member.islnk():
                    target = PurePosixPath(member.linkname)
                    if target.is_absolute():
                        return False, f"unsafe link: {member.name} -> {member.linkname}"
                    base = name.parent if member.issym() else PurePosixPath()
                    resolved = PurePosixPath(posixpath.normpath((base / target).as_posix()))
                    if ".." in resolved.parts:
                        return False, f"unsafe link: {member.name} -> {member.linkname}"
    except (OSError, tarfile.TarError) as exc:
        return False, str(exc)
    return True, "ok"


def suite_task_count(path: Path) -> int:
    suite = path / "suite.json"
    if not suite.is_file():
        return 0
    payload = json.loads(suite.read_text(encoding="utf-8"))
    runs = payload.get("runs")
    return len(runs) if isinstance(runs, list) else 0


def verify_bundle(bundle: RetiredBundle, path: Path) -> tuple[bool, list[str]]:
    checks: list[str] = []
    actual = sha256_file(path)
    if actual != bundle.sha256:
        return False, [f"sha256 mismatch: {actual}"]
    safe, detail = safe_tar(path)
    if not safe:
        return False, [detail]
    checks.append("sha256_and_tar_paths_ok")
    for group in bundle.evidence_groups:
        counts = [suite_task_count(ROOT / item) for item in group]
        if sum(counts) != 150 and not (len(group) == 1 and counts == [50]):
            return False, [f"replacement suite coverage failed: {group} -> {counts}"]
        checks.append(f"replacement_coverage:{sum(counts)}:{','.join(group)}")
    if bundle.require_oracles:
        oracles = list((ROOT / "benchmark/submissions").glob("*/oracle"))
        if len(oracles) < bundle.require_oracles:
            return False, [f"oracle coverage {len(oracles)} < {bundle.require_oracles}"]
        checks.append(f"oracle_coverage:{len(oracles)}")
    if bundle.replacement_bundle:
        replacement = ROOT / bundle.replacement_bundle
        if not replacement.is_file():
            return False, [f"missing replacement bundle: {bundle.replacement_bundle}"]
        replacement_safe, replacement_detail = safe_tar(replacement)
        if not replacement_safe:
            return False, [f"unsafe replacement bundle: {replacement_detail}"]
        checks.append(f"replacement_bundle:{bundle.replacement_bundle}")
    return True, checks


def write_aliases(moves: list[Move]) -> None:
    aliases = [
        {
            "old_prefix": move.source,
            "new_prefix": move.destination,
            "kind": move.kind,
            "status": "moved",
        }
        for move in moves
        if not move.kind.startswith("bundle")
    ]
    payload = {
        "schema_version": "featureliftbench.experiment_path_aliases.v1",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "resolution": "longest_prefix",
        "aliases": aliases,
    }
    ALIAS_PATH.parent.mkdir(parents=True, exist_ok=True)
    ALIAS_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def migrate(moves: list[Move]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for move in moves:
        source = ROOT / move.source
        destination = ROOT / move.destination
        if source.exists() and destination.exists():
            raise RuntimeError(f"migration collision: {source} and {destination}")
        if not source.exists():
            if destination.exists():
                results.append({"source": move.source, "destination": move.destination, "status": "already_moved"})
            continue
        before = tree_fingerprint(source)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.stat().st_dev != destination.parent.stat().st_dev:
            raise RuntimeError(f"cross-filesystem move refused: {source} -> {destination}")
        source.rename(destination)
        after = tree_fingerprint(destination)
        if before != after:
            raise RuntimeError(f"content changed during migration: {move.source}")
        results.append(
            {
                "source": move.source,
                "destination": move.destination,
                "kind": move.kind,
                "status": "moved",
                "content_sha256": after,
            }
        )
    for empty in (EXPERIMENTS / "configs", EXPERIMENTS / "logs"):
        if empty.is_dir() and not any(empty.iterdir()):
            empty.rmdir()
    for junk in EXPERIMENTS.rglob(".DS_Store"):
        junk.unlink()
    gitkeep = EXPERIMENTS / ".gitkeep"
    if gitkeep.exists():
        gitkeep.unlink()
    return results


def prune_bundles() -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    retired = EXPERIMENTS / "bundles/retired"
    retained = EXPERIMENTS / "bundles/archive/retained"
    for bundle in RETIRED_BUNDLES:
        path = retired / bundle.filename
        retained_path = retained / bundle.filename
        if not path.is_file() and retained_path.is_file():
            path = retained_path
        if not path.is_file():
            results.append({"filename": bundle.filename, "status": "already_absent"})
            continue
        size = path.stat().st_size
        verified, checks = verify_bundle(bundle, path)
        sidecar = path.with_name(f"{path.name}.sha256")
        record = {
            "filename": bundle.filename,
            "sha256": bundle.sha256,
            "size_bytes": size,
            "reason": bundle.reason,
            "checks": checks,
        }
        if verified:
            path.unlink()
            if sidecar.exists():
                sidecar.unlink()
            record["status"] = "deleted_verified"
        else:
            retained.mkdir(parents=True, exist_ok=True)
            target = retained / path.name
            if path != target:
                if target.exists():
                    raise RuntimeError(f"retained bundle collision: {target}")
                path.rename(target)
                if sidecar.exists():
                    sidecar.rename(retained / sidecar.name)
            record["status"] = "retained_verification_failed"
        results.append(record)
    if retained.is_dir() and not any(retained.iterdir()):
        retained.rmdir()
    return results


def validate_top_level() -> None:
    actual = {item.name for item in EXPERIMENTS.iterdir()}
    unexpected = sorted(actual - ALLOWED_TOP_LEVEL)
    missing = sorted(ALLOWED_TOP_LEVEL - actual)
    if unexpected or missing:
        raise RuntimeError(f"experiment top-level mismatch: unexpected={unexpected}, missing={missing}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="validate and print the migration plan")
    mode.add_argument("--apply", action="store_true", help="apply content-preserving moves")
    parser.add_argument(
        "--prune-verified-bundles",
        action="store_true",
        help="delete only retired bundles that pass all replacement checks",
    )
    args = parser.parse_args()
    moves = _moves()
    if not args.apply:
        collisions = [
            move for move in moves if (ROOT / move.source).exists() and (ROOT / move.destination).exists()
        ]
        if collisions:
            raise SystemExit("migration collisions:\n" + "\n".join(str(item) for item in collisions))
        pending = sum((ROOT / move.source).exists() for move in moves)
        completed = len(moves) - pending
        if pending == 0:
            validate_top_level()
            leftover_bundles = list((EXPERIMENTS / "bundles/retired").glob("*.tar.gz"))
            if leftover_bundles:
                raise SystemExit(f"unprocessed retired bundles: {leftover_bundles}")
        print(f"Experiment migration plan: pending={pending} completed={completed} collisions=0")
        return 0

    existing_ledger: dict[str, Any] = {}
    if LEDGER_PATH.is_file():
        existing_ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    current_migration = migrate(moves)
    migration_results = [
        item
        for item in existing_ledger.get("migration", [])
        if isinstance(item, dict)
    ]
    recorded_moves = {
        (str(item.get("source") or ""), str(item.get("destination") or ""))
        for item in migration_results
    }
    for item in current_migration:
        identity = (
            str(item.get("source") or ""),
            str(item.get("destination") or ""),
        )
        if identity not in recorded_moves:
            migration_results.append(item)
            recorded_moves.add(identity)
    write_aliases(moves)
    current_bundles = prune_bundles() if args.prune_verified_bundles else []
    existing_bundles = [
        item
        for item in existing_ledger.get("bundles", [])
        if isinstance(item, dict)
    ]
    if not args.prune_verified_bundles:
        bundle_results = existing_bundles
    else:
        previous_bundles = {
            item.get("filename"): item
            for item in existing_bundles
        }
        bundle_results = [
            previous_bundles.get(item.get("filename"), item)
            if item.get("status") == "already_absent"
            else item
            for item in current_bundles
        ]
    validate_top_level()
    ledger = {
        "schema_version": "featureliftbench.experiment_bundle_ledger.v1",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "migration": migration_results,
        "bundles": bundle_results,
    }
    LEDGER_PATH.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
    print(
        f"Experiment migration complete: moved={sum(item.get('status') == 'moved' for item in migration_results)} "
        f"deleted={sum(item.get('status') == 'deleted_verified' for item in bundle_results)} "
        f"retained={sum(item.get('status') == 'retained_verification_failed' for item in bundle_results)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
