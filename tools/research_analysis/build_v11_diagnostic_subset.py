#!/usr/bin/env python3
"""Build the frozen v1.1 diagnostic subset and auditable constraint report."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TAXONOMY = REPO_ROOT / "artifacts/research_analysis/python150_task_taxonomy.csv"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "artifacts/research_analysis/v1_1"
SEED = 20260714

REPRESENTATIVE_20 = (
    "alembic__revision_map_core__hard3_001",
    "astroid__nodes_core__001",
    "click__lazy_command_core__hard3_001",
    "fsspec__url_chain_core__hard3_001",
    "h11__message_parse_core__001",
    "humanize__naturaltime_core__001",
    "isodate__duration_parse_core__001",
    "jinja2__loader_inheritance_core__001",
    "parso__python_parse_core__001",
    "phonenumbers__parse_format_core__001",
    "pluggy__hook_call_order__001",
    "pydantic_settings__env_source_core__001",
    "pytest__skipif_eval_core__001",
    "pyyaml__safe_load_dump__001",
    "returns__result_pipeline_core__hard3_001",
    "setuptools_scm__version_normalize_core__hard3_001",
    "trafaret__validation_rules_core__hard3_001",
    "urllib3__retry_backoff_core__001",
    "vibe_app__plugin_registry_core__001",
    "yamale__schema_validate_core__hard3_001",
)

PILOT_10 = (
    "pluggy__hook_specs_core__001",
    "pydantic_v1__validation_error_core__001",
    "coverage__config_merge_core__001",
    "lark__grammar_loader_core__001",
    "websockets__handshake_parse_core__001",
    "boltons__iterutils_core__001",
    "schema__nested_validate_core__hard3_001",
    "requests_cache__cache_key_core__hard3_001",
    "sqlparse__format_filters_core__001",
    "celery__signal_dispatch_core__hard3_001",
)

CONTRACT_REVIEW_6 = (
    "cookiecutter__repo_finder_core__hard3_001",
    "dateutil__zone_resolver_core__hard3_001",
    "diskcache__eviction_policy_core__hard3_001",
    "jupyter_server__extension_config_core__hard3_001",
    "mkdocs__plugin_config_core__hard3_001",
    "parsel__selector_namespace_core__hard3_001",
)

MECHANISM_STRESS_4 = (
    "pyramid__configurator_action_core__hard3_001",
    "sqlalchemy__event_dispatch_core__hard3_001",
    "fs__url_opener_core__hard3_001",
    "wheel__metadata_normalize_core__hard3_001",
)

TAXONOMY_REVIEW_10 = (
    "babel__plural_core__001",
    "cerberus__schema_validate_core__001",
    "hatch__project_metadata_core__hard3_001",
    "jinja2__lexer_parser_core__001",
    "multidict__multidict_mutation_core__hard3_001",
    "platformdirs__app_dirs_core__hard3_001",
    "pytest__fixture_resolve_core__001",
    "redis__resp_parser_core__001",
    "vibe_app__session_registry_core__001",
    "xmltodict__xml_parse_core__001",
)

CANARY_5 = (
    "boltons__iterutils_core__001",
    "coverage__config_merge_core__001",
    "lark__grammar_loader_core__001",
    "pluggy__hook_specs_core__001",
    "yamale__schema_validate_core__hard3_001",
)

FEATURE_FAMILIES = (
    "parse_tokenize_decode",
    "protocol_state_transition",
    "validate_normalize_construct",
    "serialize_format_render",
    "registry_plugin_dispatch",
    "config_resolve_discover",
    "resource_metadata_loading",
    "algorithm_data_structure",
    "cache_retry_policy",
    "workflow_session_orchestration",
)
DOMAINS = (
    "parsing",
    "data_modeling",
    "testing",
    "configuration",
    "packaging",
    "networking",
    "general_utility",
    "application",
)
MECHANISMS = (
    "static_transitive_dependency",
    "implicit_runtime_dependency",
    "data_model_invariant",
    "parser_state",
    "framework_lifecycle",
    "global_state_registry",
    "config_environment",
    "resource_packaging",
    "dynamic_import_plugin",
    "third_party_contract",
)
ARCHETYPES = ("library", "framework_plugin", "developer_tooling", "application_service")
STATEFULNESS = ("stateless", "local_state", "session_state", "global_state", "lifecycle_state")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--taxonomy", type=Path, default=DEFAULT_TAXONOMY)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--taxonomy-version", default="v1")
    parser.add_argument("--check", action="store_true", help="Validate without writing outputs")
    return parser.parse_args()


def load_rows(path: Path) -> tuple[list[dict[str, str]], str]:
    raw = path.read_bytes()
    rows = list(csv.DictReader(raw.decode("utf-8").splitlines()))
    return rows, hashlib.sha256(raw).hexdigest()


def depth_bin(raw: str) -> str:
    try:
        depth = int(raw)
    except (TypeError, ValueError):
        return "unknown"
    if depth <= 1:
        return "shallow"
    if depth == 2:
        return "medium"
    return "deep"


def constraint(
    name: str, required: Any, observed: Any, satisfied: bool
) -> dict[str, Any]:
    return {
        "constraint": name,
        "required": required,
        "observed": observed,
        "satisfied": satisfied,
    }


def sorted_counts(values: list[str]) -> dict[str, int]:
    return dict(sorted(Counter(values).items()))


def build_audit(
    rows: list[dict[str, str]], *, taxonomy_sha256: str, taxonomy_version: str
) -> dict[str, Any]:
    index = {row["task_id"]: row for row in rows}
    missing = sorted(set(REPRESENTATIVE_20) - set(index))
    if missing:
        raise ValueError(f"representative tasks missing from taxonomy: {', '.join(missing)}")
    selected = [index[task_id] for task_id in REPRESENTATIVE_20]
    feature_counts = sorted_counts([row["feature_family_primary"] for row in selected])
    domain_counts = sorted_counts([row["repo_domain_primary"] for row in selected])
    archetype_counts = sorted_counts([row["repo_archetype_primary"] for row in selected])
    state_counts = sorted_counts([row["feature_statefulness"] for row in selected])
    depth_counts = sorted_counts([depth_bin(row["static_file_closure_depth"]) for row in selected])
    split_counts = sorted_counts([row["split"] for row in selected])
    provenance_counts = sorted_counts([row["repo_provenance"] for row in selected])
    mechanism_counts = Counter()
    for row in selected:
        mechanism_counts.update(
            value for value in row["normalized_entanglement_types"].split(";") if value
        )
    mechanism_observed = dict(sorted(mechanism_counts.items()))
    checks = [
        constraint("task_count", 20, len(selected), len(selected) == 20),
        constraint("unique_source_repositories", 20, len({row["source_repo"] for row in selected}), len({row["source_repo"] for row in selected}) == 20),
        constraint("split", {"core100": 13, "hard50": 7}, split_counts, split_counts == {"core100": 13, "hard50": 7}),
        constraint("feature_family", list(FEATURE_FAMILIES), feature_counts, set(FEATURE_FAMILIES) <= set(feature_counts)),
        constraint("repository_domain", list(DOMAINS), domain_counts, set(DOMAINS) <= set(domain_counts)),
        constraint("entanglement_mechanism", list(MECHANISMS), mechanism_observed, set(MECHANISMS) <= set(mechanism_observed)),
        constraint("repository_archetype", list(ARCHETYPES), archetype_counts, set(ARCHETYPES) <= set(archetype_counts)),
        constraint("closure_depth", ["shallow", "medium", "deep"], depth_counts, {"shallow", "medium", "deep"} <= set(depth_counts)),
        constraint("statefulness", list(STATEFULNESS), state_counts, set(STATEFULNESS) <= set(state_counts)),
        constraint("provenance", {"real_oss_mature": 19, "curated_vibe": 1}, provenance_counts, provenance_counts == {"curated_vibe": 1, "real_oss_mature": 19}),
    ]
    selection_mode = "exact_constraints" if all(item["satisfied"] for item in checks) else "maximum_coverage"
    uncovered: dict[str, list[str]] = {}
    for item in checks:
        missing_values = (
            sorted(set(item["required"]) - set(item["observed"]))
            if not item["satisfied"]
            and isinstance(item["required"], list)
            and isinstance(item["observed"], dict)
            else []
        )
        uncovered[item["constraint"]] = missing_values
        # Duplicate the audit context on every row so filtered/extracted rows
        # remain independently auditable.
        item.update(
            {
                "selection_mode": selection_mode,
                "uncovered_values": missing_values,
                "taxonomy_version": taxonomy_version,
                "taxonomy_sha256": taxonomy_sha256,
            }
        )
    return {
        "schema_version": "featureliftbench.representative_constraint_audit.v1",
        "seed": SEED,
        "taxonomy_version": taxonomy_version,
        "taxonomy_sha256": taxonomy_sha256,
        "task_ids": list(REPRESENTATIVE_20),
        "selection_mode": selection_mode,
        "uncovered_values": uncovered,
        "constraints": checks,
    }


def subset_manifest(*, taxonomy_sha256: str, taxonomy_version: str) -> dict[str, Any]:
    challenge = PILOT_10 + CONTRACT_REVIEW_6 + MECHANISM_STRESS_4
    return {
        "schema_version": "featureliftbench.diagnostic_subset.v1",
        "taxonomy_version": taxonomy_version,
        "taxonomy_sha256": taxonomy_sha256,
        "selection_outcome_fields_used": False,
        "representative_seed": SEED,
        "representative_20": list(REPRESENTATIVE_20),
        "challenge_20": list(challenge),
        "challenge_groups": {
            "pilot_10": list(PILOT_10),
            "contract_review_6": list(CONTRACT_REVIEW_6),
            "mechanism_stress_4": list(MECHANISM_STRESS_4),
        },
        "taxonomy_review_10": list(TAXONOMY_REVIEW_10),
        "oracle_canary_5": list(CANARY_5),
    }


def main() -> int:
    args = parse_args()
    rows, digest = load_rows(args.taxonomy)
    audit = build_audit(rows, taxonomy_sha256=digest, taxonomy_version=args.taxonomy_version)
    manifest = subset_manifest(taxonomy_sha256=digest, taxonomy_version=args.taxonomy_version)
    if args.check:
        print(json.dumps(audit, indent=2, sort_keys=True))
        return 0
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "representative20_constraint_audit.json").write_text(
        json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output_dir / "diagnostic_subset_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        f"wrote Representative-20 audit ({audit['selection_mode']}) and "
        f"Diagnostic-40 manifest to {args.output_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
