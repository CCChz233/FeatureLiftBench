#!/usr/bin/env python3
"""Emit Hard-50 design cards, ledger, matrix JSON, and empty registries.

Does not pin commits or materialize task packages.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CARDS = ROOT / "benchmark/selection/hard50_design_cards"
LEDGER = ROOT / "benchmark/selection/hard50_expansion_20260827.json"
MATRIX = ROOT / "benchmark/selection/hard50_selection_matrix.json"
HARD50_REGISTRY = ROOT / "benchmark/sources/hard50_registry.json"
COMBINED_REGISTRY = ROOT / "benchmark/sources/python200_hard_registry.json"
SUITE = ROOT / "benchmark/selection/python200_hard_suite.json"

# Overlap against Python-150 + External-50 was checked on 2026-08-27.
CATALOG: list[dict[str, str]] = [
    # --- registry / plugin / dispatch (13) ---
    dict(task_id="zope_interface__adapter_registry_core__001", package="zope.interface",
         url="https://github.com/zopefoundation/zope.interface", family="registry_plugin_dispatch",
         lift="Composite", entanglement="implicit_dependency_coupling,framework_coupling",
         one_liner="Interface declarations plus adapter registry lookup",
         api="providedBy; implementer; adapter registry lookup",
         included="declare interfaces; register adapters; query adapters by interface",
         excluded="ZCA site managers beyond optional alias; persistent ZODB",
         paper_fit="RQ1/RQ4: implicit registry closure. Removing it leaves no ZCA-style dispatch evidence.",
         why_hard="Lookup is global and interface-driven; copy of one module misses registration side effects.",
         pilot="P1"),
    dict(task_id="zope_component__site_lookup_core__001", package="zope.component",
         url="https://github.com/zopefoundation/zope.component", family="registry_plugin_dispatch",
         lift="Composite", entanglement="implicit_dependency_coupling,framework_coupling",
         one_liner="Component site manager get/query utilities",
         api="getUtility; queryUtility; provideUtility; getGlobalSiteManager",
         included="register utilities; lookup by interface; missing utility behavior",
         excluded="persistent local sites; ZODB",
         paper_fit="RQ4: site-manager closure on top of zope.interface.",
         why_hard="Depends on interface identities and a global site; naive extract misses get/query semantics."),
    dict(task_id="cliff__command_dispatch_core__001", package="cliff",
         url="https://github.com/openstack/cliff", family="registry_plugin_dispatch",
         lift="Adapted", entanglement="framework_coupling,implicit_dependency_coupling",
         one_liner="Stevedore-backed CLI command load and dispatch",
         api="Command; App; CommandManager",
         included="load named commands; parse argv; dispatch take_action",
         excluded="OpenStack cloud clients; real stdout paging TTY quirks",
         paper_fit="RQ5 lift=Adapted registry: command plugins without writing a new CLI framework.",
         why_hard="Commands are entry-point loaded; Hard vs E50 Direct CLI helpers.",
         pilot="P2"),
    dict(task_id="hydra_core__compose_initialize_core__001", package="hydra-core",
         url="https://github.com/facebookresearch/hydra", family="registry_plugin_dispatch",
         lift="Composite", entanglement="config_environment_coupling,implicit_dependency_coupling",
         one_liner="Compose configs with plugin search path and initialize context",
         api="initialize; compose; GlobalHydra",
         included="compose yaml groups; override dots; clear global Hydra",
         excluded="remote launchers; joblib/ray plugins",
         paper_fit="RQ1+RQ4: plugin search path + global initialize. Distinct from OmegaConf-only merge.",
         why_hard="GlobalHydra plus config groups; copy-all pulls launchers the slice forbids.",
         pilot="P3"),
    dict(task_id="dogpile_cache__region_backend_core__001", package="dogpile.cache",
         url="https://github.com/sqlalchemy/dogpile.cache", family="registry_plugin_dispatch",
         lift="Adapted", entanglement="implicit_dependency_coupling,resource_coupling",
         one_liner="Cache region with pluggable backend and dogpile lock",
         api="make_region; CacheRegion.configure; get_or_create",
         included="memory backend; get_or_create; invalidate; missing key",
         excluded="memcached/redis backends; distributed locks",
         paper_fit="RQ2+RQ4: backend registry with a large unused backend tree as copy-all decoy.",
         why_hard="Must wire region+backend+creator; copying redis backend fails isolation.",
         pilot="P4"),
    dict(task_id="kombu__serialization_registry_core__001", package="kombu",
         url="https://github.com/celery/kombu", family="registry_plugin_dispatch",
         lift="Adapted", entanglement="implicit_dependency_coupling,data_model_coupling",
         one_liner="Content-type serializer registry dumps/loads",
         api="dumps; loads; register; registry",
         included="json serializer roundtrip; register custom; unknown content type errors",
         excluded="AMQP transport; real broker",
         paper_fit="RQ4 registry without requiring a live broker.",
         why_hard="Serializers live in a global registry; transport code is a copy-all trap."),
    dict(task_id="connexion__openapi_resolver_core__001", package="connexion",
         url="https://github.com/spec-first/connexion", family="registry_plugin_dispatch",
         lift="Composite", entanglement="framework_coupling,implicit_dependency_coupling",
         one_liner="OpenAPI operationId resolver to Python view",
         api="ConnexionMiddleware or FlaskApp resolver; add_api",
         included="resolve operationId; validation error on missing required; mock backend",
         excluded="live HTTP servers; cloud auth",
         paper_fit="RQ1 framework_plugin: spec-driven dispatch, not greenfield Flask.",
         why_hard="Resolver+spec+framework coupling; E50 flask_cors never required spec closure."),
    dict(task_id="apispec__plugin_documenter_core__001", package="apispec",
         url="https://github.com/marshmallow-code/apispec", family="registry_plugin_dispatch",
         lift="Adapted", entanglement="implicit_dependency_coupling,data_model_coupling",
         one_liner="APISpec plugin hooks for path and component registration",
         api="APISpec; BasePlugin; spec.path; spec.components",
         included="register plugin; add path; component schema name",
         excluded="Marshmallow plugin-only extras beyond declared API",
         paper_fit="RQ5 Adapted plugin surface for OpenAPI documenters.",
         why_hard="Plugins mutate spec in-place via hooks; skipping plugin init looks like a pass then fails Hidden."),
    dict(task_id="limits__strategy_storage_core__001", package="limits",
         url="https://github.com/alisaifee/limits", family="registry_plugin_dispatch",
         lift="Adapted", entanglement="resource_coupling,implicit_dependency_coupling",
         one_liner="Rate-limit strategy over a storage backend",
         api="RateLimiter; MemoryStorage; parse; hit",
         included="fixed-window hit; remaining; reset; memory storage",
         excluded="Redis/Memcached storage",
         paper_fit="RQ4 strategy+storage registry with unused network backends as decoy.",
         why_hard="Strategy objects are not a single function; wrong storage silently breaks windows."),
    dict(task_id="oauthlib__grant_dispatch_core__001", package="oauthlib",
         url="https://github.com/oauthlib/oauthlib", family="registry_plugin_dispatch",
         lift="Adapted", entanglement="framework_coupling,data_model_coupling",
         one_liner="OAuth2 grant-type request validator dispatch",
         api="WebApplicationServer or Server; create_token_response",
         included="authorization code grant happy path with stub validator; invalid grant error",
         excluded="JWT/OIDC extras; HTTP servers",
         paper_fit="RQ1 protocol dispatch: grant type is a registry of handlers.",
         why_hard="Validator callbacks and grant classes are split; copy of tokens.py is insufficient."),
    dict(task_id="traitlets__configurable_core__001", package="traitlets",
         url="https://github.com/ipython/traitlets", family="registry_plugin_dispatch",
         lift="Adapted", entanglement="config_environment_coupling,framework_coupling",
         one_liner="HasTraits Configurable with from_config merge",
         api="HasTraits; Configurable; Integer/Unicode traits; update_config",
         included="default traits; config merge; validation error on bad type",
         excluded="IPython application bootstrap; kernel",
         paper_fit="RQ1+RQ5: Jupyter-stack config objects without jupyter_core overlap.",
         why_hard="Trait validation + config merge + help metadata; E50-style one-file extract fails.",
         pilot="P7"),
    dict(task_id="cement__controller_plugin_core__001", package="cement",
         url="https://github.com/datafolklabs/cement", family="registry_plugin_dispatch",
         lift="Composite", entanglement="framework_coupling,config_environment_coupling",
         one_liner="Cement App controller registration and plugin load",
         api="App; Controller; hook.register",
         included="register controller; run argv; hook callback",
         excluded="redis extensions; extra output handlers beyond declared",
         paper_fit="RQ4 framework plugin + hooks, a realistic extraction target.",
         why_hard="App lifecycle registers handlers; missing hook registration fails Hidden."),
    dict(task_id="falcon__responder_routing_core__001", package="falcon",
         url="https://github.com/falconry/falcon", family="registry_plugin_dispatch",
         lift="Direct", entanglement="framework_coupling,data_model_coupling",
         one_liner="Falcon App add_route and responder dispatch",
         api="App.add_route; Request; Response; testing.TestClient",
         included="route match; 404; method not allowed; resource responder",
         excluded="ASGI lifespan servers; WebSocket",
         paper_fit="RQ1 Direct-but-framework: routing table is the feature, rest of falcon is decoy.",
         why_hard="Router+responders+error handlers; copying whole falcon still fails compactness."),
    # --- config resolve / discover (11) ---
    dict(task_id="confuse__nested_view_core__001", package="confuse",
         url="https://github.com/beetbox/confuse", family="config_resolve_discover",
         lift="Adapted", entanglement="config_environment_coupling,data_model_coupling",
         one_liner="Nested Configuration views with templates and env overlay",
         api="Configuration; ConfigView; template; os.environ overlay",
         included="YAML load; dotted view; missing key; env overlay",
         excluded="Beets application; UI",
         paper_fit="RQ1 multi-source config. Distinct from python-dotenv/dynaconf already in 150/E50.",
         why_hard="Views are lazy and templated; naive dict merge fails Hidden.",
         pilot="P5"),
    dict(task_id="oslo_config__opt_group_core__001", package="oslo.config",
         url="https://github.com/openstack/oslo.config", family="config_resolve_discover",
         lift="Composite", entanglement="config_environment_coupling,implicit_dependency_coupling",
         one_liner="Cfg.CONF option groups with CLI and file overlay",
         api="ConfigOpts; Opt; OptGroup; CONF.register_opt; CONF",
         included="register opts; parse files; CLI override; default",
         excluded="OpenStack service projects; Oslo messaging",
         paper_fit="RQ4 global CONF + group registry, the classic implicit config closure.",
         why_hard="Opts must be registered before parse; copy of cfg.py without Opt types fails.",
         pilot="P6"),
    dict(task_id="pre_commit__config_load_core__001", package="pre-commit",
         url="https://github.com/pre-commit/pre-commit", family="config_resolve_discover",
         lift="Adapted", entanglement="config_environment_coupling,resource_coupling",
         one_liner="Load .pre-commit-config.yaml into Hook/Repo objects",
         api="load_config; validate; ManifestHook / ConfigHook subset",
         included="parse repos/hooks; local language; invalid schema error",
         excluded="git install; downloading hook repos; network",
         paper_fit="RQ2: huge installer/language tree is decoy around a bounded config slice.",
         why_hard="Schema+normalization+language defaults; copy-all of pre-commit is RRES~1."),
    dict(task_id="pylint__config_find_core__001", package="pylint",
         url="https://github.com/pylint-dev/pylint", family="config_resolve_discover",
         lift="Adapted", entanglement="config_environment_coupling,parser_state_coupling",
         one_liner="Find and merge pylint configuration from files",
         api="find_default_config_files; PyLinter.load_commandline_configuration subset",
         included="discover pylintrc; disable messages from config; invalid option error",
         excluded="full lint of C extensions; rewrite checkers",
         paper_fit="RQ1 discovery chain inside a large linter (copy-all trap).",
         why_hard="Config search + checker enablement; extracting one checker misses merge order."),
    dict(task_id="configargparse__layered_parse_core__001", package="ConfigArgParse",
         url="https://github.com/bw2/ConfigArgParse", family="config_resolve_discover",
         lift="Adapted", entanglement="config_environment_coupling,data_model_coupling",
         one_liner="Argparse with config-file and env overlays",
         api="ArgParser; parse_args; add_argument is_config_file",
         included="defaults < file < env < argv; unknown key; required missing",
         excluded="YAML extra parsers beyond declared",
         paper_fit="RQ5 Adapted config: argparse-shaped API with extra overlay semantics.",
         why_hard="Precedence is easy to get wrong; Hidden checks env-over-file."),
    dict(task_id="django_environ__env_cast_core__001", package="django-environ",
         url="https://github.com/joke2k/django-environ", family="config_resolve_discover",
         lift="Adapted", entanglement="framework_coupling,config_environment_coupling",
         one_liner="Env casts for Django-style settings from os.environ",
         api="Env; env.db; env.bool; env.list",
         included="bool/list/db url casts; missing required; prefix",
         excluded="running Django apps; migrate",
         paper_fit="RQ5 framework_coupling without vendoring Django.",
         why_hard="Cast helpers encode Django URL dialects; naive getenv fails db/list."),
    dict(task_id="copier__template_answers_core__001", package="copier",
         url="https://github.com/copier-org/copier", family="config_resolve_discover",
         lift="Adapted", entanglement="config_environment_coupling,resource_coupling",
         one_liner="Load copier.yml questions and compute answers",
         api="Worker or run_copy dry subset; load answers; questions",
         included="yaml questions; default answers; invalid choice",
         excluded="git clone templates; network; full project render",
         paper_fit="RQ2 large template engine with a bounded answers/config slice.",
         why_hard="Question schema + exclusion + answers file; copy-all of jinja render is wrong closure."),
    dict(task_id="python_configuration__layered_config_core__001", package="python-configuration",
         url="https://github.com/tr11/python-configuration", family="config_resolve_discover",
         lift="Adapted", entanglement="config_environment_coupling,data_model_coupling",
         one_liner="Layered config from dict/env/files with attribute access",
         api="config_from_dict; config_from_env; config_from_path; Configuration",
         included="merge layers; attribute get; missing key",
         excluded="cloud secret backends",
         paper_fit="RQ1 layered config distinct from dynaconf/omegaconf already used.",
         why_hard="Merge order and dotted keys; shallow dict wrap fails Hidden."),
    dict(task_id="goodconf__typed_env_core__001", package="goodconf",
         url="https://github.com/lincolnloop/goodconf", family="config_resolve_discover",
         lift="Adapted", entanglement="config_environment_coupling,data_model_coupling",
         one_liner="Typed GoodConf model loaded from env and files",
         api="GoodConf; Field; load; dump",
         included="env names; file overlay; validation error",
         excluded="Django integration extras beyond declared",
         paper_fit="RQ1 typed settings object (not pydantic-settings, already in 150).",
         why_hard="Field env aliases + file overlay; copying pydantic-settings mental model fails."),
    dict(task_id="bandit__config_plugin_core__001", package="bandit",
         url="https://github.com/PyCQA/bandit", family="config_resolve_discover",
         lift="Direct", entanglement="config_environment_coupling,implicit_dependency_coupling",
         one_liner="Bandit config load plus plugin test-id selection",
         api="BanditConfig; manager get_tests; config file",
         included="skip tests from config; include tests; invalid yaml",
         excluded="full AST vulnerability scan of CPython",
         paper_fit="RQ2: security scanner repo as decoy around config+plugin ids.",
         why_hard="Plugin ids are registered dynamically; config skip lists are Hidden-sensitive."),
    dict(task_id="fabric__env_config_core__001", package="fabric",
         url="https://github.com/fabric/fabric", family="config_resolve_discover",
         lift="Adapted", entanglement="framework_coupling,config_environment_coupling",
         one_liner="Fabric Config load from files and runtime overrides",
         api="Config; Connection constructor config=; load_ssh_config optional off",
         included="default config; file overlay; runtime override",
         excluded="real SSH; network; Paramiko auth",
         paper_fit="RQ4 Invoke-adjacent config (invoke already in E50) at Fabric layer.",
         why_hard="Config object is nested and SSH-flavored; tests must stay offline."),
    # --- workflow / session (8) ---
    dict(task_id="trio__nursery_cancel_core__001", package="trio",
         url="https://github.com/python-trio/trio", family="workflow_session_orchestration",
         lift="Composite", entanglement="framework_coupling,data_model_coupling",
         one_liner="Nursery start and CancelScope timeout/cancel",
         api="trio.run; open_nursery; CancelScope; would_block clocks via trio.testing",
         included="child task complete; cancel scope; timeout",
         excluded="guest-mode; IOCP; real sockets",
         paper_fit="RQ4 lifecycle/cancel Hidden. Distinct from tenacity retry in 150.",
         why_hard="Structured concurrency invariants; copying trio.socket fails isolation.",
         pilot="P8"),
    dict(task_id="anyio__task_group_core__001", package="anyio",
         url="https://github.com/agronholm/anyio", family="workflow_session_orchestration",
         lift="Adapted", entanglement="framework_coupling,implicit_dependency_coupling",
         one_liner="Backend-agnostic TaskGroup and CancelScope",
         api="create_task_group; fail_after; run",
         included="task group success; cancel; timeout",
         excluded="trio+asyncio dual production servers",
         paper_fit="RQ5 Adapted workflow over a backend factory (implicit backend pick).",
         why_hard="Backend plugin via sniffio; wrong backend or missing cancel semantics fail Hidden."),
    dict(task_id="luigi__task_requires_core__001", package="luigi",
         url="https://github.com/spotify/luigi", family="workflow_session_orchestration",
         lift="Composite", entanglement="implicit_dependency_coupling,resource_coupling",
         one_liner="Task requires/output with local target and build",
         api="Task; LocalTarget; build; requires",
         included="diamond requires; complete(); local file target",
         excluded="central scheduler HTTP; hdfs; spark",
         paper_fit="RQ2+RQ4: DAG orchestration with a huge unused contrib/ tree.",
         why_hard="requires() graph + complete() + targets; copy scheduler web fails compactness.",
         pilot="P9"),
    dict(task_id="dramatiq__actor_stub_broker_core__001", package="dramatiq",
         url="https://github.com/Bogdanp/dramatiq", family="workflow_session_orchestration",
         lift="Composite", entanglement="implicit_dependency_coupling,framework_coupling",
         one_liner="Actor send/get with StubBroker middleware",
         api="actor; StubBroker; Middleware; get_broker",
         included="send message; middleware before/after; retries off",
         excluded="RabbitMQ/Redis brokers",
         paper_fit="RQ4 actor registry + broker; unused brokers are copy-all decoy.",
         why_hard="Global broker and middleware chain; extracting @actor decorator only fails."),
    dict(task_id="spiffworkflow__bpmn_engine_core__001", package="SpiffWorkflow",
         url="https://github.com/sartography/SpiffWorkflow", family="workflow_session_orchestration",
         lift="Composite", entanglement="data_model_coupling,parser_state_coupling",
         one_liner="Load a small BPMN and run to completion",
         api="BpmnWorkflow; BpmnParser; do_engine_steps",
         included="start event; script/manual task subset; completed state",
         excluded="BPMN editor UI; DMN full suite",
         paper_fit="RQ4 real process-engine extraction, not a toy state enum.",
         why_hard="Parser+spec+workflow instance; E50 python-statemachine is a smaller cousin."),
    dict(task_id="authlib__oauth2_server_core__001", package="authlib",
         url="https://github.com/lepture/authlib", family="workflow_session_orchestration",
         lift="Adapted", entanglement="framework_coupling,data_model_coupling",
         one_liner="OAuth2 authorization-code token issuance with in-memory grants",
         api="AuthorizationServer; AuthorizationCodeGrant; save_token",
         included="create_authorization_response; create_token_response; invalid client",
         excluded="Flask/Django full apps; JWK cloud KMS",
         paper_fit="RQ1 session protocol. joserfc/pyjwt in E50 are token codecs, not grant workflow.",
         why_hard="Grant registry + validator + token mixing; token-only extract fails Hidden."),
    dict(task_id="beaker__session_cache_core__001", package="Beaker",
         url="https://github.com/bbangert/beaker", family="workflow_session_orchestration",
         lift="Adapted", entanglement="resource_coupling,framework_coupling",
         one_liner="Memory session save/load and namespace cache",
         api="Session; CacheManager; MemoryNamespaceManager",
         included="set/get session keys; persist memory; cache get_or_create",
         excluded="database/memcached namespaces; cookie crypto beyond declared",
         paper_fit="RQ4 session+cache backends; unused backends are decoy.",
         why_hard="Namespace managers are plugin-like; cookie vs memory mismatch fails Hidden."),
    dict(task_id="rocketry__cond_schedule_core__001", package="rocketry",
         url="https://github.com/Miksus/rocketry", family="workflow_session_orchestration",
         lift="Direct", entanglement="data_model_coupling,config_environment_coupling",
         one_liner="Condition parsing and Session task registration",
         api="Session; task; time conditions; session.run(once)",
         included="true/false condition; register task; run once without sleep wall-clock via time mock if declared",
         excluded="production scheduler loops; remote",
         paper_fit="RQ5 Direct scheduler DSL inside a larger session object.",
         why_hard="Condition language + session; Hidden checks combination operators."),
    # --- validate / normalize / construct (9) ---
    dict(task_id="pandera__dataframe_schema_core__001", package="pandera",
         url="https://github.com/unionai-oss/pandera", family="validate_normalize_construct",
         lift="Composite", entanglement="data_model_coupling,third_party_dependency_coupling",
         one_liner="DataFrameSchema validate and coerce with pandas",
         api="DataFrameSchema; Column; check; validate",
         included="dtype checks; coerce; SchemaError on bad column",
         excluded="Spark/Dask backends; cloud",
         paper_fit="RQ1+RQ4 stateful schema over a third-party dataframe (allowed pandas).",
         why_hard="Column checks compose; copying examples without SchemaModel fails Hidden."),
    dict(task_id="openapi_core__request_validate_core__001", package="openapi-core",
         url="https://github.com/python-openapi/openapi-core", family="validate_normalize_construct",
         lift="Composite", entanglement="data_model_coupling,framework_coupling",
         one_liner="Validate request/response against an OpenAPI spec",
         api="OpenAPI.from_dict; unmarshal_request; validate_response",
         included="valid request; missing required; response schema error",
         excluded="live servers; full Starlette integration extras",
         paper_fit="RQ4 unmarshalling vs jsonschema-only (jsonschema already in 150).",
         why_hard="Spec+request+unmarshal types; naive jsonschema.validate misses media types.",
         pilot="P10"),
    dict(task_id="mashumaro__dataclass_codec_core__001", package="mashumaro",
         url="https://github.com/Fatal1ty/mashumaro", family="validate_normalize_construct",
         lift="Adapted", entanglement="data_model_coupling,implicit_dependency_coupling",
         one_liner="DataClassDictMixin to_dict/from_dict with aliases",
         api="DataClassDictMixin; field metadata; to_dict; from_dict",
         included="alias; omit_none; missing required; nested",
         excluded="orjson/msgpack engines",
         paper_fit="RQ5 Adapted codec distinct from marshmallow/pydantic/cattrs already used.",
         why_hard="Mixin codegen and config; copying mashumaro/json only fails dialects."),
    dict(task_id="fastjsonschema__compile_validate_core__001", package="fastjsonschema",
         url="https://github.com/horejsek/python-fastjsonschema", family="validate_normalize_construct",
         lift="Adapted", entanglement="parser_state_coupling,data_model_coupling",
         one_liner="Compile a JSON Schema into a validator callable",
         api="compile; JsonSchemaValueException",
         included="draft-style required/type; compile once; invalid value exception",
         excluded="code-dump debugging CLI",
         paper_fit="RQ1 compiled validator vs jsonschema library already in 150.",
         why_hard="Compiler output must match formats/required; wrong draft fails Hidden."),
    dict(task_id="dependency_injector__container_core__001", package="dependency-injector",
         url="https://github.com/ets-labs/python-dependency-injector", family="validate_normalize_construct",
         lift="Composite", entanglement="implicit_dependency_coupling,framework_coupling",
         one_liner="Declarative container providers and wiring",
         api="DeclarativeContainer; providers.Factory; providers.Singleton; container.wire",
         included="factory vs singleton identity; override; missing provider",
         excluded="Flask/Django wiring extras beyond declared",
         paper_fit="RQ4 construct+registry: DI graph is the extraction target.",
         why_hard="Provider graph and wiring by name; copying examples/flask fails isolation."),
    dict(task_id="apischema__serialization_core__001", package="apischema",
         url="https://github.com/wyfo/apischema", family="validate_normalize_construct",
         lift="Adapted", entanglement="data_model_coupling,implicit_dependency_coupling",
         one_liner="Typed deserialize/serialize with conversions",
         api="deserialize; serialize; validator; conversions",
         included="dataclass roundtrip; validation error; conversion",
         excluded="GraphQL extra",
         paper_fit="RQ5 typed (de)ser not covered by mashumaro/pydantic slices.",
         why_hard="Conversion registry is implicit; Hidden checks alias and error paths."),
    dict(task_id="typedload__type_load_core__001", package="typedload",
         url="https://github.com/ltworf/typedload", family="validate_normalize_construct",
         lift="Direct", entanglement="data_model_coupling,parser_state_coupling",
         one_liner="Load JSON-like data into typing-annotated types",
         api="load; dump; typecheck",
         included="TypedDict/dataclass; union; extra key error",
         excluded="attr plugin extras beyond declared",
         paper_fit="RQ1 Direct constructor from types; still needs union/error Hidden.",
         why_hard="Union and extra-key policy; naive json.loads+TypeError fails."),
    dict(task_id="polyfactory__model_factory_core__001", package="polyfactory",
         url="https://github.com/litestar-org/polyfactory", family="validate_normalize_construct",
         lift="Adapted", entanglement="data_model_coupling,implicit_dependency_coupling",
         one_liner="ModelFactory build for dataclasses/pydantic-like models",
         api="DataclassFactory; build; coverage; use_args",
         included="build instance; overrides; collection fields",
         excluded="SQLAlchemy plugin; faker providers beyond declared",
         paper_fit="RQ5 construct factories; Litestar monorepo is a copy-all trap.",
         why_hard="Factory metaclass + type inspection; copying faker calls is not the feature."),
    dict(task_id="openapi_schema_validator__draft_core__001", package="openapi-schema-validator",
         url="https://github.com/python-openapi/openapi-schema-validator", family="validate_normalize_construct",
         lift="Direct", entanglement="data_model_coupling,parser_state_coupling",
         one_liner="OpenAPI-dialect JSON Schema validator",
         api="validate; OAS30/OAS31 format dialect",
         included="nullable; discriminator subset; invalid type",
         excluded="full OpenAPI document walk (that's openapi-core)",
         paper_fit="RQ5 dialect validator vs jsonschema 150 and openapi-core companion.",
         why_hard="OAS nullable/discriminator differ from JSON Schema; copy jsonschema fails."),
    # --- parse / transpile deep (4) ---
    dict(task_id="docutils__rst_transform_core__001", package="docutils",
         url="https://github.com/docutils/docutils", family="parse_tokenize_decode",
         lift="Adapted", entanglement="parser_state_coupling,data_model_coupling",
         one_liner="Publish RST to doctree and apply a transform",
         api="publish_doctree; nodes; Transformer",
         included="parse paragraph/section; doctree walk; invalid RST error",
         excluded="full HTML writer themes; Sphinx (already in 150)",
         paper_fit="RQ5 deep parser state, not E50 tinycss2 roundtrip.",
         why_hard="Settings+parser+transforms; copy rst2html launcher is the wrong closure."),
    dict(task_id="mistune__markdown_plugin_core__001", package="mistune",
         url="https://github.com/lepture/mistune", family="parse_tokenize_decode",
         lift="Adapted", entanglement="parser_state_coupling,implicit_dependency_coupling",
         one_liner="Markdown create_markdown with plugins and renderer",
         api="create_markdown; HTMLRenderer; plugins",
         included="emphasis/code; plugin hook; render html subset",
         excluded="full CLI; every plugin in tree",
         paper_fit="RQ4 plugin-parser: unused plugins are decoy.",
         why_hard="Plugin tokens + renderer methods; copying mistune.md examples fails Hidden."),
    dict(task_id="asttokens__token_annotate_core__001", package="asttokens",
         url="https://github.com/gristlabs/asttokens", family="parse_tokenize_decode",
         lift="Direct", entanglement="parser_state_coupling,data_model_coupling",
         one_liner="Annotate AST nodes with source tokens",
         api="ASTTokens; get_text; get_token",
         included="annotate tree; get_text for node; comment tokens optional if declared",
         excluded="executing/stack_data full traceback UX",
         paper_fit="RQ1 parser-state Direct with real AST coupling.",
         why_hard="Token/AST alignment is Hidden-sensitive; ast.parse alone fails."),
    dict(task_id="bytecode__code_roundtrip_core__001", package="bytecode",
         url="https://github.com/MatthieuDartiailh/bytecode", family="parse_tokenize_decode",
         lift="Direct", entanglement="parser_state_coupling,data_model_coupling",
         one_liner="Concrete bytecode encode/decode of a code object",
         api="Bytecode.from_code; to_code; Instr",
         included="roundtrip simple function; jump labels; stack effect error if declared",
         excluded="CPython peephole optimizer reimplementation",
         paper_fit="RQ4 instruction-stream state, not a string parser.",
         why_hard="Label/jump and opcode versions; copy dis.dis wrappers fail Hidden."),
    # --- direct tooling with copy-all trap (5) ---
    dict(task_id="pyfakefs__os_patch_core__001", package="pyfakefs",
         url="https://github.com/pytest-dev/pyfakefs", family="direct_tooling_copytrap",
         lift="Direct", entanglement="resource_coupling,framework_coupling",
         one_liner="Patch os/open path operations onto a fake filesystem",
         api="Patcher; FakeFilesystem; create_file; os.path existence",
         included="create file; read; exists; isolate from real cwd",
         excluded="full pytest plugin surface beyond declared",
         paper_fit="RQ2: large fake-os tree; feature is Patcher+FakeFilesystem, rest is decoy.",
         why_hard="Must patch the right modules; copying tests/examples leaks real FS."),
    dict(task_id="httpretty__uri_stub_core__001", package="HTTPretty",
         url="https://github.com/gabrielfalcao/HTTPretty", family="direct_tooling_copytrap",
         lift="Direct", entanglement="framework_coupling,resource_coupling",
         one_liner="Stub HTTP via httpretty.register_uri and last request",
         api="httpretty.enable; register_uri; last_request; disable",
         included="GET stub body; query; reset",
         excluded="real sockets; http2",
         paper_fit="RQ2 HTTP stub inside a repo with many unused adapters.",
         why_hard="Socket intercept vs requests adapters; E50 vcrpy is cassette file IO, this is monkeypatch."),
    dict(task_id="respx__route_mock_core__001", package="respx",
         url="https://github.com/lundberg/respx", family="direct_tooling_copytrap",
         lift="Direct", entanglement="framework_coupling,data_model_coupling",
         one_liner="httpx mock router with route.return_value",
         api="MockRouter; route; call.called; mock",
         included="match method/url; side_effect; call count",
         excluded="live httpx network",
         paper_fit="RQ2 httpx-oriented mock (httpx already in 150) with a bounded router slice.",
         why_hard="Route matching patterns; copying httpx internals fails isolation."),
    dict(task_id="betamax__cassette_match_core__001", package="betamax",
         url="https://github.com/betamaxpy/betamax", family="direct_tooling_copytrap",
         lift="Direct", entanglement="resource_coupling,framework_coupling",
         one_liner="Betamax cassette record/replay against a stubed session",
         api="Betamax; use_cassette; configure",
         included="replay recorded json cassette; match uri; missing cassette error",
         excluded="live recording to network",
         paper_fit="RQ5 vs E50 vcrpy: requests Session integration, still copy-trap on unused matchers.",
         why_hard="Matcher set + cassette format; naive json dump fails Hidden matchers."),
    dict(task_id="pyhamcrest__matcher_core__001", package="PyHamcrest",
         url="https://github.com/hamcrest/PyHamcrest", family="direct_tooling_copytrap",
         lift="Direct", entanglement="data_model_coupling,implicit_dependency_coupling",
         one_liner="Matcher combinators equal_to/has_item/raises",
         api="assert_that; equal_to; has_item; raises; described_as",
         included="combinators; mismatch description; raises",
         excluded="Java Hamcrest ports unused in Python tree",
         paper_fit="RQ2 matcher library with many unused combinators as decoy.",
         why_hard="Mismatch descriptions and combinators; copying assertEqual fails Hidden."),
]

BACKUP: list[dict[str, str]] = [
    dict(task_id="oslo_policy__enforcer_core__001", package="oslo.policy",
         url="https://github.com/openstack/oslo.policy", family="registry_plugin_dispatch",
         lift="Composite", entanglement="implicit_dependency_coupling,config_environment_coupling",
         one_liner="Policy enforcer with registered rules",
         api="Enforcer; Rule; register",
         included="load rules; enforce; default rule",
         excluded="OpenStack service policy.json farms",
         paper_fit="Backup for registry slot: policy rule registry.",
         why_hard="Rule parsers + enforcer; same family as oslo.config."),
    dict(task_id="cherrypy__dispatch_tool_core__001", package="CherryPy",
         url="https://github.com/cherrypy/cherrypy", family="registry_plugin_dispatch",
         lift="Composite", entanglement="framework_coupling,implicit_dependency_coupling",
         one_liner="CherryPy request dispatch and Tools hooks",
         api="Application; _cptools; expose",
         included="URL dispatch; tool hook; 404",
         excluded="production server sockets",
         paper_fit="Backup framework dispatch if falcon/connexion blocked.",
         why_hard="Tools registry + dispatch; huge unused servers."),
    dict(task_id="quart__blueprint_dispatch_core__001", package="quart",
         url="https://github.com/pallets/quart", family="registry_plugin_dispatch",
         lift="Adapted", entanglement="framework_coupling,data_model_coupling",
         one_liner="Quart app routing and blueprint register",
         api="Quart; Blueprint; test_client",
         included="route; blueprint; 404",
         excluded="hypercorn production",
         paper_fit="Backup Flask-family async dispatch without duplicating Flask 150.",
         why_hard="ASGI+blueprint; copy flask mental model misses async app."),
    dict(task_id="injector__module_bind_core__001", package="injector",
         url="https://github.com/python-injector/injector", family="validate_normalize_construct",
         lift="Adapted", entanglement="implicit_dependency_coupling,data_model_coupling",
         one_liner="Injector Module binder and get",
         api="Injector; Module; inject; Binder",
         included="bind; singleton vs noscope; missing binding",
         excluded="thread locals extras",
         paper_fit="Backup DI if dependency-injector native bits block.",
         why_hard="Binder graph; similar RQ4 construct+registry."),
    dict(task_id="myst_parser__md_to_docutils_core__001", package="myst-parser",
         url="https://github.com/executablebooks/MyST-Parser", family="parse_tokenize_decode",
         lift="Adapted", entanglement="parser_state_coupling,framework_coupling",
         one_liner="MyST markdown to docutils nodes",
         api="Parser; to_docutils; MdParserConfig",
         included="heading/link; fence; config disable",
         excluded="full Sphinx extension runtime",
         paper_fit="Backup deep markdown/docutils if docutils slice blocked.",
         why_hard="Sphinx-coupled parser; copy markdown-it-py (already in 150) is not enough."),
    dict(task_id="redbaron__fst_mutate_core__001", package="redbaron",
         url="https://github.com/PyCQA/redbaron", family="parse_tokenize_decode",
         lift="Adapted", entanglement="parser_state_coupling,data_model_coupling",
         one_liner="FST parse and mutate a function",
         api="RedBaron; find; dumps",
         included="parse; rename name node; dumps roundtrip",
         excluded="baron internals dump formats unused",
         paper_fit="Backup if asttokens/bytecode too VM-specific.",
         why_hard="FST vs AST; Hidden checks formatting preservation."),
    dict(task_id="executing__source_node_core__001", package="executing",
         url="https://github.com/alexmojaki/executing", family="parse_tokenize_decode",
         lift="Direct", entanglement="parser_state_coupling,resource_coupling",
         one_liner="Map a frame to the AST node being executed",
         api="Source.executing; node; text",
         included="simple call frame; node type; source text",
         excluded="ipython display",
         paper_fit="Backup parser-state Direct.",
         why_hard="Frame/AST mapping is fragile; naive inspect.getsource fails."),
    dict(task_id="graphene__schema_execute_core__001", package="graphene",
         url="https://github.com/graphql-python/graphene", family="workflow_session_orchestration",
         lift="Composite", entanglement="data_model_coupling,framework_coupling",
         one_liner="Graphene Schema execute a query",
         api="ObjectType; Schema; schema.execute",
         included="resolver; arguments; error path",
         excluded="Django integration",
         paper_fit="Backup workflow: GraphQL execution session.",
         why_hard="Type registry + execute; copy graphql-core only fails graphene mapping."),
    dict(task_id="taskiq__broker_task_core__001", package="taskiq",
         url="https://github.com/taskiq-python/taskiq", family="workflow_session_orchestration",
         lift="Composite", entanglement="implicit_dependency_coupling,framework_coupling",
         one_liner="InMemoryBroker task send/kicker",
         api="InMemoryBroker; task; kiq",
         included="register task; kiq; result",
         excluded="Redis/NATS brokers",
         paper_fit="Backup for dramatiq slot.",
         why_hard="Broker plugin + task registry."),
    dict(task_id="webob__request_response_core__001", package="WebOb",
         url="https://github.com/Pylons/webob", family="direct_tooling_copytrap",
         lift="Direct", entanglement="framework_coupling,data_model_coupling",
         one_liner="WebOb Request/Response from environ",
         api="Request; Response; Request.blank",
         included="GET/POST; headers; json_body",
         excluded="full Pyramid (already in 150)",
         paper_fit="Backup WSGI request object with Pyramid decoy nearby in ecosystem.",
         why_hard="Ad-hoc dict environ vs Request API; Hidden header case."),
    dict(task_id="routes__mapper_match_core__001", package="routes",
         url="https://github.com/nandoflorestan/routes", family="registry_plugin_dispatch",
         lift="Adapted", entanglement="data_model_coupling,framework_coupling",
         one_liner="Mapper connect and match/generate",
         api="Mapper; connect; match; generate",
         included="static route; wildcard; generate url",
         excluded="web frameworks",
         paper_fit="Backup routing table if falcon blocked.",
         why_hard="Match vs generate inverse; conditions."),
    dict(task_id="pika__channel_spec_core__001", package="pika",
         url="https://github.com/pika/pika", family="workflow_session_orchestration",
         lift="Adapted", entanglement="protocol_state_coupling,resource_coupling",
         one_liner="AMQP method framing encode/decode without a broker",
         api="spec; frame; encode_table",
         included="encode/decode basic methods; table types",
         excluded="BlockingConnection to live RabbitMQ",
         paper_fit="Backup protocol-state workflow; live broker forbidden.",
         why_hard="Frame codec vs connection; copy-all connection is isolation fail."),
    dict(task_id="waitress__adjustments_core__001", package="waitress",
         url="https://github.com/Pylons/waitress", family="config_resolve_discover",
         lift="Adapted", entanglement="config_environment_coupling,framework_coupling",
         one_liner="Waitress Adjustments from kwargs/env",
         api="Adjustments; parse_args subset",
         included="host/port/threads; invalid value",
         excluded="real listen sockets",
         paper_fit="Backup config object inside a server (copy-all trap).",
         why_hard="Many knobs; Hidden checks aliases and validation."),
    dict(task_id="paste__dispatch_map_core__001", package="Paste",
         url="https://github.com/cdent/paste", family="registry_plugin_dispatch",
         lift="Adapted", entanglement="framework_coupling,config_environment_coupling",
         one_liner="URLMap / dispatch composite WSGI",
         api="URLMap; parse_map_file subset",
         included="mount apps; longest prefix; 404",
         excluded="httpserver",
         paper_fit="Backup composite WSGI dispatch.",
         why_hard="Prefix matching + factory config."),
    dict(task_id="wcmatch__globmatch_core__001", package="wcmatch",
         url="https://github.com/facelessuser/wcmatch", family="direct_tooling_copytrap",
         lift="Direct", entanglement="parser_state_coupling,data_model_coupling",
         one_liner="globmatch with flags and negate",
         api="glob.globmatch; globmatch; flags",
         included="globstar; negate; case flags",
         excluded="full directory walk of huge trees",
         paper_fit="Backup Direct copy-trap if pathspec-like needed; larger than pathspec.",
         why_hard="Flag combinations; Hidden brace/negate."),
]

PILOT_ORDER = [
    "zope_interface__adapter_registry_core__001",
    "cliff__command_dispatch_core__001",
    "hydra_core__compose_initialize_core__001",
    "dogpile_cache__region_backend_core__001",
    "confuse__nested_view_core__001",
    "oslo_config__opt_group_core__001",
    "traitlets__configurable_core__001",
    "trio__nursery_cancel_core__001",
    "luigi__task_requires_core__001",
    "openapi_core__request_validate_core__001",
]


def card_markdown(row: dict[str, str], *, disposition: str, wave: str) -> str:
    types = [t.strip() for t in row["entanglement"].split(",")]
    return f"""# Design card: {row["task_id"]}

**status:** `design_card_ready`  
**disposition:** `{disposition}`  
**wave:** `{wave}`  
**package:** `{row["package"]}`  
**repository_url:** {row["url"]}  
**planned_lift_type:** {row["lift"]}  
**final_lift_type:** pending_source_review  
**reclassification_reason:**  
**feature_family:** `{row["family"]}`  
**entanglement.level:** high  
**entanglement.types:** {", ".join(f"`{t}`" for t in types)}  
**feature_one_liner:** {row["one_liner"]}  
**commit:** pending pin  

## paper_fit

{row["paper_fit"]}

## why_hard

{row["why_hard"]}

## Balance Role

{row["family"]} / {row["lift"]} / high entanglement.

## Pinned Source

- commit: *pending pin — do not materialize until a real revision is recorded*
- license: *pending pin*
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-27 name/url screen)

## Required API (draft)

{row["api"]}

## Included Behavior (draft)

{row["included"]}

## Excluded Behavior

{row["excluded"]}

## YAML contract (to fill at pin time)

```yaml
target_api:
  module:
  signatures:
  returns:
  exceptions:
  defaults:
  state_effects:
upstream_mapping:
  primary_symbols:
  supporting_components:
  semantic_delta:
oracle_basis:
  basis: upstream
scope:
  included:
  excluded:
feasibility:
  commit:
  license:
  python_versions:
  native_or_heavy_dependencies:
  offline_resources:
acceptance:
  closure_review: pending
  reference_pass: pending
  isolation_pass: pending
  no_original_import: pending
  overlap_check: pass_name_screen
```

## Gate Status

- design card: ready for pin
- package completeness: pending
- Docker / Flash calibration: pending
- promotion to `benchmark/hard50`: blocked until Pilot gate (and then 50/50) passes
"""


def ledger_row(row: dict[str, str], disposition: str) -> dict:
    types = [t.strip() for t in row["entanglement"].split(",")]
    return {
        "task_id": row["task_id"],
        "package": row["package"],
        "repository_url": row["url"],
        "disposition": disposition,
        "planned_lift_type": row["lift"],
        "feature_family": row["family"],
        "entanglement_level": "high",
        "entanglement_types": types,
        "commit": None,
        "design_card": f"benchmark/selection/hard50_design_cards/{row['task_id']}.md",
        "paper_fit": row["paper_fit"],
        "why_hard": row["why_hard"],
    }


def main() -> int:
    CARDS.mkdir(parents=True, exist_ok=True)
    for path in CARDS.glob("*.md"):
        if path.name not in {"README.md", "_TEMPLATE.md"}:
            path.unlink()

    selected_rows = [ledger_row(r, "selected") for r in CATALOG]
    backup_rows = [ledger_row(r, "backup") for r in BACKUP]
    for row, disposition, wave in (
        [(r, "selected", "selected") for r in CATALOG]
        + [(r, "backup", "backup") for r in BACKUP]
    ):
        (CARDS / f"{row['task_id']}.md").write_text(
            card_markdown(row, disposition=disposition, wave=wave), encoding="utf-8"
        )

    family_counts: dict[str, int] = {}
    lift_counts: dict[str, int] = {}
    for r in CATALOG:
        family_counts[r["family"]] = family_counts.get(r["family"], 0) + 1
        lift_counts[r["lift"]] = lift_counts.get(r["lift"], 0) + 1

    ledger = {
        "schema_version": "featureliftbench.hard50_expansion.v1",
        "selection_id": "hard50-expansion-20260827-v0-cards",
        "status": "design_cards_unpinned",
        "notes": (
            "Phase 0 only. Commits are not pinned. Do not materialize or run Flash "
            "until Pilot 10 is approved and pinned."
        ),
        "python150_freeze_id": "846b814726217623fa205cb7688bee61e6c21c43efda1ebd05e79b5ed8cb4fbd",
        "keep_external50": True,
        "new_main_suite": "python200-hard (150 + Hard-50); External-50 is a side split",
        "targets": {
            "selected": 50,
            "backup": 15,
            "families": family_counts,
            "lift_types": lift_counts,
        },
        "pilot_candidates": PILOT_ORDER,
        "rows": selected_rows + backup_rows,
    }
    LEDGER.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    matrix = {
        "schema_version": "featureliftbench.hard50_selection_matrix.v1",
        "doc": "docs/hard50_selection_matrix.md",
        "families": [
            {"id": "registry_plugin_dispatch", "target_n": 13, "rqs": ["RQ1", "RQ4", "RQ5"]},
            {"id": "config_resolve_discover", "target_n": 11, "rqs": ["RQ1", "RQ4"]},
            {"id": "workflow_session_orchestration", "target_n": 8, "rqs": ["RQ1", "RQ4"]},
            {"id": "validate_normalize_construct", "target_n": 9, "rqs": ["RQ1", "RQ4"]},
            {"id": "parse_tokenize_decode", "target_n": 4, "rqs": ["RQ1", "RQ5"]},
            {"id": "direct_tooling_copytrap", "target_n": 5, "rqs": ["RQ2", "RQ5"]},
        ],
        "realized_selected_families": family_counts,
        "realized_selected_lifts": lift_counts,
        "entanglement_policy": {
            "level": "high",
            "min_types": 2,
            "prefer": ["implicit_dependency_coupling", "framework_coupling"],
        },
        "repo_policy": {
            "min_python_loc_median_target": 8000,
            "no_overlap_with": [
                "benchmark/sources/registry.json",
                "benchmark/sources/external50_registry.json",
            ],
        },
        "calibration": {
            "flash_replace_if": ">85% or RRES≈1.0",
            "flash_prefer": "40%-65%",
            "flash_keep_if_reasonable": "20%-40%",
            "forbid": "post-hoc hidden tests to tune pass rate",
        },
    }
    MATRIX.write_text(json.dumps(matrix, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    empty_registry = {
        "schema_version": "featureliftbench.source_registry.v1",
        "policy_id": "featureliftbench.full_repository_source.v2",
        "generated_from": "hard50-expansion-20260827-v0-cards (unpinned)",
        "repositories": [],
        "snapshots": [],
        "summary": {
            "repository_count": 0,
            "snapshot_count": 0,
            "task_count": 0,
            "note": "Snapshots are added only after pin+archive.",
        },
    }
    HARD50_REGISTRY.write_text(json.dumps(empty_registry, indent=2, ensure_ascii=False) + "\n")

    combined = {
        "schema_version": "featureliftbench.source_registry.v1",
        "policy_id": "featureliftbench.full_repository_source.v2",
        "generated_from": "placeholder: frozen Python-150 registry + unpinned Hard-50",
        "repositories": [],
        "snapshots": [],
        "summary": {
            "task_count": 0,
            "note": "materialize_python200_hard_release.py fills this after Hard-50 exists.",
        },
    }
    COMBINED_REGISTRY.write_text(json.dumps(combined, indent=2, ensure_ascii=False) + "\n")

    suite = {
        "schema_version": "featureliftbench.python200_hard_suite.v1",
        "suite_id": "python200-hard-unreleased",
        "status": "not_materialized",
        "baseline_freeze_id": "846b814726217623fa205cb7688bee61e6c21c43efda1ebd05e79b5ed8cb4fbd",
        "hard50_selection_id": "hard50-expansion-20260827-v0-cards",
        "task_count": 0,
        "baseline_count": 150,
        "hard50_count": 0,
        "task_root": "benchmark/python200_hard_tasks",
        "source_registry": "benchmark/sources/python200_hard_registry.json",
        "task_ids": [],
        "note": "Do not treat this as an evaluable suite until Phase 2 release.",
    }
    SUITE.write_text(json.dumps(suite, indent=2, ensure_ascii=False) + "\n")

    print(
        f"cards={len(CATALOG)+len(BACKUP)} selected={len(CATALOG)} backup={len(BACKUP)} "
        f"families={family_counts} lifts={lift_counts}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
