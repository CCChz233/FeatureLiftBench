#!/usr/bin/env python3
"""Perform two auditable AI-assisted passes over behavior-test mappings.

This is an engineering review, not a substitute for two independent human
annotators.  It never adds a public requirement from hidden-test contents:
public clauses are materialized from metadata first, and both passes only map
test nodeids onto those frozen clauses.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools/research_analysis"
sys.path.insert(0, str(TOOLS))

from materialize_v11_audit_assets import pytest_nodeids  # noqa: E402


TASKS = ROOT / "benchmark/tasks"
OUTPUT = ROOT / "artifacts/research_analysis/v1_1/behavior_review_audit.json"
TOKEN_RE = re.compile(r"[A-Za-z0-9]+")
STOP = {
    "a", "an", "and", "api", "as", "assert", "be", "by", "class", "declared",
    "does", "feature", "featurelifted", "for", "from", "function", "hidden", "import",
    "included", "into", "is", "it", "name", "no", "not", "of", "on", "or", "package",
    "preserve", "public", "remain", "scope", "semantics", "submitted", "target", "test",
    "the", "their", "these", "this", "to", "upstream", "within", "with", "without",
}


# These corrections cover the Pilot-10 and six contract-suspect tasks.  Values
# refer only to clauses that existed before reading hidden tests; $api and
# $isolation resolve to metadata-derived public clauses.
PRIORITY_OVERRIDES: dict[str, dict[str, list[str]]] = {
    "pluggy__hook_specs_core__001": {
        "test_historic_hook_replays_for_late_registration": ["B007"],
    },
    "pydantic_v1__validation_error_core__001": {
        "test_simple_model_parses_fields": ["B001"],
        "test_missing_required_field_raises": ["B001", "B005"],
        "test_field_validator_runs": ["B002"],
        "test_validator_pre_runs_before_type_check": ["B002"],
        "test_no_pydantic_import_surface": ["$isolation"],
    },
    "coverage__config_merge_core__001": {
        "test_read_run_config_env_data_file": ["B003"],
        "test_read_run_config_multiline_lists": ["B002"],
        "test_read_run_config_relative_files_section": ["B001", "B002"],
    },
    "lark__grammar_loader_core__001": {
        "test_open_relative_import_and_common_import": ["B001", "B002", "B003"],
    },
    "diskcache__eviction_policy_core__hard3_001": {
        "test_evict_least_recently_used": ["B001"],
    },
    "sqlparse__format_filters_core__001": {
        "test_formatter_comment_stripping_and_spacing": ["B001"],
    },
    "websockets__handshake_parse_core__001": {
        "test_validate_handshake_rejects_bad_upgrade": ["B005", "B007"],
        "test_parse_websocket_request_basic": ["B003"],
        "test_parse_upgrade_case_insensitive_list": ["B001"],
        "test_parse_subprotocol_skips_empty_elements": ["B002"],
        "test_parse_request_invalid_method": ["B003", "B007"],
        "test_parse_headers_security_limit": ["B003", "B007"],
        "test_parse_extension_invalid_quoted_token": ["B002", "B007"],
        "test_build_subprotocol_roundtrip": ["B002", "$api"],
        "test_validate_subprotocols_rejects_invalid_token": ["B002", "B007"],
        "test_parse_authorization_basic_credentials": ["$api"],
        "test_parse_authorization_basic_rejects_non_basic_scheme": ["$api"],
        "test_build_www_authenticate_basic_format": ["$api"],
        "test_no_websockets_import_surface": ["$isolation"],
    },
    "boltons__iterutils_core__001": {
        "test_unique_and_bucketize": ["B003", "B004"],
        "test_partition_truthiness": ["$api"],
        "test_chunk_ranges_with_overlap": ["$api"],
        "test_backoff_exponential_growth": ["$api"],
        "test_no_boltons_import_surface": ["$isolation"],
    },
    "schema__nested_validate_core__hard3_001": {
        "test_extra_keys_rejected": ["B001"],
    },
    "requests_cache__cache_key_core__hard3_001": {
        "test_query_order_normalized": ["B003", "B004"],
        "test_ignored_parameter_redacts_value_for_matching": ["B004"],
        "test_json_body_sorting_and_redaction_affect_cache_key": ["B001", "B006"],
        "test_form_body_and_key_only_params_are_normalized": ["B004", "B006"],
        "test_match_headers_controls_key_variation": ["B005", "B007"],
        "test_header_multi_value_normalization_and_redaction": ["B005"],
    },
    "celery__signal_dispatch_core__hard3_001": {
        "test_dispatch_uid_allows_duplicate_callables": ["B001", "B003"],
        "test_exception_capture_in_send": ["B003"],
    },
    "cookiecutter__repo_finder_core__hard3_001": {
        "test_nested_template_detection": ["$api"],
    },
    "jupyter_server__extension_config_core__hard3_001": {
        "test_recursive_update_and_enable": ["B001", "B002"],
        "test_filter_enabled_extensions_masks_disabled": ["B002", "B003"],
        "test_recursive_update_prunes_empty_nested_dicts": ["B001"],
    },
    "mkdocs__plugin_config_core__hard3_001": {
        "test_plugin_collection_runs_event_by_priority": ["B002"],
        "test_unexpected_option_reported": ["B001"],
    },
    "alembic__revision_map_core__hard3_001": {
        "test_branch_label_propagates_to_branch_head": ["B004"],
        "test_dependencies_affect_ancestors_without_removing_versioned_head": ["B003", "B005"],
    },
    "fs__url_opener_core__hard3_001": {
        "test_default_protocol_injection": ["B001", "B002"],
        "test_unknown_protocol_raises": ["B002"],
    },
    "jinja2__loader_inheritance_core__001": {
        "test_loader_module_required_for_missing_template": ["B001"],
    },
    "phonenumbers__parse_format_core__001": {
        "test_parse_e164_and_format": ["B001", "B002"],
        "test_gb_national_equals_e164_parse": ["B001"],
    },
    "pluggy__hook_call_order__001": {
        "test_basic_hook_registration_and_ordering": ["B001", "B002", "B003"],
        "test_validation_unregister_and_plugin_names": ["B006", "B007"],
        "test_hook_historic_and_subset_hooknames": ["B002", "$api"],
    },
    "pytest__skipif_eval_core__001": {
        "test_invalid_syntax_raises": ["B001"],
    },
    "sqlalchemy__event_dispatch_core__hard3_001": {
        "test_once_and_remove_during_dispatch_and_propagation": ["B001", "B003", "B004"],
        "test_named_kwargs_dispatch": ["B005"],
    },
    "trafaret__validation_rules_core__hard3_001": {
        "test_dict_validates_schema": ["B001"],
        "test_or_composition": ["B001"],
    },
    "urllib3__retry_backoff_core__001": {
        "test_is_retry_status_forcelist": ["B003"],
    },
    "vibe_app__plugin_registry_core__001": {
        "test_register_and_run_plugin": ["B001", "B002"],
        "test_list_plugins_returns_registered_names": ["B001"],
    },
    "wheel__metadata_normalize_core__hard3_001": {
        "test_safe_name_and_extra": ["B001"],
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def normalize(token: str) -> str:
    value = token.lower()
    if value.endswith("ies") and len(value) > 4:
        value = value[:-3] + "y"
    elif value.endswith("ing") and len(value) > 5:
        value = value[:-3]
    elif value.endswith("ed") and len(value) > 4:
        value = value[:-2]
    elif value.endswith("s") and len(value) > 3:
        value = value[:-1]
    return value


def tokens(text: str) -> set[str]:
    return {
        normalized
        for raw in TOKEN_RE.findall(text.replace("_", " "))
        if (normalized := normalize(raw)) not in STOP and len(normalized) > 1
    }


def function_source(task: Path, nodeid: str) -> str:
    relative, *parts = nodeid.split("::")
    function_name = parts[-1]
    path = task / relative
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name:
            return ast.get_source_segment(text, node) or function_name
    return function_name


def call_names(source: str) -> set[str]:
    tree = ast.parse(source)
    values: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        function = node.func
        if isinstance(function, ast.Name):
            values.add(normalize(function.id))
        elif isinstance(function, ast.Attribute):
            values.add(normalize(function.attr))
    return values


def clause_ids_by_kind(clauses: list[dict[str, Any]], kind: str) -> list[str]:
    return [str(item["behavior_id"]) for item in clauses if item.get("clause_kind") == kind]


def rank_mapping(nodeid: str, source: str, clauses: list[dict[str, Any]], *, body_pass: bool) -> list[str]:
    function_name = nodeid.rsplit("::", 1)[-1]
    name_tokens = tokens(function_name)
    source_tokens = tokens(source) if body_pass else set()
    calls = call_names(source) if body_pass else set()
    candidates: list[tuple[float, str]] = []
    for clause in clauses:
        if clause.get("clause_kind") != "included_behavior":
            continue
        clause_tokens = tokens(str(clause.get("text") or ""))
        score = 4.0 * len(name_tokens & clause_tokens)
        if body_pass:
            score += 2.0 * len(calls & clause_tokens)
            score += 0.2 * len(source_tokens & clause_tokens)
        candidates.append((score, str(clause["behavior_id"])))
    candidates.sort(reverse=True)
    if candidates and candidates[0][0] >= 2.0:
        ceiling = candidates[0][0]
        return sorted(item[1] for item in candidates[:2] if item[0] >= max(2.0, ceiling * 0.65))
    return []


def resolve_override(values: list[str], clauses: list[dict[str, Any]]) -> list[str]:
    kinds = {
        "$api": clause_ids_by_kind(clauses, "api_surface"),
        "$isolation": clause_ids_by_kind(clauses, "isolation_constraint"),
    }
    resolved: list[str] = []
    for value in values:
        resolved.extend(kinds.get(value, [value]))
    return sorted(set(resolved))


def review_mapping(task: Path, nodeid: str, clauses: list[dict[str, Any]]) -> tuple[dict[str, Any], bool, bool]:
    source = function_source(task, nodeid)
    function_name = nodeid.rsplit("::", 1)[-1]
    pass_1 = rank_mapping(nodeid, source, clauses, body_pass=False)
    pass_2 = rank_mapping(nodeid, source, clauses, body_pass=True)
    override = PRIORITY_OVERRIDES.get(task.name, {}).get(function_name)
    isolation = clause_ids_by_kind(clauses, "isolation_constraint")
    api = clause_ids_by_kind(clauses, "api_surface")
    if override:
        chosen = resolve_override(override, clauses)
        decision = "priority_semantic_override"
    elif re.search(r"(?:no_|forbidden_).*(?:import|package)", function_name):
        chosen = isolation or api
        decision = "public_isolation_constraint"
    elif pass_2:
        chosen = pass_2
        decision = "full_test_ast_semantic_score"
    elif pass_1:
        chosen = pass_1
        decision = "nodeid_semantic_score"
    else:
        chosen = api
        decision = "declared_api_scope_fallback"
    conflict = bool(pass_1 and pass_2 and pass_1 != pass_2 and not override)
    fallback = decision == "declared_api_scope_fallback"
    return (
        {
            "nodeid": nodeid,
            "public_clause_ids": chosen,
            "mapping_method": "ai_assisted",
            "review_evidence": {
                "pass_1_nodeid_mapping": pass_1,
                "pass_2_ast_mapping": pass_2,
                "decision": decision,
                "test_source_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
            },
        },
        conflict,
        fallback,
    )


def main() -> int:
    args = parse_args()
    rows: list[dict[str, Any]] = []
    totals = {"tasks": 0, "mappings": 0, "conflicts": 0, "api_fallbacks": 0, "priority_overrides": 0}
    for task in sorted(path for path in TASKS.iterdir() if (path / "metadata.json").is_file()):
        path = task / "evaluation/behavior_contract.json"
        contract = load(path)
        clauses = contract.get("public_clauses") or []
        task_conflicts = task_fallbacks = task_overrides = 0
        for key, directory in (("public_test_mappings", "public_tests"), ("hidden_test_mappings", "hidden_tests")):
            reviewed = []
            for nodeid in pytest_nodeids(task / directory, task):
                mapping, conflict, fallback = review_mapping(task, nodeid, clauses)
                reviewed.append(mapping)
                task_conflicts += int(conflict)
                task_fallbacks += int(fallback)
                task_overrides += int(mapping["review_evidence"]["decision"] == "priority_semantic_override")
            contract[key] = reviewed
        contract["unmapped_public_test_nodeids"] = []
        contract["unmapped_hidden_test_nodeids"] = []
        contract["review_status"] = "ai_assisted_reviewed"
        contract["review"] = {
            "protocol_version": "behavior_ai_review.v1",
            "pass_1": {
                "reviewer_id": "codex_semantic_nodeid_pass",
                "reviewer_type": "ai_assisted_author",
                "input_scope": "frozen public clauses and test nodeids",
            },
            "pass_2": {
                "reviewer_id": "codex_ast_body_pass",
                "reviewer_type": "ai_assisted_second_pass_not_independent_human",
                "input_scope": "frozen public clauses and local test AST",
            },
            "conflict_count": task_conflicts,
            "api_fallback_count": task_fallbacks,
            "formal_human_double_review_pending": True,
        }
        if not args.check:
            path.write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        totals["tasks"] += 1
        totals["mappings"] += len(contract["public_test_mappings"]) + len(contract["hidden_test_mappings"])
        totals["conflicts"] += task_conflicts
        totals["api_fallbacks"] += task_fallbacks
        totals["priority_overrides"] += task_overrides
        rows.append(
            {
                "task_id": task.name,
                "conflict_count": task_conflicts,
                "api_fallback_count": task_fallbacks,
                "priority_override_count": task_overrides,
                "formal_human_double_review_pending": True,
            }
        )
    payload = {
        "schema_version": "featureliftbench.behavior_ai_review_audit.v1",
        "review_boundary": (
            "Two isolated AI-assisted passes were performed. They are not independent human annotations "
            "and do not satisfy the paper-release double-review gate."
        ),
        "totals": totals,
        "tasks": rows,
    }
    if not args.check:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(totals, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
