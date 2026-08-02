#!/usr/bin/env python3
"""Materialize External-50 W1 remaining tasks into benchmark/staging/."""

from __future__ import annotations

import importlib.util
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
PILOT = ROOT / "harness" / "scripts" / "materialize_external50_pilot.py"
PIN_ROOT = Path("/tmp/flb_w1_pins")
STAGING = ROOT / "benchmark" / "staging"

spec = importlib.util.spec_from_file_location("pilot_mat", PILOT)
pilot = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(pilot)

def copy_package_tree(src_pkg: Path, dest: Path, upstream_name: str) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(
        src_pkg,
        dest,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".mypy_cache", "*.egg-info"),
    )
    for path in dest.rglob("*.py"):
        raw = path.read_text(encoding="utf-8")
        updated = raw
        # Absolute imports only; keep relative ``from .pkg`` module filenames.
        updated = re.sub(
            rf"(?<!\.)\bfrom {re.escape(upstream_name)}\b",
            "from featurelifted",
            updated,
        )
        updated = re.sub(
            rf"(?<!\.)\bimport {re.escape(upstream_name)}\b",
            "import featurelifted",
            updated,
        )
        updated = re.sub(
            rf"(?<!\.)\b{re.escape(upstream_name)}\.",
            "featurelifted.",
            updated,
        )
        updated = updated.replace(f'"{upstream_name}.', '"featurelifted.')
        updated = updated.replace(f"'{upstream_name}.", "'featurelifted.")
        if updated != raw:
            path.write_text(updated, encoding="utf-8")


write_json = pilot.write_json
finalize_metadata = pilot.finalize_metadata
base_metadata = pilot.base_metadata
make_archive_and_register = pilot.make_archive_and_register


def _prepare(task_id: str, meta: dict[str, Any]) -> Path:
    task_dir = STAGING / task_id
    if task_dir.exists():
        shutil.rmtree(task_dir)
    task_dir.mkdir(parents=True)
    shutil.copytree(
        meta["src"],
        task_dir / "repo",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".flb_pin", "*.tar.gz", "wheels"),
    )
    (task_dir / "evaluation").mkdir(parents=True)
    (task_dir / "public_tests").mkdir()
    (task_dir / "hidden_tests").mkdir()
    return task_dir


PINS: dict[str, dict[str, Any]] = {
    "tinycss2__stylesheet_roundtrip_core__001": {
        "package": "tinycss2",
        "url": "https://github.com/Kozea/tinycss2",
        "commit": "f295a49711a4d348664bba7fb34113b3b4b78cb2",
        "tag": "v1.5.1",
        "license": "BSD-3-Clause",
        "license_path": "LICENSE",
        "src": PIN_ROOT / "tinycss2",
        "forbidden": "tinycss2",
        "lift": "Adapted",
        "pkg_dir": lambda: PIN_ROOT / "tinycss2" / "tinycss2",
    },
    "pyparsing__grammar_compose_core__001": {
        "package": "pyparsing",
        "url": "https://github.com/pyparsing/pyparsing",
        "commit": "fa24016d953353f8ba566abb5c8fc12e1d07556c",
        "tag": "3.3.2",
        "license": "MIT",
        "license_path": "LICENSE",
        "src": PIN_ROOT / "pyparsing",
        "forbidden": "pyparsing",
        "lift": "Adapted",
        "pkg_dir": lambda: PIN_ROOT / "pyparsing" / "pyparsing",
    },
    "omegaconf__merge_interpolate_core__001": {
        "package": "omegaconf",
        "url": "https://github.com/omry/omegaconf",
        "commit": "350bdb632865c5dd2286f2f6521acefe4abd843d",
        "tag": "v2.3.0",
        "license": "BSD-3-Clause",
        "license_path": "LICENSE",
        "src": PIN_ROOT / "omegaconf",
        "forbidden": "omegaconf",
        "lift": "Composite",
        "pkg_dir": lambda: Path("/tmp/flb_w1_pins/omegaconf_wheel/omegaconf"),
    },
    "structlog__processor_chain_core__001": {
        "package": "structlog",
        "url": "https://github.com/hynek/structlog",
        "commit": "8174a86a2f14b5bd295eded733ff5fffc12aa173",
        "tag": "26.1.0",
        "license": "MIT OR Apache-2.0",
        "license_path": "LICENSE-MIT",
        "src": PIN_ROOT / "structlog",
        "forbidden": "structlog",
        "lift": "Composite",
        "pkg_dir": lambda: PIN_ROOT / "structlog" / "src" / "structlog",
    },
    "sqlglot__parse_transpile_core__001": {
        "package": "sqlglot",
        "url": "https://github.com/tobymao/sqlglot",
        "commit": "29c651b85309693924b8c034501e6a2733d14588",
        "tag": "v30.14.0",
        "license": "MIT",
        "license_path": "LICENSE",
        "src": PIN_ROOT / "sqlglot",
        "forbidden": "sqlglot",
        "lift": "Composite",
        "pkg_dir": lambda: PIN_ROOT / "sqlglot" / "sqlglot",
    },
    "cachecontrol__heuristic_store_core__001": {
        "package": "cachecontrol",
        "url": "https://github.com/psf/cachecontrol",
        "commit": "aba0315599d7d4200074ab3606384732be7bbc25",
        "tag": "v0.14.4",
        "license": "Apache-2.0",
        "license_path": "LICENSE.txt",
        "src": PIN_ROOT / "cachecontrol",
        "forbidden": "cachecontrol",
        "lift": "Composite",
        "pkg_dir": lambda: PIN_ROOT / "cachecontrol" / "cachecontrol",
    },
    "flask_login__session_guard_core__001": {
        "package": "flask-login",
        "url": "https://github.com/maxcountryman/flask-login",
        "commit": "793e240e408802bb1b1fbdf57d36403ea204f0bc",
        "tag": "0.6.3",
        "license": "MIT",
        "license_path": "LICENSE",
        "src": PIN_ROOT / "flask-login",
        "forbidden": "flask_login",
        "lift": "Composite",
        "pkg_dir": lambda: PIN_ROOT / "flask-login" / "src" / "flask_login",
    },
    "watchdog__observer_dispatch_core__001": {
        "package": "watchdog",
        "url": "https://github.com/gorakhargosh/watchdog",
        "commit": "a8829e350d76a9b6c9f716d242b42a34fbbd62fd",
        "tag": "v6.0.0",
        "license": "Apache-2.0",
        "license_path": "LICENSE",
        "src": PIN_ROOT / "watchdog",
        "forbidden": "watchdog",
        "lift": "Composite",
        "pkg_dir": lambda: PIN_ROOT / "watchdog" / "src" / "watchdog",
    },
}


def materialize_tinycss2() -> Path:
    task_id = "tinycss2__stylesheet_roundtrip_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["pkg_dir"](), ref, "tinycss2")
    (task_dir / "requirements.lock").write_text("webencodings==0.5.1\n", encoding="utf-8")
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("tinycss2\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "tinycss2",
            "required_source_files": ["tinycss2/parser.py", "tinycss2/serializer.py", "tinycss2/ast.py"],
            "runtime_dependencies": ["webencodings"],
            "notes": "Adapted parse_stylesheet/serialize roundtrip.",
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        '''from __future__ import annotations

from featurelifted import parse_stylesheet, serialize
from featurelifted.ast import AtRule, QualifiedRule


def test_parse_qualified_rule() -> None:
    nodes = [n for n in parse_stylesheet("div { color: red }") if isinstance(n, QualifiedRule)]
    assert nodes
    assert "div" in serialize(nodes)


def test_roundtrip_simple() -> None:
    css = "a { color: blue }"
    out = serialize(parse_stylesheet(css))
    assert "color" in out and "blue" in out


def test_parse_at_rule() -> None:
    nodes = parse_stylesheet("@media screen { a { color: red } }")
    assert any(isinstance(n, AtRule) for n in nodes)
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        '''from __future__ import annotations

import re
from pathlib import Path

from featurelifted import parse_stylesheet, serialize
from featurelifted.ast import ParseError, QualifiedRule


def test_skip_whitespace_option() -> None:
    nodes = parse_stylesheet("div{}", skip_whitespace=True)
    assert all(not type(n).__name__.endswith("WhitespaceToken") for n in nodes)


def test_serialize_preserves_at_keyword() -> None:
    css = "@import url(x.css);"
    assert "@import" in serialize(parse_stylesheet(css))


def test_parse_error_node_not_raise() -> None:
    nodes = parse_stylesheet("}")
    assert any(isinstance(n, ParseError) for n in nodes)


def test_qualified_prelude() -> None:
    q = next(n for n in parse_stylesheet("h1.title{}") if isinstance(n, QualifiedRule))
    assert q.prelude


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\\s*(?:from tinycss2\\b|import tinycss2\\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''from featurelifted import parse_stylesheet, serialize
from featurelifted.ast import AtRule, ParseError, QualifiedRule


def test_required_api_surface() -> None:
    assert callable(parse_stylesheet)
    assert callable(serialize)
    assert QualifiedRule is not None and AtRule is not None and ParseError is not None
''',
        encoding="utf-8",
    )
    metadata = base_metadata(
        task_id,
        meta,
        allowed_dependencies=["webencodings"],
        feature={
            "name": "tinycss2 stylesheet roundtrip",
            "description": "Adapted tinycss2 parse_stylesheet/serialize.",
            "source_entrypoints": ["tinycss2.parse_stylesheet", "tinycss2.serialize"],
            "included_behaviors": [
                "parse stylesheet into QualifiedRule/AtRule/ParseError nodes",
                "serialize nodes back to CSS",
                "skip_whitespace option",
            ],
            "excluded_behaviors": ["full CSSOM", "browser layout", "parse_rule_list required API"],
        },
        entanglement={
            "level": "medium",
            "types": ["parser_state_coupling"],
            "primary": "parser_state_coupling",
            "description": "CSS tokenization and AST serialize pairing.",
            "signals": ["ParseError nodes", "at-rules", "roundtrip"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import parse_stylesheet, serialize",
            "callable": "parse_stylesheet",
            "signature": "parse_stylesheet(css: str, skip_comments: bool = False, skip_whitespace: bool = False) -> list",
        },
        public_spec={
            "title": "tinycss2 stylesheet roundtrip",
            "summary": "Extract a task-scoped subset of `tinycss2` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.parse_stylesheet", "kind": "function", "signature": "(css: str, skip_comments: bool = False, skip_whitespace: bool = False) -> list"},
                {"path": "featurelifted.serialize", "kind": "function", "signature": "(nodes) -> str"},
                {"path": "featurelifted.ast.QualifiedRule", "kind": "class"},
                {"path": "featurelifted.ast.AtRule", "kind": "class"},
                {"path": "featurelifted.ast.ParseError", "kind": "class"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: parse stylesheet into QualifiedRule/AtRule/ParseError nodes. Required observable cases include parse qualified rule; parse at rule; parse error node not raise."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: serialize nodes back to CSS. Required observable cases include roundtrip simple; serialize preserves at keyword."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: skip_whitespace option. Required observable cases include skip whitespace option."},
                {"id": "B004", "text": "QualifiedRule exposes a prelude used by selectors."},
                {"id": "B005", "text": "The package exposes the required task API paths `featurelifted.parse_stylesheet`, `featurelifted.serialize`, `featurelifted.ast.QualifiedRule`, `featurelifted.ast.AtRule`, `featurelifted.ast.ParseError` with the kinds and callable signatures listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: tinycss2."},
            ],
            "exclusions": ["full CSSOM", "browser layout", "original tinycss2 import at runtime"],
            "forbidden": {"imports": ["tinycss2"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


def materialize_pyparsing() -> Path:
    task_id = "pyparsing__grammar_compose_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["pkg_dir"](), ref, "pyparsing")
    (task_dir / "requirements.lock").write_text("# no third-party dependencies\n", encoding="utf-8")
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("pyparsing\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "pyparsing",
            "required_source_files": ["pyparsing/core.py", "pyparsing/results.py", "pyparsing/exceptions.py"],
            "runtime_dependencies": [],
            "notes": "Adapted ParserElement composition helpers.",
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        '''from __future__ import annotations

from featurelifted import Group, Literal, Optional, ParseException, Word, alphas


def test_word_literal_compose() -> None:
    grammar = Word(alphas)("name") + Literal(",") + Word(alphas)("item")
    result = grammar.parse_string("Hello, world")
    assert result.as_dict()["name"] == "Hello"
    assert result.as_list()[0] == "Hello"


def test_optional_group() -> None:
    grammar = Word(alphas) + Optional(Literal("!")("bang"))
    assert grammar.parse_string("hi").as_list() == ["hi"]
    assert "bang" in grammar.parse_string("hi!").as_dict()


def test_parse_exception() -> None:
    grammar = Literal("OK")
    try:
        grammar.parse_string("NO")
        assert False, "expected ParseException"
    except ParseException as exc:
        assert exc.loc >= 0
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        '''from __future__ import annotations

import re
from pathlib import Path

from featurelifted import (
    Group,
    Keyword,
    OneOrMore,
    ParseException,
    Regex,
    Suppress,
    Word,
    ZeroOrMore,
    alphas,
    nums,
)


def test_keyword_and_regex() -> None:
    grammar = Keyword("select") + Regex(r"[a-z]+")("col")
    assert grammar.parse_string("select name").as_dict()["col"] == "name"


def test_zero_one_or_more() -> None:
    grammar = Word(alphas) + ZeroOrMore(Suppress(",") + Word(alphas))
    assert grammar.parse_string("a,b,c").as_list() == ["a", "b", "c"]
    grammar2 = OneOrMore(Word(nums))
    assert grammar2.parse_string("1 2 3").as_list() == ["1", "2", "3"]


def test_group_structure() -> None:
    grammar = Group(Word(alphas) + Word(nums))
    result = grammar.parse_string("x 9")
    assert result.as_list() == [["x", "9"]]


def test_parse_all_flag() -> None:
    grammar = Word(alphas)
    try:
        grammar.parse_string("ab cd", parse_all=True)
        assert False
    except ParseException:
        pass


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\\s*(?:from pyparsing\\b|import pyparsing\\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''from featurelifted import (
    Group,
    Keyword,
    Literal,
    OneOrMore,
    Optional,
    ParseException,
    ParseResults,
    Regex,
    Suppress,
    Word,
    ZeroOrMore,
)


def test_required_api_surface() -> None:
    assert all(callable(x) or isinstance(x, type) for x in (
        Word, Literal, Keyword, Regex, Optional, ZeroOrMore, OneOrMore, Group, Suppress
    ))
    assert hasattr(Word(alphas := __import__('featurelifted').alphas), 'parse_string')
    assert ParseException is not None and ParseResults is not None
''',
        encoding="utf-8",
    )
    metadata = base_metadata(
        task_id,
        meta,
        feature={
            "name": "pyparsing grammar compose",
            "description": "Adapted pyparsing helpers + parse_string + ParseResults.",
            "source_entrypoints": ["pyparsing.Word", "pyparsing.ParserElement.parse_string"],
            "included_behaviors": [
                "compose Word/Literal/Keyword/Regex/Optional/ZeroOrMore/OneOrMore/Group/Suppress",
                "parse_string and named ParseResults",
                "ParseException on mismatch",
            ],
            "excluded_behaviors": ["railroad diagrams", "infixNotation suite", "parse actions"],
        },
        entanglement={
            "level": "medium",
            "types": ["parser_state_coupling"],
            "primary": "parser_state_coupling",
            "description": "ParserElement composition and results naming.",
            "signals": ["named results", "parse_all", "ParseException loc"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import Word, Literal, parse_string helpers",
            "callable": "Word",
            "signature": "Word(charset) -> ParserElement",
        },
        public_spec={
            "title": "pyparsing grammar compose",
            "summary": "Extract a task-scoped subset of `pyparsing` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.Word", "kind": "class"},
                {"path": "featurelifted.Literal", "kind": "class"},
                {"path": "featurelifted.Keyword", "kind": "class"},
                {"path": "featurelifted.Regex", "kind": "class"},
                {"path": "featurelifted.Optional", "kind": "class"},
                {"path": "featurelifted.ZeroOrMore", "kind": "class"},
                {"path": "featurelifted.OneOrMore", "kind": "class"},
                {"path": "featurelifted.Group", "kind": "class"},
                {"path": "featurelifted.Suppress", "kind": "class"},
                {"path": "featurelifted.ParseException", "kind": "exception"},
                {"path": "featurelifted.ParseResults", "kind": "class"},
                {"path": "featurelifted.alphas", "kind": "constant"},
                {"path": "featurelifted.nums", "kind": "constant"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: compose Word/Literal/Optional/Group helpers and parse_string with named results. Required observable cases include word literal compose; optional group."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: Keyword/Regex/ZeroOrMore/OneOrMore/Suppress composition. Required observable cases include keyword and regex; zero one or more; group structure."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: ParseException on mismatch including parse_all leftovers. Required observable cases include parse exception; parse all flag."},
                {"id": "B004", "text": "ParseResults supports as_list/as_dict accessors used in tests."},
                {"id": "B005", "text": "The package exposes the required task API paths for Word/Literal/Keyword/Regex/Optional/ZeroOrMore/OneOrMore/Group/Suppress/ParseException/ParseResults/alphas/nums with the kinds listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: pyparsing."},
            ],
            "exclusions": ["railroad diagrams", "infixNotation suite", "parse actions", "original pyparsing import at runtime"],
            "forbidden": {"imports": ["pyparsing"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


def materialize_structlog() -> Path:
    task_id = "structlog__processor_chain_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["pkg_dir"](), ref, "structlog")
    (task_dir / "requirements.lock").write_text("# no third-party dependencies on py3.12\n", encoding="utf-8")
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("structlog\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "structlog",
            "required_source_files": ["src/structlog/_config.py", "src/structlog/processors.py", "src/structlog/_base.py"],
            "runtime_dependencies": [],
            "notes": "Composite configure + processors + BoundLogger.",
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        '''from __future__ import annotations

import featurelifted as structlog


class ListLogger:
    def __init__(self):
        self.messages = []

    def msg(self, message):
        self.messages.append(message)

    def __getattr__(self, name):
        return self.msg


def test_bind_and_json_renderer() -> None:
    entries = []

    def factory(*args, **kwargs):
        logger = ListLogger()
        entries.append(logger)
        return logger

    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=factory,
        cache_logger_on_first_use=False,
    )
    log = structlog.get_logger().bind(user="a")
    log.info("hello", x=1)
    assert entries and '"user": "a"' in entries[0].messages[0]
    assert '"event": "hello"' in entries[0].messages[0]
    structlog.reset_defaults()


def test_key_value_renderer() -> None:
    sink = ListLogger()
    structlog.configure(
        processors=[structlog.processors.KeyValueRenderer()],
        logger_factory=lambda *a, **k: sink,
        cache_logger_on_first_use=False,
    )
    structlog.get_logger().info("evt", a=2)
    assert "a=2" in sink.messages[0] and "evt" in sink.messages[0]
    structlog.reset_defaults()
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        '''from __future__ import annotations

import re
from pathlib import Path

import featurelifted as structlog


class ListLogger:
    def __init__(self):
        self.messages = []

    def msg(self, message):
        self.messages.append(message)

    def __getattr__(self, name):
        return self.msg


def test_timestamp_and_unbind() -> None:
    sink = ListLogger()
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=lambda *a, **k: sink,
        cache_logger_on_first_use=False,
    )
    log = structlog.get_logger().bind(k=1).unbind("k").bind(k=2)
    log.warning("w")
    msg = sink.messages[0]
    assert '"k": 2' in msg and "timestamp" in msg and '"level": "warning"' in msg
    structlog.reset_defaults()


def test_new_context() -> None:
    sink = ListLogger()
    structlog.configure(
        processors=[structlog.processors.JSONRenderer()],
        logger_factory=lambda *a, **k: sink,
        cache_logger_on_first_use=False,
    )
    log = structlog.get_logger().bind(a=1).new(b=2)
    log.info("n")
    assert '"b": 2' in sink.messages[0] and '"a"' not in sink.messages[0]
    structlog.reset_defaults()


def test_processor_order() -> None:
    seen = []

    def mark(name):
        def proc(logger, method_name, event_dict):
            seen.append(name)
            return event_dict

        return proc

    sink = ListLogger()
    structlog.configure(
        processors=[mark("a"), mark("b"), structlog.processors.JSONRenderer()],
        logger_factory=lambda *a, **k: sink,
        cache_logger_on_first_use=False,
    )
    structlog.get_logger().info("x")
    assert seen == ["a", "b"]
    structlog.reset_defaults()


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\\s*(?:from structlog\\b|import structlog\\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''import featurelifted as structlog


def test_required_api_surface() -> None:
    assert callable(structlog.configure)
    assert callable(structlog.get_logger)
    assert callable(structlog.reset_defaults)
    assert structlog.processors.JSONRenderer is not None
    assert structlog.processors.KeyValueRenderer is not None
    assert structlog.processors.TimeStamper is not None
    assert structlog.processors.add_log_level is not None
''',
        encoding="utf-8",
    )
    metadata = base_metadata(
        task_id,
        meta,
        feature={
            "name": "structlog processor chain",
            "description": "Composite configure/get_logger/processors/bind.",
            "source_entrypoints": ["structlog.configure", "structlog.get_logger"],
            "included_behaviors": [
                "configure processor chain and get_logger",
                "bind/unbind/new context",
                "JSONRenderer KeyValueRenderer TimeStamper add_log_level",
            ],
            "excluded_behaviors": ["twisted/asyncio", "stdlib LoggerFactory integrations"],
        },
        entanglement={
            "level": "high",
            "types": ["data_model_coupling"],
            "primary": "data_model_coupling",
            "description": "Global configure state + ordered processors + bound context.",
            "signals": ["processor order", "bind/unbind", "reset_defaults"],
        },
        output={
            "package": "featurelifted",
            "import": "import featurelifted as structlog",
            "callable": "configure",
            "signature": "configure(processors=..., logger_factory=..., cache_logger_on_first_use=False)",
        },
        public_spec={
            "title": "structlog processor chain",
            "summary": "Extract a task-scoped subset of `structlog` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.configure", "kind": "function"},
                {"path": "featurelifted.get_logger", "kind": "function"},
                {"path": "featurelifted.reset_defaults", "kind": "function"},
                {"path": "featurelifted.processors.JSONRenderer", "kind": "class"},
                {"path": "featurelifted.processors.KeyValueRenderer", "kind": "class"},
                {"path": "featurelifted.processors.TimeStamper", "kind": "class"},
                {"path": "featurelifted.processors.add_log_level", "kind": "function"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: configure processor chain with JSONRenderer and bind context. Required observable cases include bind and json renderer; key value renderer."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: TimeStamper/add_log_level and unbind/new context. Required observable cases include timestamp and unbind; new context."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: processors run in configure order. Required observable cases include processor order."},
                {"id": "B004", "text": "reset_defaults clears global configuration between tests."},
                {"id": "B005", "text": "The package exposes the required task API paths `featurelifted.configure`, `featurelifted.get_logger`, `featurelifted.reset_defaults`, and the frozen processors with the kinds listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: structlog."},
            ],
            "exclusions": ["twisted/asyncio", "stdlib LoggerFactory integrations", "original structlog import at runtime"],
            "forbidden": {"imports": ["structlog"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


def materialize_sqlglot() -> Path:
    task_id = "sqlglot__parse_transpile_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["pkg_dir"](), ref, "sqlglot")
    # sqlglot may need version file
    ver = ref / "__init__.py"
    text = ver.read_text(encoding="utf-8")
    if "__version__" not in text:
        ver.write_text(text + '\n__version__ = "30.14.0"\n', encoding="utf-8")
    (task_dir / "requirements.lock").write_text("# no third-party dependencies\n", encoding="utf-8")
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("sqlglot\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "sqlglot",
            "required_source_files": ["sqlglot/__init__.py", "sqlglot/expressions.py", "sqlglot/dialects/"],
            "runtime_dependencies": [],
            "notes": "parse/transpile for sqlite/postgres/mysql only.",
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        '''from __future__ import annotations

from featurelifted import exp, parse_one, transpile
from featurelifted.errors import ParseError


def test_parse_one_select() -> None:
    node = parse_one("SELECT a FROM t")
    assert isinstance(node, exp.Select)
    rendered = node.sql()
    assert rendered == "SELECT a FROM t"


def test_transpile_sqlite_to_postgres() -> None:
    out = transpile("SELECT a FROM t", read="sqlite", write="postgres")
    assert out == ["SELECT a FROM t"]


def test_parse_error() -> None:
    try:
        parse_one("SELECT FROM")
        assert False
    except ParseError:
        pass
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        '''from __future__ import annotations

import re
from pathlib import Path

from featurelifted import exp, parse, parse_one, transpile


def test_parse_multiple() -> None:
    nodes = parse("SELECT 1; SELECT 2")
    assert len(nodes) == 2
    assert all(isinstance(n, exp.Select) for n in nodes)


def test_mysql_dialect_backticks() -> None:
    node = parse_one("SELECT `a` FROM t", read="mysql")
    assert isinstance(node, exp.Select)
    sql = node.sql(dialect="mysql")
    assert "a" in sql


def test_pretty_sql() -> None:
    node = parse_one("SELECT a, b FROM t")
    sql = node.sql(pretty=True)
    assert "SELECT" in sql and "FROM" in sql


def test_transpile_mysql_to_sqlite() -> None:
    out = transpile("SELECT `x` FROM t", read="mysql", write="sqlite")
    assert isinstance(out, list) and out and "x" in out[0]


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\\s*(?:from sqlglot\\b|import sqlglot\\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''from featurelifted import exp, parse, parse_one, transpile
from featurelifted.errors import ParseError


def test_required_api_surface() -> None:
    assert callable(parse_one) and callable(parse) and callable(transpile)
    assert exp.Select is not None and exp.Column is not None
    assert issubclass(ParseError, Exception)
''',
        encoding="utf-8",
    )
    metadata = base_metadata(
        task_id,
        meta,
        timeout=120,
        feature={
            "name": "sqlglot parse transpile",
            "description": "Composite parse/transpile for sqlite/postgres/mysql.",
            "source_entrypoints": ["sqlglot.parse_one", "sqlglot.transpile"],
            "included_behaviors": [
                "parse_one/parse into Expression",
                "transpile across sqlite/postgres/mysql",
                "Expression.sql and ParseError",
            ],
            "excluded_behaviors": ["optimizer suite", "execute against DB"],
        },
        entanglement={
            "level": "high",
            "types": ["parser_state_coupling"],
            "primary": "parser_state_coupling",
            "description": "SQL dialects and expression tree transform.",
            "signals": ["dialect read/write", "ParseError", "pretty sql"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import parse_one, transpile",
            "callable": "parse_one",
            "signature": "parse_one(sql: str, read: str | None = None) -> Expression",
        },
        public_spec={
            "title": "sqlglot parse transpile",
            "summary": "Extract a task-scoped subset of `sqlglot` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.parse_one", "kind": "function", "signature": "(sql: str, read: str | None = None)"},
                {"path": "featurelifted.parse", "kind": "function", "signature": "(sql: str, read: str | None = None)"},
                {"path": "featurelifted.transpile", "kind": "function", "signature": "(sql: str, read: str | None = None, write: str | None = None, pretty: bool = False)"},
                {"path": "featurelifted.exp.Select", "kind": "class"},
                {"path": "featurelifted.exp.Column", "kind": "class"},
                {"path": "featurelifted.errors.ParseError", "kind": "exception"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: parse_one/parse into Select expressions and raise ParseError on invalid SQL. Required observable cases include parse one select; parse error; parse multiple."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: transpile across sqlite/postgres/mysql. Required observable cases include transpile sqlite to postgres; transpile mysql to sqlite; mysql dialect backticks."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: Expression.sql with pretty formatting. Required observable cases include pretty sql."},
                {"id": "B004", "text": "Frozen dialects for required tests are sqlite, postgres, and mysql only."},
                {"id": "B005", "text": "The package exposes the required task API paths `featurelifted.parse_one`, `featurelifted.parse`, `featurelifted.transpile`, `featurelifted.exp.Select`, `featurelifted.exp.Column`, `featurelifted.errors.ParseError` with the kinds listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: sqlglot."},
            ],
            "exclusions": ["optimizer suite", "execute against DB", "original sqlglot import at runtime"],
            "forbidden": {"imports": ["sqlglot"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


def materialize_omegaconf() -> Path:
    task_id = "omegaconf__merge_interpolate_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    # Use wheel package (includes generated grammar parsers)
    copy_package_tree(meta["pkg_dir"](), ref, "omegaconf")
    (task_dir / "requirements.lock").write_text(
        "antlr4-python3-runtime==4.9.3\nPyYAML==6.0.2\n", encoding="utf-8"
    )
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("omegaconf\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "omegaconf",
            "required_source_files": ["omegaconf/omegaconf.py", "omegaconf/base.py", "omegaconf/grammar/"],
            "runtime_dependencies": ["antlr4-python3-runtime", "PyYAML"],
            "notes": "repo git tree omits generated grammar/gen; reference uses release wheel artifacts.",
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        '''from __future__ import annotations

from featurelifted import OmegaConf


def test_create_merge_resolve() -> None:
    a = OmegaConf.create({"x": 1, "y": "${x}"})
    b = OmegaConf.create({"z": 2})
    m = OmegaConf.merge(a, b)
    assert OmegaConf.to_container(m, resolve=True) == {"x": 1, "y": 1, "z": 2}


def test_select() -> None:
    cfg = OmegaConf.create({"a": {"b": 3}})
    assert OmegaConf.select(cfg, "a.b") == 3
    assert OmegaConf.select(cfg, "a.c", default=9) == 9


def test_is_helpers() -> None:
    cfg = OmegaConf.create({"m": "???", "n": None, "o": 1})
    assert OmegaConf.is_missing(cfg, "m")
    assert OmegaConf.select(cfg, "n") is None
    assert OmegaConf.is_config(cfg)
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        '''from __future__ import annotations

import re
from pathlib import Path

import pytest
from featurelifted import OmegaConf
from featurelifted.errors import ConfigKeyError, InterpolationResolutionError


def test_resolve_inplace() -> None:
    cfg = OmegaConf.create({"a": 1, "b": "${a}"})
    OmegaConf.resolve(cfg)
    assert cfg.b == 1


def test_interpolation_error() -> None:
    cfg = OmegaConf.create({"b": "${missing}"})
    with pytest.raises(InterpolationResolutionError):
        OmegaConf.to_container(cfg, resolve=True)


def test_struct_mode_key_error() -> None:
    cfg = OmegaConf.create({"a": 1})
    OmegaConf.set_struct(cfg, True)
    with pytest.raises((ConfigKeyError, KeyError, Exception)):
        cfg.missing = 2  # type: ignore[attr-defined]


def test_list_config_merge() -> None:
    a = OmegaConf.create({"items": [1, 2]})
    b = OmegaConf.create({"items": [3]})
    m = OmegaConf.merge(a, b)
    assert OmegaConf.to_container(m)["items"] == [3]


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\\s*(?:from omegaconf\\b|import omegaconf\\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''from featurelifted import OmegaConf
from featurelifted.errors import ConfigKeyError, InterpolationResolutionError


def test_required_api_surface() -> None:
    assert hasattr(OmegaConf, "create")
    assert hasattr(OmegaConf, "merge")
    assert hasattr(OmegaConf, "to_container")
    assert hasattr(OmegaConf, "select")
    assert hasattr(OmegaConf, "resolve")
    assert hasattr(OmegaConf, "is_missing")
    assert hasattr(OmegaConf, "is_config")
    assert hasattr(OmegaConf, "set_struct")
    assert InterpolationResolutionError is not None and ConfigKeyError is not None
''',
        encoding="utf-8",
    )
    metadata = base_metadata(
        task_id,
        meta,
        allowed_dependencies=["antlr4-python3-runtime", "PyYAML"],
        feature={
            "name": "omegaconf merge interpolate",
            "description": "Composite create/merge/interpolate/select.",
            "source_entrypoints": ["omegaconf.OmegaConf"],
            "included_behaviors": [
                "create/merge/to_container/select/resolve",
                "is_missing/is_config and null select",
                "struct mode key errors and interpolation errors",
            ],
            "excluded_behaviors": ["dataclass structured configs", "custom resolver registration"],
        },
        entanglement={
            "level": "high",
            "types": ["config_environment_coupling"],
            "primary": "config_environment_coupling",
            "description": "Config tree merge + interpolation resolution.",
            "signals": ["${} interpolate", "struct mode", "merge lists"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import OmegaConf",
            "callable": "OmegaConf.merge",
            "signature": "OmegaConf.merge(*configs) -> DictConfig",
        },
        public_spec={
            "title": "omegaconf merge interpolate",
            "summary": "Extract a task-scoped subset of `omegaconf` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.OmegaConf.create", "kind": "method"},
                {"path": "featurelifted.OmegaConf.merge", "kind": "method"},
                {"path": "featurelifted.OmegaConf.to_container", "kind": "method"},
                {"path": "featurelifted.OmegaConf.select", "kind": "method"},
                {"path": "featurelifted.OmegaConf.resolve", "kind": "method"},
                {"path": "featurelifted.OmegaConf.is_missing", "kind": "method"},
                {"path": "featurelifted.OmegaConf.is_config", "kind": "method"},
                {"path": "featurelifted.OmegaConf.set_struct", "kind": "method"},
                {"path": "featurelifted.errors.InterpolationResolutionError", "kind": "exception"},
                {"path": "featurelifted.errors.ConfigKeyError", "kind": "exception"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: create/merge/to_container with interpolation resolve and select. Required observable cases include create merge resolve; select."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: is_missing/is_config helpers and resolve inplace. Required observable cases include is helpers; resolve inplace."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: InterpolationResolutionError and struct-mode key errors. Required observable cases include interpolation error; struct mode key error."},
                {"id": "B004", "text": "ListConfig merge replaces list values as upstream default merge semantics used in tests."},
                {"id": "B005", "text": "The package exposes the required OmegaConf methods and InterpolationResolutionError/ConfigKeyError with the kinds listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: omegaconf."},
            ],
            "exclusions": ["dataclass structured configs", "custom resolver registration", "original omegaconf import at runtime"],
            "forbidden": {"imports": ["omegaconf"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


def materialize_cachecontrol() -> Path:
    task_id = "cachecontrol__heuristic_store_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["pkg_dir"](), ref, "cachecontrol")
    init = ref / "__init__.py"
    text = init.read_text(encoding="utf-8")
    if "0.14.4" not in text:
        init.write_text(
            text.replace(
                'importlib.metadata.version("cachecontrol")',
                '"0.14.4"',
            ).replace(
                'importlib.metadata.version("featurelifted")',
                '"0.14.4"',
            ),
            encoding="utf-8",
        )
    # re-export frozen symbols
    if "DictCache" not in init.read_text(encoding="utf-8").split("importlib")[0]:
        init.write_text(
            init.read_text(encoding="utf-8")
            + "\nfrom .cache import DictCache, BaseCache\n"
            + "from .heuristics import ExpiresAfter\n"
            + "from .serialize import Serializer\n"
            + "from .controller import CacheController\n",
            encoding="utf-8",
        )
    (task_dir / "requirements.lock").write_text(
        "requests==2.32.3\nmsgpack==1.1.0\n", encoding="utf-8"
    )
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("cachecontrol\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "cachecontrol",
            "required_source_files": [
                "cachecontrol/cache.py",
                "cachecontrol/heuristics.py",
                "cachecontrol/serialize.py",
                "cachecontrol/controller.py",
            ],
            "runtime_dependencies": ["requests", "msgpack"],
            "notes": "Offline DictCache + ExpiresAfter + Serializer; no live HTTP.",
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        '''from __future__ import annotations

from featurelifted import DictCache, ExpiresAfter, Serializer


def test_dict_cache_roundtrip() -> None:
    cache = DictCache()
    cache.set("k", b"value")
    assert cache.get("k") == b"value"
    cache.delete("k")
    assert cache.get("k") is None


def test_expires_after_construct() -> None:
    h = ExpiresAfter(days=1, hours=2)
    assert h is not None


def test_serializer_construct() -> None:
    assert Serializer() is not None
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        '''from __future__ import annotations

import re
from pathlib import Path

from featurelifted import BaseCache, CacheController, DictCache, ExpiresAfter, Serializer


def test_base_cache_interface() -> None:
    assert issubclass(DictCache, BaseCache)


def test_cache_controller_construct() -> None:
    ctrl = CacheController(DictCache())
    assert ctrl.cache is not None


def test_expires_after_days_hours() -> None:
    h = ExpiresAfter(days=0, hours=1)
    assert getattr(h, "delta", None) is not None or h is not None


def test_serializer_serde_version() -> None:
    ser = Serializer()
    version = getattr(ser, "serde_version", "1")
    assert version


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\\s*(?:from cachecontrol\\b|import cachecontrol\\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''from featurelifted import BaseCache, CacheController, DictCache, ExpiresAfter, Serializer


def test_required_api_surface() -> None:
    assert DictCache is not None and BaseCache is not None
    assert ExpiresAfter is not None and Serializer is not None and CacheController is not None
''',
        encoding="utf-8",
    )
    metadata = base_metadata(
        task_id,
        meta,
        allowed_dependencies=["requests", "msgpack"],
        feature={
            "name": "cachecontrol heuristic store",
            "description": "Composite DictCache + ExpiresAfter + Serializer + CacheController offline.",
            "source_entrypoints": [
                "cachecontrol.cache.DictCache",
                "cachecontrol.heuristics.ExpiresAfter",
                "cachecontrol.serialize.Serializer",
            ],
            "included_behaviors": [
                "DictCache get/set/delete",
                "ExpiresAfter construction",
                "Serializer and CacheController construction",
            ],
            "excluded_behaviors": ["requests Session integration", "FileCache", "network"],
        },
        entanglement={
            "level": "high",
            "types": ["data_model_coupling"],
            "primary": "data_model_coupling",
            "description": "Cache store + heuristic + serializer composition.",
            "signals": ["DictCache", "ExpiresAfter", "Serializer"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import DictCache, ExpiresAfter, Serializer, CacheController",
            "callable": "DictCache",
            "signature": "DictCache()",
        },
        public_spec={
            "title": "cachecontrol heuristic store",
            "summary": "Extract a task-scoped subset of `cachecontrol` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.DictCache", "kind": "class"},
                {"path": "featurelifted.BaseCache", "kind": "class"},
                {"path": "featurelifted.ExpiresAfter", "kind": "class"},
                {"path": "featurelifted.Serializer", "kind": "class"},
                {"path": "featurelifted.CacheController", "kind": "class"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: DictCache get/set/delete. Required observable cases include dict cache roundtrip."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: ExpiresAfter and Serializer construction. Required observable cases include expires after construct; serializer construct; expires after days hours; serializer serde version."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: CacheController wraps a cache and DictCache subclasses BaseCache. Required observable cases include cache controller construct; base cache interface."},
                {"id": "B004", "text": "No live HTTP is required; tests use in-memory DictCache only."},
                {"id": "B005", "text": "The package exposes DictCache/BaseCache/ExpiresAfter/Serializer/CacheController with the kinds listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: cachecontrol."},
            ],
            "exclusions": ["requests Session integration", "FileCache", "network", "original cachecontrol import at runtime"],
            "forbidden": {"imports": ["cachecontrol"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


def materialize_flask_login() -> Path:
    task_id = "flask_login__session_guard_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["pkg_dir"](), ref, "flask_login")
    (task_dir / "requirements.lock").write_text(
        "Flask==3.0.3\nWerkzeug==3.0.3\nJinja2==3.1.4\nitsdangerous==2.2.0\nclick==8.1.7\nblinker==1.8.2\n",
        encoding="utf-8",
    )
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("flask_login\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "flask_login",
            "required_source_files": [
                "src/flask_login/login_manager.py",
                "src/flask_login/utils.py",
                "src/flask_login/mixins.py",
            ],
            "runtime_dependencies": ["Flask"],
            "notes": "Flask test_request_context only; flask allowed, flask_login forbidden.",
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        '''from __future__ import annotations

from flask import Flask

from featurelifted import LoginManager, UserMixin, current_user, login_user, logout_user


class User(UserMixin):
    def __init__(self, id_: str) -> None:
        self.id = id_


def test_login_logout_current_user() -> None:
    app = Flask(__name__)
    app.secret_key = "test"
    lm = LoginManager()
    lm.init_app(app)

    @lm.user_loader
    def load_user(user_id: str):
        return User(user_id)

    with app.test_request_context("/"):
        user = User("1")
        assert login_user(user) is True
        user_proxy = current_user
        assert user_proxy.is_authenticated
        assert user_proxy.get_id() == "1"
        logout_user()
        user_proxy = current_user
        assert not user_proxy.is_authenticated


def test_user_mixin_anonymous() -> None:
    u = User("x")
    assert u.is_authenticated and not u.is_anonymous
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        '''from __future__ import annotations

import re
from pathlib import Path

from flask import Flask

from featurelifted import LoginManager, UserMixin, login_required, login_user


class User(UserMixin):
    def __init__(self, id_: str) -> None:
        self.id = id_


def test_login_required_redirects_anonymous() -> None:
    app = Flask(__name__)
    app.secret_key = "test"
    lm = LoginManager()
    lm.init_app(app)
    lm.login_view = "login"

    @lm.user_loader
    def load_user(user_id: str):
        return User(user_id)

    @app.route("/login")
    def login():
        return "login"

    @app.route("/private")
    @login_required
    def private():
        return "secret"

    client = app.test_client()
    resp = client.get("/private")
    assert resp.status_code in {302, 401}


def test_remember_flag() -> None:
    app = Flask(__name__)
    app.secret_key = "test"
    lm = LoginManager()
    lm.init_app(app)

    @lm.user_loader
    def load_user(user_id: str):
        return User(user_id)

    with app.test_request_context("/"):
        assert login_user(User("2"), remember=True) is True


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\\s*(?:from flask_login\\b|import flask_login\\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''from featurelifted import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)


def test_required_api_surface() -> None:
    assert LoginManager is not None and UserMixin is not None
    assert callable(login_user) and callable(logout_user) and callable(login_required)
    assert current_user is not None
''',
        encoding="utf-8",
    )
    metadata = base_metadata(
        task_id,
        meta,
        allowed_dependencies=["Flask", "Werkzeug", "Jinja2", "itsdangerous", "click", "blinker"],
        feature={
            "name": "flask-login session guard",
            "description": "Composite LoginManager + session user helpers.",
            "source_entrypoints": [
                "flask_login.LoginManager",
                "flask_login.login_user",
                "flask_login.current_user",
            ],
            "included_behaviors": [
                "user_loader login/logout current_user",
                "login_required guard",
                "UserMixin flags and remember",
            ],
            "excluded_behaviors": ["LDAP", "real HTTP servers"],
        },
        entanglement={
            "level": "high",
            "types": ["framework_coupling"],
            "primary": "framework_coupling",
            "description": "Flask request/session context required.",
            "signals": ["login_required", "current_user", "session keys"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import LoginManager, login_user, current_user",
            "callable": "login_user",
            "signature": "login_user(user, remember: bool = False) -> bool",
        },
        public_spec={
            "title": "flask-login session guard",
            "summary": "Extract a task-scoped subset of `flask-login` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.LoginManager", "kind": "class"},
                {"path": "featurelifted.UserMixin", "kind": "class"},
                {"path": "featurelifted.login_user", "kind": "function"},
                {"path": "featurelifted.logout_user", "kind": "function"},
                {"path": "featurelifted.login_required", "kind": "function"},
                {"path": "featurelifted.current_user", "kind": "attribute"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: login/logout/current_user with UserMixin. Required observable cases include login logout current user; user mixin anonymous."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: login_required guards anonymous users. Required observable cases include login required redirects anonymous."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: remember flag on login_user. Required observable cases include remember flag."},
                {"id": "B004", "text": "Tests use Flask test_request_context/test_client only; Flask is an allowed dependency."},
                {"id": "B005", "text": "The package exposes LoginManager/UserMixin/login_user/logout_user/login_required/current_user with the kinds listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: flask_login."},
            ],
            "exclusions": ["LDAP", "real HTTP servers", "original flask_login import at runtime"],
            "forbidden": {"imports": ["flask_login"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


def materialize_watchdog() -> Path:
    task_id = "watchdog__observer_dispatch_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["pkg_dir"](), ref, "watchdog")
    # Prefer PollingObserver as Observer for deterministic tests
    init = ref / "__init__.py"
    # export convenience names via events/observers packages already
    (ref / "__init__.py").write_text(
        (init.read_text(encoding="utf-8") if init.exists() else "")
        + "\nfrom .observers.polling import PollingObserver as Observer\n"
        + "from .events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent, FileDeletedEvent\n",
        encoding="utf-8",
    )
    (task_dir / "requirements.lock").write_text("# no third-party dependencies\n", encoding="utf-8")
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("watchdog\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "watchdog",
            "required_source_files": [
                "src/watchdog/observers/polling.py",
                "src/watchdog/events.py",
            ],
            "runtime_dependencies": [],
            "notes": "PollingObserver exported as Observer for deterministic offline tests.",
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        '''from __future__ import annotations

import time
from pathlib import Path

from featurelifted import FileSystemEventHandler, Observer


class Handler(FileSystemEventHandler):
    def __init__(self) -> None:
        self.created = []

    def on_created(self, event):  # type: ignore[override]
        self.created.append(event.src_path)


def test_observer_create_event(tmp_path: Path) -> None:
    handler = Handler()
    obs = Observer(timeout=0.2)
    obs.schedule(handler, str(tmp_path), recursive=False)
    obs.start()
    try:
        target = tmp_path / "a.txt"
        target.write_text("x", encoding="utf-8")
        deadline = time.time() + 3
        while time.time() < deadline and not handler.created:
            time.sleep(0.1)
        assert any(str(target) in p or p.endswith("a.txt") for p in handler.created)
    finally:
        obs.stop()
        obs.join(timeout=3)
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        '''from __future__ import annotations

import re
import time
from pathlib import Path

from featurelifted import (
    FileCreatedEvent,
    FileDeletedEvent,
    FileModifiedEvent,
    FileSystemEventHandler,
    Observer,
)


class Collect(FileSystemEventHandler):
    def __init__(self) -> None:
        self.events = []

    def on_any_event(self, event):  # type: ignore[override]
        self.events.append(type(event).__name__)


def test_modify_and_delete(tmp_path: Path) -> None:
    handler = Collect()
    obs = Observer(timeout=0.2)
    obs.schedule(handler, str(tmp_path), recursive=False)
    obs.start()
    try:
        f = tmp_path / "b.txt"
        f.write_text("1", encoding="utf-8")
        time.sleep(0.4)
        f.write_text("2", encoding="utf-8")
        time.sleep(0.4)
        f.unlink()
        deadline = time.time() + 3
        while time.time() < deadline and len(handler.events) < 2:
            time.sleep(0.1)
        assert handler.events
    finally:
        obs.stop()
        obs.join(timeout=3)


def test_event_types_exist() -> None:
    assert FileCreatedEvent is not None
    assert FileModifiedEvent is not None
    assert FileDeletedEvent is not None


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\\s*(?:from watchdog\\b|import watchdog\\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''from featurelifted import (
    FileCreatedEvent,
    FileDeletedEvent,
    FileModifiedEvent,
    FileSystemEventHandler,
    Observer,
)


def test_required_api_surface() -> None:
    assert Observer is not None and FileSystemEventHandler is not None
    assert FileCreatedEvent and FileModifiedEvent and FileDeletedEvent
''',
        encoding="utf-8",
    )
    metadata = base_metadata(
        task_id,
        meta,
        timeout=120,
        feature={
            "name": "watchdog observer dispatch",
            "description": "Composite PollingObserver-as-Observer + event handler callbacks.",
            "source_entrypoints": [
                "watchdog.observers.polling.PollingObserver",
                "watchdog.events.FileSystemEventHandler",
            ],
            "included_behaviors": [
                "schedule/start/stop observer",
                "on_created/modify/delete callbacks",
                "event type classes",
            ],
            "excluded_behaviors": ["inotify-specific flags", "watchmedo CLI"],
        },
        entanglement={
            "level": "high",
            "types": ["resource_coupling"],
            "primary": "resource_coupling",
            "description": "Filesystem observer thread + handler dispatch.",
            "signals": ["PollingObserver", "temp dir events", "start/stop"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import Observer, FileSystemEventHandler",
            "callable": "Observer.schedule",
            "signature": "schedule(handler, path: str, recursive: bool = False)",
        },
        public_spec={
            "title": "watchdog observer dispatch",
            "summary": "Extract a task-scoped subset of `watchdog` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.Observer", "kind": "class"},
                {"path": "featurelifted.FileSystemEventHandler", "kind": "class"},
                {"path": "featurelifted.FileCreatedEvent", "kind": "class"},
                {"path": "featurelifted.FileModifiedEvent", "kind": "class"},
                {"path": "featurelifted.FileDeletedEvent", "kind": "class"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: Observer schedule/start/stop delivers create events to FileSystemEventHandler. Required observable cases include observer create event."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: modify/delete callbacks fire for temp-dir file changes. Required observable cases include modify and delete."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: FileCreatedEvent/FileModifiedEvent/FileDeletedEvent types exist. Required observable cases include event types exist."},
                {"id": "B004", "text": "Observer is the polling implementation for deterministic offline tests."},
                {"id": "B005", "text": "The package exposes Observer/FileSystemEventHandler/FileCreatedEvent/FileModifiedEvent/FileDeletedEvent with the kinds listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: watchdog."},
            ],
            "exclusions": ["inotify-specific flags", "watchmedo CLI", "original watchdog import at runtime"],
            "forbidden": {"imports": ["watchdog"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


BUILDERS: dict[str, Callable[[], Path]] = {
    "tinycss2__stylesheet_roundtrip_core__001": materialize_tinycss2,
    "pyparsing__grammar_compose_core__001": materialize_pyparsing,
    "structlog__processor_chain_core__001": materialize_structlog,
    "sqlglot__parse_transpile_core__001": materialize_sqlglot,
    "omegaconf__merge_interpolate_core__001": materialize_omegaconf,
    "cachecontrol__heuristic_store_core__001": materialize_cachecontrol,
    "flask_login__session_guard_core__001": materialize_flask_login,
    "watchdog__observer_dispatch_core__001": materialize_watchdog,
}


def main(argv: list[str]) -> int:
    targets = argv[1:] or list(BUILDERS)
    for task_id in targets:
        if task_id not in BUILDERS:
            print(f"unknown/not-yet-supported: {task_id}", file=sys.stderr)
            return 1
        path = BUILDERS[task_id]()
        print(f"materialized {task_id} -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
