#!/usr/bin/env python3
"""Build the auditable task-level taxonomy for the 150 Python main tasks.

The table deliberately contains only task-intrinsic evidence from metadata,
oracle manifests, source snapshots, and public/hidden tests.  Agent trajectories,
submissions, and evaluation outcomes are never read by this script.

Semantic labels are frozen in explicit source/task maps after a 20-task trial
audit.  Structural metrics and behavioral-risk tags are recomputed from files.
Unknown measurements are written as ``NA`` rather than inferred from outcomes.
"""

from __future__ import annotations

import argparse
import ast
import csv
import json
import re
import sys
import warnings
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


HARNESS_ROOT = Path(__file__).resolve().parents[2] / "harness"
if str(HARNESS_ROOT) not in sys.path:
    sys.path.insert(0, str(HARNESS_ROOT))

from featureliftbench.closure_gold import load_closure_gold  # noqa: E402


TAXONOMY_VERSION = "v1"
NA = "NA"

REPO_ARCHETYPES = {
    "library",
    "framework_plugin",
    "developer_tooling",
    "application_service",
}
REPO_PROVENANCE = {"real_oss_mature", "real_oss_legacy", "curated_vibe"}
REPO_DOMAINS = {
    "parsing",
    "data_modeling",
    "testing",
    "configuration",
    "packaging",
    "networking",
    "general_utility",
    "application",
}
FEATURE_FAMILIES = {
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
}
FEATURE_STATEFULNESS = {
    "stateless",
    "local_state",
    "session_state",
    "global_state",
    "lifecycle_state",
}
ENTANGLEMENT_MECHANISMS = {
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
}
BEHAVIORAL_RISKS = {
    "exception_semantics",
    "ordering_semantics",
    "boundary_cases",
    "mutation_side_effects",
    "lifecycle_semantics",
    "platform_variation",
}
CODEBASE_CONDITIONS = {
    "legacy_clutter",
    "duplicated_implementation",
    "dead_code_distractors",
    "generated_code",
    "weak_module_boundaries",
}

FIELDNAMES = (
    "task_id",
    "split",
    "source_repo",
    "source_commit",
    "source_group_id",
    "repo_archetype_primary",
    "repo_archetype_secondary",
    "repo_provenance",
    "repo_domain_primary",
    "repo_domain_secondary",
    "feature_family_primary",
    "feature_family_secondary",
    "feature_statefulness",
    "entanglement_primary_original",
    "entanglement_types_original",
    "normalized_entanglement_types",
    "behavioral_risk_tags",
    "codebase_condition_tags",
    "reference_file_count",
    "reference_symbol_count",
    "reference_loc",
    "source_entrypoint_count",
    "direct_internal_dependency_count",
    "transitive_internal_dependency_count",
    "external_dependency_count",
    "static_file_closure_depth",
    "resource_file_count",
    "has_dynamic_import",
    "has_global_state",
    "has_registry",
    "has_framework_lifecycle",
    "adapter_required",
    "public_test_count",
    "hidden_test_count",
    "classification_evidence",
    "classification_confidence",
    "review_status",
    "taxonomy_version",
)


# Trial tasks were deliberately drawn from different upstream repositories and
# every original primary entanglement type.  The final specification records
# the ambiguities found and the resulting label decisions.
TRIAL_TASK_IDS = {
    "alembic__revision_map_core__hard3_001",
    "attrs__validators_core__001",
    "babel__plural_core__001",
    "build__pyproject_backend_core__hard3_001",
    "celery__signal_dispatch_core__hard3_001",
    "coverage__config_merge_core__001",
    "dynaconf__settings_merge_core__001",
    "h11__message_parse_core__001",
    "importlib_resources__traversable_tree_core__hard3_001",
    "jinja2__lexer_parser_core__001",
    "keyring__backend_select_core__hard3_001",
    "lark__grammar_loader_core__001",
    "networkx__dag_topo_core__001",
    "phonenumbers__parse_format_core__001",
    "pluggy__hook_call_order__001",
    "pydantic_v1__validation_error_core__001",
    "requests_cache__cache_key_core__hard3_001",
    "sqlparse__parse_format_core__001",
    "vibe_app__plugin_registry_core__001",
    "yarl__url_model_core__001",
}


# Source-level labels are explicit and exhaustive.  Domain labels describe the
# upstream repository, not the feature selected by a particular task.
SOURCE_DOMAINS: dict[str, tuple[str, ...]] = {
    "parsing": (
        "arrow", "astroid", "bleach", "chameleon", "croniter", "email-validator",
        "isodate", "jinja2", "json5", "jsonpath-ng", "jsonpointer", "lark",
        "license_expression", "mako", "Markdown", "markdown-it-py", "msgpack-python",
        "parsel", "parso", "pendulum", "pygments", "python-frontmatter",
        "python-multipart", "PyYAML", "rfc3986", "rich", "ruamel.yaml", "sqlparse",
        "tomlkit", "xmltodict",
    ),
    "data_modeling": (
        "attrs", "cattrs", "cerberus", "dataclasses-json", "jsonschema", "marshmallow",
        "pydantic", "referencing", "schema", "trafaret", "voluptuous", "yamale",
    ),
    "testing": ("coveragepy", "pytest", "responses"),
    "configuration": (
        "click", "configobj", "dynaconf", "environs", "isort", "jupyter_core",
        "pathvalidate", "platformdirs", "pydantic-settings", "python-box", "python-dotenv",
        "tox", "virtualenv",
    ),
    "packaging": (
        "build", "distlib", "hatch", "importlib_metadata", "importlib_resources",
        "installer", "packaging", "poetry_core", "readme_renderer", "setuptools_scm", "wheel",
    ),
    "networking": (
        "aiohttp", "h11", "h2", "httpx", "redis", "requests_cache", "starlette",
        "urllib3", "websockets", "werkzeug", "wsproto", "yarl",
    ),
    "application": (
        "alembic", "celery", "jupyter_server", "mkdocs", "pyramid", "scrapy", "sphinx",
        "sqlalchemy", "vibe_app",
    ),
    "general_utility": (
        "apscheduler", "babel", "bidict", "boltons", "cachetools", "cookiecutter", "dateutil",
        "deepdiff", "diskcache", "Faker", "flake8", "fs", "fsspec", "glom", "humanize",
        "intervaltree", "json_logic", "keyring", "multidict", "networkx", "passlib",
        "phonenumbers", "pluggy", "python-dateutil", "returns", "sortedcontainers", "stevedore",
        "tabulate", "tenacity", "transitions", "typer",
    ),
}

DEVELOPER_TOOLING_SOURCES = {
    "alembic", "astroid", "build", "cookiecutter", "coveragepy", "distlib", "flake8",
    "hatch", "installer", "isort", "jupyter_core", "mkdocs", "packaging", "poetry_core",
    "pytest", "readme_renderer", "setuptools_scm", "sphinx", "tox", "virtualenv", "wheel",
}
FRAMEWORK_PLUGIN_SOURCES = {
    "celery", "jinja2", "keyring", "pluggy", "pyramid", "scrapy", "sqlalchemy", "starlette",
    "stevedore", "werkzeug",
}
APPLICATION_SERVICE_SOURCES = {"jupyter_server", "vibe_app"}

REPO_DOMAIN_SECONDARY: dict[str, tuple[str, ...]] = {
    "coveragepy": ("configuration",),
    "pytest": ("configuration",),
    "packaging": ("parsing",),
    "jinja2": ("general_utility",),
    "requests_cache": ("general_utility",),
    "vibe_app": ("configuration",),
    "starlette": ("application",),
    "werkzeug": ("application",),
}


# Feature-family labels are task-level and explicit.  Grouping the IDs by label
# makes overlaps and omissions machine-checkable at build time.
FEATURE_GROUPS: dict[str, tuple[str, ...]] = {
    "parse_tokenize_decode": (
        "arrow__parse_format_core__001", "astroid__nodes_core__001", "click__option_parser__001",
        "email_validator__validate_core__001", "isodate__duration_parse_core__001",
        "jinja2__lexer_parser_core__001", "json5__parse_core__001",
        "jsonpath_ng__expression_eval_core__001", "jsonpointer__resolve_core__001",
        "lark__parse_tree_core__001", "license_expression__policy_core__hard3_001",
        "mako__lexer_expression_core__001", "markdown__extensions_core__001",
        "markdown_it__commonmark_render__001", "packaging__requirement_marker_specifier__001",
        "parsel__selector_namespace_core__hard3_001", "parso__python_parse_core__001",
        "pendulum__parse_format_core__001", "phonenumbers__parse_format_core__001",
        "pygments__lexer_core__001", "pytest__mark_expression_core__001",
        "python_multipart__form_parse_core__001", "rfc3986__uri_parse_core__001",
        "rich__markup_parse_core__001", "sqlparse__parse_format_core__001",
        "sqlparse__parse_split_core__001", "sqlparse__token_tree_core__001",
        "tox__factor_expression_core__hard3_001", "virtualenv__interpreter_spec_core__hard3_001",
        "yarl__url_model_core__001",
    ),
    "protocol_state_transition": (
        "apscheduler__cron_trigger_core__hard3_001", "croniter__cron_parse_core__001",
        "h11__message_parse_core__001", "h2__frame_parse_core__001",
        "python_dateutil__rrule_core__001", "redis__resp_parser_core__001",
        "transitions__state_machine_core__hard3_001", "websockets__handshake_parse_core__001",
        "wsproto__frame_parse_core__001",
    ),
    "validate_normalize_construct": (
        "aiohttp__url_params_core__hard3_001", "attrs__validators_core__001",
        "bleach__sanitize_core__001", "build__pyproject_backend_core__hard3_001",
        "cerberus__schema_validate_core__001", "httpx__request_model_core__001",
        "jsonschema__validator_core__001", "passlib__hash_context_core__001",
        "pathvalidate__sanitize_core__001", "pydantic__field_validator_core__hard3_001",
        "pydantic_v1__validation_error_core__001", "schema__nested_validate_core__hard3_001",
        "trafaret__validation_rules_core__hard3_001", "voluptuous__schema_validate_core__001",
        "yamale__schema_validate_core__hard3_001",
    ),
    "serialize_format_render": (
        "cattrs__structure_core__001", "chameleon__template_compile_core__001",
        "coverage__report_core__001", "dataclasses_json__serde_core__001",
        "humanize__naturaltime_core__001", "jinja2__compile_render_core__001",
        "marshmallow__schema_core__001", "msgpack__pack_unpack_core__001",
        "pygments__formatter_core__001", "python_frontmatter__roundtrip_core__001",
        "pyyaml__safe_load_dump__001", "readme_renderer__content_type_core__hard3_001",
        "ruamel_yaml__roundtrip_core__001", "sqlparse__format_filters_core__001",
        "tabulate__table_format_core__001", "tomlkit__roundtrip_document__001",
        "vibe_app__orm_query_ast_core__001", "xmltodict__xml_parse_core__001",
    ),
    "registry_plugin_dispatch": (
        "celery__signal_dispatch_core__hard3_001", "click__lazy_command_core__hard3_001",
        "flake8__plugin_options_core__hard3_001", "fs__url_opener_core__hard3_001",
        "jinja2__extensions_core__001", "jinja2__filters_tests_core__001",
        "jupyter_server__extension_config_core__hard3_001", "keyring__backend_select_core__hard3_001",
        "mkdocs__plugin_config_core__hard3_001", "pluggy__hook_call_order__001",
        "pluggy__hook_specs_core__001", "pluggy__hook_wrapper_core__hard3_001",
        "pytest__fixture_resolve_core__001", "pytest__marker_registry_core__hard3_001",
        "responses__request_matcher_core__hard3_001", "scrapy__item_loader_core__hard3_001",
        "sphinx__extension_registry_core__hard3_001", "sqlalchemy__event_dispatch_core__hard3_001",
        "starlette__route_matching_core__hard3_001", "stevedore__extension_manager_core__hard3_001",
        "vibe_app__plugin_registry_core__001", "werkzeug__routing_core__001",
    ),
    "config_resolve_discover": (
        "configobj__roundtrip_config_core__001", "cookiecutter__repo_finder_core__hard3_001",
        "coverage__config_merge_core__001", "coverage__glob_matcher_core__001",
        "coverage__path_remap_core__001", "coverage__source_selection_core__001",
        "dynaconf__settings_merge_core__001", "environs__typed_env_core__001",
        "fsspec__url_chain_core__hard3_001", "isort__settings_resolver_core__hard3_001",
        "jupyter_core__paths_resolver_core__hard3_001", "platformdirs__app_dirs_core__hard3_001",
        "pydantic_settings__env_source_core__001", "pytest__ini_markers_core__001",
        "python_box__config_box_core__001", "python_dotenv__env_parse_core__001",
        "referencing__json_schema_refs_core__001", "vibe_app__yaml_config_bootstrap__001",
    ),
    "resource_metadata_loading": (
        "dateutil__zone_resolver_core__hard3_001", "distlib__wheel_metadata_core__hard3_001",
        "faker__provider_core__001", "hatch__project_metadata_core__hard3_001",
        "importlib_metadata__entry_points_core__001",
        "importlib_resources__traversable_tree_core__hard3_001",
        "installer__wheel_record_core__hard3_001", "jinja2__loader_inheritance_core__001",
        "lark__grammar_loader_core__001", "poetry_core__dependency_groups_core__hard3_001",
        "setuptools_scm__version_normalize_core__hard3_001",
        "wheel__metadata_normalize_core__hard3_001",
    ),
    "algorithm_data_structure": (
        "alembic__revision_map_core__hard3_001", "bidict__bidirectional_map_core__001",
        "boltons__iterutils_core__001", "deepdiff__deep_compare_core__001",
        "intervaltree__interval_tree_core__001", "lark__visitor_transform_core__001",
        "multidict__multidict_mutation_core__hard3_001", "networkx__dag_topo_core__001",
        "python_dateutil__relativedelta_core__001", "sortedcontainers__sorted_list_core__001",
    ),
    "cache_retry_policy": (
        "babel__plural_core__001", "cachetools__cache_eviction_core__001",
        "diskcache__eviction_policy_core__hard3_001", "glom__spec_eval_core__hard3_001",
        "json_logic__evaluator_core__hard3_001", "pytest__skipif_eval_core__001",
        "requests_cache__cache_key_core__hard3_001", "tenacity__retry_state_core__hard3_001",
        "urllib3__retry_backoff_core__001", "vibe_app__pricing_rules_core__001",
        "vibe_app__rules_engine_core__001",
    ),
    "workflow_session_orchestration": (
        "pyramid__configurator_action_core__hard3_001", "returns__result_pipeline_core__hard3_001",
        "typer__command_parser_core__001", "vibe_app__csv_transform_core__001",
        "vibe_app__session_registry_core__001",
    ),
}

FEATURE_SECONDARY: dict[str, tuple[str, ...]] = {
    "arrow__parse_format_core__001": ("serialize_format_render",),
    "astroid__nodes_core__001": ("algorithm_data_structure",),
    "chameleon__template_compile_core__001": ("parse_tokenize_decode",),
    "click__option_parser__001": ("workflow_session_orchestration",),
    "croniter__cron_parse_core__001": ("parse_tokenize_decode",),
    "h11__message_parse_core__001": ("parse_tokenize_decode",),
    "h2__frame_parse_core__001": ("parse_tokenize_decode",),
    "importlib_metadata__entry_points_core__001": ("registry_plugin_dispatch",),
    "isodate__duration_parse_core__001": ("serialize_format_render",),
    "jinja2__loader_inheritance_core__001": ("serialize_format_render",),
    "license_expression__policy_core__hard3_001": ("cache_retry_policy",),
    "markdown__extensions_core__001": ("registry_plugin_dispatch",),
    "markdown_it__commonmark_render__001": ("serialize_format_render",),
    "marshmallow__schema_core__001": ("validate_normalize_construct",),
    "pendulum__parse_format_core__001": ("serialize_format_render",),
    "phonenumbers__parse_format_core__001": ("serialize_format_render",),
    "poetry_core__dependency_groups_core__hard3_001": ("config_resolve_discover",),
    "pyramid__configurator_action_core__hard3_001": ("registry_plugin_dispatch",),
    "python_dotenv__env_parse_core__001": ("parse_tokenize_decode",),
    "python_frontmatter__roundtrip_core__001": ("parse_tokenize_decode",),
    "pyyaml__safe_load_dump__001": ("serialize_format_render",),
    "sqlparse__format_filters_core__001": ("parse_tokenize_decode",),
    "sqlparse__parse_format_core__001": ("serialize_format_render",),
    "tenacity__retry_state_core__hard3_001": ("protocol_state_transition",),
    "tomlkit__roundtrip_document__001": ("parse_tokenize_decode",),
    "typer__command_parser_core__001": ("parse_tokenize_decode",),
    "vibe_app__session_registry_core__001": ("registry_plugin_dispatch",),
    "xmltodict__xml_parse_core__001": ("parse_tokenize_decode",),
}

# These cases retain a v1 label but are genuinely cross-family/domain and need
# a human domain-expert adjudication before a paper uses the exact label.
NEEDS_REVIEW_TASKS = {
    "aiohttp__url_params_core__hard3_001",
    "alembic__revision_map_core__hard3_001",
    "build__pyproject_backend_core__hard3_001",
    "coverage__glob_matcher_core__001",
    "coverage__path_remap_core__001",
    "fs__url_opener_core__hard3_001",
    "glom__spec_eval_core__hard3_001",
    "jinja2__filters_tests_core__001",
    "lark__visitor_transform_core__001",
    "parsel__selector_namespace_core__hard3_001",
    "pyramid__configurator_action_core__hard3_001",
    "referencing__json_schema_refs_core__001",
    "starlette__route_matching_core__hard3_001",
    "werkzeug__routing_core__001",
    "wheel__metadata_normalize_core__hard3_001",
}

# v1.1 AI-assisted adjudication.  These overrides are based only on task
# metadata, source entrypoints, source snapshots, and tests; no trajectory or
# evaluation outcome is used.  The status is intentionally distinct from a
# human adjudication and remains subject to paper-release double review.
AI_REVIEW_OVERRIDES: dict[str, dict[str, str]] = {
    "aiohttp__url_params_core__hard3_001": {
        "has_global_state": "false", "has_registry": "false",
    },
    "alembic__revision_map_core__hard3_001": {},
    "build__pyproject_backend_core__hard3_001": {
        "has_registry": "false", "has_framework_lifecycle": "false",
    },
    "coverage__glob_matcher_core__001": {
        "normalized_entanglement_types": "config_environment;implicit_runtime_dependency;static_transitive_dependency",
        "has_dynamic_import": "false", "has_global_state": "false", "has_registry": "false",
    },
    "coverage__path_remap_core__001": {
        "normalized_entanglement_types": "config_environment;implicit_runtime_dependency;static_transitive_dependency",
        "has_dynamic_import": "false", "has_global_state": "false", "has_registry": "false",
        "has_framework_lifecycle": "false",
    },
    "fs__url_opener_core__hard3_001": {"static_file_closure_depth": "1"},
    "glom__spec_eval_core__hard3_001": {
        "feature_family_primary": "algorithm_data_structure",
        "feature_statefulness": "local_state",
        "has_registry": "false",
    },
    "jinja2__filters_tests_core__001": {
        "feature_family_primary": "serialize_format_render",
        "feature_family_secondary": "registry_plugin_dispatch",
        "feature_statefulness": "local_state",
    },
    "lark__visitor_transform_core__001": {},
    "parsel__selector_namespace_core__hard3_001": {"has_framework_lifecycle": "false"},
    "pyramid__configurator_action_core__hard3_001": {},
    "referencing__json_schema_refs_core__001": {"feature_statefulness": "local_state"},
    "starlette__route_matching_core__hard3_001": {"feature_statefulness": "local_state"},
    "werkzeug__routing_core__001": {
        "feature_statefulness": "local_state", "has_dynamic_import": "false", "has_global_state": "false",
    },
    "wheel__metadata_normalize_core__hard3_001": {"has_registry": "false"},
}

AI_REVIEW_RATIONALES = {
    "aiohttp__url_params_core__hard3_001": "URL/header helpers are stateless; module constants are not mutable global state or a registry.",
    "alembic__revision_map_core__hard3_001": "RevisionMap is a local graph/data-structure closure; existing cross-family labels remain the best fit.",
    "build__pyproject_backend_core__hard3_001": "The extracted table parser validates data and does not execute backend registry lifecycle.",
    "coverage__glob_matcher_core__001": "Glob compilation uses platform/config semantics but no dynamic plugin loading, packaged resource, or mutable registry.",
    "coverage__path_remap_core__001": "PathAliases is instance-local path/config logic; shared utilities do not imply plugin or framework lifecycle.",
    "fs__url_opener_core__hard3_001": "The registry entrypoint depends on the parser file, giving a one-edge static closure.",
    "glom__spec_eval_core__hard3_001": "Spec evaluation is a local recursive data-structure interpreter, not a cache/retry policy.",
    "jinja2__filters_tests_core__001": "Rendering/filter application is primary; mutable Environment filter/test registries are secondary and instance-local.",
    "lark__visitor_transform_core__001": "Tree visitor/transformer remains a local-state algorithm with parser closure.",
    "parsel__selector_namespace_core__hard3_001": "Namespace registration is instance-local selector state, not framework lifecycle.",
    "pyramid__configurator_action_core__hard3_001": "Action commit/conflict resolution is lifecycle orchestration with registry semantics.",
    "referencing__json_schema_refs_core__001": "Registry/Resolver objects carry immutable-local resolution state across chained lookups.",
    "starlette__route_matching_core__hard3_001": "Route matching mutates/reads Router instance state but does not require application startup lifecycle.",
    "werkzeug__routing_core__001": "Map/MapAdapter state is instance-local; converter tables do not require dynamic imports or mutable global state.",
    "wheel__metadata_normalize_core__hard3_001": "Metadata normalization and filename parsing do not implement a registry.",
}


ORIGINAL_ENTANGLEMENT_MAP = {
    "implicit_dependency_coupling": "implicit_runtime_dependency",
    "data_model_coupling": "data_model_invariant",
    "parser_state_coupling": "parser_state",
    "framework_coupling": "framework_lifecycle",
    "global_state_registry_coupling": "global_state_registry",
    "config_environment_coupling": "config_environment",
    "resource_coupling": "resource_packaging",
    "third_party_dependency_coupling": "third_party_contract",
}

GLOBAL_STATE_FEATURES = {
    "celery__signal_dispatch_core__hard3_001", "faker__provider_core__001",
    "pytest__marker_registry_core__hard3_001", "vibe_app__csv_transform_core__001",
    "vibe_app__orm_query_ast_core__001", "vibe_app__plugin_registry_core__001",
    "vibe_app__pricing_rules_core__001", "vibe_app__rules_engine_core__001",
    "vibe_app__session_registry_core__001", "vibe_app__yaml_config_bootstrap__001",
}
SESSION_STATE_FEATURES = {
    task_id
    for task_id in FEATURE_GROUPS["protocol_state_transition"]
} | {
    "tenacity__retry_state_core__hard3_001", "vibe_app__session_registry_core__001",
}
LIFECYCLE_STATE_FEATURES = set(FEATURE_GROUPS["registry_plugin_dispatch"]) | {
    "pydantic_v1__validation_error_core__001", "pyramid__configurator_action_core__hard3_001",
}


RISK_PATTERNS: dict[str, re.Pattern[str]] = {
    "exception_semantics": re.compile(
        r"pytest\.raises|assert_raises|\b(error|exception|invalid|failure|missing|required|conflict)\b",
        re.IGNORECASE,
    ),
    "ordering_semantics": re.compile(
        r"\b(order|ordering|ordered|sort|sorted|priority|precedence|before|after|first|last|stable|head)\w*\b",
        re.IGNORECASE,
    ),
    "boundary_cases": re.compile(
        r"\b(empty|none|null|zero|boundary|edge|overflow|underflow|unknown|missing|min|max)\w*\b",
        re.IGNORECASE,
    ),
    "mutation_side_effects": re.compile(
        r"\b(mutat|update|set_|delete|remove|append|pop|clear|inplace|side_effect|counter|global_state)\w*\b",
        re.IGNORECASE,
    ),
    "lifecycle_semantics": re.compile(
        r"\b(register|unregister|setup|teardown|enable|disable|start|stop|close|enter|exit|hook|wrapper|lifecycle)\w*\b",
        re.IGNORECASE,
    ),
    "platform_variation": re.compile(
        r"os\.environ|setenv|delenv|sys\.platform|platform\.|\b(windows|win32|posix|linux|darwin|home_dir|xdg)\b",
        re.IGNORECASE,
    ),
}

DYNAMIC_PATTERN = re.compile(
    r"__import__|importlib\.import_module|import_module|entry[_ ]?points?|iter_entry_points|load_entry_point",
    re.IGNORECASE,
)
DYNAMIC_METADATA_PATTERN = re.compile(
    r"dynamic (?:import|dependency|loading)|entry point (?:discovery|selection|loading)|"
    r"plugin discovery|lazy import",
    re.IGNORECASE,
)
REGISTRY_PATTERN = re.compile(
    r"\b(registry|register|plugin|hook|entry[_ ]?point|signal|extension)\w*\b",
    re.IGNORECASE,
)
LIFECYCLE_PATTERN = re.compile(
    r"\b(setup|teardown|register|unregister|enable|disable|start|stop|close|initialize|lifecycle|wrapper)\w*\b",
    re.IGNORECASE,
)
ADAPTER_PATTERN = re.compile(r"\b(adapter|required shim|compatibility shim|facade)\b", re.IGNORECASE)


@dataclass
class SourceAnalysis:
    entry_files: list[Path]
    scope_files: list[Path]
    direct_internal_dependency_count: int | str
    transitive_internal_dependency_count: int | str
    external_dependency_count: int | str
    static_file_closure_depth: int | str
    has_dynamic_import: bool | str
    has_global_state: bool | str
    has_registry: bool | str
    source_evidence: list[Path]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="FeatureLiftBench repository root",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/research_analysis/python150_task_taxonomy.csv"),
        help="CSV output path, relative to --repo-root unless absolute",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("docs/research_analysis/BENCHMARK_TAXONOMY_REPORT.md"),
        help="Markdown report output path, relative to --repo-root unless absolute",
    )
    parser.add_argument("--strict", action="store_true", help="fail on any audit invariant violation")
    return parser.parse_args(argv)


def resolve_output(root: Path, path: Path) -> Path:
    return path if path.is_absolute() else root / path


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def flatten_feature_map() -> dict[str, str]:
    result: dict[str, str] = {}
    for family, task_ids in FEATURE_GROUPS.items():
        if family not in FEATURE_FAMILIES:
            raise ValueError(f"unknown feature family: {family}")
        for task_id in task_ids:
            if task_id in result:
                raise ValueError(f"feature task assigned twice: {task_id}")
            result[task_id] = family
    return result


def flatten_source_domains() -> dict[str, str]:
    result: dict[str, str] = {}
    for domain, sources in SOURCE_DOMAINS.items():
        if domain not in REPO_DOMAINS:
            raise ValueError(f"unknown repository domain: {domain}")
        for source in sources:
            if source in result:
                raise ValueError(f"source assigned to two domains: {source}")
            result[source] = domain
    return result


def repo_archetype(source: str) -> str:
    if source in APPLICATION_SERVICE_SOURCES:
        return "application_service"
    if source in FRAMEWORK_PLUGIN_SOURCES:
        return "framework_plugin"
    if source in DEVELOPER_TOOLING_SOURCES:
        return "developer_tooling"
    return "library"


def repo_provenance(source: str, metadata: dict[str, Any]) -> str:
    if source == "vibe_app":
        return "curated_vibe"
    # v1 does not infer project age or maintenance from reputation.  A pinned
    # upstream URL/commit without an explicit legacy flag uses the benchmark's
    # nominal real_oss_mature bucket; real_oss_legacy remains intentionally empty.
    tags = {str(tag).lower() for tag in metadata.get("tags") or []}
    return "real_oss_legacy" if "real_oss_legacy" in tags else "real_oss_mature"


def task_python_files(directory: Path) -> list[Path]:
    if not directory.is_dir():
        return []
    return [
        path
        for path in sorted(directory.rglob("*.py"))
        if ".pytest_cache" not in path.parts and "__pycache__" not in path.parts
    ]


def parse_python(path: Path) -> ast.Module | None:
    text = path.read_text(encoding="utf-8", errors="replace")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SyntaxWarning)
        try:
            return ast.parse(text)
        except SyntaxError:
            return None


def count_static_tests(directory: Path) -> int:
    count = 0
    for path in task_python_files(directory):
        tree = parse_python(path)
        if tree is None:
            continue
        count += sum(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test")
            for node in ast.walk(tree)
        )
    return count


def oracle_entries(oracle: dict[str, Any]) -> list[str]:
    values = oracle.get("required_source_files")
    if not isinstance(values, list) or not values:
        values = oracle.get("source_files")
    return [str(value) for value in values if isinstance(value, str)] if isinstance(values, list) else []


def resolve_oracle_entry(task_dir: Path, raw: str) -> Path | None:
    candidates = [task_dir / raw, task_dir / "repo" / raw]
    if raw.startswith("repo/"):
        candidates.insert(0, task_dir / raw)
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def expand_oracle_files(task_dir: Path, entries: list[str]) -> tuple[list[Path], bool]:
    files: list[Path] = []
    all_resolved = True
    for raw in entries:
        path = resolve_oracle_entry(task_dir, raw)
        if path is None:
            all_resolved = False
            continue
        if path.is_dir():
            files.extend(item for item in sorted(path.rglob("*")) if item.is_file())
        elif path.is_file():
            files.append(path)
    return sorted(set(files)), all_resolved


def physical_python_loc(paths: Iterable[Path]) -> int:
    total = 0
    for path in paths:
        if path.suffix != ".py":
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        total += sum(bool(line.strip()) for line in text.splitlines())
    return total


def explicit_reference_symbol_count(oracle: dict[str, Any]) -> int | str:
    for key in ("target_symbols", "target_api"):
        values = oracle.get(key)
        if isinstance(values, list) and values:
            return len({str(value) for value in values})
    return NA


def module_variants(path: Path, repo_dir: Path) -> set[str]:
    try:
        rel = path.relative_to(repo_dir).with_suffix("")
    except ValueError:
        return set()
    parts = list(rel.parts)
    starts = {0}
    for marker in ("src", "lib", "python"):
        if marker in parts:
            starts.add(parts.index(marker) + 1)
    variants: set[str] = set()
    for start in starts:
        selected = parts[start:]
        if selected and selected[-1] == "__init__":
            selected = selected[:-1]
        if selected:
            variants.add(".".join(selected))
    return variants


def build_module_index(repo_dir: Path) -> tuple[dict[str, Path], dict[Path, str]]:
    index: dict[str, Path] = {}
    canonical: dict[Path, str] = {}
    for path in task_python_files(repo_dir):
        variants = module_variants(path, repo_dir)
        for module in sorted(variants, key=len, reverse=True):
            index.setdefault(module, path)
        if variants:
            canonical[path] = max(variants, key=lambda value: (value.count("."), len(value)))
    return index, canonical


def top_level_symbols(path: Path) -> set[str]:
    tree = parse_python(path)
    if tree is None:
        return set()
    symbols: set[str] = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            symbols.add(node.name)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Name):
                    symbols.add(target.id)
    return symbols


def locate_entry_files(
    metadata: dict[str, Any],
    module_index: dict[str, Path],
    preferred_files: set[Path],
) -> list[Path]:
    feature = metadata.get("feature") if isinstance(metadata.get("feature"), dict) else {}
    entrypoints = [str(value) for value in feature.get("source_entrypoints") or []]
    found: set[Path] = set()
    symbol_cache: dict[Path, set[str]] = {}
    all_paths = sorted(set(module_index.values()), key=lambda path: (path not in preferred_files, str(path)))
    for entrypoint in entrypoints:
        parts = entrypoint.split(".")
        exact: Path | None = None
        for end in range(len(parts), 0, -1):
            module = ".".join(parts[:end])
            if module in module_index:
                exact = module_index[module]
                break
        symbol = parts[-1]
        symbol_matches: list[Path] = []
        for path in all_paths:
            symbols = symbol_cache.setdefault(path, top_level_symbols(path))
            if symbol in symbols:
                symbol_matches.append(path)
        if symbol_matches and (exact is None or exact.name == "__init__.py"):
            found.add(symbol_matches[0])
        elif exact is not None:
            found.add(exact)
    return sorted(found)


def dotted_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = dotted_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    return ""


def resolve_module(module: str, module_index: dict[str, Path]) -> Path | None:
    parts = module.split(".") if module else []
    for end in range(len(parts), 0, -1):
        candidate = ".".join(parts[:end])
        if candidate in module_index:
            return module_index[candidate]
    return None


def imports_for_file(
    path: Path,
    module_index: dict[str, Path],
    canonical: dict[Path, str],
) -> tuple[set[Path], set[str], bool, bool, bool]:
    text = path.read_text(encoding="utf-8", errors="replace")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SyntaxWarning)
        try:
            tree = ast.parse(text)
        except SyntaxError:
            tree = None
    if tree is None:
        return set(), set(), False, False, False
    internal: set[Path] = set()
    external: set[str] = set()
    current = canonical.get(path, "")
    package_parts = current.split(".")[:-1] if path.name != "__init__.py" else current.split(".")
    for node in ast.walk(tree):
        modules: list[str] = []
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base_parts = package_parts[: max(0, len(package_parts) - node.level + 1)]
                if node.module:
                    base_parts.extend(node.module.split("."))
                base = ".".join(base_parts)
            else:
                base = node.module or ""
            modules.append(base)
            modules.extend(f"{base}.{alias.name}" for alias in node.names if base)
        for module in modules:
            target = resolve_module(module, module_index)
            if target is not None and target != path:
                internal.add(target)
            elif module:
                top = module.split(".")[0]
                if top not in sys.stdlib_module_names:
                    external.add(top)
    call_names = {dotted_name(node.func) for node in ast.walk(tree) if isinstance(node, ast.Call)}
    identifiers = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    identifiers.update(node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute))
    dynamic = any(DYNAMIC_PATTERN.search(name) for name in call_names)
    registry = any(REGISTRY_PATTERN.search(name) for name in identifiers | call_names)
    global_state = any(isinstance(node, ast.Global) for node in ast.walk(tree))
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            value = node.value
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            target_names = [target.id for target in targets if isinstance(target, ast.Name)]
            stateful_name = any(
                re.search(
                    r"state|registry|cache|hooks?|plugins?|receivers?|handlers?|providers?|instances?|stack|current",
                    name,
                    re.IGNORECASE,
                )
                for name in target_names
            )
            if stateful_name and isinstance(value, (ast.Dict, ast.List, ast.Set)):
                global_state = True
            elif stateful_name and isinstance(value, ast.Call) and re.search(
                r"cache|registry|weak.*dictionary|defaultdict", dotted_name(value.func), re.IGNORECASE
            ):
                global_state = True
    return internal, external, dynamic, global_state, registry


def analyze_source(
    task_dir: Path,
    metadata: dict[str, Any],
    explicit_files: list[Path],
) -> SourceAnalysis:
    repo_dir = task_dir / "repo"
    module_index, canonical = build_module_index(repo_dir)
    explicit_python = {path for path in explicit_files if path.suffix == ".py"}
    entry_files = locate_entry_files(metadata, module_index, explicit_python)
    if not entry_files:
        return SourceAnalysis([], sorted(explicit_python), NA, NA, NA, NA, NA, NA, NA, [])

    allowed = explicit_python or set(module_index.values())
    queue: deque[tuple[Path, int]] = deque((path, 0) for path in entry_files)
    distances = {path: 0 for path in entry_files}
    graph: dict[Path, set[Path]] = defaultdict(set)
    external: set[str] = set()
    dynamic = False
    global_state = False
    registry = False
    source_evidence: set[Path] = set(entry_files)
    while queue:
        path, depth = queue.popleft()
        internal, imported_external, file_dynamic, file_global, file_registry = imports_for_file(
            path, module_index, canonical
        )
        internal &= allowed
        graph[path].update(internal)
        external.update(imported_external)
        dynamic |= file_dynamic
        global_state |= file_global
        registry |= file_registry
        if file_dynamic or file_global or file_registry:
            source_evidence.add(path)
        for target in internal:
            if target not in distances:
                distances[target] = depth + 1
                queue.append((target, depth + 1))

    direct = set().union(*(graph[path] for path in entry_files)) if entry_files else set()
    reachable = set(distances)
    transitive = reachable - set(entry_files) - direct
    scope = sorted(explicit_python or reachable)
    return SourceAnalysis(
        entry_files=entry_files,
        scope_files=scope,
        direct_internal_dependency_count=len(direct),
        transitive_internal_dependency_count=len(transitive),
        external_dependency_count=len(external),
        static_file_closure_depth=max(distances.values(), default=0),
        has_dynamic_import=dynamic,
        has_global_state=global_state,
        has_registry=registry,
        source_evidence=sorted(source_evidence),
    )


def bool_or_na(value: bool | str) -> str:
    if value == NA:
        return NA
    return "true" if bool(value) else "false"


def metadata_semantic_text(metadata: dict[str, Any]) -> str:
    """Return task semantics without JSON field names such as source_entrypoints."""
    feature = metadata.get("feature") if isinstance(metadata.get("feature"), dict) else {}
    entanglement = metadata.get("entanglement") if isinstance(metadata.get("entanglement"), dict) else {}
    values: list[Any] = [
        feature.get("name"),
        feature.get("description"),
        feature.get("included_behaviors"),
        feature.get("excluded_behaviors"),
        entanglement.get("description"),
        entanglement.get("signals"),
        metadata.get("tags"),
    ]
    return "\n".join(
        str(item)
        for value in values
        for item in (value if isinstance(value, list) else [value])
        if item is not None
    )


def join_tags(values: Iterable[str]) -> str:
    return ";".join(sorted(set(values)))


def hidden_behavioral_risks(task_dir: Path) -> tuple[list[str], list[Path]]:
    files = task_python_files(task_dir / "hidden_tests")
    text = "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in files)
    return [name for name, pattern in RISK_PATTERNS.items() if pattern.search(text)], files


def feature_statefulness(task_id: str, primary: str, normalized: set[str]) -> str:
    if task_id in GLOBAL_STATE_FEATURES:
        return "global_state"
    if task_id in SESSION_STATE_FEATURES:
        return "session_state"
    if task_id in LIFECYCLE_STATE_FEATURES or "framework_lifecycle" in normalized:
        return "lifecycle_state"
    if primary in {"parse_tokenize_decode", "algorithm_data_structure", "serialize_format_render"}:
        return "local_state"
    return "stateless"


def codebase_conditions(
    task_id: str,
    metadata_text: str,
    explicit_files: list[Path],
    normalized: set[str],
) -> set[str]:
    result: set[str] = set()
    if "legacy_vibe_clutter" in metadata_text:
        result.add("legacy_clutter")
    if re.search(r"duplicate (?:string |merge )?helpers|duplicate utils|wrong helpers", metadata_text, re.I):
        result.add("duplicated_implementation")
    if re.search(r"wrong helpers|factory clutter|pipeline .* clutter|legacy loader paths", metadata_text, re.I):
        result.add("dead_code_distractors")
    if any(re.search(r"generated|_generated", path.name, re.I) for path in explicit_files):
        result.add("generated_code")
    python_file_count = sum(path.suffix == ".py" for path in explicit_files)
    if python_file_count >= 3 and "implicit_runtime_dependency" in normalized:
        result.add("weak_module_boundaries")
    if task_id.startswith("vibe_app__") and "dead_code_distractors" not in result:
        # The metadata explicitly lists legacy/wrong helper entry points for all
        # curated-vibe tasks; the label remains evidence-backed, not outcome-derived.
        if re.search(r"legacy|clutter|wrong", metadata_text, re.I):
            result.add("dead_code_distractors")
    return result


def normalized_entanglement(
    original_types: list[str],
    source: SourceAnalysis,
    metadata_text: str,
    reference_file_count: int | str,
) -> set[str]:
    result = {ORIGINAL_ENTANGLEMENT_MAP[value] for value in original_types if value in ORIGINAL_ENTANGLEMENT_MAP}
    if (
        isinstance(reference_file_count, int)
        and reference_file_count > 1
        or isinstance(source.transitive_internal_dependency_count, int)
        and source.transitive_internal_dependency_count > 0
    ):
        result.add("static_transitive_dependency")
    if source.has_dynamic_import is True or DYNAMIC_METADATA_PATTERN.search(metadata_text):
        result.add("dynamic_import_plugin")
    return result


def concrete_evidence_paths(
    root: Path,
    task_dir: Path,
    hidden_files: list[Path],
    source_files: list[Path],
) -> str:
    paths = [
        task_dir / "metadata.json",
        task_dir / "evaluation" / "oracle_manifest.json",
    ]
    public_files = task_python_files(task_dir / "public_tests")
    if public_files:
        paths.append(public_files[0])
    if hidden_files:
        paths.append(hidden_files[0])
    paths.extend(source_files[:3])
    unique: list[str] = []
    for path in paths:
        try:
            rel = path.relative_to(root).as_posix()
        except ValueError:
            rel = path.as_posix()
        if rel not in unique:
            unique.append(rel)
    return ";".join(unique)


def build_row(
    root: Path,
    task_dir: Path,
    feature_map: dict[str, str],
    source_domains: dict[str, str],
) -> dict[str, Any]:
    metadata_path = task_dir / "metadata.json"
    oracle_path = task_dir / "evaluation" / "oracle_manifest.json"
    metadata = load_json(metadata_path)
    oracle = load_json(oracle_path)
    task_id = str(metadata.get("task_id") or task_dir.name)
    source_block = metadata.get("source") if isinstance(metadata.get("source"), dict) else {}
    source = str(source_block.get("name") or "")
    feature = metadata.get("feature") if isinstance(metadata.get("feature"), dict) else {}
    entanglement = metadata.get("entanglement") if isinstance(metadata.get("entanglement"), dict) else {}
    original_types = [str(value) for value in entanglement.get("types") or []]
    closure = load_closure_gold(task_dir)
    entries = sorted(closure.approved_artifact_values("file"))
    explicit_files, all_resolved = expand_oracle_files(task_dir, entries)
    reference_file_count: int | str = len(explicit_files) if entries and all_resolved else NA
    reference_loc: int | str = physical_python_loc(explicit_files) if entries and all_resolved else NA
    resource_count: int | str = (
        sum(path.suffix != ".py" for path in explicit_files) if entries and all_resolved else NA
    )
    source_analysis = analyze_source(task_dir, metadata, explicit_files)
    metadata_text = metadata_semantic_text(metadata)
    normalized = normalized_entanglement(
        original_types, source_analysis, metadata_text, reference_file_count
    )
    hidden_risks, hidden_files = hidden_behavioral_risks(task_dir)
    primary_feature = feature_map[task_id]
    adapter_match = ADAPTER_PATTERN.search(metadata_text + "\n" + json.dumps(oracle))
    has_dynamic = source_analysis.has_dynamic_import is True or bool(DYNAMIC_METADATA_PATTERN.search(metadata_text))
    has_global = source_analysis.has_global_state is True or "global_state_registry_coupling" in original_types
    has_registry = source_analysis.has_registry is True or bool(REGISTRY_PATTERN.search(metadata_text))
    has_framework = "framework_lifecycle" in normalized or bool(LIFECYCLE_PATTERN.search(metadata_text))
    row = {
        "task_id": task_id,
        "split": "hard50" if task_id.endswith("__hard3_001") or "batch-3" in metadata.get("tags", []) else "core100",
        "source_repo": source,
        "source_commit": str(source_block.get("commit") or NA),
        "source_group_id": slug(source),
        "repo_archetype_primary": repo_archetype(source),
        "repo_archetype_secondary": "",
        "repo_provenance": repo_provenance(source, metadata),
        "repo_domain_primary": source_domains[source],
        "repo_domain_secondary": join_tags(REPO_DOMAIN_SECONDARY.get(source, ())),
        "feature_family_primary": primary_feature,
        "feature_family_secondary": join_tags(FEATURE_SECONDARY.get(task_id, ())),
        "feature_statefulness": feature_statefulness(task_id, primary_feature, normalized),
        "entanglement_primary_original": str(entanglement.get("primary") or NA),
        "entanglement_types_original": join_tags(original_types),
        "normalized_entanglement_types": join_tags(normalized),
        "behavioral_risk_tags": join_tags(hidden_risks),
        "codebase_condition_tags": join_tags(
            codebase_conditions(task_id, metadata_text, explicit_files, normalized)
        ),
        "reference_file_count": reference_file_count,
        "reference_symbol_count": explicit_reference_symbol_count(oracle),
        "reference_loc": reference_loc,
        "source_entrypoint_count": len(feature.get("source_entrypoints") or []),
        "direct_internal_dependency_count": source_analysis.direct_internal_dependency_count,
        "transitive_internal_dependency_count": source_analysis.transitive_internal_dependency_count,
        "external_dependency_count": source_analysis.external_dependency_count,
        "static_file_closure_depth": source_analysis.static_file_closure_depth,
        "resource_file_count": resource_count,
        "has_dynamic_import": bool_or_na(has_dynamic),
        "has_global_state": bool_or_na(has_global),
        "has_registry": bool_or_na(has_registry),
        "has_framework_lifecycle": bool_or_na(has_framework),
        "adapter_required": "true" if adapter_match else NA,
        "public_test_count": count_static_tests(task_dir / "public_tests"),
        "hidden_test_count": count_static_tests(task_dir / "hidden_tests"),
        "classification_evidence": concrete_evidence_paths(
            root, task_dir, hidden_files, source_analysis.source_evidence
        ),
        "classification_confidence": "medium" if task_id in NEEDS_REVIEW_TASKS else "high",
        "review_status": "needs_review" if task_id in NEEDS_REVIEW_TASKS else "reviewed_v1",
        "taxonomy_version": TAXONOMY_VERSION,
    }
    if task_id in AI_REVIEW_OVERRIDES:
        row.update(AI_REVIEW_OVERRIDES[task_id])
        row["classification_confidence"] = "medium"
        row["review_status"] = "ai_assisted_reviewed_v1"
    return row


def validate_rows(rows: list[dict[str, Any]], task_dirs: list[Path]) -> list[str]:
    errors: list[str] = []
    expected_ids = {path.name for path in task_dirs}
    actual_ids = {str(row["task_id"]) for row in rows}
    if len(rows) != 150:
        errors.append(f"expected 150 rows, found {len(rows)}")
    if expected_ids != actual_ids:
        errors.append(f"task id mismatch missing={sorted(expected_ids-actual_ids)} extra={sorted(actual_ids-expected_ids)}")
    feature_map = flatten_feature_map()
    if set(feature_map) != expected_ids:
        errors.append(
            f"feature map mismatch missing={sorted(expected_ids-set(feature_map))} extra={sorted(set(feature_map)-expected_ids)}"
        )
    source_domains = flatten_source_domains()
    actual_sources = {str(row["source_repo"]) for row in rows}
    if set(source_domains) != actual_sources:
        errors.append(
            f"source domain mismatch missing={sorted(actual_sources-set(source_domains))} extra={sorted(set(source_domains)-actual_sources)}"
        )
    root = task_dirs[0].parents[2]
    for row in rows:
        if row["repo_archetype_primary"] not in REPO_ARCHETYPES:
            errors.append(f"{row['task_id']}: invalid archetype")
        if row["repo_provenance"] not in REPO_PROVENANCE:
            errors.append(f"{row['task_id']}: invalid provenance")
        if row["repo_domain_primary"] not in REPO_DOMAINS:
            errors.append(f"{row['task_id']}: invalid domain")
        if row["feature_family_primary"] not in FEATURE_FAMILIES:
            errors.append(f"{row['task_id']}: invalid feature family")
        if row["feature_statefulness"] not in FEATURE_STATEFULNESS:
            errors.append(f"{row['task_id']}: invalid statefulness")
        normalized = set(str(row["normalized_entanglement_types"]).split(";")) - {""}
        if not normalized <= ENTANGLEMENT_MECHANISMS:
            errors.append(f"{row['task_id']}: invalid entanglement {sorted(normalized-ENTANGLEMENT_MECHANISMS)}")
        risks = set(str(row["behavioral_risk_tags"]).split(";")) - {""}
        if not risks <= BEHAVIORAL_RISKS:
            errors.append(f"{row['task_id']}: invalid behavioral risk")
        conditions = set(str(row["codebase_condition_tags"]).split(";")) - {""}
        if not conditions <= CODEBASE_CONDITIONS:
            errors.append(f"{row['task_id']}: invalid codebase condition")
        evidence = str(row["classification_evidence"]).split(";")
        if not evidence or any(not (Path(path).is_absolute() or (root / path).exists()) for path in evidence):
            errors.append(f"{row['task_id']}: missing concrete evidence path")
    if not TRIAL_TASK_IDS <= actual_ids:
        errors.append("20-task trial set is not a subset of taxonomy rows")
    return errors


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def count_primary(rows: list[dict[str, Any]], key: str) -> Counter[str]:
    return Counter(str(row[key]) for row in rows)


def count_multilabel(rows: list[dict[str, Any]], key: str) -> Counter[str]:
    counter: Counter[str] = Counter()
    for row in rows:
        counter.update(value for value in str(row[key]).split(";") if value)
    return counter


def markdown_count_table(
    counter: Counter[str], total: int, categories: Iterable[str] | None = None
) -> list[str]:
    lines = ["| 类别 | 任务数 | 占比 |", "|---|---:|---:|"]
    items = [(label, counter[label]) for label in categories] if categories is not None else list(counter.items())
    for label, count in sorted(items, key=lambda item: (-item[1], item[0])):
        lines.append(f"| `{label}` | {count} | {count / total:.1%} |")
    return lines


def markdown_matrix(
    rows: list[dict[str, Any]],
    row_key: str,
    col_key: str,
    *,
    col_multilabel: bool = False,
) -> list[str]:
    row_labels = sorted({str(row[row_key]) for row in rows})
    if col_multilabel:
        col_labels = sorted(count_multilabel(rows, col_key))
    else:
        col_labels = sorted({str(row[col_key]) for row in rows})
    lines = ["| " + row_key + " | " + " | ".join(f"`{value}`" for value in col_labels) + " | Total |"]
    lines.append("|---|" + "---:|" * (len(col_labels) + 1))
    for row_label in row_labels:
        values: list[int] = []
        selected = [row for row in rows if str(row[row_key]) == row_label]
        for col_label in col_labels:
            if col_multilabel:
                values.append(sum(col_label in str(row[col_key]).split(";") for row in selected))
            else:
                values.append(sum(str(row[col_key]) == col_label for row in selected))
        lines.append(
            f"| `{row_label}` | " + " | ".join(str(value) for value in values) + f" | {len(selected)} |"
        )
    return lines


def depth_bin(value: Any) -> str:
    if value == NA or value == "":
        return "NA"
    depth = int(value)
    if depth <= 1:
        return "shallow_0_1"
    if depth == 2:
        return "medium_2"
    return "deep_3_plus"


def near_duplicate_candidates(rows: list[dict[str, Any]]) -> list[tuple[str, list[str]]]:
    by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_source[str(row["source_repo"])].append(row)
    result: list[tuple[str, list[str]]] = []
    for source, group in sorted(by_source.items()):
        if len(group) < 2:
            continue
        families = defaultdict(list)
        for row in group:
            families[str(row["feature_family_primary"])].append(str(row["task_id"]))
        for family, task_ids in families.items():
            if len(task_ids) >= 2:
                result.append((f"{source} / {family}", sorted(task_ids)))
    return result


def render_report(rows: list[dict[str, Any]], csv_path: Path, errors: list[str]) -> str:
    total = len(rows)
    lines = [
        "# FeatureLiftBench Python-150 Benchmark Taxonomy Report",
        "",
        f"- Taxonomy version: `{TAXONOMY_VERSION}`",
        f"- Task-level rows: **{total}**",
        "- Evidence boundary: metadata, oracle manifests, source snapshots, public tests, hidden tests.",
        "- Explicitly excluded: trajectories, submissions, evaluation results, and historical pass/fail labels.",
        f"- Generated from: `{csv_path.as_posix()}`",
        f"- Audit invariant errors: **{len(errors)}**",
        "",
        "## Repository archetype",
        "",
        *markdown_count_table(count_primary(rows, "repo_archetype_primary"), total, REPO_ARCHETYPES),
        "",
        "## Repository provenance",
        "",
        *markdown_count_table(count_primary(rows, "repo_provenance"), total, REPO_PROVENANCE),
        "",
        "`real_oss_legacy` is empty in v1 because project age/maintenance is not inferable from the local task package. "
        "The label is reserved for future tasks carrying explicit provenance evidence.",
        "",
        "## Repository domain",
        "",
        *markdown_count_table(count_primary(rows, "repo_domain_primary"), total, REPO_DOMAINS),
        "",
        "## Feature family",
        "",
        *markdown_count_table(count_primary(rows, "feature_family_primary"), total, FEATURE_FAMILIES),
        "",
        "## Feature statefulness",
        "",
        *markdown_count_table(count_primary(rows, "feature_statefulness"), total, FEATURE_STATEFULNESS),
        "",
        "## Normalized entanglement mechanisms (multi-label)",
        "",
        "Percentages use all 150 tasks as denominator and therefore sum above 100%.",
        "",
        *markdown_count_table(
            count_multilabel(rows, "normalized_entanglement_types"), total, ENTANGLEMENT_MECHANISMS
        ),
        "",
        "## Behavioral hidden-risk tags (multi-label)",
        "",
        "Tags are deterministic lexical/AST audits of hidden tests; they describe tested contract dimensions, not outcomes.",
        "",
        *markdown_count_table(count_multilabel(rows, "behavioral_risk_tags"), total, BEHAVIORAL_RISKS),
        "",
        "## Codebase condition tags (multi-label)",
        "",
        *markdown_count_table(count_multilabel(rows, "codebase_condition_tags"), total, CODEBASE_CONDITIONS),
        "",
        "## Repository archetype × feature family",
        "",
        *markdown_matrix(rows, "repo_archetype_primary", "feature_family_primary"),
        "",
        "## Feature family × entanglement mechanism",
        "",
        *markdown_matrix(rows, "feature_family_primary", "normalized_entanglement_types", col_multilabel=True),
        "",
        "## Core100 × Hard50",
        "",
        *markdown_matrix(rows, "split", "feature_family_primary"),
        "",
        "### Split totals",
        "",
        *markdown_count_table(count_primary(rows, "split"), total, ("core100", "hard50")),
        "",
        "Hard50 is not a scaled copy of Core100: registry/plugin features are 15/50 in Hard50 versus 7/100 in "
        "Core100, while parse/tokenize features are 4/50 versus 26/100. Any aggregate comparison must therefore "
        "report split- and feature-stratified results.",
        "",
        "## Source repository concentration",
        "",
        "There are **{}** unique upstream source groups.".format(len({row["source_group_id"] for row in rows})),
        "",
        "| Source repo | Tasks | Share |",
        "|---|---:|---:|",
    ]
    source_counts = count_primary(rows, "source_repo")
    for source, count in sorted(source_counts.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"| `{source}` | {count} | {count / total:.1%} |")

    depth_counts = Counter(depth_bin(row["static_file_closure_depth"]) for row in rows)
    lines.extend([
        "",
        "## Static closure depth",
        "",
        "Depth is the maximum shortest import path from located source entrypoint files, bounded by the explicit "
        "oracle source-file set when present. `NA` means entrypoints or reference closure could not be located reliably.",
        "",
        *markdown_count_table(depth_counts, total),
        "",
        "## Dynamic import, global state, registry, and lifecycle signals",
        "",
        "| Signal | true | false | NA |",
        "|---|---:|---:|---:|",
    ])
    for key in ("has_dynamic_import", "has_global_state", "has_registry", "has_framework_lifecycle"):
        counts = count_primary(rows, key)
        lines.append(f"| `{key}` | {counts['true']} | {counts['false']} | {counts[NA]} |")

    sparse_primary: list[tuple[str, str, int]] = []
    primary_categories = {
        "repo_archetype_primary": REPO_ARCHETYPES,
        "repo_provenance": REPO_PROVENANCE,
        "repo_domain_primary": REPO_DOMAINS,
        "feature_family_primary": FEATURE_FAMILIES,
    }
    for key, categories in primary_categories.items():
        counts = count_primary(rows, key)
        for label in categories:
            count = counts[label]
            if count < 5:
                sparse_primary.append((key, label, count))
    sparse_multi: list[tuple[str, str, int]] = []
    multi_categories = {
        "normalized_entanglement_types": ENTANGLEMENT_MECHANISMS,
        "behavioral_risk_tags": BEHAVIORAL_RISKS,
        "codebase_condition_tags": CODEBASE_CONDITIONS,
    }
    for key, categories in multi_categories.items():
        counts = count_multilabel(rows, key)
        for label in categories:
            count = counts[label]
            if count < 5:
                sparse_multi.append((key, label, count))
    lines.extend([
        "",
        "## Sparse and imbalanced categories",
        "",
        "A category with fewer than five tasks must not support a standalone performance claim.",
        "",
        "| Field | Category | N | Allowed use |",
        "|---|---|---:|---|",
    ])
    for key, label, count in sorted(sparse_primary + sparse_multi):
        lines.append(f"| `{key}` | `{label}` | {count} | descriptive only |")
    if not sparse_primary and not sparse_multi:
        lines.append("| — | — | — | no category below threshold |")

    largest_family = count_primary(rows, "feature_family_primary").most_common(1)[0]
    largest_domain = count_primary(rows, "repo_domain_primary").most_common(1)[0]
    multi_source = [(source, count) for source, count in source_counts.items() if count > 1]
    lines.extend([
        "",
        "The dominant feature family is `{}` ({}/{}); the dominant repository domain is `{}` ({}/{}).".format(
            largest_family[0], largest_family[1], total, largest_domain[0], largest_domain[1], total
        ),
        f"{len(multi_source)} source repositories contribute more than one task. The largest single source contributes "
        f"{source_counts.most_common(1)[0][1]}/{total} tasks, below 5% but not independent for uncertainty estimates.",
        "Paper-scale comparisons should cluster uncertainty by `source_group_id` and report source-disjoint sensitivity.",
        "",
        "## Near-duplicate candidates",
        "",
        "This is a conservative review queue: same source repository and same primary feature family. "
        "It does not assert semantic duplication.",
        "",
        "| Candidate cluster | Tasks |",
        "|---|---|",
    ])
    candidates = near_duplicate_candidates(rows)
    for label, task_ids in candidates:
        lines.append(f"| `{label}` | {', '.join(f'`{task_id}`' for task_id in task_ids)} |")
    if not candidates:
        lines.append("| none | — |")

    review_tasks = [str(row["task_id"]) for row in rows if row["review_status"] == "needs_review"]
    lines.extend([
        "",
        "## Review status",
        "",
        f"- `reviewed_v1`: **{total - len(review_tasks)}**",
        f"- `needs_review`: **{len(review_tasks)}**",
        "",
        "The following tasks have cross-family/domain ambiguity. Their v1 labels are usable for pilot stratification but "
        "must be adjudicated before making a narrow per-category paper claim:",
        "",
        *[f"- `{task_id}`" for task_id in review_tasks],
        "",
        "## Statistical-use guidance",
        "",
        "- Categories with `N >= 5` may support descriptive slices; confirmatory method comparisons still require enough "
        "runs per arm and source-clustered uncertainty.",
        "- Categories with `N < 5` are descriptive only and must be pooled into a preregistered broader mechanism for tests.",
        "- Multi-label mechanism counts are not mutually exclusive; do not use a naive chi-square table that treats them as such.",
        "- The 10-task pilot is mechanism-finding and cannot support population-level performance claims.",
        "- Outcome fields must be joined later by `task_id`; they must never be copied into this taxonomy table.",
        "",
        "## Missing measurements",
        "",
        "| Field | NA rows | Reason |",
        "|---|---:|---|",
    ])
    for key in (
        "reference_file_count", "reference_symbol_count", "reference_loc",
        "direct_internal_dependency_count", "transitive_internal_dependency_count",
        "external_dependency_count", "static_file_closure_depth", "resource_file_count", "adapter_required",
    ):
        count = sum(str(row[key]) == NA for row in rows)
        lines.append(f"| `{key}` | {count} | no explicit reliable evidence; not imputed |")
    lines.extend(["", "## Reproduction", "", "```bash", "python3 tools/research_analysis/build_benchmark_taxonomy.py --strict", "```", ""])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.repo_root.resolve()
    output = resolve_output(root, args.output)
    report = resolve_output(root, args.report)
    task_dirs = sorted(path.parent for path in (root / "benchmark" / "tasks").glob("*/metadata.json"))
    feature_map = flatten_feature_map()
    source_domains = flatten_source_domains()
    rows = [build_row(root, task_dir, feature_map, source_domains) for task_dir in task_dirs]
    errors = validate_rows(rows, task_dirs)
    if errors and args.strict:
        raise SystemExit("taxonomy audit failed:\n- " + "\n- ".join(errors))
    write_csv(output, rows)
    ledger_path = root / "artifacts/research_analysis/v1_1/taxonomy_ai_review_ledger.json"
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    ledger_path.write_text(
        json.dumps(
            {
                "schema_version": "featureliftbench.taxonomy_ai_review_ledger.v1",
                "taxonomy_version": TAXONOMY_VERSION,
                "review_boundary": (
                    "This adjudication is AI-assisted author review, not independent human double review."
                ),
                "tasks": [
                    {
                        "task_id": task_id,
                        "field_overrides": AI_REVIEW_OVERRIDES[task_id],
                        "rationale": AI_REVIEW_RATIONALES[task_id],
                        "reviewer_id": "codex_taxonomy_semantic_pass",
                        "reviewer_type": "ai_assisted_author",
                        "formal_human_review_pending": True,
                    }
                    for task_id in sorted(AI_REVIEW_OVERRIDES)
                ],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(render_report(rows, output.relative_to(root), errors), encoding="utf-8")
    print(f"wrote {len(rows)} rows to {output}")
    print(f"wrote report to {report}")
    print(f"wrote AI-assisted review ledger to {ledger_path}")
    print(f"needs_review={sum(row['review_status'] == 'needs_review' for row in rows)}")
    if errors:
        print("audit errors:")
        for error in errors:
            print(f"- {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
