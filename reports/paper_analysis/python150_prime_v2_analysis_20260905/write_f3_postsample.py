#!/usr/bin/env python3
"""Write Luna/Qwen/OSS stratified L1 postsample annotations (separate from Pro+Flash census)."""
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PACKETS = OUT / "postsample_l1_packets.json"
ROWS = OUT / "task_results.csv"
PROCESS = OUT / "process_tag_screen.json"

SUITES = {
    "gpt-5.6-luna": "experiments/python/openhands/gpt-5.6-luna/python200-prime-v2-main-r1",
    "qwen3.6-35b-a3b-fp8": "experiments/python/openhands/qwen3.6-35b-a3b-fp8/python200-prime-v2-main-r1",
    "gpt-oss-120b": "experiments/python/openhands/gpt-oss-120b/python200-prime-v2-main-r1",
}

STAGE_LOG = {
    "public_failure": "eval/logs/public.stdout",
    "hidden_failure": "eval/logs/hidden.stdout",
    "build_failure": "eval/logs/build.stderr",
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

DEFECTS = {
    "click__lazy_command_core__hard3_001": {
        "root_cause_primary": "task_or_evaluator_defect",
        "secondary_tags": "undeclared_api",
        "contract_clause_ids": "",
        "validity_override": "benchmark_invalid_candidate",
        "validity_reason": "Public test calls LazyCommandCollection.invoke, which is absent from required_api and from B003/B004 (get_command/resolve only).",
        "evidence_summary": "First failure is an evaluator call to undeclared invoke; not attributed as an agent closure miss.",
    },
    "pluggy__hook_wrapper_core__hard3_001": {
        "root_cause_primary": "task_or_evaluator_defect",
        "secondary_tags": "undeclared_api",
        "contract_clause_ids": "",
        "validity_override": "benchmark_invalid_candidate",
        "validity_reason": "Public test calls call_historic, which is absent from required_api and from the published hook-wrapper clauses.",
        "evidence_summary": "First failure is an evaluator call to undeclared call_historic; excluded from the agent-cause denominator.",
    },
    "flake8__plugin_options_core__hard3_001": {
        "root_cause_primary": "task_or_evaluator_defect",
        "secondary_tags": "undeclared_api",
        "contract_clause_ids": "",
        "validity_override": "benchmark_invalid_candidate",
        "validity_reason": "Public test calls OptionManager.register_options and options[dest]; required_api lists OptionManager with no members, and B001 only says to register options.",
        "evidence_summary": "First failure uses undeclared OptionManager.register_options / dict options lookup; excluded from the agent-cause denominator.",
    },
    "hatch__project_metadata_core__hard3_001": {
        "root_cause_primary": "task_or_evaluator_defect",
        "secondary_tags": "undeclared_normalization_rule",
        "contract_clause_ids": "",
        "validity_override": "benchmark_invalid_candidate",
        "validity_reason": "B001 requires lowercasing names; the public test additionally requires space-to-hyphen canonicalization (my package vs my-package).",
        "evidence_summary": "Failure is hyphenation beyond the published lowercase-name rule; excluded from the agent-cause denominator.",
    },
    "readme_renderer__content_type_core__hard3_001": {
        "root_cause_primary": "task_or_evaluator_defect",
        "secondary_tags": "undeclared_output_marker",
        "contract_clause_ids": "",
        "validity_override": "benchmark_invalid_candidate",
        "validity_reason": "Public test requires a literal markdown marker beyond the rendered heading already required by the published clauses.",
        "evidence_summary": "Failure is an extra literal marker check; excluded from the agent-cause denominator.",
    },
    "pytest__ini_markers_core__001": {
        "root_cause_primary": "task_or_evaluator_defect",
        "secondary_tags": "undeclared_normalization_rule",
        "contract_clause_ids": "",
        "validity_override": "benchmark_invalid_candidate",
        "validity_reason": "B003 preserves description whitespace; the public test strips it. Hidden-only fails of this task are the same clause clash.",
        "evidence_summary": "Public strip vs B003 preserve-description clash; excluded from the agent-cause denominator.",
    },
    "setuptools_scm__version_normalize_core__hard3_001": {
        "root_cause_primary": "task_or_evaluator_defect",
        "secondary_tags": "undeclared_normalization_rule;default_values",
        "contract_clause_ids": "",
        "validity_override": "benchmark_invalid_candidate",
        "validity_reason": "required_api defaults node to g1234567 and B003 requires a local segment when node is present; the public test omits node and asserts a clean 1.2.3.",
        "evidence_summary": "Public exact 1.2.3 clashes with the published default node plus B003 local segment; excluded from the agent-cause denominator.",
    },
}

# (model, task_id) -> spec. Public known-defect tasks use DEFECTS unless overridden.
BY_KEY: dict[tuple[str, str], dict[str, str]] = {
    ("gpt-5.6-luna", "coverage__path_remap_core__001"): {
        "root_cause_primary": "contract_api_completion",
        "secondary_tags": "api_surface;packaging_export",
        "contract_clause_ids": "B006",
        "evidence_summary": "Package import fails with ModuleNotFoundError for featurelifted.path_aliases; PathAliases is declared but the module file is absent.",
    },
    ("gpt-5.6-luna", "pygments__lexer_core__001"): {
        "root_cause_primary": "contract_api_completion",
        "secondary_tags": "api_surface",
        "contract_clause_ids": "B006",
        "evidence_summary": "Importing the package hits a SyntaxError in lexer.py (assignment expression used as a comprehension iterable), so the required lexer API never loads.",
    },
    ("gpt-5.6-luna", "astroid__nodes_core__001"): {
        "root_cause_primary": "contract_api_completion",
        "secondary_tags": "api_surface;data_structure_semantics",
        "contract_clause_ids": "B002;B003",
        "evidence_summary": "Parsed trees are returned, but a required node field named value is missing on the reconstructed node.",
    },
    ("gpt-5.6-luna", "importlib_resources__traversable_tree_core__hard3_001"): {
        "root_cause_primary": "contract_api_completion",
        "secondary_tags": "exception_semantics;validation_boundary",
        "contract_clause_ids": "B005",
        "evidence_summary": "joinpath / slash traversal does not raise TraversalError on an escape above the package root.",
    },
    ("gpt-5.6-luna", "jupyter_server__extension_config_core__hard3_001"): {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "ordering_precedence;state_lifecycle",
        "contract_clause_ids": "B002",
        "evidence_summary": "ExtensionConfigStore applies jupyter_server_config.json after jupyter_server_config.d fragments, so a later .d disable does not override the base file.",
    },
    ("gpt-5.6-luna", "apscheduler__cron_trigger_core__hard3_001"): {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "default_values;argument_binding",
        "contract_clause_ids": "B002;B003",
        "evidence_summary": "get_next_fire_time ignores the provided start datetime because unset start_time defaults to now, returning 2026-09-04 09:15 instead of 2024-01-01 09:15.",
    },
    ("gpt-5.6-luna", "croniter__cron_parse_core__001"): {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "parsing_normalization;return_value",
        "contract_clause_ids": "B001;B002",
        "evidence_summary": "Weekday field 1 with DOM * is OR-combined so get_next from the public base datetime lands on 2024-01-16 instead of 2024-01-22.",
    },
    ("gpt-5.6-luna", "filelock__reentrant_lock_core__001"): {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "state_lifecycle",
        "contract_clause_ids": "B002;B004",
        "evidence_summary": "After the context manager exits, is_locked is false but the lock file is left on disk.",
    },
    ("qwen3.6-35b-a3b-fp8", "lark__parse_tree_core__001"): {
        "root_cause_primary": "dependency_closure",
        "secondary_tags": "api_surface;resource_loading",
        "contract_clause_ids": "B006",
        "evidence_summary": "Package import fails with ImportError: ContextualLexer is referenced from parser_frontends but not exported by lexer.py.",
    },
    ("qwen3.6-35b-a3b-fp8", "readme_renderer__content_type_core__hard3_001"): {
        "root_cause_primary": "dependency_closure",
        "secondary_tags": "resource_loading",
        "contract_clause_ids": "B004",
        "evidence_summary": "markdown.py imports pygments, which is not installed in the eval environment, so the package cannot import.",
    },
    ("qwen3.6-35b-a3b-fp8", "sqlparse__parse_format_core__001"): {
        "root_cause_primary": "packaging_modularization",
        "secondary_tags": "packaging_export",
        "contract_clause_ids": "B006",
        "evidence_summary": "Importing featurelifted hits a circular import between engine/__init__.py and engine/grouping.py, so the standalone package never loads.",
    },
    ("qwen3.6-35b-a3b-fp8", "attrs__validators_core__001"): {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "state_lifecycle;validation_boundary",
        "contract_clause_ids": "B001;B005",
        "evidence_summary": "validators.set_disabled exists, but define() still runs field validators because _make.validate reads a stale _run_validators flag.",
    },
    ("qwen3.6-35b-a3b-fp8", "glom__spec_eval_core__hard3_001"): {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "data_structure_semantics;return_value",
        "contract_clause_ids": "B002",
        "evidence_summary": "Coalesce is present, but a list of child path specs is treated as one list spec, so evaluation returns the configured default instead of the first successful child.",
    },
    ("qwen3.6-35b-a3b-fp8", "python_decouple__config_repository_core__001"): {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "parsing_normalization",
        "contract_clause_ids": "B002",
        "evidence_summary": "Quoted .env values keep surrounding quotes and a trailing inline comment instead of returning the unquoted value.",
    },
    ("qwen3.6-35b-a3b-fp8", "alembic__revision_map_core__hard3_001"): {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "state_lifecycle;data_structure_semantics",
        "contract_clause_ids": "B003;B006",
        "evidence_summary": "get_revision('base') resolves the symbolic base and returns None, so the revision whose id is base has no is_branch_point.",
    },
    ("qwen3.6-35b-a3b-fp8", "celery__signal_dispatch_core__hard3_001"): {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "validation_boundary;call_signature",
        "contract_clause_ids": "B001",
        "evidence_summary": "Signal connect rejects an ordinary callable that does not accept keyword arguments, so send never reaches the receiver.",
    },
    ("qwen3.6-35b-a3b-fp8", "dynaconf__settings_merge_core__001"): {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "argument_binding;resource_loading",
        "contract_clause_ids": "B002",
        "evidence_summary": "Dynaconf only binds SETTINGS_FILES-style kwargs, so settings_files and envvar_prefix never load the TOML file and HOST remains None.",
    },
    ("qwen3.6-35b-a3b-fp8", "poetry_core__dependency_groups_core__hard3_001"): {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "parsing_normalization",
        "contract_clause_ids": "B001;B002",
        "evidence_summary": "parse_project_dependencies returns {} for project.dependencies / optional-dependencies input instead of building main and optional groups.",
    },
    ("qwen3.6-35b-a3b-fp8", "pygments__formatter_core__001"): {
        "root_cause_primary": "dependency_closure",
        "secondary_tags": "resource_loading;api_surface",
        "contract_clause_ids": "B001;B002",
        "evidence_summary": "highlight fails because featurelifted.styles.default has no __all__, so the formatter cannot load the default style table.",
    },
    ("gpt-oss-120b", "lark__parse_tree_core__001"): {
        "root_cause_primary": "packaging_modularization",
        "secondary_tags": "packaging_export;resource_loading",
        "contract_clause_ids": "B006;B007",
        "evidence_summary": "The submitted package loads Lark from an eval-time repo/ path; that path is absent in isolation, so import raises FileNotFoundError.",
    },
    ("gpt-oss-120b", "readme_renderer__content_type_core__hard3_001"): {
        "root_cause_primary": "dependency_closure",
        "secondary_tags": "resource_loading",
        "contract_clause_ids": "B004",
        "evidence_summary": "Package import fails with ModuleNotFoundError for nh3, which is not an eval-provided dependency.",
    },
    ("gpt-oss-120b", "sqlparse__parse_format_core__001"): {
        "root_cause_primary": "packaging_modularization",
        "secondary_tags": "packaging_export",
        "contract_clause_ids": "B006;B007",
        "evidence_summary": "Submitted engine modules import sqlparse rather than the standalone featurelifted package, and the isolation audit records that import.",
    },
    ("gpt-oss-120b", "sqlparse__token_tree_core__001"): {
        "root_cause_primary": "packaging_modularization",
        "secondary_tags": "packaging_export",
        "contract_clause_ids": "B006;B007",
        "evidence_summary": "__init__.py calls import_module('sqlparse'); sqlparse is not present in the isolated eval environment.",
    },
    ("gpt-oss-120b", "coverage__config_merge_core__001"): {
        "root_cause_primary": "contract_api_completion",
        "secondary_tags": "api_surface;default_values",
        "contract_clause_ids": "B002;B005",
        "evidence_summary": "CoverageConfig exposes source but not source_pkgs, so a required run-config list option cannot be read.",
    },
    ("gpt-oss-120b", "python_dateutil__relativedelta_core__001"): {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "data_structure_semantics;return_value",
        "contract_clause_ids": "B002;B005",
        "evidence_summary": "relativedelta difference mode folds leftover days into seconds and leaves days at 0 instead of keeping calendar days.",
    },
    ("gpt-oss-120b", "voluptuous__schema_validate_core__001"): {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "return_value;validation_boundary",
        "contract_clause_ids": "B004",
        "evidence_summary": "MultipleInvalid error paths list nested keys in a different sequence than the required aggregated failure paths.",
    },
    ("gpt-oss-120b", "email_validator__validate_core__001"): {
        "root_cause_primary": "packaging_modularization",
        "secondary_tags": "packaging_export",
        "contract_clause_ids": "B010",
        "evidence_summary": "Behavior gates passed; isolation fails because validate_email.py imports the forbidden extra module dns.",
    },
    ("gpt-oss-120b", "arrow__parse_format_core__001"): {
        "root_cause_primary": "contract_api_completion",
        "secondary_tags": "api_surface",
        "contract_clause_ids": "B001;B005",
        "evidence_summary": "get() returns an Arrow with year/month/day but no hour attribute, so the ISO datetime case cannot be observed.",
    },
    ("gpt-oss-120b", "cattrs__structure_core__001"): {
        "root_cause_primary": "contract_api_completion",
        "secondary_tags": "data_structure_semantics;call_signature",
        "contract_clause_ids": "B001;B002",
        "evidence_summary": "Converter.unstructure works, but structure hits TypeError from isinstance() on string field annotations instead of round-tripping the attrs instance.",
    },
    ("gpt-oss-120b", "dataclasses_json__serde_core__001"): {
        "root_cause_primary": "behavior_drift",
        "secondary_tags": "serialization_rendering;parsing_normalization",
        "contract_clause_ids": "B002;B003",
        "evidence_summary": "config(field_name=...) is ignored; to_dict emits given_name instead of givenName.",
    },
    ("gpt-oss-120b", "jinja2__lexer_parser_core__001"): {
        "root_cause_primary": "contract_api_completion",
        "secondary_tags": "api_surface;data_structure_semantics",
        "contract_clause_ids": "B002;B005",
        "evidence_summary": "Environment.parse returns a Template node that has no body attribute, so variable-output AST navigation cannot start.",
    },
    ("gpt-oss-120b", "redis__resp_parser_core__001"): {
        "root_cause_primary": "contract_api_completion",
        "secondary_tags": "api_surface",
        "contract_clause_ids": "B001;B006",
        "evidence_summary": "_RESP2Parser is exported but has no on_connect, so RESP2 simple/bulk replies cannot be fed to the parser.",
    },
}


def leak_check(text: str, task_id: str) -> None:
    if re.search(r"hidden_tests/|test_hidden|::test_", text or ""):
        raise ValueError(f"{task_id}: annotation exposes a private test identifier")


def evidence_path(model: str, task_id: str, stage: str) -> str:
    rel = SUITES[model]
    suffix = STAGE_LOG.get(stage, "eval/result.json")
    path = ROOT / rel / task_id / suffix
    if not path.is_file():
        alt = ROOT / rel / task_id / "eval/result.json"
        if alt.is_file():
            return f"{rel}/{task_id}/eval/result.json"
        alt2 = ROOT / rel / task_id / "eval/logs/build.stdout"
        if alt2.is_file():
            return f"{rel}/{task_id}/eval/logs/build.stdout"
    return f"{rel}/{task_id}/{suffix}"


def spec_for(model: str, task_id: str, stage: str) -> dict[str, str]:
    if (model, task_id) in BY_KEY:
        return dict(BY_KEY[(model, task_id)])
    if task_id in DEFECTS and stage in {"public_failure", "hidden_failure"}:
        # Known public-clause clashes. Readme/build is NOT this defect (see BY_KEY).
        if task_id == "readme_renderer__content_type_core__hard3_001" and stage != "public_failure":
            raise KeyError(task_id)
        return dict(DEFECTS[task_id])
    raise KeyError(f"unlabeled {(model, task_id)}")


def main() -> None:
    data = json.loads(PACKETS.read_text(encoding="utf-8"))
    meta_by = {}
    with ROWS.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            meta_by[(row["model"], row["task_id"])] = row
    proc = {}
    if PROCESS.is_file():
        for row in json.loads(PROCESS.read_text(encoding="utf-8")).get("rows") or []:
            proc[(row["model"], row["task_id"])] = row

    out_rows = []
    for packet in data["packets"]:
        model = packet["model"]
        task_id = packet["task_id"]
        stage = packet["first_failure_stage"]
        spec = spec_for(model, task_id, stage)
        cause = spec["root_cause_primary"]
        if cause not in VALID_CAUSES:
            raise ValueError(f"{task_id}: bad cause {cause}")
        override = spec.get("validity_override", "")
        reason = spec.get("validity_reason", "")
        if cause == "task_or_evaluator_defect" and override != "benchmark_invalid_candidate":
            raise ValueError(f"{task_id}: defect requires override")
        leak_check(spec["evidence_summary"], task_id)
        leak_check(reason, task_id)
        row_meta = meta_by[(model, task_id)]
        eligibility = override or "valid_agent_evidence"
        out_rows.append(
            {
                "task_id": task_id,
                "model": model,
                "split": "python150",
                "lift_type": row_meta.get("lift_type") or "",
                "feature_family": row_meta.get("feature_family") or "",
                "evidence_eligibility": eligibility,
                "functional_pass": "false",
                "first_failure_stage": stage,
                "root_cause_primary": cause,
                "secondary_tags": spec.get("secondary_tags", ""),
                "contract_clause_ids": spec.get("contract_clause_ids", ""),
                "context_violation": row_meta.get("process_context_violation") or "False",
                "evidence_summary": spec["evidence_summary"].strip(),
                "evidence_path": evidence_path(model, task_id, stage),
                "review_status": "assistant_first_pass",
                "annotator": "assistant_first_pass",
                "adjudicated": "false",
                "independent_human_review": "false",
                "validity_override": override,
                "validity_reason": reason,
                "close_read_tier": "L1",
                "sample_kind": "stratified_postsample",
                "process_tag": (proc.get((model, task_id)) or {}).get("process_tag") or "",
            }
        )

    csv_path = OUT / "postsample_annotations.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(out_rows[0]))
        writer.writeheader()
        writer.writerows(out_rows)

    valid = [r for r in out_rows if r["evidence_eligibility"] == "valid_agent_evidence"]
    defects = [r for r in out_rows if r["evidence_eligibility"] == "benchmark_invalid_candidate"]
    by_cause = Counter(r["root_cause_primary"] for r in valid)
    by_model = {}
    for r in valid:
        by_model.setdefault(r["model"], Counter())[r["root_cause_primary"]] += 1
    by_stage = Counter(r["first_failure_stage"] for r in valid)
    summary = {
        "schema_version": "featureliftbench.failure_analysis.v1",
        "split": "python150",
        "kind": "stratified_postsample",
        "seed": data.get("seed"),
        "models": ["gpt-5.6-luna", "qwen3.6-35b-a3b-fp8", "gpt-oss-120b"],
        "review_status": "assistant_first_pass",
        "independent_human_review": False,
        "n_annotated": len(out_rows),
        "n_valid_agent": len(valid),
        "n_benchmark_invalid_candidate": len(defects),
        "defect_task_ids": sorted({r["task_id"] for r in defects}),
        "root_cause_valid_agent": dict(sorted(by_cause.items())),
        "root_cause_valid_agent_by_model": {
            model: dict(sorted(counts.items())) for model, counts in sorted(by_model.items())
        },
        "valid_by_first_failure_stage": dict(sorted(by_stage.items())),
        "closure_n": sum(by_cause[c] for c in CLOSURE),
        "localization_n": by_cause["localization"],
        "packaging_n": by_cause["packaging_modularization"],
        "unknown_n": by_cause["unknown"],
        "dependency_closure_n": by_cause["dependency_closure"],
        "close_read_tier": "L1",
        "caveats": [
            "Stratified sample of Luna/Qwen/OSS artifact failures, not a census. Do not merge into the Pro+Flash 67 denominator.",
            "Known public-clause defects were included when those tasks artifact-failed; readme/build failures are agent causes, not the markdown-marker defect.",
            "flake8 register_options and setuptools_scm default-node vs public 1.2.3 were recoded as defects after Luna close-read; also applied to the Pro+Flash census.",
            "Qwen pytest Hidden-only is the same B003 vs public-strip clash and is excluded.",
            "L1 assistant_first_pass; not L2.",
        ],
    }
    (OUT / "f3_postsample_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print("wrote", csv_path)


if __name__ == "__main__":
    main()
