#!/usr/bin/env python3.12
"""Copy remaining Hard-50 pins into hard50_pilot repo/ + import-rewritten oracles."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from materialize_hard50_pilot_oracles import (  # noqa: E402
    PIN_ROOT,
    PILOT,
    append_init,
    copy_repo,
    copy_rewritten,
    update_oracle_manifest,
    write_lock,
)

TEST_DIR_NAMES = {"tests", "test", "testing"}

TASKS: dict[str, dict] = {
    "zope_component__site_lookup_core__001": {
        "src": "src/zope/component",
        "old": "zope.component",
        "deps": ["zope.interface==7.2", "zope.event==5.1"],
    },
    "connexion__openapi_resolver_core__001": {"src": "connexion", "old": "connexion", "deps": []},
    "apispec__plugin_documenter_core__001": {"src": "src/apispec", "old": "apispec", "deps": ["packaging==25.0"]},
    "limits__strategy_storage_core__001": {"src": "limits", "old": "limits", "deps": []},
    "oauthlib__grant_dispatch_core__001": {"src": "oauthlib", "old": "oauthlib", "deps": []},
    "cement__controller_plugin_core__001": {"src": "cement", "old": "cement", "deps": []},
    "falcon__responder_routing_core__001": {"src": "falcon", "old": "falcon", "deps": []},
    "pre_commit__config_load_core__001": {"src": "pre_commit", "old": "pre_commit", "deps": ["cfgv==3.4.0", "identify==2.6.1", "nodeenv==1.9.1", "pyyaml==6.0.2", "virtualenv==20.29.3"]},
    "pylint__config_find_core__001": {"src": "pylint", "old": "pylint", "deps": []},
    "django_environ__env_cast_core__001": {"src": "environ", "old": "environ", "deps": []},
    "copier__template_answers_core__001": {"src": "copier", "old": "copier", "deps": []},
    "python_configuration__layered_config_core__001": {"src": "src/config", "old": "config", "deps": ["PyYAML==6.0.2"]},
    "goodconf__typed_env_core__001": {"src": "goodconf", "old": "goodconf", "deps": []},
    "bandit__config_plugin_core__001": {"src": "bandit", "old": "bandit", "deps": ["PyYAML==6.0.2", "stevedore==5.6.0"]},
    "anyio__task_group_core__001": {"src": "src/anyio", "old": "anyio", "deps": ["idna==3.19", "sniffio==1.3.1"]},
    "dramatiq__actor_stub_broker_core__001": {"src": "dramatiq", "old": "dramatiq", "deps": []},
    "spiffworkflow__bpmn_engine_core__001": {"src": "SpiffWorkflow", "old": "SpiffWorkflow", "deps": []},
    "authlib__oauth2_server_core__001": {"src": "authlib", "old": "authlib", "deps": []},
    "beaker__session_cache_core__001": {"src": "beaker", "old": "beaker", "deps": []},
    "rocketry__cond_schedule_core__001": {"src": "rocketry", "old": "rocketry", "deps": []},
    "pandera__dataframe_schema_core__001": {"src": "pandera", "old": "pandera", "deps": ["pandas==2.2.3", "numpy==2.2.6", "packaging==25.0", "typing-extensions==4.15.0"]},
    "mashumaro__dataclass_codec_core__001": {"src": "mashumaro", "old": "mashumaro", "deps": ["typing-extensions==4.15.0"]},
    "fastjsonschema__compile_validate_core__001": {"src": "fastjsonschema", "old": "fastjsonschema", "deps": []},
    "apischema__serialization_core__001": {"src": "apischema", "old": "apischema", "deps": []},
    "typedload__type_load_core__001": {"src": "typedload", "old": "typedload", "deps": []},
    "openapi_schema_validator__draft_core__001": {"src": "openapi_schema_validator", "old": "openapi_schema_validator", "deps": ["jsonschema==4.23.0", "rfc3339-validator==0.1.4"]},
    "docutils__rst_transform_core__001": {"src": "docutils/docutils", "old": "docutils", "deps": []},
    "mistune__markdown_plugin_core__001": {"src": "src/mistune", "old": "mistune", "deps": []},
    "asttokens__token_annotate_core__001": {"src": "asttokens", "old": "asttokens", "deps": []},
    "bytecode__code_roundtrip_core__001": {"src": "src/bytecode", "old": "bytecode", "deps": []},
    "pyfakefs__os_patch_core__001": {"src": "pyfakefs", "old": "pyfakefs", "deps": []},
    "httpretty__uri_stub_core__001": {"src": "httpretty", "old": "httpretty", "deps": []},
    "respx__route_mock_core__001": {"src": "respx", "old": "respx", "deps": ["httpx==0.28.1"]},
    "betamax__cassette_match_core__001": {"src": "src/betamax", "old": "betamax", "deps": ["requests==2.32.5"]},
    "oslo_policy__enforcer_core__001": {"src": "oslo_policy", "old": "oslo_policy", "deps": ["oslo.config==9.8.0", "oslo.serialization==5.8.0", "PyYAML==6.0.2", "requests==2.32.5", "stevedore==5.6.0"]},
    "cherrypy__dispatch_tool_core__001": {"src": "cherrypy", "old": "cherrypy", "deps": []},
    "quart__blueprint_dispatch_core__001": {"src": "src/quart", "old": "quart", "deps": []},
    "redbaron__fst_mutate_core__001": {"src": "redbaron", "old": "redbaron", "deps": []},
    "routes__mapper_match_core__001": {"src": "routes", "old": "routes", "deps": []},
    "wcmatch__globmatch_core__001": {"src": "wcmatch", "old": "wcmatch", "deps": ["bracex==2.5.post1"]},
}


def strip_tests(package_root: Path) -> None:
    for path in list(package_root.rglob("*")):
        if path.is_dir() and path.name in TEST_DIR_NAMES:
            shutil.rmtree(path)


def materialize() -> None:
    for task_id, spec in TASKS.items():
        clone = PIN_ROOT / task_id
        src = clone / spec["src"]
        if not clone.exists() or not src.exists():
            print(f"SKIP missing {task_id} src={src}")
            continue
        task_dir = PILOT / task_id
        task_dir.mkdir(parents=True, exist_ok=True)
        print(f"materializing {task_id}")
        copy_repo(clone, task_dir / "repo")
        dest = task_dir / "reference_solution" / "featurelifted"
        copy_rewritten(src, dest, spec["old"], spec.get("extra"))
        strip_tests(dest)
        if spec.get("init"):
            append_init(dest, spec["init"])
        write_lock(task_dir, spec.get("deps") or [])
        (task_dir / "evaluation").mkdir(exist_ok=True)
        (task_dir / "evaluation" / "forbidden_imports.txt").write_text(spec["old"] + "\n", encoding="utf-8")
        py_files = sorted(str(p.relative_to(dest)).replace("\\", "/") for p in dest.rglob("*.py") if p.is_file())
        update_oracle_manifest(
            task_dir,
            spec["old"],
            [f"{spec['old']}/{name}" for name in py_files[:40]],
            [line.split("==")[0] for line in spec.get("deps") or []],
            "Import-rewritten upstream package used as oracle; in-package tests stripped.",
        )


if __name__ == "__main__":
    materialize()
