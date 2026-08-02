#!/usr/bin/env python3
"""Fill External-50 design cards with executable design specs (design_card_ready)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LEDGER = ROOT / "benchmark/selection/external50_expansion_20260731.json"
CARDS = ROOT / "benchmark/selection/external50_design_cards"

# task_id -> filled sections
CARDS_DATA: dict[str, dict] = {}


def card(
    tid: str,
    *,
    final_lift: str | None = None,
    reclass: str | None = None,
    signatures: list[str],
    returns: list[str],
    exceptions: list[str],
    defaults: list[str],
    state_effects: list[str],
    primary: list[str],
    supporting: list[str],
    delta: list[str],
    basis: str,
    oracle_notes: str,
    included: list[str],
    excluded: list[str],
    license: str,
    native: str,
    offline: str,
    py: list[str] | None = None,
):
    CARDS_DATA[tid] = {
        "final_lift_type": final_lift,
        "reclassification_reason": reclass,
        "signatures": signatures,
        "returns": returns,
        "exceptions": exceptions,
        "defaults": defaults,
        "state_effects": state_effects,
        "primary": primary,
        "supporting": supporting,
        "delta": delta,
        "basis": basis,
        "oracle_notes": oracle_notes,
        "included": included,
        "excluded": excluded,
        "license": license,
        "native": native,
        "offline": offline,
        "python_versions": py or ["3.10", "3.11", "3.12"],
    }


# --- Pilot + Direct/Adapted/Composite fills ---

card(
    "semver__version_core__001",
    final_lift="Direct",
    signatures=[
        "featurelifted.Version.parse(version: str) -> Version",
        "featurelifted.Version(major: int, minor: int = 0, patch: int = 0, prerelease: str | None = None, build: str | None = None)",
        "featurelifted.Version.compare(self, other: Version) -> int",
        "featurelifted.Version.bump_major/minor/patch(self) -> Version",
        "featurelifted.Version.replace(self, **parts) -> Version",
        "str(Version) / Version.__eq__/__lt__",
    ],
    returns=["Version objects; compare returns -1/0/1; bump returns new Version"],
    exceptions=["ValueError on invalid version strings"],
    defaults=["minor/patch default 0; prerelease/build default None"],
    state_effects=["immutable Version instances"],
    primary=["semver.Version", "semver.VersionInfo (compat alias if present)"],
    supporting=[],
    delta=["Package as featurelifted; keep semver public Version API subset"],
    basis="upstream",
    oracle_notes="Direct extract of Version parse/compare/bump.",
    included=["parse, compare, bump_major/minor/patch, replace, str formatting"],
    excluded=["CLI, file reading helpers, deprecated VersionInfo-only quirks beyond alias"],
    license="BSD-3-Clause",
    native="none",
    offline="pure functions on strings",
)

card(
    "uritools__uri_join_normalize_core__001",
    final_lift="Adapted",
    signatures=[
        "featurelifted.urisplit(uri: str) -> SplitResult",
        "featurelifted.uriunsplit(parts: SplitResult | tuple) -> str",
        "featurelifted.urijoin(base: str, ref: str, strict: bool = False) -> str",
        "featurelifted.urinorm(uri: str) -> str",
        "featurelifted.uridecode(s: str, encoding: str = 'utf-8') -> str",
        "featurelifted.uriencode(s: str, safe: str = '', encoding: str = 'utf-8') -> str",
    ],
    returns=["SplitResult named fields scheme/authority/path/query/fragment; join/norm return str"],
    exceptions=["ValueError on malformed URI when strict validation applies"],
    defaults=["urijoin strict=False; encode safe=''"],
    state_effects=["none"],
    primary=["uritools.urisplit", "uritools.urijoin", "uritools.urinorm"],
    supporting=["uritools.uriencode", "uritools.uridecode"],
    delta=["Export flat featurelifted helpers; document SplitResult fields explicitly"],
    basis="upstream",
    oracle_notes="Adapted packaging of uritools helpers as one Required API surface.",
    included=["split/unsplit/join/norm/encode/decode for absolute and relative refs"],
    excluded=["network fetch, IRI-only edge tables beyond what uritools implements"],
    license="MIT",
    native="none",
    offline="string-only URI ops",
)

card(
    "cssselect__selector_xpath_core__001",
    final_lift="Adapted",
    reclass="Upstream GenericTranslator/HTMLTranslator already expose css→xpath; not a new multi-component surface. Planned Composite → Adapted.",
    signatures=[
        "featurelifted.parse(selector: str) -> SelectorGroup",
        "featurelifted.GenericTranslator().css_to_xpath(selector: str, prefix: str = 'descendant-or-self::') -> str",
        "featurelifted.HTMLTranslator().css_to_xpath(selector: str, prefix: str = 'descendant-or-self::') -> str",
        "featurelifted.SelectorError",
        "featurelifted.ExpressionError",
    ],
    returns=["xpath string; parse returns selector AST objects opaque except for translation"],
    exceptions=["SelectorError/ExpressionError on invalid selectors"],
    defaults=["prefix='descendant-or-self::'"],
    state_effects=["translators are stateless"],
    primary=["cssselect.parse", "cssselect.GenericTranslator", "cssselect.HTMLTranslator"],
    supporting=["cssselect.xpath", "cssselect.parser"],
    delta=["Task-facing Required API lists translator methods + exceptions; no invented facade"],
    basis="upstream",
    oracle_notes="Single library cssselect translation surface.",
    included=["CSS3 subset supported by cssselect; HTML vs generic translators"],
    excluded=["executing xpath against documents (lxml); scrapy Selector integration"],
    license="BSD-3-Clause",
    native="none",
    offline="string selector → xpath only",
)

card(
    "dateparser__parse_settings_pipeline_core__001",
    final_lift="Composite",
    signatures=[
        "featurelifted.Settings(**options) -> Settings",
        "featurelifted.parse(date_string: str, date_formats: list[str] | None = None, languages: list[str] | None = None, locales: list[str] | None = None, region: str | None = None, settings: Settings | dict | None = None) -> datetime | None",
        "featurelifted.detect_languages(text: str, languages: list[str] | None = None) -> list",
    ],
    returns=["datetime or None; detect_languages returns language id list"],
    exceptions=["ValueError for invalid settings keys if validated; TypeError on bad types"],
    defaults=["settings PREFER_DATES_FROM etc. as declared subset of dateparser defaults"],
    state_effects=["Settings may cache language detectors; must be process-local and offline"],
    primary=["dateparser.parse", "dateparser.conf.Settings"],
    supporting=["dateparser.languages", "dateparser.search (optional excluded)", "dateparser_data"],
    delta=["Compose Settings + language detection + parse into one declared pipeline; freeze allowed settings keys in TASK"],
    basis="mixed",
    oracle_notes="Upstream parse with Settings; language detect is supporting component. Declare exact settings keys.",
    included=["parse with formats/languages/settings; language detection helper; timezone-aware results when settings say so"],
    excluded=["dateparser.search.search_dates; network; fresh language model downloads"],
    license="BSD-3-Clause",
    native="none expected (pure python + data files)",
    offline="bundle needed locale/date data in source tree; no download",
)

card(
    "tinydb__query_storage_core__001",
    final_lift="Composite",
    signatures=[
        "featurelifted.TinyDB(storage: Storage | str) -> TinyDB",
        "featurelifted.TinyDB.insert/insert_multiple/all/get/search/update/remove/truncate/close",
        "featurelifted.Query() -> Query",
        "featurelifted.Query.fragment / field test operators (==, exists, matches, test, ... declared subset)",
        "featurelifted.JSONStorage(path: str)",
        "featurelifted.MemoryStorage()",
    ],
    returns=["doc ids; search returns list[dict]; get returns dict|None"],
    exceptions=["ValueError/RuntimeError on closed DB ops as upstream"],
    defaults=["default table name '_default'"],
    state_effects=["mutates storage; MemoryStorage in-memory only"],
    primary=["tinydb.TinyDB", "tinydb.queries.Query"],
    supporting=["tinydb.storages.JSONStorage", "tinydb.storages.MemoryStorage", "tinydb.table.Table"],
    delta=["Target API requires DB + Query + Storage together as one contract"],
    basis="upstream",
    oracle_notes="Composite of DB, query DSL, and storage backends.",
    included=["CRUD, query operators subset, JSONStorage+MemoryStorage"],
    excluded=["middleware caching, SQL storage, concurrent multi-process locking guarantees"],
    license="MIT",
    native="none",
    offline="MemoryStorage or temp JSON file",
)

card(
    "omegaconf__merge_interpolate_core__001",
    final_lift="Composite",
    signatures=[
        "featurelifted.OmegaConf.create(obj: dict | list | str | None = None) -> DictConfig | ListConfig",
        "featurelifted.OmegaConf.merge(*configs) -> DictConfig",
        "featurelifted.OmegaConf.to_container(cfg, resolve: bool = False) -> Any",
        "featurelifted.OmegaConf.select(cfg, key: str, default: Any = None) -> Any",
        "featurelifted.OmegaConf.is_missing / is_null / is_config helpers (declared subset)",
        "interpolation: ${...} resolution via resolve=True or OmegaConf.resolve(cfg)",
    ],
    returns=["DictConfig/ListConfig; to_container returns plain dict/list"],
    exceptions=["omegaconf.errors.* subset: InterpolationResolutionError, ConfigKeyError, ValidationError — list exact names in TASK"],
    defaults=["struct mode off unless set_struct; resolve default False on to_container"],
    state_effects=["configs are mutable nodes; merge returns new tree"],
    primary=["omegaconf.OmegaConf", "omegaconf.DictConfig"],
    supporting=["omegaconf.resolvers", "omegaconf.errors"],
    delta=["Compose create/merge/interpolate/select as one extraction contract"],
    basis="upstream",
    oracle_notes="Merge + interpolation + struct flags are distinct capabilities.",
    included=["dict/list config, merge, dot-select, interpolations, to_container"],
    excluded=["CLI flags, dataclass structured configs beyond declared subset, custom resolvers registration unless listed"],
    license="BSD-3-Clause",
    native="none",
    offline="in-memory configs only",
)

card(
    "watchdog__observer_dispatch_core__001",
    final_lift="Composite",
    signatures=[
        "featurelifted.Observer()",
        "featurelifted.Observer.schedule(handler, path: str, recursive: bool = False) -> Watch",
        "featurelifted.Observer.start/stop/join",
        "featurelifted.FileSystemEventHandler with on_created/modified/deleted/moved hooks",
        "featurelifted.events: FileCreatedEvent, FileModifiedEvent, ... (declared subset)",
    ],
    returns=["schedule returns watch object; events delivered to handler methods"],
    exceptions=["ValueError on invalid paths; OSError from FS"],
    defaults=["recursive=False"],
    state_effects=["background observer thread; tests must start/stop deterministically"],
    primary=["watchdog.observers.Observer", "watchdog.events.FileSystemEventHandler"],
    supporting=["watchdog.events event classes", "platform emitter"],
    delta=["Compose observer + handler + event types; tests use temp dir + short polling"],
    basis="mixed",
    oracle_notes="Emitter behavior is platform-specific; freeze test strategy with temp files and timeouts.",
    included=["schedule recursive/non-recursive, handler callbacks for create/modify/delete"],
    excluded=["inotify-specific flags, watchdog.watchmedo CLI, remote FS"],
    license="Apache-2.0",
    native="may use platform backends; pure polling fallback preferred in tests",
    offline="local temp directory only; no network",
)

card(
    "cachecontrol__heuristic_store_core__001",
    final_lift="Composite",
    signatures=[
        "featurelifted.DictCache()",
        "featurelifted.BaseCache.get/set/delete(key)",
        "featurelifted.Heuristic / ExpiresAfter(days=..., hours=...) apply(response) API (declare exact class)",
        "featurelifted.serialize/deserialize cached response body+headers helpers used by CacheController subset",
        "featurelifted.CacheController(cache, cacheable_methods=...) cached_request/update_cached_response subset",
    ],
    returns=["cache hit returns stored response parts; miss None"],
    exceptions=["KeyError/ValueError on bad cache keys if any"],
    defaults=["ExpiresAfter duration fields"],
    state_effects=["DictCache mutable"],
    primary=["cachecontrol.caches.DictCache", "cachecontrol.heuristics", "cachecontrol.controller.CacheController"],
    supporting=["cachecontrol.serialize"],
    delta=["Offline: do not wrap real urllib3; test heuristic+cache+serialize composition with fake response objects"],
    basis="mixed",
    oracle_notes="Avoid live HTTP; construct response-like objects.",
    included=["DictCache, expiration heuristic, serialize roundtrip, controller cache lookup/update"],
    excluded=["requests Session integration, FileCache, RedisCache, network"],
    license="Apache-2.0",
    native="none",
    offline="fake response objects + DictCache only",
)

card(
    "structlog__processor_chain_core__001",
    final_lift="Composite",
    signatures=[
        "featurelifted.configure(processors: list, wrapper_class=..., context_class=dict, logger_factory=..., cache_logger_on_first_use: bool = False)",
        "featurelifted.get_logger(*args, **initial_values) -> BoundLogger",
        "featurelifted.BoundLogger.bind/unbind/new(**values)",
        "featurelifted.stdlib processors subset: KeyValueRenderer, JSONRenderer, TimeStamper, add_log_level (declare list)",
        "featurelifted.reset_defaults()",
    ],
    returns=["log method calls run processor chain and emit via factory (capture with list logger)"],
    exceptions=["DropEvent if used; TypeError on bad processors"],
    defaults=["cache_logger_on_first_use False in tests"],
    state_effects=["global configure state — tests must reset_defaults"],
    primary=["structlog.configure", "structlog.get_logger", "structlog.BoundLoggerLazyProxy"],
    supporting=["structlog.processors", "structlog.stdlib"],
    delta=["Contract is configure+processors+bound logger together"],
    basis="upstream",
    oracle_notes="Use MemoryLoggerFactory or list append factory for offline capture.",
    included=["bind context, processor ordering, JSON/KeyValue render, timestamp/level"],
    excluded=["twisted/asyncio integrations, PrintLogger exotic configs"],
    license="MIT OR Apache-2.0",
    native="none",
    offline="in-memory logger factory",
)

card(
    "flask_login__session_guard_core__001",
    final_lift="Composite",
    signatures=[
        "featurelifted.LoginManager()",
        "featurelifted.LoginManager.init_app(app)",
        "featurelifted.LoginManager.user_loader(callback)",
        "featurelifted.login_user(user, remember: bool = False)",
        "featurelifted.logout_user()",
        "featurelifted.current_user proxy attributes is_authenticated/is_anonymous/get_id",
        "featurelifted.login_required decorator",
        "featurelifted.UserMixin",
    ],
    returns=["login_user returns bool; current_user is proxy"],
    exceptions=["Flask LoginException subset if any — prefer undocumented none; unauthorized handler"],
    defaults=["remember=False"],
    state_effects=["session keys _user_id/_fresh; requires Flask app/request/session context"],
    primary=["flask_login.LoginManager", "flask_login.login_user", "flask_login.current_user"],
    supporting=["flask_login.mixins.UserMixin", "flask_login.utils"],
    delta=["Compose manager+loader+session user + login_required; tests use Flask test_request_context"],
    basis="mixed",
    oracle_notes="Needs Flask as test dependency; no network. Declare Flask version bound in lockfile.",
    included=["user_loader, login/logout, login_required, UserMixin, remember flag basic"],
    excluded=["LDAP, real HTTP servers, cookie encryption beyond Flask session"],
    license="MIT",
    native="none",
    offline="Flask test client / request context only",
)

card(
    "sqlglot__parse_transpile_core__001",
    final_lift="Composite",
    signatures=[
        "featurelifted.parse_one(sql: str, read: str | None = None) -> Expression",
        "featurelifted.parse(sql: str, read: str | None = None) -> list[Expression]",
        "featurelifted.transpile(sql: str, read: str | None = None, write: str | None = None, pretty: bool = False) -> list[str]",
        "featurelifted.Expression.sql(dialect: str | None = None, pretty: bool = False) -> str",
        "featurelifted.exp node types used in tests must be listed (Select, Column, ...)",
        "featurelifted.errors.ParseError",
    ],
    returns=["Expression trees; transpile returns SQL strings"],
    exceptions=["ParseError on invalid SQL"],
    defaults=["pretty=False"],
    state_effects=["none"],
    primary=["sqlglot.parse_one", "sqlglot.transpile"],
    supporting=["sqlglot.expressions", "sqlglot.dialects", "sqlglot.optimizer (only if included)"],
    delta=["Parse + transpile (+ optional optimize if in scope) as pipeline; freeze dialect names"],
    basis="upstream",
    oracle_notes="Large repo — keep dialect subset small (e.g. sqlite/postgres/mysql).",
    included=["parse_one/parse, transpile across declared dialects, Expression.sql"],
    excluded=["execute against DB, full optimizer suite unless explicitly listed"],
    license="MIT",
    native="none",
    offline="SQL string transforms only",
)

card(
    "pyparsing__grammar_compose_core__001",
    final_lift="Adapted",
    reclass="Composing ParserElements is the normal upstream API, not a novel multi-system surface. Planned Composite → Adapted.",
    signatures=[
        "featurelifted.Word / Literal / Keyword / Regex / Optional / ZeroOrMore / OneOrMore / Group / Suppress helpers used",
        "featurelifted.ParserElement.parse_string(instring, parse_all: bool = False)",
        "featurelifted.ParseResults accessors (as_list, as_dict, named results)",
        "featurelifted.ParseException",
    ],
    returns=["ParseResults"],
    exceptions=["ParseException with loc/msg"],
    defaults=["parse_all=False"],
    state_effects=["grammars may set parse actions — declare if used"],
    primary=["pyparsing.ParserElement", "pyparsing.core common helpers"],
    supporting=["pyparsing.results.ParseResults"],
    delta=["Task provides a sample composed grammar API surface rather than inventing a new engine"],
    basis="upstream",
    oracle_notes="Adapted extract of pyparsing composition+parse.",
    included=["build grammar from helpers, parse_string, named results, ParseException"],
    excluded=["diagram generation, railroad, infixNotation full suite unless listed"],
    license="MIT",
    native="none",
    offline="string parse only",
)

card(
    "tinycss2__stylesheet_roundtrip_core__001",
    final_lift="Adapted",
    reclass="parse_stylesheet + serialize are paired upstream entrypoints. Planned Composite → Adapted.",
    signatures=[
        "featurelifted.parse_stylesheet(css: str, skip_comments: bool = False, skip_whitespace: bool = False) -> list",
        "featurelifted.parse_rule_list(...)",
        "featurelifted.parse_component_value_list(...)",
        "featurelifted.serialize(nodes) -> str",
        "node types: QualifiedRule, AtRule, ParseError — declare tested ones",
    ],
    returns=["list of nodes; serialize returns CSS string"],
    exceptions=["nodes can be ParseError objects rather than raising — document"],
    defaults=["skip_comments/skip_whitespace False"],
    state_effects=["none"],
    primary=["tinycss2.parse_stylesheet", "tinycss2.serialize"],
    supporting=["tinycss2.ast"],
    delta=["Round-trip contract explicitly in TASK"],
    basis="upstream",
    oracle_notes="Adapted parse/serialize pair.",
    included=["stylesheet parse, serialize roundtrip, selected at-rules"],
    excluded=["full CSSOM, browser layout"],
    license="BSD-3-Clause",
    native="none",
    offline="CSS strings only",
)

card(
    "typeguard__check_type_pipeline_core__001",
    final_lift="Composite",
    signatures=[
        "featurelifted.check_type(value, expected_type, *, collection_check_strategy=...)",
        "featurelifted.TypeCheckError",
        "featurelifted.typechecked decorator (optional if included)",
        "forward-ref resolution behavior declared",
    ],
    returns=["check_type returns value on success"],
    exceptions=["TypeCheckError with details"],
    defaults=["strategy defaults per typeguard version — pin and declare"],
    state_effects=["none unless typechecked wraps functions"],
    primary=["typeguard.check_type", "typeguard.TypeCheckError"],
    supporting=["typeguard._transformers / collection checks"],
    delta=["Nested collection + Union + Optional checking treated as composed checkers"],
    basis="upstream",
    oracle_notes="Pin typeguard major; API shifted across v2/v4.",
    included=["check_type for builtins, Optional, Union, list/dict nesting"],
    excluded=["pytest plugin, import hook instrumentation"],
    license="MIT",
    native="none",
    offline="pure type checks",
)

card(
    "frictionless__schema_resource_validate_core__001",
    final_lift="Composite",
    signatures=[
        "featurelifted.Schema.from_descriptor(descriptor: dict) -> Schema",
        "featurelifted.Resource(data=...|path=..., schema=...) ",
        "featurelifted.Resource.validate() -> Report",
        "featurelifted.Checklist / validate helpers used — declare",
        "Report.valid / Report.tasks / error list accessors",
    ],
    returns=["Report with valid bool and errors"],
    exceptions=["FrictionlessException subset"],
    defaults=["declare"],
    state_effects=["may read local files if path used — prefer inline data"],
    primary=["frictionless.Schema", "frictionless.Resource", "frictionless.Report"],
    supporting=["frictionless.checklist", "frictionless.errors"],
    delta=["Schema+Resource+Report pipeline; keep descriptors JSON-serializable"],
    basis="upstream",
    oracle_notes="Heavy package — shrink to table schema validate on inline rows.",
    included=["schema descriptor load, resource validate inline data, error collection"],
    excluded=["remote URLs, SQL dialects, pandas full stack if avoidable"],
    license="MIT",
    native="none expected",
    offline="inline Python data only; no HTTP",
)

card(
    "strictyaml__schema_load_core__001",
    final_lift="Composite",
    signatures=[
        "featurelifted.load(yaml_string: str, schema, label: str = 'string')",
        "validators: Map, Seq, Str, Int, Bool, Optional, MapPattern — declare set",
        "YAML result .data for plain python",
        "exceptions: YAMLValidationError, YAMLParseError (exact names)",
    ],
    returns=["YAML object; .data returns primitives"],
    exceptions=["YAMLValidationError, YAMLParseError"],
    defaults=["label='string'"],
    state_effects=["none"],
    primary=["strictyaml.load", "strictyaml.Map", "strictyaml.Seq"],
    supporting=["strictyaml validators module"],
    delta=["Schema combinators + load as one contract"],
    basis="upstream",
    oracle_notes="Composite validators+load.",
    included=["Map/Seq/scalars, optional keys, validation errors"],
    excluded=["ruamel round-trip fancy types beyond strictyaml"],
    license="MIT",
    native="none",
    offline="YAML strings",
)

card(
    "pykwalify__map_seq_validate_core__001",
    final_lift="Composite",
    signatures=[
        "featurelifted.Core(source_data=dict, schema_data=dict).validate()",
        "schema types map/seq/str/int/bool/any — declare",
        "featurelifted.SchemaError / Core validation error reporting",
    ],
    returns=["validate returns True or raises; document"],
    exceptions=["SchemaError, PyKwalifyException names as upstream"],
    defaults=["declare"],
    state_effects=["none"],
    primary=["pykwalify.core.Core"],
    supporting=["pykwalify.rule", "pykwalify.errors"],
    delta=["Rule tree + core validate composition"],
    basis="upstream",
    oracle_notes="Dict schema validation only.",
    included=["map/seq nested validate, required keys, type checks"],
    excluded=["YAML file path loading from disk unless fixture; extensions ecosystem"],
    license="MIT",
    native="none",
    offline="in-memory dict schemas",
)

card(
    "premailer__inline_css_core__001",
    final_lift="Composite",
    signatures=[
        "featurelifted.Premailer(html: str, **options).transform() -> str",
        "options: remove_classes, strip_important, keep_style_tags — declare subset",
        "featurelifted.transform(html: str, **options) convenience if kept",
    ],
    returns=["HTML string with inlined styles"],
    exceptions=["document upstream exceptions if any"],
    defaults=["option defaults frozen in TASK"],
    state_effects=["none"],
    primary=["premailer.Premailer", "premailer.transform"],
    supporting=["cssutils / lxml via premailer — treat as deps"],
    delta=["HTML parse + CSS parse + inline merge"],
    basis="upstream",
    oracle_notes="May pull cssutils/lxml; pin versions; no network.",
    included=["style tag and inline style merging for simple HTML"],
    excluded=["fetch external stylesheets over HTTP", "email send"],
    license="BSD-3-Clause",
    native="lxml may use binary wheels",
    offline="HTML/CSS strings only; disable URL loading",
)

card(
    "libcst__parse_transform_core__001",
    final_lift="Composite",
    signatures=[
        "featurelifted.parse_module(source: str) -> Module",
        "featurelifted.Module.code / code_for_node",
        "featurelifted.CSTTransformer visit_* methods used in tests",
        "featurelifted.RemovalSentinel / SkipChildren as needed",
        "featurelifted.ensure_type helpers if used",
    ],
    returns=["Module CST; codegen returns str"],
    exceptions=["ParserSyntaxError"],
    defaults=["declare"],
    state_effects=["transformer returns new trees"],
    primary=["libcst.parse_module", "libcst.CSTTransformer"],
    supporting=["libcst._nodes", "libcst.metadata optional excluded"],
    delta=["parse + transform + codegen pipeline"],
    basis="upstream",
    oracle_notes="Keep transforms tiny (rename/remove node).",
    included=["parse_module, simple transformer, codegen"],
    excluded=["full metadata providers, codemod CLI"],
    license="MIT",
    native="none",
    offline="source strings",
)

card(
    "textx__metamodel_model_core__001",
    final_lift="Composite",
    signatures=[
        "featurelifted.metamodel_from_str(grammar: str, **kwargs) -> MetaModel",
        "featurelifted.MetaModel.model_from_str(model_str: str)",
        "object attribute access on model as grammar defines",
        "textx exceptions TextXError / TextXSyntaxError",
    ],
    returns=["model object tree"],
    exceptions=["TextXSyntaxError, TextXSemanticError"],
    defaults=["declare"],
    state_effects=["none"],
    primary=["textx.metamodel_from_str"],
    supporting=["textx.model", "textx.exceptions"],
    delta=["grammar metamodel + model parse"],
    basis="upstream",
    oracle_notes="Provide grammar string in tests.",
    included=["metamodel_from_str, model_from_str, basic RREL-free grammars"],
    excluded=["textx-lang registration, generators, VS Code"],
    license="MIT",
    native="none",
    offline="grammar+model strings",
)

card(
    "parsimonious__grammar_visitor_core__001",
    final_lift="Adapted",
    reclass="Grammar + NodeVisitor is the documented upstream workflow; treat as Adapted unless task invents a new facade.",
    signatures=[
        "featurelifted.Grammar(rules: str)",
        "featurelifted.Grammar.parse(text: str) -> Node",
        "featurelifted.NodeVisitor.visit(node) / generic_visit",
        "featurelifted.ParseError",
    ],
    returns=["Node tree; visitor returns evaluated values"],
    exceptions=["ParseError", "VisitationError if any"],
    defaults=["declare"],
    state_effects=["none"],
    primary=["parsimonious.Grammar", "parsimonious.NodeVisitor"],
    supporting=["parsimonious.nodes.Node"],
    delta=["Documented grammar+visitor pair as Adapted packaging"],
    basis="upstream",
    oracle_notes="Adapted, not Composite, unless extra glue API added.",
    included=["PEG grammar parse, visitor evaluation"],
    excluded=["left-recursion hacks beyond upstream"],
    license="MIT",
    native="none",
    offline="strings only",
)

card(
    "anytree__tree_resolve_render_core__001",
    final_lift="Composite",
    signatures=[
        "featurelifted.Node(name, parent=None, children=None, **kwargs)",
        "featurelifted.Resolver(pathattr='name').get(node, path)",
        "featurelifted.RenderTree(node) iteration of Render rows",
        "featurelifted.PreOrderIter / findall if included",
    ],
    returns=["Node; Resolver.get returns Node; RenderTree yields rows with words"],
    exceptions=["Resolver error types (RootResolverError, ChildResolverError) declare"],
    defaults=["pathattr='name'"],
    state_effects=["parent/children mutation on Node"],
    primary=["anytree.Node", "anytree.Resolver", "anytree.RenderTree"],
    supporting=["anytree.iterators"],
    delta=["Node + resolve + render composed in one task surface"],
    basis="upstream",
    oracle_notes="Three APIs, one tree domain.",
    included=["build tree, path resolve, ASCII render"],
    excluded=["dot export, dict attachment persistence"],
    license="Apache-2.0",
    native="none",
    offline="in-memory trees",
)

card(
    "toolz__compose_pipe_core__001",
    final_lift="Direct",
    reclass="Thin extract of functoolz compose/pipe/curry. Planned Composite → Direct.",
    signatures=[
        "featurelifted.compose(*funcs)",
        "featurelifted.pipe(data, *funcs)",
        "featurelifted.curry(func, *args, **kwargs)",
        "featurelifted.identity optional",
    ],
    returns=["compose returns callable; pipe returns value; curry returns curried callable"],
    exceptions=["TypeError on bad call arities"],
    defaults=["curry underscores partial application rules as upstream"],
    state_effects=["none"],
    primary=["toolz.functoolz.compose", "toolz.functoolz.pipe", "toolz.functoolz.curry"],
    supporting=[],
    delta=["Direct extract"],
    basis="upstream",
    oracle_notes="Direct.",
    included=["compose, pipe, curry basic"],
    excluded=["cytoolz, parallelism"],
    license="BSD-3-Clause",
    native="none (pytoolz)",
    offline="pure functions",
)

card(
    "boolean_py__expr_simplify_core__001",
    final_lift="Composite",
    signatures=[
        "featurelifted.BooleanAlgebra()",
        "featurelifted.BooleanAlgebra.parse(expr: str)",
        "expression .simplify() / .subs() as upstream",
        "Symbol / AND / OR / NOT constructors if exposed",
    ],
    returns=["Expression objects; simplify returns expression"],
    exceptions=["parse errors as upstream"],
    defaults=["declare"],
    state_effects=["algebra instance may hold symbols"],
    primary=["boolean.BooleanAlgebra"],
    supporting=["boolean.boolean Symbol/Expression classes"],
    delta=["parse + algebraic simplify composition"],
    basis="upstream",
    oracle_notes="Composite parse+simplify.",
    included=["parse boolean expressions, simplify, equality"],
    excluded=["SAT solvers"],
    license="BSD-2-Clause",
    native="none",
    offline="strings",
)

card(
    "huey__task_schedule_core__001",
    final_lift="Composite",
    signatures=[
        "featurelifted.MemoryHuey(name: str = ...)",
        "featurelifted.Huey.task() decorator",
        "featurelifted.Task.then / call / schedule APIs used",
        "featurelifted.crontab(minute='*', ...) schedule helper",
        "featurelifted.Huey.execute / result store get",
    ],
    returns=["task result values via Result"],
    exceptions=["TaskException declare"],
    defaults=["MemoryHuey immediate/eager mode for tests — declare"],
    state_effects=["in-memory broker state"],
    primary=["huey.api.Huey", "huey.api.MemoryHuey", "huey.api.crontab"],
    supporting=["huey.storage", "huey.consumer excluded"],
    delta=["task + crontab + memory result compose; eager execution in tests"],
    basis="mixed",
    oracle_notes="No Redis; MemoryHuey only.",
    included=["define tasks, enqueue, crontab schedule objects, fetch results in memory"],
    excluded=["RedisHuey, consumer process, signals"],
    license="MIT",
    native="none",
    offline="MemoryHuey",
)

card(
    "invoke__collection_context_core__001",
    final_lift="Composite",
    signatures=[
        "featurelifted.task decorator",
        "featurelifted.Collection(*tasks|**kwargs)",
        "featurelifted.Context / MockContext for run()",
        "featurelifted.Program or Executor subset used to invoke tasks — declare",
        "Result stdout/stderr/exited",
    ],
    returns=["task return values; Result from run"],
    exceptions=["UnexpectedExit, Failure — declare"],
    defaults=["declare echo/pty defaults False"],
    state_effects=["MockContext records run calls"],
    primary=["invoke.task", "invoke.Collection", "invoke.Context"],
    supporting=["invoke.runners", "invoke.mock"],
    delta=["Collection namespace + Context execution"],
    basis="mixed",
    oracle_notes="Use MockContext; do not spawn real shells if avoidable.",
    included=["build collection, call tasks with ctx, mock run"],
    excluded=["real SSH fabric, config files discovery beyond declared"],
    license="BSD-2-Clause",
    native="none",
    offline="MockContext only",
)

card(
    "icalendar__component_roundtrip_core__001",
    final_lift="Composite",
    signatures=[
        "featurelifted.Calendar.from_ical(data: str|bytes)",
        "featurelifted.Calendar.to_ical() -> bytes",
        "featurelifted.Event / Todo property setters dtstart/dtend/summary",
        "featurelifted.vDDDTypes / prop codecs as needed — minimize",
    ],
    returns=["Calendar; to_ical bytes"],
    exceptions=["ValueError on bad ical"],
    defaults=["declare"],
    state_effects=["component graphs mutable"],
    primary=["icalendar.Calendar", "icalendar.Event"],
    supporting=["icalendar.prop"],
    delta=["parse + build components"],
    basis="upstream",
    oracle_notes="Round-trip ICS strings.",
    included=["parse calendar, create Event, serialize"],
    excluded=["recurrence full RRULE engines beyond what is declared"],
    license="BSD-3-Clause",
    native="none",
    offline="ICS strings",
)

card(
    "tldextract__suffix_resolve_core__001",
    final_lift="Composite",
    signatures=[
        "featurelifted.TLDExtract(cache_dir=False|path, suffix_list_urls=()) -> callable extractor",
        "extractor(url: str) -> ExtractResult(subdomain, domain, suffix, ...)",
        "featurelifted.extract(url) convenience if included",
    ],
    returns=["ExtractResult fields"],
    exceptions=["declare"],
    defaults=["cache_dir=False; suffix_list_urls=() to force packaged list"],
    state_effects=["optional disk cache — disable in tests"],
    primary=["tldextract.TLDExtract", "tldextract.extract"],
    supporting=["public suffix list data packaged"],
    delta=["suffix data resource + extract logic"],
    basis="mixed",
    oracle_notes="Must disable network suffix fetch; use bundled list.",
    included=["extract domain parts for HTTP URLs and hosts"],
    excluded=["live PSL download"],
    license="BSD-3-Clause",
    native="none",
    offline="suffix_list_urls empty; no HTTP",
)

card(
    "vcrpy__cassette_match_core__001",
    final_lift="Composite",
    signatures=[
        "featurelifted.use_cassette(path, matcher=..., record_mode='none')",
        "featurelifted.matchers method/uri/host/path/query subset",
        "featurelifted.VCR(record_mode=..., match_on=...)",
    ],
    returns=["cassette context restores recorded responses"],
    exceptions=["CannotOverwriteExistingCassetteException; network errors if misconfigured"],
    defaults=["record_mode='none' in tests"],
    state_effects=["patches HTTP libs — only urllib/stdlib in tests"],
    primary=["vcr.VCR", "vcr.use_cassette"],
    supporting=["vcr.matchers", "vcr.cassette"],
    delta=["matchers + cassette store + replay"],
    basis="mixed",
    oracle_notes="Ship cassette fixtures; never record online in CI.",
    included=["replay cassette, match_on uri/method, custom matcher registration"],
    excluded=["recording against internet, selenium"],
    license="MIT",
    native="none",
    offline="pre-recorded cassettes only",
)

card(
    "joserfc__jwt_claims_core__001",
    final_lift="Composite",
    signatures=[
        "featurelifted.jwt.encode(header: dict, claims: dict, key) -> str",
        "featurelifted.jwt.decode(token: str, key, algorithms: list[str]) -> token object with claims",
        "featurelifted.JWTClaimsRegistry / claims validate helpers used",
        "featurelifted.OctKey.import_key / generate_key for tests",
        "exceptions: JoseError, ExpiredTokenError, InvalidClaimError — declare",
    ],
    returns=["compact JWT string; claims dict"],
    exceptions=["JoseError hierarchy"],
    defaults=["alg HS256 in tests"],
    state_effects=["none"],
    primary=["joserfc.jwt", "joserfc.jwk.OctKey"],
    supporting=["joserfc.errors", "joserfc.jws"],
    delta=["encode/decode + claims validation pipeline"],
    basis="upstream",
    oracle_notes="HS256 only for offline tests.",
    included=["HS256 JWT encode/decode, exp/nbf/iss claim checks"],
    excluded=["JWKS URL fetch, asymmetric clouds KMS"],
    license="BSD-3-Clause",
    native="none",
    offline="local oct keys",
)

# Adapted remaining
card(
    "dill__serialize_settings_core__001",
    final_lift="Adapted",
    signatures=[
        "featurelifted.dumps(obj, protocol=None, byref=None, fmode=None, recurse=None) -> bytes",
        "featurelifted.loads(s: bytes) -> Any",
        "featurelifted.dump/load file variants if included",
        "featurelifted.settings / detect as needed — declare",
    ],
    returns=["bytes; reconstituted objects"],
    exceptions=["PicklingError"],
    defaults=["protocol defaults as dill"],
    state_effects=["none"],
    primary=["dill.dumps", "dill.loads"],
    supporting=["dill.settings"],
    delta=["Settings/flags as adapted surface over pickle-compatible API"],
    basis="upstream",
    oracle_notes="Serialize simple callables/closures subset.",
    included=["dumps/loads roundtrip for functions/lambdas supported by dill"],
    excluded=["interactive session dump tricks, undetected objects"],
    license="BSD-3-Clause",
    native="none",
    offline="in-memory bytes",
)

card(
    "python_json_logger__json_formatter_core__001",
    final_lift="Adapted",
    signatures=[
        "featurelifted.JsonFormatter(fmt=None, datefmt=None, style='%', rename_fields: dict | None = None, static_fields: dict | None = None, ...)",
        "featurelifted.JsonFormatter.format(record: logging.LogRecord) -> str",
    ],
    returns=["JSON line string"],
    exceptions=["declare"],
    defaults=["style='%'; rename_fields None"],
    state_effects=["none"],
    primary=["pythonjsonlogger.json.JsonFormatter or pythonjsonlogger.jsonlogger.JsonFormatter (pin import path)"],
    supporting=["logging.LogRecord"],
    delta=["Document exact import path for v3 package layout"],
    basis="upstream",
    oracle_notes="Adapted formatter options.",
    included=["format LogRecord to JSON, rename_fields, static_fields"],
    excluded=["SocketHandler networking"],
    license="BSD-2-Clause",
    native="none",
    offline="LogRecord manufactured in tests",
)

card(
    "flask_cors__cors_options_core__001",
    final_lift="Adapted",
    signatures=[
        "featurelifted.CORS(app=None, **options)",
        "featurelifted.cross_origin(**options) decorator",
        "options: origins, methods, allow_headers, supports_credentials — declare",
    ],
    returns=["decorated view; CORS installs after_request"],
    exceptions=["declare"],
    defaults=["origins='*' unless tightened"],
    state_effects=["mutates Flask app hooks"],
    primary=["flask_cors.CORS", "flask_cors.cross_origin"],
    supporting=["flask_cors.core"],
    delta=["Options object/decorator adapted API; Flask test client"],
    basis="upstream",
    oracle_notes="Needs Flask.",
    included=["attach CORS, verify ACAO headers on test client responses"],
    excluded=["real browsers"],
    license="MIT",
    native="none",
    offline="Flask test client",
)

card(
    "jsonpickle__handler_roundtrip_core__001",
    final_lift="Adapted",
    signatures=[
        "featurelifted.encode(obj, unpicklable: bool = True, make_refs: bool = True) -> str",
        "featurelifted.decode(string: str) -> Any",
        "featurelifted.register(cls, handler)",
        "featurelifted.handlers.BaseHandler",
    ],
    returns=["JSON string; decoded objects"],
    exceptions=["declare"],
    defaults=["unpicklable=True"],
    state_effects=["global handler registry — reset between tests"],
    primary=["jsonpickle.encode", "jsonpickle.decode", "jsonpickle.register"],
    supporting=["jsonpickle.handlers"],
    delta=["Handler registration adapted surface"],
    basis="upstream",
    oracle_notes="Reset handlers in fixtures.",
    included=["encode/decode, custom handler for a sample class"],
    excluded=["numpy/pandas backends"],
    license="BSD-3-Clause",
    native="none",
    offline="in-memory",
)

card(
    "furl__url_mutate_core__001",
    final_lift="Adapted",
    signatures=[
        "featurelifted.furl(url: str = '')",
        "attributes set: scheme/host/port/path/query/fragment",
        "featurelifted.furl.set / add / remove / join / url / pathstr / querystr",
    ],
    returns=["furl object; .url str"],
    exceptions=["declare ValueError cases"],
    defaults=["empty url"],
    state_effects=["mutable furl"],
    primary=["furl.furl"],
    supporting=["furl.Path", "furl.Query"],
    delta=["Mutation-oriented URL API packaging"],
    basis="upstream",
    oracle_notes="Adapted URL model.",
    included=["parse, mutate query/path, serialize"],
    excluded=["network"],
    license="Unlicense",
    native="none",
    offline="strings",
)

card(
    "packageurl__purl_parse_core__001",
    final_lift="Adapted",
    signatures=[
        "featurelifted.PackageURL.from_string(purl: str) -> PackageURL",
        "featurelifted.PackageURL(type, namespace=None, name=..., version=None, qualifiers=None, subpath=None)",
        "featurelifted.PackageURL.to_string() -> str",
    ],
    returns=["PackageURL; to_string purl"],
    exceptions=["ValueError on invalid purl"],
    defaults=["namespace/version optional"],
    state_effects=["none"],
    primary=["packageurl.PackageURL"],
    supporting=[],
    delta=["Normalize qualifiers ordering as upstream"],
    basis="upstream",
    oracle_notes="PURL parse/normalize.",
    included=["from_string, to_string, field access"],
    excluded=["package ecosystem network lookups"],
    license="MIT",
    native="none",
    offline="strings",
)

card(
    "python_crontab__cron_item_core__001",
    final_lift="Adapted",
    signatures=[
        "featurelifted.CronSlices(line: str)",
        "featurelifted.CronItem(command=None, comment=None, user=None, pre_comment=False)",
        "CronItem.setall / render / is_valid / schedule frequency helpers used — declare",
    ],
    returns=["slices/item; render returns cron line str"],
    exceptions=["ValueError on invalid slices"],
    defaults=["declare"],
    state_effects=["none"],
    primary=["crontab.CronSlices", "crontab.CronItem"],
    supporting=["crontab.CronTab excluded for file/user system"],
    delta=["Item/slices without touching system crontab files"],
    basis="upstream",
    oracle_notes="No /etc/crontab access.",
    included=["parse slice strings, render, validity"],
    excluded=["reading user crontabs from OS"],
    license="LGPL-3.0",
    native="none",
    offline="strings only",
)

card(
    "freezegun__freeze_time_core__001",
    final_lift="Adapted",
    signatures=[
        "featurelifted.freeze_time(time_to_freeze=None, tick: bool = False, ...)",
        "context manager and decorator forms",
        "frozen_time.move_to / tick APIs if included",
    ],
    returns=["context yields FrozenDateTimeFactory"],
    exceptions=["declare"],
    defaults=["tick=False"],
    state_effects=["patches datetime/time — must stop"],
    primary=["freezegun.freeze_time"],
    supporting=["freezegun.api"],
    delta=["Test-only time freeze facade"],
    basis="upstream",
    oracle_notes="Adapted datetime patching.",
    included=["freeze, tick, move_to, decorator"],
    excluded=["patching third-party C extensions clocks"],
    license="Apache-2.0",
    native="none",
    offline="no network",
)

card(
    "cloudpickle__dumps_loads_core__001",
    final_lift="Adapted",
    signatures=[
        "featurelifted.dumps(obj, protocol=None) -> bytes",
        "featurelifted.loads(data: bytes) -> Any",
        "featurelifted.CloudPickler if needed",
    ],
    returns=["bytes; objects"],
    exceptions=["PicklingError"],
    defaults=["protocol default"],
    state_effects=["none"],
    primary=["cloudpickle.dumps", "cloudpickle.loads"],
    supporting=[],
    delta=["Dynamic function pickling adapted from pickle"],
    basis="upstream",
    oracle_notes="Roundtrip nested functions.",
    included=["dumps/loads for local functions and closures supported by cloudpickle"],
    excluded=["interactive __main__ edge cases unless listed"],
    license="BSD-3-Clause",
    native="none",
    offline="bytes",
)

card(
    "ijson__event_parse_core__001",
    final_lift="Adapted",
    signatures=[
        "featurelifted.parse(file_or_bytes) -> iterator of (prefix, event, value)",
        "featurelifted.items(file, prefix)",
        "featurelifted.kvitems(file, prefix)",
        "backend note: use pure python backend if possible (ijson.backends.python)",
    ],
    returns=["event tuples; items yields decoded values"],
    exceptions=["IncompleteJSONError, JSONError"],
    defaults=["declare backend"],
    state_effects=["none"],
    primary=["ijson.parse", "ijson.items"],
    supporting=["ijson.backends.python"],
    delta=["Force python backend for portability"],
    basis="upstream",
    oracle_notes="Adapted incremental JSON API.",
    included=["parse events, items for arrays/objects"],
    excluded=["yajl C backend requirement"],
    license="BSD-3-Clause",
    native="prefer pure python backend",
    offline="BytesIO JSON",
)

card(
    "hyperlink__url_parse_core__001",
    final_lift="Adapted",
    signatures=[
        "featurelifted.URL.from_text(text: str) -> URL",
        "featurelifted.URL.replace(**parts) -> URL",
        "featurelifted.URL.click(relative) / to_text()",
        "attributes: scheme, userinfo, host, port, path, query, fragment",
    ],
    returns=["URL immutable; to_text str"],
    exceptions=["URLParseError / ValueError declare"],
    defaults=["declare"],
    state_effects=["immutable"],
    primary=["hyperlink.URL"],
    supporting=[],
    delta=["Immutable URL adapted surface"],
    basis="upstream",
    oracle_notes="Adapted.",
    included=["from_text, replace, to_text, query manipulation"],
    excluded=["network resolve"],
    license="MIT",
    native="none",
    offline="strings",
)

card(
    "pyjwt__encode_decode_core__001",
    final_lift="Adapted",
    signatures=[
        "featurelifted.encode(payload: dict, key: str, algorithm: str = 'HS256', headers: dict | None = None) -> str",
        "featurelifted.decode(jwt: str, key: str, algorithms: list[str], options: dict | None = None) -> dict",
        "exceptions: InvalidTokenError, ExpiredSignatureError, InvalidSignatureError",
    ],
    returns=["JWT str; payload dict"],
    exceptions=["PyJWT error types above"],
    defaults=["algorithm HS256"],
    state_effects=["none"],
    primary=["jwt.encode", "jwt.decode"],
    supporting=["jwt.exceptions"],
    delta=["Adapted JWT encode/decode"],
    basis="upstream",
    oracle_notes="HS256 only.",
    included=["encode/decode, exp validation option"],
    excluded=["JWKS fetch"],
    license="MIT",
    native="none",
    offline="local secrets",
)

card(
    "configupdater__ini_roundtrip_core__001",
    final_lift="Adapted",
    signatures=[
        "featurelifted.ConfigUpdater()",
        "featurelifted.ConfigUpdater.read_string / read",
        "section/option get set space-preserving API",
        "featurelifted.ConfigUpdater.to_string()",
        "UpdateError exceptions declare",
    ],
    returns=["updater; to_string INI text"],
    exceptions=["NoConfigFileError / NoSectionError variants declare"],
    defaults=["declare"],
    state_effects=["mutable AST of INI"],
    primary=["configupdater.ConfigUpdater"],
    supporting=[],
    delta=["Comment-preserving INI adapted from ConfigParser mental model"],
    basis="upstream",
    oracle_notes="Round-trip comments/spacing.",
    included=["read_string, modify values, to_string preserves comments"],
    excluded=["interpolation beyond declared"],
    license="MIT",
    native="none",
    offline="strings",
)

# Direct remaining
card(
    "more_itertools__recipes_core__001",
    final_lift="Direct",
    signatures=[
        "featurelifted.chunked(iterable, n)",
        "featurelifted.sliced(seq, n)",
        "featurelifted.consume / first / one / only / unique_everseen / windowed — declare exact set from recipes/more",
    ],
    returns=["iterators/values per helper"],
    exceptions=["ValueError for one/only failures"],
    defaults=["declare"],
    state_effects=["consume advances iterators"],
    primary=["more_itertools.recipes", "more_itertools.more"],
    supporting=[],
    delta=["Direct toolkit extract"],
    basis="upstream",
    oracle_notes="Direct.",
    included=["listed helpers only"],
    excluded=["entire more_itertools surface"],
    license="MIT",
    native="none",
    offline="pure",
)

card(
    "fasteners__process_lock_core__001",
    final_lift="Direct",
    signatures=[
        "featurelifted.InterProcessLock(path: str)",
        "acquire(blocking: bool = True) / release / __enter__/__exit__",
    ],
    returns=["acquire returns bool"],
    exceptions=["Threading conflicts declare"],
    defaults=["blocking=True"],
    state_effects=["creates lock file in temp"],
    primary=["fasteners.process_lock.InterProcessLock"],
    supporting=[],
    delta=["Direct"],
    basis="upstream",
    oracle_notes="Use tmp_path lock files.",
    included=["acquire/release/context manager"],
    excluded=["redis locks, readers-writer unless listed"],
    license="Apache-2.0",
    native="none",
    offline="local filesystem",
)

card(
    "portalocker__file_lock_core__001",
    final_lift="Direct",
    signatures=[
        "featurelifted.lock(file, flags=LOCK_EX)",
        "featurelifted.unlock(file)",
        "featurelifted.Lock(filename, mode='a', timeout=...) context manager",
        "constants LOCK_EX/LOCK_SH/LOCK_NB",
    ],
    returns=["Lock context yields file object"],
    exceptions=["LockException / AlreadyLocked — declare"],
    defaults=["timeout defaults"],
    state_effects=["locks files"],
    primary=["portalocker.lock", "portalocker.Lock"],
    supporting=[],
    delta=["Direct"],
    basis="upstream",
    oracle_notes="tmp files.",
    included=["exclusive lock context manager"],
    excluded=["redis lock"],
    license="BSD-3-Clause",
    native="none",
    offline="local FS",
)

card(
    "pyotp__totp_hotp_core__001",
    final_lift="Direct",
    signatures=[
        "featurelifted.TOTP(secret: str | bytes)",
        "featurelifted.TOTP.at(for_time) / now / verify",
        "featurelifted.HOTP(secret).at(count) / verify",
        "featurelifted.random_base32()",
    ],
    returns=["otp strings; verify bool"],
    exceptions=["declare"],
    defaults=["interval 30 for TOTP"],
    state_effects=["none"],
    primary=["pyotp.TOTP", "pyotp.HOTP"],
    supporting=[],
    delta=["Direct"],
    basis="upstream",
    oracle_notes="Fix time with freezegun only if needed; prefer at(timestamp).",
    included=["TOTP/HOTP generate/verify, random_base32"],
    excluded=["QR provisioning network"],
    license="MIT",
    native="none",
    offline="local",
)

card(
    "chardet__detect_core__001",
    final_lift="Direct",
    signatures=[
        "featurelifted.detect(byte_str: bytes) -> dict encoding/confidence/language",
    ],
    returns=["dict with encoding, confidence"],
    exceptions=["declare empty input behavior"],
    defaults=["none"],
    state_effects=["none"],
    primary=["chardet.detect"],
    supporting=["chardet.universaldetector optional excluded"],
    delta=["Direct"],
    basis="upstream",
    oracle_notes="Fixture byte samples.",
    included=["detect on provided fixtures"],
    excluded=["cli chardetect"],
    license="LGPL-2.1",
    native="none",
    offline="bytes fixtures",
)

card(
    "ftfy__fix_text_core__001",
    final_lift="Direct",
    signatures=[
        "featurelifted.fix_text(text: str, ...) -> str",
        "featurelifted.guess_bytes if included",
        "config flags: normalization, explain — declare",
    ],
    returns=["fixed unicode str"],
    exceptions=["declare"],
    defaults=["ftfy defaults frozen"],
    state_effects=["none"],
    primary=["ftfy.fix_text"],
    supporting=[],
    delta=["Direct"],
    basis="upstream",
    oracle_notes="Mojibake fixtures.",
    included=["fix_text common mojibake cases"],
    excluded=["cli"],
    license="Apache-2.0",
    native="none",
    offline="strings",
)

card(
    "pyrsistent__pmap_pvector_core__001",
    final_lift="Direct",
    signatures=[
        "featurelifted.pmap(initial=None) / pvector(initial=())",
        "PMap.set/remove/get; PVector.append/set/extend",
        "evolution transform() if included",
        "thaw/freeze helpers if included",
    ],
    returns=["persistent structures; updates return new objects"],
    exceptions=["KeyError/IndexError"],
    defaults=["empty structures"],
    state_effects=["persistent — old versions unchanged"],
    primary=["pyrsistent.pmap", "pyrsistent.pvector"],
    supporting=["pyrsistent.PMap", "pyrsistent.PVector"],
    delta=["Direct"],
    basis="upstream",
    oracle_notes="Direct persistent collections.",
    included=["pmap/pvector core ops"],
    excluded=["pset/pdeque/pclass unless listed", "optional C extension requirement"],
    license="MIT",
    native="optional C ext; allow pure",
    offline="pure",
)


def render(meta: dict, data: dict) -> str:
    final = data["final_lift_type"]
    reclass = data["reclassification_reason"]
    status = "design_card_ready"
    lines = [
        f"# Design card: {meta['task_id']}",
        "",
        f"**status:** `{status}`  ",
        f"**wave:** {meta.get('wave')}  ",
        f"**package:** `{meta.get('package')}`  ",
        f"**repository_url:** {meta.get('repository_url')}  ",
        f"**planned_lift_type:** {meta.get('planned_lift_type') or meta.get('lift_type')}  ",
        f"**final_lift_type:** {final}  ",
        f"**reclassification_reason:** {reclass}  ",
        f"**feature_family:** {meta.get('feature_family')}  ",
        f"**entanglement:** {meta.get('entanglement')}  ",
        f"**feature_one_liner:** {meta.get('feature_one_liner')}  ",
        f"**lift_review_flag:** {meta.get('lift_review_flag') or 'none'}",
        "",
        "> Filled for design_card phase. `feasibility.commit` still unresolved until pin.  ",
        "> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/PLAN_EXTERNAL50_EXPANSION.md`.",
        "",
        "## target_api",
        "",
        "```yaml",
        "module: featurelifted",
        "signatures:",
    ]
    for s in data["signatures"]:
        lines.append(f"  - {s!r}" if False else f"  - {json.dumps(s)}")
    lines.append("returns:")
    for s in data["returns"]:
        lines.append(f"  - {json.dumps(s)}")
    lines.append("exceptions:")
    for s in data["exceptions"]:
        lines.append(f"  - {json.dumps(s)}")
    lines.append("defaults:")
    for s in data["defaults"]:
        lines.append(f"  - {json.dumps(s)}")
    lines.append("state_effects:")
    for s in data["state_effects"]:
        lines.append(f"  - {json.dumps(s)}")
    lines.extend(
        [
            "```",
            "",
            "## upstream_mapping",
            "",
            "```yaml",
            "primary_symbols:",
        ]
    )
    for s in data["primary"]:
        lines.append(f"  - {json.dumps(s)}")
    lines.append("supporting_components:")
    for s in data["supporting"]:
        lines.append(f"  - {json.dumps(s)}")
    lines.append("semantic_delta:")
    for s in data["delta"]:
        lines.append(f"  - {json.dumps(s)}")
    lines.extend(
        [
            "```",
            "",
            "## oracle_basis",
            "",
            "```yaml",
            f"basis: {data['basis']}",
            "notes: |",
        ]
    )
    for ln in data["oracle_notes"].splitlines() or [""]:
        lines.append(f"  {ln}")
    lines.extend(
        [
            "```",
            "",
            "## scope",
            "",
            "```yaml",
            "included:",
        ]
    )
    for s in data["included"]:
        lines.append(f"  - {json.dumps(s)}")
    lines.append("excluded:")
    for s in data["excluded"]:
        lines.append(f"  - {json.dumps(s)}")
    lines.extend(
        [
            "```",
            "",
            "## feasibility",
            "",
            "```yaml",
            "commit: null  # resolve at pin/materialize",
            f"license: {json.dumps(data['license'])}",
            "python_versions:",
        ]
    )
    for v in data["python_versions"]:
        lines.append(f"  - {json.dumps(v)}")
    lines.extend(
        [
            f"native_or_heavy_dependencies: {json.dumps(data['native'])}",
            f"offline_resources: {json.dumps(data['offline'])}",
            "```",
            "",
            "## acceptance",
            "",
            "```yaml",
            "closure_review: pending",
            "reference_pass: pending",
            "isolation_pass: pending",
            "no_original_import: pending",
            "overlap_check: pending",
            "```",
            "",
            "## agent_notes",
            "",
            f"- Staging path: `benchmark/staging/{meta['task_id']}/`",
            "- Do not materialize until human skim of target_api + lift (esp. reclassified cards).",
            "- Do not promote to `benchmark/tasks/` in design_card phase.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    ledger = json.loads(LEDGER.read_text())
    selected = [r for r in ledger["rows"] if r.get("disposition") == "selected"]
    missing = [r["task_id"] for r in selected if r["task_id"] not in CARDS_DATA]
    if missing:
        raise SystemExit(f"missing card data for {len(missing)}: {missing[:10]}")

    for r in selected:
        tid = r["task_id"]
        data = CARDS_DATA[tid]
        # sync lift fields
        if data["final_lift_type"]:
            r["final_lift_type"] = data["final_lift_type"]
        if data["reclassification_reason"]:
            r["reclassification_reason"] = data["reclassification_reason"]
        r["design_card_status"] = "design_card_ready"
        r["status"] = "design_ready"
        (CARDS / f"{tid}.md").write_text(render(r, data))

    # refresh index
    idx = [
        "# External-50 design cards index",
        "",
        "| wave | task_id | planned | final | card_status |",
        "| --- | --- | --- | --- | --- |",
    ]
    for r in sorted(selected, key=lambda x: (x.get("wave") or "", x["task_id"])):
        idx.append(
            f"| {r.get('wave')} | [`{r['task_id']}`]({r['task_id']}.md) | {r.get('planned_lift_type') or r.get('lift_type')} | {r.get('final_lift_type')} | {r.get('design_card_status')} |"
        )
    # count finals
    from collections import Counter

    finals = Counter(r.get("final_lift_type") for r in selected)
    idx += ["", "## final_lift_type counts (after card fill)", "", "```", str(dict(finals)), "```", ""]
    (CARDS / "README.md").write_text("\n".join(idx))
    LEDGER.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n")
    print("filled", len(selected), "finals", dict(finals))


if __name__ == "__main__":
    main()
