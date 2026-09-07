#!/usr/bin/env python3
"""Write L1 SOP annotations for Pro+Flash artifact failures (close-read, not packet residual)."""
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PACKETS = OUT / "f3_evidence_packets.json"
ROWS = OUT / "task_results.csv"

SUITES = {
    "deepseek-v4-pro": "experiments/python/openhands/deepseek-v4-pro/python150-prime-v2-main-r1",
    "deepseek-v4-flash": "experiments/python/openhands/deepseek-v4-flash/python200-prime-v2-main-r1",
}

STAGE_LOG = {
    "public_failure": "eval/logs/public.stdout",
    "hidden_failure": "eval/logs/hidden.stdout",
    "build_failure": "eval/logs/build.stdout",
    "isolation_failure": "eval/result.json",
}

VALID_CAUSES = {
    "agent_process_non_delivery",
    "localization",
    "contract_api_completion",
    "dependency_closure",
    "behavior_drift",
    "packaging_modularization",
    "test_gaming_narrow",
    "task_or_evaluator_defect",
    "unknown",
}

CLOSURE = {"contract_api_completion", "dependency_closure", "behavior_drift"}

# Default by task_id. Model-specific overrides below.
BY_TASK: dict[str, dict[str, str]] = {
    "aiohttp__url_params_core__hard3_001": {
        "root_cause_primary": "contract_api_completion",
        "secondary_tags": "validation_boundary;exception_semantics",
        "contract_clause_ids": "B003",
        "evidence_summary": "InvalidHeaderName and a token check exist, but a hidden invalid-name case still does not raise the declared exception.",
    },
    "alembic__revision_map_core__hard3_001": {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "state_lifecycle;data_structure_semantics",
        "contract_clause_ids": "B003;B007",
        "evidence_summary": "Merge head lookup succeeds, but get_revision('base') resolves the symbolic base and returns None, shadowing the revision whose id is base.",
    },
    "build__pyproject_backend_core__hard3_001": {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "default_values",
        "contract_clause_ids": "B001",
        "evidence_summary": "Missing build-system table uses a legacy backend string instead of the required default backend.",
    },
    "celery__signal_dispatch_core__hard3_001": {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "validation_boundary;call_signature",
        "contract_clause_ids": "B001",
        "evidence_summary": "Signal connect rejects an ordinary callable that does not accept keyword arguments, so send never reaches the receiver.",
    },
    "click__lazy_command_core__hard3_001": {
        "root_cause_primary": "task_or_evaluator_defect",
        "secondary_tags": "undeclared_api",
        "contract_clause_ids": "",
        "validity_override": "benchmark_invalid_candidate",
        "validity_reason": "Public test calls LazyCommandCollection.invoke, which is absent from required_api and from B003/B004 (get_command/resolve only).",
        "evidence_summary": "First failure is an evaluator call to undeclared invoke; not attributed as an agent closure miss.",
    },
    "cookiecutter__repo_finder_core__hard3_001": {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "parsing_normalization",
        "contract_clause_ids": "B001",
        "evidence_summary": "Abbreviation expansion raises IndexError on a multi-placeholder template instead of returning a complete path.",
    },
    "decorator__signature_preserving_core__001": {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "argument_binding;call_signature",
        "contract_clause_ids": "B001;B002",
        "evidence_summary": "Decorator keeps metadata but forwards a different args/kwargs shape than the wrapped call.",
    },
    "filelock__reentrant_lock_core__001": {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "state_lifecycle",
        "contract_clause_ids": "B002;B004",
        "evidence_summary": "After the context manager exits, is_locked is false but the lock file is left on disk.",
    },
    "flake8__plugin_options_core__hard3_001": {
        "root_cause_primary": "task_or_evaluator_defect",
        "secondary_tags": "undeclared_api",
        "contract_clause_ids": "",
        "validity_override": "benchmark_invalid_candidate",
        "validity_reason": "Public test calls OptionManager.register_options and options[dest]; required_api lists OptionManager with no members, and B001 only says to register options.",
        "evidence_summary": "First failure uses undeclared OptionManager.register_options / dict options lookup; excluded from the agent-cause denominator.",
    },
    "flask__route_dispatch_core__001": {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "return_value;equality_protocol",
        "contract_clause_ids": "B001;B003",
        "evidence_summary": "Route dispatch returns a Response-like object whose observable equality or normalization does not match the required Response contract.",
    },
    "hatch__project_metadata_core__hard3_001": {
        "root_cause_primary": "task_or_evaluator_defect",
        "secondary_tags": "undeclared_normalization_rule",
        "contract_clause_ids": "",
        "validity_override": "benchmark_invalid_candidate",
        "validity_reason": "B001 requires lowercasing names; the public test additionally requires space-to-hyphen canonicalization (my package vs my-package).",
        "evidence_summary": "Failure is hyphenation beyond the published lowercase-name rule; excluded from the agent-cause denominator.",
    },
    "json_logic__evaluator_core__hard3_001": {
        "root_cause_primary": "contract_api_completion",
        "secondary_tags": "state_lifecycle;validation_boundary",
        "contract_clause_ids": "B003",
        "evidence_summary": "Logical conjunction does not short-circuit; a later failing operand is still evaluated and raises ZeroDivisionError.",
    },
    "jupyter_core__paths_resolver_core__hard3_001": {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "platform_path",
        "contract_clause_ids": "B002",
        "evidence_summary": "Platform data-dir defaults join a Windows layout onto the current POSIX runtime instead of returning the declared Windows path.",
    },
    "keyring__backend_select_core__hard3_001": {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "ordering_precedence;registry_dispatch",
        "contract_clause_ids": "B006;B007",
        "evidence_summary": "select_backend returns the highest-priority backend class rather than an instance of that class.",
    },
    "license_expression__policy_core__hard3_001": {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "return_value;validation_boundary",
        "contract_clause_ids": "B001;B003",
        "evidence_summary": "Unknown-symbol validation reports 'license key(s)' instead of the clause wording 'license symbol'.",
    },
    "mkdocs__plugin_config_core__hard3_001": {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "registry_dispatch;argument_binding",
        "contract_clause_ids": "B002",
        "evidence_summary": "PluginCollection exists and records names, but load looks up hook_registry by plugin name and expects on_* methods; the public registry uses dotted event keys, so run_event returns [].",
    },
    "multidict__multidict_mutation_core__hard3_001": {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "data_structure_semantics;ordering_precedence",
        "contract_clause_ids": "B001;B002",
        "evidence_summary": "Duplicate-key MultiDict mutation/getall order does not match the required latest-wins or getall contract.",
    },
    "parsel__selector_namespace_core__hard3_001": {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "parsing_normalization;return_value",
        "contract_clause_ids": "B001",
        "evidence_summary": "Selector.css/get surface exists but CSS id selection does not return the required node text.",
    },
    "platformdirs__app_dirs_core__hard3_001": {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "platform_path",
        "contract_clause_ids": "B005;B006",
        "evidence_summary": "Windows author/roaming/cache layout uses POSIX separators or a different vendor/app nesting than the declared layout.",
    },
    "pluggy__hook_wrapper_core__hard3_001": {
        "root_cause_primary": "task_or_evaluator_defect",
        "secondary_tags": "undeclared_api",
        "contract_clause_ids": "",
        "validity_override": "benchmark_invalid_candidate",
        "validity_reason": "Public test calls HookCaller.call_historic; required_api only lists add_hookimpl, call_extra, and get_hookimpls.",
        "evidence_summary": "First failure is an evaluator call to undeclared call_historic; excluded from the agent-cause denominator.",
    },
    "poetry_core__dependency_groups_core__hard3_001": {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "parsing_normalization",
        "contract_clause_ids": "B002;B003",
        "evidence_summary": "Trajectory inspects poetry-core; parse_project_dependencies still reads PEP 735 dependency-groups and returns {}, while the public input uses project.dependencies and optional-dependencies.",
    },
    "pygments__lexer_core__001": {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "tokenization",
        "contract_clause_ids": "B004",
        "evidence_summary": "Lexer option that should drop whitespace tokens still emits ordinary text tokens.",
    },
    "pytest__ini_markers_core__001": {
        "root_cause_primary": "task_or_evaluator_defect",
        "secondary_tags": "undeclared_normalization_rule",
        "contract_clause_ids": "",
        "validity_override": "benchmark_invalid_candidate",
        "validity_reason": "B003 requires preserving description whitespace after the colon; the public test requires the description to be stripped.",
        "evidence_summary": "First failure is description leading-space; that contradicts the published preserve-whitespace clause.",
    },
    "pytest__marker_registry_core__hard3_001": {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "exception_semantics",
        "contract_clause_ids": "B003",
        "evidence_summary": "Strict unknown-marker handling emits a warning instead of the declared exception type.",
    },
    "python_decouple__config_repository_core__001": {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "parsing_normalization",
        "contract_clause_ids": "B001;B002;B003;B004",
        "evidence_summary": ".env parsing does not strip quotes or trailing comments to the normalized values required by the public clauses.",
    },
    "readme_renderer__content_type_core__hard3_001": {
        "root_cause_primary": "task_or_evaluator_defect",
        "secondary_tags": "undeclared_output_marker",
        "contract_clause_ids": "",
        "validity_override": "benchmark_invalid_candidate",
        "validity_reason": "B001 only requires selecting a markdown renderer; the public test asserts the literal substring markdown appears in HTML for a heading that already rendered as h1.",
        "evidence_summary": "Failure is an undeclared output-marker check, not a missing renderer selection.",
    },
    "requests_cache__cache_key_core__hard3_001": {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "parsing_normalization;data_structure_semantics",
        "contract_clause_ids": "B005",
        "evidence_summary": "Header multi-value normalization looks up a header name that is not present under the expected case/key, so cache-key construction raises KeyError.",
    },
    "responses__request_matcher_core__hard3_001": {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "state_lifecycle;registry_dispatch",
        "contract_clause_ids": "B002;B003",
        "evidence_summary": "Once-matcher hit count or call history after the first match does not follow the required matcher lifecycle.",
    },
    "schema__nested_validate_core__hard3_001": {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "parsing_normalization;return_value",
        "contract_clause_ids": "B003",
        "evidence_summary": "And composition does not apply a callable transform; a string that should be uppercased is returned unchanged.",
    },
    "scrapy__item_loader_core__hard3_001": {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "call_signature;argument_binding",
        "contract_clause_ids": "B002;B003",
        "evidence_summary": "ItemLoader treats an item class or list as an instantiated mapping and then fails inside processor application; default_output_processor is also missing.",
    },
    "setuptools_scm__version_normalize_core__hard3_001": {
        "root_cause_primary": "task_or_evaluator_defect",
        "secondary_tags": "undeclared_normalization_rule;default_values",
        "contract_clause_ids": "",
        "validity_override": "benchmark_invalid_candidate",
        "validity_reason": "required_api defaults node to g1234567 and B003 requires a local segment when node is present; the public test omits node and asserts a clean 1.2.3.",
        "evidence_summary": "Public exact 1.2.3 clashes with the published default node plus B003 local segment; excluded from the agent-cause denominator.",
    },
    "starlette__route_matching_core__hard3_001": {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "return_value;call_signature",
        "contract_clause_ids": "B002;B003",
        "evidence_summary": "Route/Mount matching or url_path_for binding does not implement the required method-mismatch or mount-prefix calling convention.",
    },
    "tox__factor_expression_core__hard3_001": {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "parsing_normalization",
        "contract_clause_ids": "B001;B003",
        "evidence_summary": "Factor expressions with brace groups expand to an empty env set instead of the cartesian env names.",
    },
    "virtualenv__interpreter_spec_core__hard3_001": {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "resource_loading;platform_path",
        "contract_clause_ids": "",
        "evidence_summary": "parse_spec treats a glob path as a constraint instead of returning constraint=None and filtering discover_paths.",
    },
    "yamale__schema_validate_core__hard3_001": {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "parsing_normalization;validation_boundary",
        "contract_clause_ids": "B001;B004",
        "evidence_summary": "Schema parser rejects the required shorthand validator expression (Name.func / enclosed-validator path).",
    },
    "bleach__sanitize_core__001": {
        "root_cause_primary": "packaging_modularization",
        "secondary_tags": "packaging_export",
        "contract_clause_ids": "B006",
        "evidence_summary": "Public behavior passed and the isolation gate passed, but submitted source still contains a forbidden import of the original package name (public isolation clause B006).",
    },
    "dateutil__zone_resolver_core__hard3_001": {
        "root_cause_primary": "contract_api_completion",
        "secondary_tags": "state_lifecycle",
        "contract_clause_ids": "B003",
        "evidence_summary": "Zone aliases can be registered but load does not resolve an alias to the canonical zone.",
    },
    "glom__spec_eval_core__hard3_001": {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "default_values;return_value",
        "contract_clause_ids": "B002",
        "evidence_summary": "Coalesce/default spec evaluation returns a different defaulted value than the required spec semantics.",
    },
    "installer__wheel_record_core__hard3_001": {
        "root_cause_primary": "contract_api_completion",
        "secondary_tags": "validation_boundary;exception_semantics",
        "contract_clause_ids": "B002",
        "evidence_summary": "Submission locates dist-info but does not raise the declared error when multiple dist-info candidates are present.",
    },
    "jupyter_server__extension_config_core__hard3_001": {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "ordering_precedence;state_lifecycle",
        "contract_clause_ids": "B001;B002",
        "evidence_summary": "Extension enable/disable precedence leaves a disabled extension still enabled in the merged config.",
    },
    "pendulum__parse_format_core__001": {
        "root_cause_primary": "contract_api_completion",
        "secondary_tags": "api_surface;call_signature",
        "contract_clause_ids": "B004",
        "evidence_summary": "featurelifted.datetime is a module, not a callable constructor, so token formatting cannot be invoked.",
    },
    "pydantic__field_validator_core__hard3_001": {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "call_signature;return_value",
        "contract_clause_ids": "B002;B003",
        "evidence_summary": "ValidationError.errors is a method, so subscripting it for the field name fails on the after-validator failure path.",
    },
    "python_dateutil__relativedelta_core__001": {
        "root_cause_primary": "contract_api_completion",
        "secondary_tags": "api_surface;call_signature",
        "contract_clause_ids": "B002",
        "evidence_summary": "relativedelta is exported as a non-callable module and weekday constants are missing, so datetime arithmetic cannot start.",
    },
    "tenacity__retry_state_core__hard3_001": {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "state_lifecycle;return_value",
        "contract_clause_ids": "B008",
        "evidence_summary": "Retry snapshots keep idle equal to sleep (0.5) instead of the required idle 0.0 on the first observed state.",
    },
    "typer__command_parser_core__001": {
        "root_cause_primary": "packaging_modularization",
        "secondary_tags": "packaging_export;api_surface",
        "contract_clause_ids": "B006",
        "evidence_summary": "Build and behavior gates passed; isolation fails forbidden_imports, and the required testing.CliRunner export is absent from the standalone package.",
    },
}

OVERRIDES: dict[tuple[str, str], dict[str, str]] = {
    (
        "deepseek-v4-flash",
        "flask__route_dispatch_core__001",
    ): {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "return_value",
        "contract_clause_ids": "B003",
        "evidence_summary": "View returns a dict; Response normalization does not accept dict as a valid response type.",
    },
    (
        "deepseek-v4-flash",
        "keyring__backend_select_core__hard3_001",
    ): {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "registry_dispatch;name_resolution",
        "contract_clause_ids": "B006;B007",
        "evidence_summary": "Env override with a registered backend name raises BackendNotFound instead of selecting that candidate.",
    },
    (
        "deepseek-v4-flash",
        "starlette__route_matching_core__hard3_001",
    ): {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "call_signature;argument_binding",
        "contract_clause_ids": "B002;B003;B004",
        "evidence_summary": "Mount.url_path_for binds the name argument twice (positional plus keyword), so mount-prefix URL generation cannot run.",
    },
}


def leak_check(text: str, task_id: str) -> None:
    if re.search(r"hidden_tests/|test_hidden|::test_", text):
        raise ValueError(f"{task_id}: annotation exposes a private test identifier")


def evidence_path(model: str, task_id: str, stage: str) -> str:
    rel = SUITES[model]
    suffix = STAGE_LOG.get(stage, "eval/result.json")
    path = ROOT / rel / task_id / suffix
    if not path.is_file() and suffix != "eval/result.json":
        alt = ROOT / rel / task_id / "eval/result.json"
        if alt.is_file():
            return f"{rel}/{task_id}/eval/result.json"
    return f"{rel}/{task_id}/{suffix}"


def main() -> None:
    packets = json.loads(PACKETS.read_text(encoding="utf-8"))
    meta_by = {}
    with ROWS.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            meta_by[(row["model"], row["task_id"])] = row

    out_rows = []
    missing = []
    for packet in packets:
        model = packet["model"]
        task_id = packet["task_id"]
        spec = dict(BY_TASK.get(task_id) or {})
        spec.update(OVERRIDES.get((model, task_id)) or {})
        if not spec:
            missing.append((model, task_id))
            continue
        cause = spec["root_cause_primary"]
        if cause not in VALID_CAUSES:
            raise ValueError(f"{task_id}: bad cause {cause}")
        override = spec.get("validity_override", "")
        reason = spec.get("validity_reason", "")
        if cause == "task_or_evaluator_defect" and override != "benchmark_invalid_candidate":
            raise ValueError(f"{task_id}: defect requires override")
        if override == "benchmark_invalid_candidate" and cause != "task_or_evaluator_defect":
            raise ValueError(f"{task_id}: override/cause mismatch")
        if override and not reason:
            raise ValueError(f"{task_id}: override needs reason")
        clauses = spec.get("contract_clause_ids", "")
        if clauses and any(re.fullmatch(r"B[0-9]{3}", part) is None for part in clauses.split(";")):
            raise ValueError(f"{task_id}: bad clauses {clauses}")
        summary = spec["evidence_summary"].strip()
        leak_check(summary, task_id)
        leak_check(reason, task_id)
        leak_check(spec.get("secondary_tags", ""), task_id)
        row_meta = meta_by[(model, task_id)]
        stage = packet["first_failure_stage"]
        eligibility = override or "valid_agent_evidence"
        out_rows.append(
            {
                "task_id": task_id,
                "model": model,
                "split": row_meta.get("suite_split") or "python150",
                "lift_type": row_meta.get("lift_type") or "",
                "feature_family": row_meta.get("feature_family") or packet.get("feature_family") or "",
                "evidence_eligibility": eligibility,
                "functional_pass": "false",
                "first_failure_stage": stage,
                "root_cause_primary": cause,
                "secondary_tags": spec.get("secondary_tags", ""),
                "contract_clause_ids": clauses,
                "context_violation": row_meta.get("process_context_violation") or "False",
                "evidence_summary": summary,
                "evidence_path": evidence_path(model, task_id, stage),
                "review_status": "assistant_first_pass",
                "annotator": "assistant_first_pass",
                "adjudicated": "false",
                "independent_human_review": "false",
                "validity_override": override,
                "validity_reason": reason,
                "close_read_tier": "L1",
            }
        )

    if missing:
        raise SystemExit(f"unlabeled packets: {missing}")

    fieldnames = list(out_rows[0])
    csv_path = OUT / "failure_root_cause_annotations.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)

    valid = [r for r in out_rows if r["evidence_eligibility"] == "valid_agent_evidence"]
    defects = [r for r in out_rows if r["evidence_eligibility"] == "benchmark_invalid_candidate"]
    by_cause = Counter(r["root_cause_primary"] for r in valid)
    by_model_cause: dict[str, Counter[str]] = {}
    for r in valid:
        by_model_cause.setdefault(r["model"], Counter())[r["root_cause_primary"]] += 1
    closure_n = sum(by_cause[c] for c in CLOSURE)
    loc_n = by_cause["localization"]
    pack_n = by_cause["packaging_modularization"]
    unknown_n = by_cause["unknown"]

    summary = {
        "schema_version": "featureliftbench.failure_analysis.v1",
        "split": "python150",
        "models": ["deepseek-v4-pro", "deepseek-v4-flash"],
        "review_status": "assistant_first_pass",
        "independent_human_review": False,
        "n_annotated": len(out_rows),
        "n_valid_agent": len(valid),
        "n_benchmark_invalid_candidate": len(defects),
        "defect_task_ids": sorted({r["task_id"] for r in defects}),
        "root_cause_valid_agent": dict(sorted(by_cause.items())),
        "root_cause_valid_agent_by_model": {
            model: dict(sorted(counts.items())) for model, counts in sorted(by_model_cause.items())
        },
        "closure_classes": sorted(CLOSURE),
        "closure_n": closure_n,
        "localization_n": loc_n,
        "packaging_n": pack_n,
        "unknown_n": unknown_n,
        "closure_share_of_valid": None if not valid else round(closure_n / len(valid), 4),
        "close_read_tier": "L1",
        "scope": "python150 artifact failures for deepseek-v4-pro and deepseek-v4-flash",
        "caveats": [
            "L1 output-side close-read of contract, first-failure log, and submission. Not L2 dual review.",
            "Trajectory screen: every remaining valid_agent_evidence failure issued deep repo inspect (find/grep/cat or file view under repo/). Localization primary remains 0 after that screen, not because it was skipped.",
            "Hidden summaries are desensitized; no hidden test names or assertions.",
            "Hidden-only fairness (Protocol §11) is AI-assisted clause-mapping only; freeze contracts still mark formal_human_double_review_pending.",
            "Qwen/Luna/OSS unlabeled in the Pro+Flash census. Stratified L1 postsample is postsample_annotations.csv / f3_postsample_summary.json; do not merge those counts into the census valid denominator.",
            "Process-layer screen: process_layer_summary.json. Finding 3 does not use process tags as the primary cause.",
            "Defects excluded: click.invoke, pluggy.call_historic, hatch hyphenation, readme markdown marker, pytest ini description strip vs B003, flake8 undeclared register_options, setuptools_scm default node vs public 1.2.3.",
            "poetry_core recoded from unknown to behavior_drift after trajectory showed poetry-core inspection plus wrong metadata schema.",
        ],
    }
    (OUT / "f3_annotation_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print("wrote", csv_path)


if __name__ == "__main__":
    main()
