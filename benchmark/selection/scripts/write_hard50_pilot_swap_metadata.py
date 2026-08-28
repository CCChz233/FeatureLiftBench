#!/usr/bin/env python3.12
"""Write public_spec metadata for Hard-50 Pilot swap tasks, then sync TASK.md."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "harness"))
from scripts.sync_external50_task_contract import sync_task  # noqa: E402

PILOT = ROOT / "benchmark" / "hard50_pilot"


def clause(behavior_id: str, text: str) -> dict:
    return {"behavior_id": behavior_id, "clause_kind": "included_behavior", "text": text}


def mapping(nodeid: str, behavior_ids: list[str]) -> dict:
    return {"nodeid": nodeid, "behavior_ids": behavior_ids, "mapping_method": "ai_assisted"}


def coverage(path: str, test: str) -> dict:
    return {"path": path, "covered_by_tests": [test]}


REVIEW = {
    "reviewed_at": "2026-08-27",
    "reviewer": "hard50_materialization_agent",
    "reviewer_type": "ai_assisted_task_level_review",
    "checklist_passed": True,
    "notes": "Checked required API closure, observable behavior wording, test mappings, and hidden-spec inclusion.",
}

API_SURFACE = "hidden_tests/test_required_api_surface.py::test_required_api_surface"


def waitress() -> dict:
    behaviors = [
        {
            "id": "B001",
            "text": "Constructing `Adjustments` with `host`, `port`, and `threads` stores those values on the instance; omitting them leaves the defaults `port=8080` and `threads=4`.",
        },
        {
            "id": "B002",
            "text": "Passing `listen` together with `host` or `port`, or passing `unix_socket` together with `host`, raises `ValueError`; an unknown keyword raises `ValueError` whose message includes `Unknown adjustment`.",
        },
        {
            "id": "B003",
            "text": "Boolean knobs such as `expose_tracebacks` coerce the strings `yes`/`true` to `True` and `off`/`0` to `False`; `url_prefix` is stored with a single leading slash and without a trailing slash.",
        },
        {
            "id": "B004",
            "text": "Setting `trusted_proxy_count` without `trusted_proxy` raises `ValueError` mentioning `trusted_proxy_count`.",
        },
        {
            "id": "B005",
            "text": "The package exposes `Adjustments` with the constructor and attributes listed in this contract.",
        },
        {
            "id": "B006",
            "text": "The submitted package source does not import the forbidden upstream package `waitress`.",
        },
    ]
    return {
        "task_id": "waitress__adjustments_core__001",
        "language": "python",
        "difficulty": "hard",
        "status": "materialized_candidate",
        "task_revision": 1,
        "tags": ["hard50", "pilot", "lift", "adapted", "configuration"],
        "source": {
            "name": "waitress",
            "url": "https://github.com/Pylons/waitress",
            "commit": "7a855a2d36e4a672b4ff2db8c8483dde3de590dd",
            "license": "ZPL-2.1",
        },
        "feature": {
            "name": "Waitress Adjustments",
            "description": "Lift waitress server tuning from constructor kwargs, including type coercion and mutually exclusive listen settings.",
            "source_entrypoints": ["waitress.adjustments.Adjustments"],
            "included_behaviors": [
                "host/port/threads",
                "boolean and url_prefix coercion",
                "listen/unix_socket mutual exclusion",
                "unknown adjustment rejection",
            ],
            "excluded_behaviors": [
                "real listen sockets and request serving",
                "Paste deploy runner",
                "proxy header rewriting at request time",
            ],
        },
        "entanglement": {
            "level": "high",
            "types": ["config_environment_coupling", "framework_coupling"],
            "primary": "config_environment_coupling",
            "description": "Adjustment validation is coupled to listen/socket family setup inside the WSGI server package.",
            "signals": ["mutual exclusion", "type coercion", "unknown keys"],
        },
        "output": {
            "package": "featurelifted",
            "import": "from featurelifted import Adjustments",
            "callable": "Adjustments",
            "signature": "Adjustments(**kw)",
        },
        "environment": {
            "python": "3.12",
            "network": False,
            "timeout_seconds": 90,
            "dependency_lock": "requirements.lock",
            "allowed_dependencies": [],
            "forbidden_dependencies": ["waitress"],
            "forbidden_imports": ["waitress"],
            "forbidden_paths": ["repo/", "waitress/"],
        },
        "tests": {"public": "public_tests/", "hidden": "hidden_tests/", "command": "pytest"},
        "spec_status": "compliant",
        "public_spec": {
            "title": "Waitress Adjustments",
            "summary": "Build a standalone `featurelifted` package providing waitress-style `Adjustments` construction, coercion, and validation without serving sockets.",
            "required_api": [
                {
                    "path": "featurelifted.Adjustments",
                    "kind": "class",
                    "signature": "(**kw)",
                    "members": [
                        {
                            "path": "featurelifted.Adjustments.__init__",
                            "kind": "method",
                            "signature": "(self, **kw) -> None",
                        },
                        {"path": "featurelifted.Adjustments.host", "kind": "attribute"},
                        {"path": "featurelifted.Adjustments.port", "kind": "attribute"},
                        {"path": "featurelifted.Adjustments.threads", "kind": "attribute"},
                        {"path": "featurelifted.Adjustments.url_prefix", "kind": "attribute"},
                        {"path": "featurelifted.Adjustments.expose_tracebacks", "kind": "attribute"},
                    ],
                }
            ],
            "optional_api": [],
            "behaviors": behaviors,
            "exclusions": [
                "real listen sockets and request serving",
                "Paste deploy runner",
                "proxy header rewriting at request time",
                "runtime import of waitress",
            ],
            "forbidden": {"imports": ["waitress"], "paths": []},
        },
        "evaluation_spec": {
            "public_clauses": [clause(b["id"], b["text"]) for b in behaviors],
            "public_test_mappings": [
                mapping("public_tests/test_public_api.py::test_host_port_threads_and_defaults", ["B001"]),
                mapping("public_tests/test_public_api.py::test_listen_conflicts_with_host", ["B002"]),
                mapping("public_tests/test_public_api.py::test_boolean_and_url_prefix_coercion", ["B003"]),
                mapping("public_tests/test_public_api.py::test_unknown_adjustment_rejected", ["B002"]),
            ],
            "hidden_test_mappings": [
                mapping(
                    "hidden_tests/test_hidden_behavior.py::test_listen_and_unix_socket_are_mutually_exclusive_with_host_port",
                    ["B001", "B002"],
                ),
                mapping("hidden_tests/test_hidden_behavior.py::test_url_prefix_and_bool_aliases", ["B003"]),
                mapping(
                    "hidden_tests/test_hidden_behavior.py::test_unknown_and_trusted_proxy_count_without_proxy",
                    ["B002", "B004"],
                ),
                mapping("hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface", ["B006"]),
                mapping(API_SURFACE, ["B005"]),
            ],
            "required_api_coverage": [
                coverage("featurelifted.Adjustments", API_SURFACE),
                coverage("featurelifted.Adjustments.__init__", API_SURFACE),
                coverage("featurelifted.Adjustments.host", API_SURFACE),
                coverage("featurelifted.Adjustments.port", API_SURFACE),
                coverage("featurelifted.Adjustments.threads", API_SURFACE),
                coverage("featurelifted.Adjustments.url_prefix", API_SURFACE),
                coverage("featurelifted.Adjustments.expose_tracebacks", API_SURFACE),
            ],
            "manual_review": REVIEW,
        },
    }


def polyfactory() -> dict:
    behaviors = [
        {
            "id": "B001",
            "text": "A `DataclassFactory` subclass for a dataclass model builds instances of that model, filling undeclared fields with generated values of the annotated types, including nested dataclass fields.",
        },
        {
            "id": "B002",
            "text": "`build(**overrides)` uses the provided keyword values instead of generated ones for those fields.",
        },
        {
            "id": "B003",
            "text": "A factory class attribute assigned `Use(callable)` supplies that callable's return value for the matching model field.",
        },
        {
            "id": "B004",
            "text": "`batch(n, **overrides)` returns `n` instances; a `Use`/`Require`/`Ignore` factory field whose name is not a model field raises `ConfigurationException` when the factory class is created.",
        },
        {
            "id": "B005",
            "text": "The package exposes `DataclassFactory`, `Use`, and `ConfigurationException` with the callable paths listed in this contract.",
        },
        {
            "id": "B006",
            "text": "The submitted package source does not import the forbidden upstream package `polyfactory`.",
        },
    ]
    return {
        "task_id": "polyfactory__model_factory_core__001",
        "language": "python",
        "difficulty": "hard",
        "status": "materialized_candidate",
        "task_revision": 1,
        "tags": ["hard50", "pilot", "lift", "adapted", "validation"],
        "source": {
            "name": "polyfactory",
            "url": "https://github.com/litestar-org/polyfactory",
            "commit": "e420486b11b9f82b7816d86a8f53c20ce29df86f",
            "license": "MIT",
        },
        "feature": {
            "name": "Dataclass model factories",
            "description": "Lift DataclassFactory construction, overrides, Use fields, and batch generation without SQLAlchemy or Pydantic plugins.",
            "source_entrypoints": [
                "polyfactory.factories.dataclass_factory.DataclassFactory",
                "polyfactory.fields.Use",
            ],
            "included_behaviors": [
                "typed dataclass build",
                "overrides",
                "Use callables",
                "batch",
                "unknown factory field errors",
            ],
            "excluded_behaviors": [
                "SQLAlchemy factory plugin",
                "Pydantic ModelFactory",
                "async persistence",
            ],
        },
        "entanglement": {
            "level": "high",
            "types": ["data_model_coupling", "implicit_dependency_coupling"],
            "primary": "data_model_coupling",
            "description": "Factory metaclass inspects dataclass fields and nested types through a shared BaseFactory registry.",
            "signals": ["generic model inference", "Use descriptors", "nested factories"],
        },
        "output": {
            "package": "featurelifted",
            "import": "from featurelifted import DataclassFactory, Use, ConfigurationException",
            "callable": "DataclassFactory",
            "signature": "DataclassFactory[T]",
        },
        "environment": {
            "python": "3.12",
            "network": False,
            "timeout_seconds": 90,
            "dependency_lock": "requirements.lock",
            "allowed_dependencies": ["faker", "typing-extensions"],
            "forbidden_dependencies": ["polyfactory"],
            "forbidden_imports": ["polyfactory"],
            "forbidden_paths": ["repo/", "polyfactory/"],
        },
        "tests": {"public": "public_tests/", "hidden": "hidden_tests/", "command": "pytest"},
        "spec_status": "compliant",
        "public_spec": {
            "title": "Dataclass model factories",
            "summary": "Build a standalone `featurelifted` package providing dataclass factories with overrides, `Use` fields, and batch construction.",
            "required_api": [
                {
                    "path": "featurelifted.DataclassFactory",
                    "kind": "class",
                    "members": [
                        {
                            "path": "featurelifted.DataclassFactory.build",
                            "kind": "method",
                            "signature": "(cls, **kwargs) -> T",
                        },
                        {
                            "path": "featurelifted.DataclassFactory.batch",
                            "kind": "method",
                            "signature": "(cls, size: int, **kwargs) -> list[T]",
                        },
                    ],
                },
                {
                    "path": "featurelifted.Use",
                    "kind": "class",
                    "signature": "(fn, *args, **kwargs)",
                    "members": [
                        {
                            "path": "featurelifted.Use.__init__",
                            "kind": "method",
                            "signature": "(self, fn, *args, **kwargs)",
                        }
                    ],
                },
                {
                    "path": "featurelifted.ConfigurationException",
                    "kind": "class",
                    "signature": "",
                },
            ],
            "optional_api": [],
            "behaviors": behaviors,
            "exclusions": [
                "SQLAlchemy factory plugin",
                "Pydantic ModelFactory",
                "async persistence",
                "runtime import of polyfactory",
            ],
            "forbidden": {"imports": ["polyfactory"], "paths": []},
        },
        "evaluation_spec": {
            "public_clauses": [clause(b["id"], b["text"]) for b in behaviors],
            "public_test_mappings": [
                mapping("public_tests/test_public_api.py::test_build_generates_typed_dataclass", ["B001", "B003"]),
                mapping("public_tests/test_public_api.py::test_build_overrides", ["B002"]),
                mapping("public_tests/test_public_api.py::test_use_field_and_batch", ["B003", "B004"]),
            ],
            "hidden_test_mappings": [
                mapping(
                    "hidden_tests/test_hidden_behavior.py::test_nested_dataclass_and_override_do_not_clobber_siblings",
                    ["B001", "B002"],
                ),
                mapping(
                    "hidden_tests/test_hidden_behavior.py::test_unknown_factory_field_raises_configuration_exception",
                    ["B004"],
                ),
                mapping("hidden_tests/test_hidden_behavior.py::test_batch_size_and_use_callable", ["B003", "B004"]),
                mapping("hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface", ["B006"]),
                mapping(API_SURFACE, ["B005"]),
            ],
            "required_api_coverage": [
                coverage("featurelifted.DataclassFactory", API_SURFACE),
                coverage("featurelifted.DataclassFactory.build", API_SURFACE),
                coverage("featurelifted.DataclassFactory.batch", API_SURFACE),
                coverage("featurelifted.Use", API_SURFACE),
                coverage("featurelifted.Use.__init__", API_SURFACE),
                coverage("featurelifted.ConfigurationException", API_SURFACE),
            ],
            "manual_review": REVIEW,
        },
    }


def graphene() -> dict:
    behaviors = [
        {
            "id": "B001",
            "text": "A `Schema` constructed with a query `ObjectType` executes a GraphQL operation string; a field resolver that takes an argument declared as `String(name=String(default_value=...))` uses that default when the argument is omitted and the provided value when it is present.",
        },
        {
            "id": "B002",
            "text": "A query field declared with `Field(NestedType)` returns nested selected scalars from an `ObjectType` instance returned by the resolver.",
        },
        {
            "id": "B003",
            "text": "By default `Schema(auto_camelcase=True)` exposes a snake_case Python field such as `hello_world` as the GraphQL field `helloWorld`; querying the snake_case name fails with errors and `data is None`.",
        },
        {
            "id": "B004",
            "text": "Executing a query for a field that is not on the query type yields `data is None` and a non-empty `errors` collection.",
        },
        {
            "id": "B005",
            "text": "The package exposes `ObjectType`, `Schema`, `Schema.execute`, `String`, `Int`, and `Field` with the callable paths listed in this contract.",
        },
        {
            "id": "B006",
            "text": "The submitted package source does not import the forbidden upstream package `graphene`.",
        },
    ]
    return {
        "task_id": "graphene__schema_execute_core__001",
        "language": "python",
        "difficulty": "hard",
        "status": "materialized_candidate",
        "task_revision": 1,
        "tags": ["hard50", "pilot", "lift", "composite", "workflow"],
        "source": {
            "name": "graphene",
            "url": "https://github.com/graphql-python/graphene",
            "commit": "82903263080b3b7f22c2ad84319584d7a3b1a1f6",
            "license": "MIT",
        },
        "feature": {
            "name": "Graphene schema execution",
            "description": "Lift Graphene ObjectType/Schema query execution, including arguments, nested fields, and default camelCase field names.",
            "source_entrypoints": [
                "graphene.types.schema.Schema",
                "graphene.types.objecttype.ObjectType",
            ],
            "included_behaviors": [
                "schema.execute",
                "field arguments with defaults",
                "nested ObjectType fields",
                "auto_camelcase",
                "invalid field errors",
            ],
            "excluded_behaviors": [
                "Django integration",
                "Relay connections and mutations",
                "async execute",
            ],
        },
        "entanglement": {
            "level": "high",
            "types": ["data_model_coupling", "framework_coupling"],
            "primary": "framework_coupling",
            "description": "Graphene type registry maps ObjectType fields onto graphql-core execution.",
            "signals": ["type map", "camelCase transform", "resolver binding"],
        },
        "output": {
            "package": "featurelifted",
            "import": "from featurelifted import ObjectType, Schema, String, Int, Field",
            "callable": "Schema",
            "signature": "Schema(query=None, mutation=None, subscription=None, types=None, directives=None, auto_camelcase=True)",
        },
        "environment": {
            "python": "3.12",
            "network": False,
            "timeout_seconds": 120,
            "dependency_lock": "requirements.lock",
            "allowed_dependencies": [
                "graphql-core",
                "graphql-relay",
                "python-dateutil",
                "six",
                "typing-extensions",
            ],
            "forbidden_dependencies": ["graphene"],
            "forbidden_imports": ["graphene"],
            "forbidden_paths": ["repo/", "graphene/"],
        },
        "tests": {"public": "public_tests/", "hidden": "hidden_tests/", "command": "pytest"},
        "spec_status": "compliant",
        "public_spec": {
            "title": "Graphene schema execution",
            "summary": "Build a standalone `featurelifted` package providing Graphene-style `ObjectType` definitions and `Schema.execute` for queries.",
            "required_api": [
                {
                    "path": "featurelifted.ObjectType",
                    "kind": "class",
                },
                {
                    "path": "featurelifted.Schema",
                    "kind": "class",
                    "signature": "(query=None, mutation=None, subscription=None, types=None, directives=None, auto_camelcase=True)",
                    "members": [
                        {
                            "path": "featurelifted.Schema.__init__",
                            "kind": "method",
                            "signature": "(self, query=None, mutation=None, subscription=None, types=None, directives=None, auto_camelcase=True)",
                        },
                        {
                            "path": "featurelifted.Schema.execute",
                            "kind": "method",
                            "signature": "(self, *args, **kwargs)",
                        },
                    ],
                },
                {"path": "featurelifted.String", "kind": "class"},
                {"path": "featurelifted.Int", "kind": "class"},
                {
                    "path": "featurelifted.Field",
                    "kind": "class",
                    "signature": "(type_, args=None, resolver=None, source=None, deprecation_reason=None, name=None, description=None, required=False, default_value=None, **extra_args)",
                    "members": [
                        {
                            "path": "featurelifted.Field.__init__",
                            "kind": "method",
                            "signature": "(self, type_, args=None, resolver=None, source=None, deprecation_reason=None, name=None, description=None, required=False, default_value=None, **extra_args)",
                        }
                    ],
                },
            ],
            "optional_api": [],
            "behaviors": behaviors,
            "exclusions": [
                "Django integration",
                "Relay connections and mutations",
                "async execute",
                "runtime import of graphene",
            ],
            "forbidden": {"imports": ["graphene"], "paths": []},
        },
        "evaluation_spec": {
            "public_clauses": [clause(b["id"], b["text"]) for b in behaviors],
            "public_test_mappings": [
                mapping("public_tests/test_public_api.py::test_default_argument_resolver", ["B001"]),
                mapping("public_tests/test_public_api.py::test_explicit_argument", ["B001"]),
                mapping("public_tests/test_public_api.py::test_nested_object_field", ["B002"]),
                mapping("public_tests/test_public_api.py::test_unknown_field_reports_errors", ["B004"]),
            ],
            "hidden_test_mappings": [
                mapping(
                    "hidden_tests/test_hidden_behavior.py::test_default_argument_is_overridable_and_nested_fields_resolve",
                    ["B001", "B002"],
                ),
                mapping(
                    "hidden_tests/test_hidden_behavior.py::test_auto_camelcase_exposes_snake_fields_as_camel_case",
                    ["B003"],
                ),
                mapping("hidden_tests/test_hidden_behavior.py::test_unknown_field_leaves_data_none", ["B004"]),
                mapping("hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface", ["B006"]),
                mapping(API_SURFACE, ["B005"]),
            ],
            "required_api_coverage": [
                coverage("featurelifted.ObjectType", API_SURFACE),
                coverage("featurelifted.Schema", API_SURFACE),
                coverage("featurelifted.Schema.__init__", API_SURFACE),
                coverage("featurelifted.Schema.execute", API_SURFACE),
                coverage("featurelifted.String", API_SURFACE),
                coverage("featurelifted.Int", API_SURFACE),
                coverage("featurelifted.Field", API_SURFACE),
                coverage("featurelifted.Field.__init__", API_SURFACE),
            ],
            "manual_review": REVIEW,
        },
    }


def paste() -> dict:
    behaviors = [
        {
            "id": "B001",
            "text": "Assigning a WSGI application to `URLMap[prefix]` dispatches requests whose `PATH_INFO` equals that prefix: the application is called, `SCRIPT_NAME` gains the prefix, and `PATH_INFO` becomes empty.",
        },
        {
            "id": "B002",
            "text": "When both a shorter prefix and a longer prefix are mounted, the longest matching prefix is selected; a path that continues past the shorter prefix but does not match the longer one still uses the shorter prefix and forwards the remainder in `PATH_INFO`.",
        },
        {
            "id": "B003",
            "text": "A request whose `PATH_INFO` matches no mounted prefix is answered with an HTTP 404 status.",
        },
        {
            "id": "B004",
            "text": "A mount key of the form `http://host/path` only matches that HTTP host; the same path on another host is not found, while host-less prefixes still match any host.",
        },
        {
            "id": "B005",
            "text": "The package exposes `URLMap` with construction, `__setitem__`, `__getitem__`, and WSGI `__call__` as listed in this contract.",
        },
        {
            "id": "B006",
            "text": "The submitted package source does not import the forbidden upstream package `paste`.",
        },
    ]
    return {
        "task_id": "paste__dispatch_map_core__001",
        "language": "python",
        "difficulty": "hard",
        "status": "materialized_candidate",
        "task_revision": 1,
        "tags": ["hard50", "pilot", "lift", "adapted", "registry"],
        "source": {
            "name": "Paste",
            "url": "https://github.com/cdent/paste",
            "commit": "28e461548498138b8814b243be432a04a7895dba",
            "license": "MIT",
        },
        "feature": {
            "name": "URLMap prefix dispatch",
            "description": "Lift Paste URLMap prefix and host dispatch without running Paste's HTTP server.",
            "source_entrypoints": ["paste.urlmap.URLMap"],
            "included_behaviors": [
                "prefix dispatch",
                "longest prefix",
                "PATH_INFO/SCRIPT_NAME rewrite",
                "host-specific mounts",
                "404 miss",
            ],
            "excluded_behaviors": [
                "HTTP server sockets",
                "Paste Deploy config factories",
                "HTTPS/proxy applications",
            ],
        },
        "entanglement": {
            "level": "high",
            "types": ["framework_coupling", "config_environment_coupling"],
            "primary": "framework_coupling",
            "description": "URLMap is a WSGI composite that rewrites SCRIPT_NAME/PATH_INFO and consults HTTP_HOST.",
            "signals": ["longest prefix sort", "host tuples", "404 app"],
        },
        "output": {
            "package": "featurelifted",
            "import": "from featurelifted import URLMap",
            "callable": "URLMap",
            "signature": "URLMap(not_found_app=None)",
        },
        "environment": {
            "python": "3.12",
            "network": False,
            "timeout_seconds": 90,
            "dependency_lock": "requirements.lock",
            "allowed_dependencies": [],
            "forbidden_dependencies": ["Paste", "paste"],
            "forbidden_imports": ["paste"],
            "forbidden_paths": ["repo/", "paste/"],
        },
        "tests": {"public": "public_tests/", "hidden": "hidden_tests/", "command": "pytest"},
        "spec_status": "compliant",
        "public_spec": {
            "title": "URLMap prefix dispatch",
            "summary": "Build a standalone `featurelifted` package providing Paste-style `URLMap` prefix dispatch for WSGI applications.",
            "required_api": [
                {
                    "path": "featurelifted.URLMap",
                    "kind": "class",
                    "signature": "(not_found_app=None)",
                    "members": [
                        {
                            "path": "featurelifted.URLMap.__init__",
                            "kind": "method",
                            "signature": "(self, not_found_app=None)",
                        },
                        {
                            "path": "featurelifted.URLMap.__setitem__",
                            "kind": "method",
                            "signature": "(self, url, app) -> None",
                        },
                        {
                            "path": "featurelifted.URLMap.__getitem__",
                            "kind": "method",
                            "signature": "(self, url)",
                        },
                        {
                            "path": "featurelifted.URLMap.__call__",
                            "kind": "method",
                            "signature": "(self, environ, start_response)",
                        },
                    ],
                }
            ],
            "optional_api": [],
            "behaviors": behaviors,
            "exclusions": [
                "HTTP server sockets",
                "Paste Deploy config factories",
                "HTTPS/proxy applications",
                "runtime import of paste",
            ],
            "forbidden": {"imports": ["paste"], "paths": []},
        },
        "evaluation_spec": {
            "public_clauses": [clause(b["id"], b["text"]) for b in behaviors],
            "public_test_mappings": [
                mapping("public_tests/test_public_api.py::test_prefix_dispatch_strips_matched_path", ["B001"]),
                mapping("public_tests/test_public_api.py::test_longest_prefix_wins", ["B002"]),
                mapping("public_tests/test_public_api.py::test_unknown_path_is_not_found", ["B003"]),
                mapping("public_tests/test_public_api.py::test_remaining_path_is_forwarded", ["B001", "B002"]),
            ],
            "hidden_test_mappings": [
                mapping(
                    "hidden_tests/test_hidden_behavior.py::test_longer_prefix_does_not_steal_shorter_unrelated_path",
                    ["B001", "B002"],
                ),
                mapping("hidden_tests/test_hidden_behavior.py::test_domain_specific_mount", ["B004"]),
                mapping("hidden_tests/test_hidden_behavior.py::test_unknown_path_is_not_found", ["B003"]),
                mapping("hidden_tests/test_hidden_behavior.py::test_getitem_roundtrip", ["B005"]),
                mapping("hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface", ["B006"]),
                mapping(API_SURFACE, ["B005"]),
            ],
            "required_api_coverage": [
                coverage("featurelifted.URLMap", API_SURFACE),
                coverage("featurelifted.URLMap.__init__", API_SURFACE),
                coverage("featurelifted.URLMap.__setitem__", API_SURFACE),
                coverage("featurelifted.URLMap.__getitem__", API_SURFACE),
                coverage("featurelifted.URLMap.__call__", API_SURFACE),
            ],
            "manual_review": REVIEW,
        },
    }


def main() -> int:
    builders = {
        "paste__dispatch_map_core__001": paste,
        "polyfactory__model_factory_core__001": polyfactory,
        "graphene__schema_execute_core__001": graphene,
    }
    exit_code = 0
    for task_id, builder in builders.items():
        task_dir = PILOT / task_id
        metadata = builder()
        (task_dir / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
        result = sync_task(task_dir, validate=True)
        print(json.dumps(result, ensure_ascii=False))
        if result.get("valid") is False:
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
