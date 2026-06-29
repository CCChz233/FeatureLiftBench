#!/usr/bin/env python3
"""Build a featurelifted oracle submission by copying modules from a task repo snapshot."""

from __future__ import annotations

import argparse
import ast
import json
import re
import shutil
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "harness") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "harness"))

from featureliftbench.paths import SUBMISSIONS_DIR, VENDOR_WHEELS_DIR

IMPORT_RE = re.compile(
    r"\b(?P<name>sqlparse|coverage|jinja2|_pytest|pytest|vibe_app|werkzeug|typer|importlib_metadata|h11|redis|httpx|pydantic|dateutil|jsonpath_ng|configobj|croniter|websockets|voluptuous|cerberus|sortedcontainers|pathvalidate|bidict|xmltodict|email_validator|cattrs|mako|msgpack|dataclasses_json|dotenv|python_multipart|multipart|pendulum|environs|dynaconf|phonenumbers|passlib|pydantic_settings|chameleon)\b"
)


def rewrite_source(text: str, package: str) -> str:
    """Rewrite package imports and module paths without touching string literals."""
    patterns = [
        (re.compile(rf"^(\s*)from {package}\.", re.MULTILINE), rf"\1from featurelifted."),
        (re.compile(rf"^(\s*)from {package}\b", re.MULTILINE), rf"\1from featurelifted"),
        (re.compile(rf"^(\s*)import {package}\.", re.MULTILINE), rf"\1import featurelifted."),
        (re.compile(rf"^(\s*)import {package}\b", re.MULTILINE), rf"\1import featurelifted"),
    ]
    for pattern, replacement in patterns:
        text = pattern.sub(replacement, text)
    return text


def copy_tree(
    src_root: Path,
    dst_root: Path,
    rel_paths: list[str],
    *,
    package: str,
) -> None:
    if dst_root.exists():
        shutil.rmtree(dst_root)
    dst_root.mkdir(parents=True, exist_ok=True)

    for rel in rel_paths:
        src = src_root / rel
        if not src.exists():
            raise FileNotFoundError(f"missing source path: {src}")
        dst = dst_root / rel.replace(f"{package}/", "featurelifted/", 1)
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            continue
        content = rewrite_source(src.read_text(encoding="utf-8"), package)
        dst.write_text(content, encoding="utf-8")

    for rel in rel_paths:
        src = src_root / rel
        if src.is_dir():
            dst = dst_root / rel.replace(f"{package}/", "featurelifted/", 1)
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            for path in dst.rglob("*.py"):
                path.write_text(
                    rewrite_source(path.read_text(encoding="utf-8"), package),
                    encoding="utf-8",
                )


def write_init(dst_root: Path, content: str) -> None:
    init_path = dst_root / "featurelifted" / "__init__.py"
    init_path.parent.mkdir(parents=True, exist_ok=True)
    init_path.write_text(content, encoding="utf-8")


def write_filters_init(dst_root: Path) -> None:
    init_path = dst_root / "featurelifted" / "filters" / "__init__.py"
    init_path.parent.mkdir(parents=True, exist_ok=True)
    init_path.write_text(
        'from featurelifted.filters.others import StripTrailingSemicolonFilter\n\n'
        '__all__ = ["StripTrailingSemicolonFilter"]\n',
        encoding="utf-8",
    )


def patch_filter_stack_import(dst_root: Path) -> None:
    path = dst_root / "featurelifted" / "engine" / "filter_stack.py"
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        "from featurelifted.filters import StripTrailingSemicolonFilter",
        "from featurelifted.filters.others import StripTrailingSemicolonFilter",
    )
    path.write_text(text, encoding="utf-8")


SQLPARSE_PARSE_SPLIT_PATHS = [
    "sqlparse/__init__.py",
    "sqlparse/exceptions.py",
    "sqlparse/keywords.py",
    "sqlparse/lexer.py",
    "sqlparse/sql.py",
    "sqlparse/tokens.py",
    "sqlparse/utils.py",
    "sqlparse/engine/__init__.py",
    "sqlparse/engine/grouping.py",
    "sqlparse/engine/statement_splitter.py",
    "sqlparse/engine/filter_stack.py",
    "sqlparse/filters/others.py",
]

SQLPARSE_FORMAT_PATHS = SQLPARSE_PARSE_SPLIT_PATHS + [
    "sqlparse/formatter.py",
    "sqlparse/engine/filter_stack.py",
    "sqlparse/filters/__init__.py",
    "sqlparse/filters/aligned_indent.py",
    "sqlparse/filters/others.py",
    "sqlparse/filters/output.py",
    "sqlparse/filters/reindent.py",
    "sqlparse/filters/right_margin.py",
    "sqlparse/filters/tokens.py",
]

SQLPARSE_PARSE_SPLIT_INIT = '''\
"""Parse SQL statements (parse/split only)."""

from collections.abc import Generator
from typing import IO

from featurelifted import engine, sql, tokens

__all__ = ["engine", "sql", "tokens", "parse", "parsestream", "split"]


def parse(sql: str, encoding: str | None = None) -> tuple[sql.Statement, ...]:
    return tuple(parsestream(sql, encoding))


def parsestream(
    stream: str | IO[str], encoding: str | None = None
) -> Generator[sql.Statement, None, None]:
    stack = engine.FilterStack()
    stack.enable_grouping()
    return stack.run(stream, encoding)


def split(
    sql: str, encoding: str | None = None, strip_semicolon: bool = False
) -> list[str]:
    stack = engine.FilterStack(strip_semicolon=strip_semicolon)
    return [str(stmt).strip() for stmt in stack.run(sql, encoding)]
'''

SQLPARSE_FORMAT_INIT = '''\
"""Parse and format SQL statements."""

from collections.abc import Generator
from typing import IO, Any

from featurelifted import engine, filters, formatter, sql, tokens

__all__ = ["engine", "filters", "formatter", "sql", "tokens", "parse", "parsestream", "split", "format"]


def parse(sql: str, encoding: str | None = None) -> tuple[sql.Statement, ...]:
    return tuple(parsestream(sql, encoding))


def parsestream(
    stream: str | IO[str], encoding: str | None = None
) -> Generator[sql.Statement, None, None]:
    stack = engine.FilterStack()
    stack.enable_grouping()
    return stack.run(stream, encoding)


def format(sql: str, encoding: str | None = None, **options: Any) -> str:
    stack = engine.FilterStack()
    options = formatter.validate_options(options)
    stack = formatter.build_filter_stack(stack, options)
    stack.postprocess.append(filters.SerializerUnicode())
    return "".join(stack.run(sql, encoding))


def split(
    sql: str, encoding: str | None = None, strip_semicolon: bool = False
) -> list[str]:
    stack = engine.FilterStack(strip_semicolon=strip_semicolon)
    return [str(stmt).strip() for stmt in stack.run(sql, encoding)]
'''

SQLPARSE_FORMAT_ONLY_INIT = '''\
"""Format SQL statements."""

from typing import Any

from featurelifted import engine, filters, formatter

__all__ = ["format"]


def format(sql: str, encoding: str | None = None, **options: Any) -> str:
    stack = engine.FilterStack()
    options = formatter.validate_options(options)
    stack = formatter.build_filter_stack(stack, options)
    stack.postprocess.append(filters.SerializerUnicode())
    return "".join(stack.run(sql, encoding))
'''

SQLPARSE_TOKEN_TREE_INIT = '''\
"""Parse SQL statements and navigate token trees."""

from collections.abc import Generator
from typing import IO

from featurelifted import engine, sql, tokens

__all__ = ["engine", "sql", "tokens", "parse", "parsestream"]


def parse(sql: str, encoding: str | None = None) -> tuple[sql.Statement, ...]:
    return tuple(parsestream(sql, encoding))


def parsestream(
    stream: str | IO[str], encoding: str | None = None
) -> Generator[sql.Statement, None, None]:
    stack = engine.FilterStack()
    stack.enable_grouping()
    return stack.run(stream, encoding)
'''


def build_sqlparse(task_dir: Path, profile: str, output: Path) -> None:
    repo_pkg = task_dir / "repo" / "sqlparse"
    if not repo_pkg.is_dir():
        raise SystemExit(f"missing repo snapshot: {repo_pkg}")

    if profile == "parse_split":
        paths = SQLPARSE_PARSE_SPLIT_PATHS
        init = SQLPARSE_PARSE_SPLIT_INIT
    elif profile == "token_tree":
        paths = SQLPARSE_PARSE_SPLIT_PATHS
        init = SQLPARSE_TOKEN_TREE_INIT
    elif profile == "format_filters":
        paths = SQLPARSE_FORMAT_PATHS
        init = SQLPARSE_FORMAT_ONLY_INIT
    elif profile == "parse_format":
        paths = SQLPARSE_FORMAT_PATHS
        init = SQLPARSE_FORMAT_INIT
    else:
        raise SystemExit(f"unknown sqlparse profile: {profile}")

    copy_tree(task_dir / "repo", output, paths, package="sqlparse")
    write_init(output, init)
    if profile in {"parse_split", "token_tree"}:
        write_filters_init(output)
        patch_filter_stack_import(output)


VIBE_APP_PRICING_PATHS = [
    "vibe_app/state.py",
    "vibe_app/helpers/__init__.py",
    "vibe_app/helpers/money.py",
    "vibe_app/pricing/__init__.py",
    "vibe_app/pricing/discounts.py",
    "vibe_app/pricing/tiers.py",
    "vibe_app/pricing/rules.py",
]

VIBE_APP_CONFIG_PATHS = [
    "vibe_app/state.py",
    "vibe_app/yaml_compat.py",
    "vibe_app/config_merge.py",
    "vibe_app/config_loader.py",
]

VIBE_APP_CSV_PATHS = [
    "vibe_app/state.py",
    "vibe_app/helpers/strings.py",
    "vibe_app/csv_transform/__init__.py",
    "vibe_app/csv_transform/schema.py",
    "vibe_app/csv_transform/reader.py",
    "vibe_app/csv_transform/mapper.py",
    "vibe_app/csv_transform/cleaner.py",
    "vibe_app/csv_transform/writer.py",
    "vibe_app/csv_transform/pipeline.py",
    "vibe_app/csv_transform/transforms/__init__.py",
    "vibe_app/csv_transform/transforms/normalize.py",
    "vibe_app/csv_transform/transforms/filter_rows.py",
    "vibe_app/csv_transform/transforms/aggregate.py",
    "vibe_app/csv_transform/transforms/dedupe.py",
]

VIBE_APP_RULES_ENGINE_PATHS = [
    "vibe_app/state.py",
    "vibe_app/rules_engine/__init__.py",
    "vibe_app/rules_engine/conditions.py",
    "vibe_app/rules_engine/actions.py",
    "vibe_app/rules_engine/engine.py",
]

VIBE_APP_SESSION_REGISTRY_PATHS = [
    "vibe_app/state.py",
    "vibe_app/session_registry/__init__.py",
    "vibe_app/session_registry/tokens.py",
    "vibe_app/session_registry/store.py",
    "vibe_app/session_registry/registry.py",
]

VIBE_APP_ORM_QUERY_PATHS = [
    "vibe_app/state.py",
    "vibe_app/orm_query/__init__.py",
    "vibe_app/orm_query/ast.py",
    "vibe_app/orm_query/query.py",
    "vibe_app/orm_query/compiler.py",
]

VIBE_APP_PLUGIN_REGISTRY_PATHS = [
    "vibe_app/state.py",
    "vibe_app/plugin_registry/__init__.py",
    "vibe_app/plugin_registry/base.py",
    "vibe_app/plugin_registry/metaclass.py",
    "vibe_app/plugin_registry/registry.py",
]

VIBE_APP_PRICING_INIT = '''\
"""Pricing rules engine."""

from featurelifted.pricing.rules import PricingContext, compute_line_price

__all__ = ["PricingContext", "compute_line_price"]
'''

VIBE_APP_CONFIG_INIT = '''\
"""YAML config bootstrap and merge."""

from featurelifted.config_loader import bootstrap_config
from featurelifted.config_merge import merge_config_layers

__all__ = ["bootstrap_config", "merge_config_layers"]
'''

VIBE_APP_CSV_INIT = '''\
"""CSV transform pipeline."""

from featurelifted.csv_transform.pipeline import TransformOptions, transform_csv

__all__ = ["TransformOptions", "transform_csv"]
'''

VIBE_APP_RULES_ENGINE_INIT = '''\
"""Business rules evaluation engine."""

from featurelifted.rules_engine.engine import Rule, RulesEngine, evaluate_rules

__all__ = ["Rule", "RulesEngine", "evaluate_rules"]
'''

VIBE_APP_SESSION_REGISTRY_INIT = '''\
"""Session token registry."""

from featurelifted.session_registry.registry import SessionRegistry

__all__ = ["SessionRegistry"]
'''

VIBE_APP_ORM_QUERY_INIT = '''\
"""ORM query builder and SQL AST compiler."""

from featurelifted.orm_query.compiler import compile_query
from featurelifted.orm_query.query import Query

__all__ = ["Query", "compile_query"]
'''

VIBE_APP_PLUGIN_REGISTRY_INIT = '''\
"""Plugin registry and metaclass discovery."""

from featurelifted.plugin_registry.base import BasePlugin
from featurelifted.plugin_registry.metaclass import PluginMeta
from featurelifted.plugin_registry.registry import PluginRegistry

__all__ = ["BasePlugin", "PluginMeta", "PluginRegistry"]
'''


COVERAGE_BASE_PATHS = [
    "coverage/env.py",
    "coverage/exceptions.py",
    "coverage/types.py",
    "coverage/misc.py",
]

COVERAGE_GLOB_PATHS = COVERAGE_BASE_PATHS + [
    "coverage/files.py",
]

COVERAGE_PATH_REMAP_PATHS = COVERAGE_GLOB_PATHS

COVERAGE_CONFIG_PATHS = COVERAGE_BASE_PATHS + [
    "coverage/config.py",
    "coverage/tomlconfig.py",
]

COVERAGE_SOURCE_PATHS = COVERAGE_BASE_PATHS + [
    "coverage/files.py",
    "coverage/config.py",
    "coverage/tomlconfig.py",
    "coverage/disposition.py",
    "coverage/inorout.py",
]

COVERAGE_REPORT_PATHS = COVERAGE_BASE_PATHS + [
    "coverage/files.py",
    "coverage/version.py",
    "coverage/results.py",
    "coverage/plugin.py",
    "coverage/report_core.py",
    "coverage/xmlreport.py",
    "coverage/config.py",
    "coverage/tomlconfig.py",
]

COVERAGE_GLOB_INIT = '''\
"""Glob pattern matching for coverage file paths."""

from featurelifted.files import GlobMatcher, globs_to_regex, prep_patterns

__all__ = ["GlobMatcher", "globs_to_regex", "prep_patterns"]
'''

COVERAGE_CONFIG_INIT = '''\
"""Coverage.py run-section configuration reading and merging."""

from featurelifted.config import CoverageConfig, read_coverage_config


def read_run_config(
    config_file: bool | str = True,
    warn=None,
    **kwargs,
):
    """Read configuration with run-section merge semantics."""
    if warn is None:
        warn = lambda _msg: None
    return read_coverage_config(config_file, warn, **kwargs)


__all__ = ["CoverageConfig", "read_coverage_config", "read_run_config"]
'''

COVERAGE_PATH_REMAP_INIT = '''\
"""Path alias remapping for combined coverage data."""

from featurelifted.files import PathAliases

__all__ = ["PathAliases"]
'''

COVERAGE_SOURCE_INIT = '''\
"""Source/include/omit file selection for coverage measurement."""

from __future__ import annotations

from featurelifted.config import CoverageConfig
from featurelifted.inorout import InOrOut


class SourceSelector:
    """Determine whether a file should be measured."""

    def __init__(
        self,
        *,
        source: list[str] | None = None,
        source_pkgs: list[str] | None = None,
        run_include: list[str] | None = None,
        run_omit: list[str] | None = None,
        cover_pylib: bool = False,
    ) -> None:
        config = CoverageConfig()
        config.source = source
        config.source_pkgs = list(source_pkgs or [])
        config.run_include = list(run_include or [])
        config.run_omit = list(run_omit or [])
        config.cover_pylib = cover_pylib
        self._inorout = InOrOut(
            config,
            warn=lambda _msg, slug=None: None,
            debug=None,
            include_namespace_packages=False,
        )

    def skip_reason(self, filename: str, modulename: str | None = None) -> str | None:
        """Return a skip reason, or None if the file should be measured."""
        if modulename is None:
            return self._inorout.check_include_omit_etc(filename, None)

        import featurelifted.inorout as inorout_mod

        original = inorout_mod.name_for_module
        inorout_mod.name_for_module = lambda _filename, _frame: modulename
        try:
            return self._inorout.check_include_omit_etc(filename, None)
        finally:
            inorout_mod.name_for_module = original


__all__ = ["SourceSelector"]
'''

COVERAGE_REPORT_INIT = '''\
"""Cobertura XML report writer for coverage.py."""

from featurelifted.config import CoverageConfig
from featurelifted.results import Analysis
from featurelifted.xmlreport import XmlReporter, rate, serialize_xml

__all__ = ["Analysis", "CoverageConfig", "XmlReporter", "rate", "serialize_xml"]
'''

PYTHON_MINIMAL = '''\
"""Minimal python helpers needed by source selection."""

from __future__ import annotations

import os
import types

from featurelifted import env
from featurelifted.exceptions import CoverageException
from featurelifted.types import TMorf


def source_for_file(filename: str) -> str:
    """Return the source filename for `filename`."""
    if filename.endswith(".py"):
        return filename
    if filename.endswith((".pyc", ".pyo")):
        py_filename = filename[:-1]
        if os.path.exists(py_filename):
            return py_filename
        if env.WINDOWS:
            pyw_filename = py_filename + "w"
            if os.path.exists(pyw_filename):
                return pyw_filename
        return py_filename
    return filename


def source_for_morf(morf: TMorf) -> str:
    """Get the source filename for the module-or-file `morf`."""
    if hasattr(morf, "__file__") and morf.__file__:
        filename = morf.__file__
    elif isinstance(morf, types.ModuleType):
        raise CoverageException(f"Module {morf} has no file")
    elif isinstance(morf, str):
        filename = morf
    else:
        raise CoverageException(f"Don't know how to get source for {morf!r}")
    return source_for_file(filename)
'''


def write_python_minimal(dst_root: Path) -> None:
    path = dst_root / "featurelifted" / "python.py"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(PYTHON_MINIMAL, encoding="utf-8")


def build_coverage(task_dir: Path, profile: str, output: Path) -> None:
    repo_pkg = task_dir / "repo" / "coverage"
    if not repo_pkg.is_dir():
        raise SystemExit(f"missing repo snapshot: {repo_pkg}")

    if profile == "glob_matcher":
        paths = COVERAGE_GLOB_PATHS
        init = COVERAGE_GLOB_INIT
    elif profile == "path_remap":
        paths = COVERAGE_PATH_REMAP_PATHS
        init = COVERAGE_PATH_REMAP_INIT
    elif profile == "config_merge":
        paths = COVERAGE_CONFIG_PATHS
        init = COVERAGE_CONFIG_INIT
    elif profile == "source_selection":
        paths = COVERAGE_SOURCE_PATHS
        init = COVERAGE_SOURCE_INIT
    elif profile == "report_core":
        paths = COVERAGE_REPORT_PATHS
        init = COVERAGE_REPORT_INIT
    else:
        raise SystemExit(f"unknown coverage profile: {profile}")

    copy_tree(task_dir / "repo", output, paths, package="coverage")
    write_init(output, init)
    if profile == "source_selection":
        write_python_minimal(output)
    post_process = MANIFEST_POST_PROCESS.get(task_dir.name)
    if post_process:
        post_process(output)


def build_vibe_app(task_dir: Path, profile: str, output: Path) -> None:
    repo_pkg = task_dir / "repo" / "vibe_app"
    if not repo_pkg.is_dir():
        raise SystemExit(f"missing repo snapshot: {repo_pkg}")

    if profile == "pricing_rules":
        paths = VIBE_APP_PRICING_PATHS
        init = VIBE_APP_PRICING_INIT
    elif profile == "yaml_config":
        paths = VIBE_APP_CONFIG_PATHS
        init = VIBE_APP_CONFIG_INIT
    elif profile == "csv_transform":
        paths = VIBE_APP_CSV_PATHS
        init = VIBE_APP_CSV_INIT
    elif profile == "rules_engine":
        paths = VIBE_APP_RULES_ENGINE_PATHS
        init = VIBE_APP_RULES_ENGINE_INIT
    elif profile == "session_registry":
        paths = VIBE_APP_SESSION_REGISTRY_PATHS
        init = VIBE_APP_SESSION_REGISTRY_INIT
    elif profile == "orm_query":
        paths = VIBE_APP_ORM_QUERY_PATHS
        init = VIBE_APP_ORM_QUERY_INIT
    elif profile == "plugin_registry":
        paths = VIBE_APP_PLUGIN_REGISTRY_PATHS
        init = VIBE_APP_PLUGIN_REGISTRY_INIT
    else:
        raise SystemExit(f"unknown vibe_app profile: {profile}")

    copy_tree(task_dir / "repo", output, paths, package="vibe_app")
    write_init(output, init)


JINJA_PKG = "src/jinja2"

JINJA2_LEXER_PARSER_PATHS = [
    f"{JINJA_PKG}/exceptions.py",
    f"{JINJA_PKG}/utils.py",
    f"{JINJA_PKG}/_identifier.py",
    f"{JINJA_PKG}/constants.py",
    f"{JINJA_PKG}/lexer.py",
    f"{JINJA_PKG}/nodes.py",
    f"{JINJA_PKG}/parser.py",
]

JINJA2_COMPILE_RENDER_PATHS = JINJA2_LEXER_PARSER_PATHS + [
    f"{JINJA_PKG}/defaults.py",
    f"{JINJA_PKG}/async_utils.py",
    f"{JINJA_PKG}/visitor.py",
    f"{JINJA_PKG}/idtracking.py",
    f"{JINJA_PKG}/optimizer.py",
    f"{JINJA_PKG}/compiler.py",
    f"{JINJA_PKG}/runtime.py",
    f"{JINJA_PKG}/filters.py",
    f"{JINJA_PKG}/tests.py",
    f"{JINJA_PKG}/environment.py",
]

JINJA2_LOADER_PATHS = JINJA2_COMPILE_RENDER_PATHS + [f"{JINJA_PKG}/loaders.py"]

JINJA2_EXTENSIONS_PATHS = JINJA2_COMPILE_RENDER_PATHS + [f"{JINJA_PKG}/ext.py"]

JINJA2_ENVIRONMENT_LEXER = '''\
"""Minimal environment for lex/parse."""

from __future__ import annotations

import typing as t

from featurelifted import nodes
from featurelifted.exceptions import TemplateSyntaxError
from featurelifted.lexer import Lexer

BLOCK_START_STRING = "{%"
BLOCK_END_STRING = "%}"
VARIABLE_START_STRING = "{{"
VARIABLE_END_STRING = "}}"
COMMENT_START_STRING = "{#"
COMMENT_END_STRING = "#}"
LINE_STATEMENT_PREFIX: t.Optional[str] = None
LINE_COMMENT_PREFIX: t.Optional[str] = None
TRIM_BLOCKS = False
LSTRIP_BLOCKS = False
NEWLINE_SEQUENCE: "te.Literal['\\\\n', '\\\\r\\\\n', '\\\\r']" = "\\n"
KEEP_TRAILING_NEWLINE = False

if t.TYPE_CHECKING:
    import typing_extensions as te


class Environment:
    """Environment with lex/parse only."""

    def __init__(
        self,
        block_start_string: str = BLOCK_START_STRING,
        block_end_string: str = BLOCK_END_STRING,
        variable_start_string: str = VARIABLE_START_STRING,
        variable_end_string: str = VARIABLE_END_STRING,
        comment_start_string: str = COMMENT_START_STRING,
        comment_end_string: str = COMMENT_END_STRING,
        line_statement_prefix: t.Optional[str] = LINE_STATEMENT_PREFIX,
        line_comment_prefix: t.Optional[str] = LINE_COMMENT_PREFIX,
        trim_blocks: bool = TRIM_BLOCKS,
        lstrip_blocks: bool = LSTRIP_BLOCKS,
        newline_sequence: "te.Literal['\\\\n', '\\\\r\\\\n', '\\\\r']" = NEWLINE_SEQUENCE,
        keep_trailing_newline: bool = KEEP_TRAILING_NEWLINE,
    ) -> None:
        self.block_start_string = block_start_string
        self.block_end_string = block_end_string
        self.variable_start_string = variable_start_string
        self.variable_end_string = variable_end_string
        self.comment_start_string = comment_start_string
        self.comment_end_string = comment_end_string
        self.line_statement_prefix = line_statement_prefix
        self.line_comment_prefix = line_comment_prefix
        self.trim_blocks = trim_blocks
        self.lstrip_blocks = lstrip_blocks
        self.newline_sequence = newline_sequence
        self.keep_trailing_newline = keep_trailing_newline
        self.lexer = Lexer(self)

    def iter_extensions(self) -> t.Iterator[t.Any]:
        return iter(())

    def preprocess(
        self,
        source: str,
        name: t.Optional[str] = None,
        filename: t.Optional[str] = None,
    ) -> str:
        return str(source)

    def _tokenize(
        self,
        source: str,
        name: t.Optional[str],
        filename: t.Optional[str] = None,
        state: t.Optional[str] = None,
    ):
        source = self.preprocess(source, name, filename)
        return self.lexer.tokenize(source, name, filename, state)

    def handle_exception(self, source: t.Optional[str] = None) -> None:
        raise

    def lex(
        self,
        source: str,
        name: t.Optional[str] = None,
        filename: t.Optional[str] = None,
    ) -> t.Iterator[t.Tuple[int, str, str]]:
        source = str(source)
        try:
            return self.lexer.tokeniter(source, name, filename)
        except TemplateSyntaxError:
            self.handle_exception(source=source)
            raise

    def parse(
        self,
        source: str,
        name: t.Optional[str] = None,
        filename: t.Optional[str] = None,
    ) -> nodes.Template:
        from featurelifted.parser import Parser

        try:
            return Parser(self, source, name, filename).parse()
        except TemplateSyntaxError:
            self.handle_exception(source=source)
            raise
'''

JINJA2_LEXER_PARSER_INIT = '''\
"""Jinja2 lexer and parser core."""

from featurelifted import nodes
from featurelifted.environment import Environment

__all__ = ["Environment", "nodes"]
'''

JINJA2_COMPILE_RENDER_INIT = '''\
"""Jinja2 compile and render core."""

from featurelifted import nodes
from featurelifted.environment import Environment, Template

__all__ = ["Environment", "Template", "nodes"]
'''

JINJA2_LOADER_INIT = '''\
"""Jinja2 loader and inheritance core."""

from featurelifted.environment import Environment, Template
from featurelifted.loaders import BaseLoader, DictLoader

__all__ = ["Environment", "Template", "BaseLoader", "DictLoader"]
'''

JINJA2_FILTERS_TESTS_INIT = '''\
"""Jinja2 filters and tests core."""

from featurelifted.environment import Environment

__all__ = ["Environment"]
'''

JINJA2_EXTENSIONS_INIT = '''\
"""Jinja2 extension loading and registration."""

from featurelifted.environment import Environment
from featurelifted.ext import Extension

__all__ = ["Environment", "Extension"]
'''

PYTEST_MARK_EXPRESSION_INIT = '''\
"""pytest -m mark expression evaluator."""

from featurelifted.expression import Expression, ParseError

__all__ = ["Expression", "ParseError"]
'''

PYTEST_SKIPIF_MODULE = '''\
"""skipif condition evaluation subset."""

from __future__ import annotations

import os
import platform
import sys
import traceback
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any


class EvaluationError(Exception):
    """Raised when a skipif condition cannot be evaluated."""


@dataclass
class Mark:
    name: str
    kwargs: Mapping[str, Any] = field(default_factory=dict)


@dataclass
class EvalContext:
    config: Any = None
    obj_globals: Mapping[str, Any] | None = None
    markeval_namespace: Sequence[Mapping[str, Any]] = ()


def evaluate_condition(
    context: EvalContext, mark: Mark, condition: object
) -> tuple[bool, str]:
    if isinstance(condition, str):
        globals_: dict[str, Any] = {
            "os": os,
            "sys": sys,
            "platform": platform,
            "config": context.config,
        }
        for dictionary in reversed(context.markeval_namespace):
            if not isinstance(dictionary, Mapping):
                raise ValueError(
                    "markeval_namespace entries must be dicts, "
                    f"got {dictionary!r}"
                )
            globals_.update(dictionary)
        if context.obj_globals is not None:
            globals_.update(context.obj_globals)
        try:
            filename = f"<{mark.name} condition>"
            condition_code = compile(condition, filename, "eval")
            result = eval(condition_code, globals_)
        except SyntaxError as exc:
            msglines = [
                f"Error evaluating {mark.name!r} condition",
                "    " + condition,
                "    " + " " * (exc.offset or 0) + "^",
                "SyntaxError: invalid syntax",
            ]
            raise EvaluationError("\\n".join(msglines)) from exc
        except Exception as exc:
            msglines = [
                f"Error evaluating {mark.name!r} condition",
                "    " + condition,
                *traceback.format_exception_only(type(exc), exc),
            ]
            raise EvaluationError("".join(msglines)) from exc
    else:
        try:
            result = bool(condition)
        except Exception as exc:
            msglines = [
                f"Error evaluating {mark.name!r} condition as a boolean",
                *traceback.format_exception_only(type(exc), exc),
            ]
            raise EvaluationError("".join(msglines)) from exc

    reason = mark.kwargs.get("reason", None)
    if reason is None:
        if isinstance(condition, str):
            reason = "condition: " + condition
        else:
            msg = (
                f"Error evaluating {mark.name!r}: "
                "you need to specify reason=STRING when using booleans as conditions."
            )
            raise EvaluationError(msg)

    return result, reason
'''

PYTEST_SKIPIF_INIT = '''\
"""skipif condition evaluation."""

from featurelifted.skipif import EvalContext, EvaluationError, Mark, evaluate_condition

__all__ = ["EvalContext", "EvaluationError", "Mark", "evaluate_condition"]
'''

PYTEST_INI_MARKERS_MODULE = '''\
"""pytest ini markers linelist parsing subset."""

from __future__ import annotations

from dataclasses import dataclass, field


def parse_linelist(value: str | list[str]) -> list[str]:
    if isinstance(value, str):
        return [item for item in map(str.strip, value.split("\\n")) if item]
    return list(value)


def split_marker_line(line: str) -> tuple[str, str]:
    parts = line.split(":", 1)
    name = parts[0].strip()
    rest = parts[1] if len(parts) == 2 else ""
    return name, rest


@dataclass
class MarkerRegistry:
    lines: list[str] = field(default_factory=list)

    @classmethod
    def from_ini(cls, value: str | list[str]) -> "MarkerRegistry":
        return cls.from_lines(parse_linelist(value))

    @classmethod
    def from_lines(cls, lines: list[str]) -> "MarkerRegistry":
        return cls(lines=list(lines))

    def add_line(self, line: str) -> None:
        self.lines.append(line)

    def names(self) -> list[str]:
        return [split_marker_line(line)[0] for line in self.lines]

    def description(self, name: str) -> str:
        for line in self.lines:
            marker_name, desc = split_marker_line(line)
            if marker_name == name:
                return desc.strip()
        raise KeyError(name)
'''

PYTEST_INI_MARKERS_INIT = '''\
"""pytest ini markers parsing."""

from featurelifted.ini_markers import MarkerRegistry, parse_linelist, split_marker_line

__all__ = ["MarkerRegistry", "parse_linelist", "split_marker_line"]
'''

PYTEST_FIXTURE_RESOLVE_MODULE = '''\
"""Fixture name resolution subset from _pytest.fixtures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import AbstractSet, Callable, Iterable, TypeVar

FixtureFunction = TypeVar("FixtureFunction", bound=Callable[..., object])

_SCOPE_ORDER = {
    "function": 1,
    "class": 2,
    "module": 3,
    "package": 4,
    "session": 5,
}


@dataclass(frozen=True)
class FixtureDef:
    argname: str
    argnames: tuple[str, ...]
    baseid: str
    scope: str = "function"


@dataclass
class FixtureFunctionMarker:
    scope: str = "function"
    name: str | None = None

    def __call__(self, function: FixtureFunction) -> FixtureFunction:
        marker_name = self.name or function.__name__
        function._pytestfixturefunction = self  # type: ignore[attr-defined]
        function.__fixture_name__ = marker_name  # type: ignore[attr-defined]
        return function


class FixtureLookupError(LookupError):
    """Could not return a requested fixture (missing or invalid)."""

    def __init__(
        self,
        argname: str,
        *,
        available: Iterable[str] = (),
        msg: str | None = None,
    ) -> None:
        self.argname = argname
        self.available = tuple(sorted(set(available)))
        if msg is None:
            msg = f"fixture '{argname}' not found"
            if self.available:
                msg += "\\n available fixtures: " + ", ".join(self.available)
        super().__init__(msg)


class FixtureRegistry:
    """Registry of fixture definitions keyed by argname."""

    def __init__(self) -> None:
        self._arg2fixturedefs: dict[str, list[FixtureDef]] = {}

    def register(self, fixturedef: FixtureDef) -> None:
        self._arg2fixturedefs.setdefault(fixturedef.argname, []).append(fixturedef)

    def getfixturedefs(
        self, argname: str, parent_nodeids: AbstractSet[str]
    ) -> tuple[FixtureDef, ...] | None:
        try:
            fixturedefs = self._arg2fixturedefs[argname]
        except KeyError:
            return None
        matched = tuple(fd for fd in fixturedefs if fd.baseid in parent_nodeids)
        return matched if matched else tuple()


def deduplicate_names(*seqs: Iterable[str]) -> tuple[str, ...]:
    """De-duplicate fixture name sequences while preserving order."""
    return tuple(dict.fromkeys(name for seq in seqs for name in seq))


def getfixturemarker(obj: object) -> FixtureFunctionMarker | None:
    """Return the fixture marker attached to an object, if any."""
    return getattr(obj, "_pytestfixturefunction", None)


def fixture(
    fixture_function: FixtureFunction | None = None,
    *,
    scope: str = "function",
    name: str | None = None,
) -> FixtureFunctionMarker | FixtureFunction:
    marker = FixtureFunctionMarker(scope=scope, name=name)
    if fixture_function is not None:
        return marker(fixture_function)
    return marker


def resolve_fixture_closure(
    parent_nodeids: AbstractSet[str],
    initialnames: tuple[str, ...],
    registry: FixtureRegistry,
    ignore_args: AbstractSet[str] | None = None,
) -> tuple[list[str], dict[str, tuple[FixtureDef, ...]]]:
    """Compute transitive fixture closure and matching FixtureDefs."""
    ignored = ignore_args or frozenset()
    fixturenames_closure = list(initialnames)
    arg2fixturedefs: dict[str, tuple[FixtureDef, ...]] = {}
    lastlen = -1
    while lastlen != len(fixturenames_closure):
        lastlen = len(fixturenames_closure)
        for argname in fixturenames_closure:
            if argname in ignored:
                continue
            if argname in arg2fixturedefs:
                continue
            fixturedefs = registry.getfixturedefs(argname, parent_nodeids)
            if fixturedefs:
                arg2fixturedefs[argname] = fixturedefs
                for arg in fixturedefs[-1].argnames:
                    if arg not in fixturenames_closure:
                        fixturenames_closure.append(arg)

    def sort_by_scope(arg_name: str) -> int:
        try:
            fixturedefs = arg2fixturedefs[arg_name]
        except KeyError:
            return _SCOPE_ORDER["function"]
        return _SCOPE_ORDER.get(fixturedefs[-1].scope, 1)

    fixturenames_closure.sort(key=sort_by_scope, reverse=True)
    return fixturenames_closure, arg2fixturedefs
'''

PYTEST_FIXTURE_RESOLVE_INIT = '''\
"""pytest fixture name resolution."""

from featurelifted.fixture_resolve import (
    FixtureDef,
    FixtureFunctionMarker,
    FixtureLookupError,
    FixtureRegistry,
    deduplicate_names,
    fixture,
    getfixturemarker,
    resolve_fixture_closure,
)

__all__ = [
    "FixtureDef",
    "FixtureFunctionMarker",
    "FixtureLookupError",
    "FixtureRegistry",
    "deduplicate_names",
    "fixture",
    "getfixturemarker",
    "resolve_fixture_closure",
]
'''


def write_module(dst_root: Path, rel_path: str, content: str) -> None:
    path = dst_root / "featurelifted" / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def vendor_markupsafe(dst_root: Path) -> None:
    import tarfile

    tarball = VENDOR_WHEELS_DIR / "MarkupSafe-2.1.5.tar.gz"
    if not tarball.is_file():
        raise SystemExit(f"missing vendored MarkupSafe source: {tarball}")
    dst = dst_root / "featurelifted" / "vendor" / "markupsafe"
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True)
    with tarfile.open(tarball, "r:gz") as archive:
        for member in archive.getmembers():
            if not member.name.startswith("MarkupSafe-2.1.5/src/markupsafe/"):
                continue
            rel = member.name.split("src/markupsafe/", 1)[1]
            if not rel or rel.endswith("/"):
                continue
            target = dst / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            extracted = archive.extractfile(member)
            if extracted is not None:
                target.write_bytes(extracted.read())


JINJA2_VENDOR_BOOTSTRAP = '''\
import sys
from pathlib import Path

_vendor = Path(__file__).resolve().parent / "vendor"
if _vendor.is_dir() and str(_vendor) not in sys.path:
    sys.path.insert(0, str(_vendor))

'''


def build_jinja2(task_dir: Path, profile: str, output: Path) -> None:
    repo_pkg = task_dir / "repo" / "src" / "jinja2"
    if not repo_pkg.is_dir():
        raise SystemExit(f"missing repo snapshot: {repo_pkg}")

    if profile == "lexer_parser":
        paths = JINJA2_LEXER_PARSER_PATHS
        init = JINJA2_LEXER_PARSER_INIT
    elif profile == "compile_render":
        paths = JINJA2_COMPILE_RENDER_PATHS
        init = JINJA2_COMPILE_RENDER_INIT
    elif profile == "loader_inheritance":
        paths = JINJA2_LOADER_PATHS
        init = JINJA2_LOADER_INIT
    elif profile == "filters_tests":
        paths = JINJA2_COMPILE_RENDER_PATHS
        init = JINJA2_FILTERS_TESTS_INIT
    elif profile == "extensions":
        paths = JINJA2_EXTENSIONS_PATHS
        init = JINJA2_EXTENSIONS_INIT
    else:
        raise SystemExit(f"unknown jinja2 profile: {profile}")

    copy_tree(task_dir / "repo", output, paths, package=JINJA_PKG)
    if profile == "lexer_parser":
        write_module(output, "environment.py", JINJA2_ENVIRONMENT_LEXER)
    vendor_markupsafe(output)
    write_init(output, JINJA2_VENDOR_BOOTSTRAP + init)


def build_pytest(task_dir: Path, profile: str, output: Path) -> None:
    if profile == "mark_expression":
        src = task_dir / "repo" / "src" / "_pytest" / "mark" / "expression.py"
        if not src.is_file():
            raise SystemExit(f"missing expression module: {src}")
        if output.exists():
            shutil.rmtree(output)
        output.mkdir(parents=True, exist_ok=True)
        write_module(
            output,
            "expression.py",
            rewrite_source(src.read_text(encoding="utf-8")),
        )
        write_init(output, PYTEST_MARK_EXPRESSION_INIT)
    elif profile == "skipif_eval":
        if output.exists():
            shutil.rmtree(output)
        output.mkdir(parents=True, exist_ok=True)
        write_module(output, "skipif.py", PYTEST_SKIPIF_MODULE)
        write_init(output, PYTEST_SKIPIF_INIT)
    elif profile == "ini_markers":
        if output.exists():
            shutil.rmtree(output)
        output.mkdir(parents=True, exist_ok=True)
        write_module(output, "ini_markers.py", PYTEST_INI_MARKERS_MODULE)
        write_init(output, PYTEST_INI_MARKERS_INIT)
    elif profile == "fixture_resolve":
        if output.exists():
            shutil.rmtree(output)
        output.mkdir(parents=True, exist_ok=True)
        write_module(output, "fixture_resolve.py", PYTEST_FIXTURE_RESOLVE_MODULE)
        write_init(output, PYTEST_FIXTURE_RESOLVE_INIT)
    else:
        raise SystemExit(f"unknown pytest profile: {profile}")


PYGMENTS_LEXER_PATHS = [
    "pygments/lexer.py",
    "pygments/token.py",
    "pygments/util.py",
    "pygments/filter.py",
    "pygments/filters/__init__.py",
    "pygments/regexopt.py",
    "pygments/plugin.py",
    "pygments/modeline.py",
    "pygments/unistring.py",
    "pygments/lexers/__init__.py",
    "pygments/lexers/_mapping.py",
    "pygments/lexers/python.py",
]

PYGMENTS_FORMATTER_PATHS = PYGMENTS_LEXER_PATHS + [
    "pygments/formatter.py",
    "pygments/formatters/__init__.py",
    "pygments/formatters/_mapping.py",
    "pygments/formatters/html.py",
    "pygments/style.py",
    "pygments/styles/__init__.py",
]

PYGMENTS_LEXER_INIT = '''\
"""Pygments lexer core."""

from featurelifted.lexer import Lexer, RegexLexer
from featurelifted.lexers import PythonLexer, get_lexer_by_name
from featurelifted import token


def lex(code, lexer):
    try:
        return lexer.get_tokens(code)
    except TypeError:
        if isinstance(lexer, type) and issubclass(lexer, RegexLexer):
            raise TypeError(
                "lex() argument must be a lexer instance, not a class"
            )
        raise


__all__ = [
    "Lexer",
    "RegexLexer",
    "PythonLexer",
    "get_lexer_by_name",
    "lex",
    "token",
]
'''

PYGMENTS_FORMATTER_INIT = '''\
"""Pygments HTML highlight core."""

from io import StringIO

from featurelifted.formatter import Formatter
from featurelifted.formatters.html import HtmlFormatter
from featurelifted.lexers import PythonLexer, get_lexer_by_name


def highlight(code, lexer, formatter, outfile=None):
    try:
        tokens = lexer.get_tokens(code)
    except TypeError:
        from featurelifted.lexer import RegexLexer

        if isinstance(lexer, type) and issubclass(lexer, RegexLexer):
            raise TypeError(
                "highlight() argument must be a lexer instance, not a class"
            )
        raise
    if outfile is None:
        realout = StringIO()
        formatter.format(tokens, realout)
        return realout.getvalue()
    formatter.format(tokens, outfile)
    return None


__all__ = [
    "Formatter",
    "HtmlFormatter",
    "PythonLexer",
    "get_lexer_by_name",
    "highlight",
]
'''

LARK_CORE_PATHS = [
    "lark/exceptions.py",
    "lark/utils.py",
    "lark/common.py",
    "lark/grammar.py",
    "lark/lexer.py",
    "lark/load_grammar.py",
    "lark/parse_tree_builder.py",
    "lark/parser_frontends.py",
    "lark/lark.py",
    "lark/tree.py",
    "lark/visitors.py",
    "lark/parsers/",
    "lark/grammars/",
]

LARK_VISITOR_EXTRA_PATHS = [
    "lark/ast_utils.py",
    "lark/tree_matcher.py",
]

LARK_PARSE_INIT = '''\
"""Lark parse tree core."""

from featurelifted.exceptions import UnexpectedCharacters, UnexpectedToken
from featurelifted.lark import Lark
from featurelifted.lexer import Token
from featurelifted.tree import Tree

__all__ = [
    "Lark",
    "Tree",
    "Token",
    "UnexpectedToken",
    "UnexpectedCharacters",
]
'''

LARK_VISITOR_INIT = '''\
"""Lark visitor and transformer core."""

from featurelifted.exceptions import UnexpectedCharacters, UnexpectedToken
from featurelifted.lark import Lark
from featurelifted.lexer import Token
from featurelifted.tree import Tree
from featurelifted.visitors import Discard, Transformer, Visitor, v_args

__all__ = [
    "Lark",
    "Tree",
    "Token",
    "Transformer",
    "Visitor",
    "v_args",
    "Discard",
    "UnexpectedToken",
    "UnexpectedCharacters",
]
'''

ATTR_VALIDATORS_PATHS = [
    "attr/_make.py",
    "attr/_compat.py",
    "attr/_config.py",
    "attr/_funcs.py",
    "attr/_next_gen.py",
    "attr/_version_info.py",
    "attr/converters.py",
    "attr/exceptions.py",
    "attr/validators.py",
    "attr/setters.py",
]

ATTR_VALIDATORS_INIT = '''\
"""attrs validators core."""

from featurelifted._next_gen import define, field
from featurelifted import validators
from featurelifted._make import validate

__all__ = ["define", "field", "validators", "validate"]
'''


def build_pygments(task_dir: Path, profile: str, output: Path) -> None:
    repo_pkg = task_dir / "repo" / "pygments"
    if not repo_pkg.is_dir():
        raise SystemExit(f"missing repo snapshot: {repo_pkg}")

    if profile == "lexer_core":
        paths = PYGMENTS_LEXER_PATHS
        init = PYGMENTS_LEXER_INIT
    elif profile == "formatter_core":
        paths = PYGMENTS_FORMATTER_PATHS
        init = PYGMENTS_FORMATTER_INIT
    else:
        raise SystemExit(f"unknown pygments profile: {profile}")

    copy_tree(task_dir / "repo", output, paths, package="pygments")
    write_init(output, init)


def build_lark(task_dir: Path, profile: str, output: Path) -> None:
    repo_pkg = task_dir / "repo" / "lark"
    if not repo_pkg.is_dir():
        raise SystemExit(f"missing repo snapshot: {repo_pkg}")

    if profile == "parse_tree_core":
        paths = LARK_CORE_PATHS
        init = LARK_PARSE_INIT
    elif profile == "visitor_transform_core":
        paths = LARK_CORE_PATHS + LARK_VISITOR_EXTRA_PATHS
        init = LARK_VISITOR_INIT
    else:
        raise SystemExit(f"unknown lark profile: {profile}")

    copy_tree(task_dir / "repo", output, paths, package="lark")
    write_init(output, init)


def build_attrs(task_dir: Path, profile: str, output: Path) -> None:
    repo_pkg = task_dir / "repo" / "attr"
    if not repo_pkg.is_dir():
        raise SystemExit(f"missing repo snapshot: {repo_pkg}")

    if profile != "validators_core":
        raise SystemExit(f"unknown attrs profile: {profile}")

    copy_tree(task_dir / "repo", output, ATTR_VALIDATORS_PATHS, package="attr")
    write_init(output, ATTR_VALIDATORS_INIT)


WERKZEUG_ROUTING_EXCLUDE_DIRS = frozenset(
    {"middleware", "debug", "__pycache__", "cli"}
)
WERKZEUG_ROUTING_EXCLUDE_FILES = frozenset(
    {"serving.py", "test.py", "testapp.py", "_reloader.py"}
)

WERKZEUG_ROUTING_INIT = '''\
"""Werkzeug URL routing core."""

from featurelifted.routing import (
    Map,
    MapAdapter,
    Rule,
    Subdomain,
    Submount,
    BuildError,
    RequestRedirect,
)

__all__ = [
    "Map",
    "MapAdapter",
    "Rule",
    "Subdomain",
    "Submount",
    "BuildError",
    "RequestRedirect",
]
'''

TYPER_VENDOR_BOOTSTRAP = '''\
import sys
from pathlib import Path

_vendor = Path(__file__).resolve().parent / "vendor"
if _vendor.is_dir() and str(_vendor) not in sys.path:
    sys.path.insert(0, str(_vendor))

'''

TYPER_INIT = '''\
"""Typer command parser core."""

from featurelifted.main import Typer, launch, run
from featurelifted.params import Argument, Option
from featurelifted.testing import CliRunner

__all__ = ["Typer", "launch", "run", "Argument", "Option", "CliRunner"]
'''

IMPORTLIB_VENDOR_BOOTSTRAP = '''\
import sys
from pathlib import Path

_vendor = Path(__file__).resolve().parent / "vendor"
if _vendor.is_dir() and str(_vendor) not in sys.path:
    sys.path.insert(0, str(_vendor))

'''

IMPORTLIB_INIT = '''\
"""importlib_metadata entry points core."""

from featurelifted import (
    EntryPoint,
    EntryPoints,
    PathDistribution,
    Sectioned,
    distribution,
    entry_points,
)

__all__ = [
    "EntryPoint",
    "EntryPoints",
    "PathDistribution",
    "Sectioned",
    "distribution",
    "entry_points",
]
'''

H11_INIT = '''\
"""HTTP/1.1 message parse core."""

from featurelifted._connection import Connection, NEED_DATA, PAUSED
from featurelifted._events import (
    ConnectionClosed,
    Data,
    EndOfMessage,
    Event,
    InformationalResponse,
    Request,
    Response,
)
from featurelifted._state import (
    CLIENT,
    CLOSED,
    DONE,
    ERROR,
    IDLE,
    MIGHT_SWITCH_PROTOCOL,
    MUST_CLOSE,
    SEND_BODY,
    SEND_RESPONSE,
    SERVER,
    SWITCHED_PROTOCOL,
)
from featurelifted._util import LocalProtocolError, ProtocolError, RemoteProtocolError

__all__ = [
    "Connection",
    "NEED_DATA",
    "PAUSED",
    "ConnectionClosed",
    "Data",
    "EndOfMessage",
    "Event",
    "InformationalResponse",
    "Request",
    "Response",
    "CLIENT",
    "CLOSED",
    "DONE",
    "ERROR",
    "IDLE",
    "MUST_CLOSE",
    "SEND_BODY",
    "SEND_RESPONSE",
    "SERVER",
    "SWITCHED_PROTOCOL",
    "ProtocolError",
    "LocalProtocolError",
    "RemoteProtocolError",
]
'''

REDIS_UTILS_MINIMAL = '''\
"""Minimal redis utils for RESP parser."""

from typing import Any

SENTINEL: Any = object()

try:
    import ssl  # noqa: F401

    SSL_AVAILABLE = True
except ImportError:
    SSL_AVAILABLE = False
'''

REDIS_PARSER_BASE = '''\
"""Trimmed RESP parser base without network client coupling."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Protocol, Union

from featurelifted.exceptions import (
    AskError,
    AuthenticationError,
    AuthenticationWrongNumberOfArgsError,
    BusyLoadingError,
    ClusterCrossSlotError,
    ClusterDownError,
    ConnectionError,
    ExecAbortError,
    ExternalAuthProviderError,
    MasterDownError,
    ModuleError,
    MovedError,
    NoPermissionError,
    NoScriptError,
    OutOfMemoryError,
    ReadOnlyError,
    ResponseError,
    TryAgainError,
)
from featurelifted.typing import EncodableT
from featurelifted._parsers.encoders import Encoder
from featurelifted._parsers.socket import SERVER_CLOSED_CONNECTION_ERROR, SocketBuffer
from featurelifted.utils import SENTINEL

MODULE_LOAD_ERROR = "Error loading the extension. Please check the server logs."
NO_SUCH_MODULE_ERROR = "Error unloading module: no such module with that name"
MODULE_UNLOAD_NOT_POSSIBLE_ERROR = "Error unloading module: operation not possible."
MODULE_EXPORTS_DATA_TYPES_ERROR = (
    "Error unloading module: the module "
    "exports one or more module-side data "
    "types, can't unload"
)
NO_AUTH_SET_ERROR = {
    "AUTH <password> called without any password "
    "configured for the default user. Are you sure "
    "your configuration is correct?": AuthenticationError,
    "Client sent AUTH, but no password is set": AuthenticationError,
}
EXTERNAL_AUTH_PROVIDER_ERROR = {
    "problem with LDAP service": ExternalAuthProviderError,
}


class BaseParser(ABC):
    EXCEPTION_CLASSES = {
        "ERR": {
            "max number of clients reached": ConnectionError,
            "invalid password": AuthenticationError,
            "wrong number of arguments "
            "for 'auth' command": AuthenticationWrongNumberOfArgsError,
            "wrong number of arguments "
            "for 'AUTH' command": AuthenticationWrongNumberOfArgsError,
            MODULE_LOAD_ERROR: ModuleError,
            MODULE_EXPORTS_DATA_TYPES_ERROR: ModuleError,
            NO_SUCH_MODULE_ERROR: ModuleError,
            MODULE_UNLOAD_NOT_POSSIBLE_ERROR: ModuleError,
            **NO_AUTH_SET_ERROR,
            **EXTERNAL_AUTH_PROVIDER_ERROR,
        },
        "OOM": OutOfMemoryError,
        "WRONGPASS": AuthenticationError,
        "EXECABORT": ExecAbortError,
        "LOADING": BusyLoadingError,
        "NOSCRIPT": NoScriptError,
        "READONLY": ReadOnlyError,
        "NOAUTH": AuthenticationError,
        "NOPERM": NoPermissionError,
        "ASK": AskError,
        "TRYAGAIN": TryAgainError,
        "MOVED": MovedError,
        "CLUSTERDOWN": ClusterDownError,
        "CROSSSLOT": ClusterCrossSlotError,
        "MASTERDOWN": MasterDownError,
    }

    @classmethod
    def parse_error(cls, response):
        error_code = response.split(" ")[0]
        if error_code in cls.EXCEPTION_CLASSES:
            response = response[len(error_code) + 1 :]
            exception_class = cls.EXCEPTION_CLASSES[error_code]
            if isinstance(exception_class, dict):
                exception_class = exception_class.get(response, ResponseError)
            return exception_class(response, status_code=error_code)
        return ResponseError(response)

    @abstractmethod
    def on_disconnect(self):
        pass

    @abstractmethod
    def on_connect(self, connection):
        pass


class PushNotificationsParser(Protocol):
    pubsub_push_handler_func: object


class _RESPBase(BaseParser):
    def __init__(self, socket_read_size):
        self.socket_read_size = socket_read_size
        self.encoder = None
        self._sock = None
        self._buffer = None

    def __del__(self):
        try:
            self.on_disconnect()
        except Exception:
            pass

    def on_connect(self, connection):
        self._sock = connection._sock
        self._buffer = SocketBuffer(
            self._sock, self.socket_read_size, connection.socket_timeout
        )
        self.encoder = connection.encoder

    def on_disconnect(self):
        self._sock = None
        if self._buffer is not None:
            self._buffer.close()
            self._buffer = None
        self.encoder = None

    def can_read(self, timeout: float = 0) -> bool:
        if self._buffer is None:
            return False
        return self._buffer.can_read(timeout)
'''

REDIS_PARSER_INIT = '''\
"""Redis RESP parser core."""

from featurelifted._parsers import Encoder, _RESP2Parser, _RESP3Parser

__all__ = ["Encoder", "_RESP2Parser", "_RESP3Parser"]
'''


def _discover_werkzeug_routing_paths(repo_root: Path) -> list[str]:
    pkg_root = repo_root / "werkzeug"
    rel_files: list[str] = []
    for path in sorted(pkg_root.rglob("*")):
        if not path.is_file() or path.suffix != ".py":
            continue
        if any(part in WERKZEUG_ROUTING_EXCLUDE_DIRS for part in path.parts):
            continue
        if path.name in WERKZEUG_ROUTING_EXCLUDE_FILES:
            continue
        rel_files.append(path.relative_to(repo_root).as_posix())
    return rel_files


def _discover_package_paths(repo_root: Path, package: str) -> list[str]:
    pkg_root = _find_package_root(repo_root, package)
    rel_files: list[str] = []
    for path in sorted(pkg_root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix not in {".py", ".typed", ".pyi"}:
            continue
        if any(part in EXCLUDED_PATH_PARTS for part in path.parts):
            continue
        rel_files.append(path.relative_to(repo_root).as_posix())
    return rel_files


def prepend_after_future(init_path: Path, prefix: str) -> None:
    text = init_path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    insert_at = 0
    while insert_at < len(lines) and lines[insert_at].startswith("from __future__"):
        insert_at += 1
    lines.insert(insert_at, prefix)
    init_path.write_text("".join(lines), encoding="utf-8")


def rewrite_click_bundled(text: str, *, replace_usage: bool = False) -> str:
    """Rewrite click imports to the bundled internal package."""
    text = re.sub(
        r"^(\s*)import click\.(.+)$",
        r"\1from featurelifted._bundled_click import \2",
        text,
        flags=re.MULTILINE,
    )
    text = re.sub(
        r"^(\s*)import click\s*$",
        r"\1from featurelifted import _bundled_click as _clk",
        text,
        flags=re.MULTILINE,
    )
    text = re.sub(
        r"^(\s*)from click(\.|\b)",
        r"\1from featurelifted._bundled_click\2",
        text,
        flags=re.MULTILINE,
    )
    if replace_usage:
        text = re.sub(r"(?<![.\w])click\.", "_clk.", text)
    return text


def vendor_click(dst_root: Path, task_dir: Path) -> None:
    src = task_dir / "repo" / "click"
    if not src.is_dir():
        raise SystemExit(f"missing click snapshot for typer task: {src}")
    dst = dst_root / "featurelifted" / "_bundled_click"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    for path in dst.rglob("*.py"):
        path.write_text(
            rewrite_click_bundled(path.read_text(encoding="utf-8")),
            encoding="utf-8",
        )


def _rewrite_typer_tree(output: Path) -> None:
    pkg_root = output / "featurelifted"
    for path in pkg_root.rglob("*.py"):
        if "_bundled_click" in path.parts or path.name == "__init__.py":
            continue
        text = path.read_text(encoding="utf-8")
        path.write_text(
            rewrite_click_bundled(text, replace_usage=True),
            encoding="utf-8",
        )
    init_path = pkg_root / "__init__.py"
    if init_path.is_file():
        prepend_after_future(
            init_path,
            "from featurelifted import _bundled_click as _clk\n",
        )
        text = init_path.read_text(encoding="utf-8")
        init_path.write_text(rewrite_click_bundled(text, replace_usage=True), encoding="utf-8")



def vendor_zipp(dst_root: Path, task_dir: Path) -> None:
    src = task_dir / "repo" / "zipp"
    if not src.is_dir():
        raise SystemExit(f"missing zipp snapshot for importlib_metadata task: {src}")
    dst = dst_root / "featurelifted" / "vendor" / "zipp"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


def build_werkzeug(task_dir: Path, output: Path) -> None:
    repo_pkg = task_dir / "repo" / "werkzeug"
    if not repo_pkg.is_dir():
        raise SystemExit(f"missing repo snapshot: {repo_pkg}")
    paths = _discover_werkzeug_routing_paths(task_dir / "repo")
    copy_tree(task_dir / "repo", output, paths, package="werkzeug")
    write_init(output, WERKZEUG_ROUTING_INIT)


def build_typer(task_dir: Path, output: Path) -> None:
    repo_pkg = task_dir / "repo" / "typer"
    if not repo_pkg.is_dir():
        raise SystemExit(f"missing repo snapshot: {repo_pkg}")
    paths = _discover_package_paths(task_dir / "repo", "typer")
    copy_tree(task_dir / "repo", output, paths, package="typer")
    vendor_click(output, task_dir)
    _rewrite_typer_tree(output)


def build_importlib_metadata(task_dir: Path, output: Path) -> None:
    repo_pkg = task_dir / "repo" / "importlib_metadata"
    if not repo_pkg.is_dir():
        raise SystemExit(f"missing repo snapshot: {repo_pkg}")
    paths = _discover_package_paths(task_dir / "repo", "importlib_metadata")
    copy_tree(task_dir / "repo", output, paths, package="importlib_metadata")
    vendor_zipp(output, task_dir)
    init_path = output / "featurelifted" / "__init__.py"
    prepend_after_future(init_path, IMPORTLIB_VENDOR_BOOTSTRAP)


def _trim_httpx_models(text: str) -> str:
    """Keep Headers, Request, and Cookies; drop Response and decoder-only imports."""
    response_idx = text.index("class Response:")
    cookies_idx = text.index("class Cookies")
    header = text[:response_idx]
    cookies = text[cookies_idx:]
    lines = []
    skip_decoder = False
    for line in header.splitlines(keepends=True):
        if line.startswith("from ._decoders import"):
            skip_decoder = True
            continue
        if skip_decoder:
            if line.strip() == ")":
                skip_decoder = False
            continue
        if line.startswith("from ._status_codes import"):
            continue
        lines.append(line)
    header = "".join(lines)
    header = header.replace(
        "from ._content import ByteStream, UnattachedStream, encode_request, encode_response",
        "from ._content import ByteStream, UnattachedStream, encode_request",
    )
    header = header.replace(
        "    HTTPStatusError,\n",
        "",
    )
    header = header.replace(
        "    ResponseNotRead,\n",
        "",
    )
    header = header.replace(
        "    request_context,\n",
        "",
    )
    # Remove extract_cookies method block from Cookies - it references Response
    cookies_lines = []
    skip_method = False
    for line in cookies.splitlines(keepends=True):
        if line.startswith("    def extract_cookies"):
            skip_method = True
            continue
        if skip_method:
            if line.startswith("    def ") and not line.startswith("    def extract_cookies"):
                skip_method = False
            else:
                continue
        cookies_lines.append(line)
    return header + "".join(cookies_lines)


def _trim_httpx_content(text: str) -> str:
    content_idx = text.find("\ndef encode_response")
    if content_idx != -1:
        text = text[:content_idx] + "\n"
    return text


HTT_CLIENT_MERGE = '''\
from __future__ import annotations

import typing

from ._models import Cookies, Headers, Request
from ._types import CookieTypes, HeaderTypes, QueryParamTypes, URLTypes
from ._urls import QueryParams, URL


def _merge_url(base_url: URLTypes | str, url: URLTypes) -> URL:
    base = URL(base_url) if base_url else URL("")
    merge_url = URL(url)
    if not base or str(base) in ("", "/"):
        return merge_url
    if merge_url.is_relative_url:
        merge_raw_path = base.raw_path + merge_url.raw_path.lstrip(b"/")
        return base.copy_with(raw_path=merge_raw_path)
    return merge_url


def _merge_cookies(
    default_cookies: CookieTypes | None,
    cookies: CookieTypes | None,
) -> CookieTypes | None:
    if cookies or default_cookies:
        merged = Cookies(default_cookies)
        merged.update(cookies)
        return merged
    return cookies


def _merge_headers(
    default_headers: HeaderTypes | None,
    headers: HeaderTypes | None,
) -> HeaderTypes | None:
    merged = Headers(default_headers)
    merged.update(headers)
    return merged


def _merge_queryparams(
    default_params: QueryParamTypes | None,
    params: QueryParamTypes | None,
) -> QueryParamTypes | None:
    if params or default_params:
        merged = QueryParams(default_params)
        return merged.merge(params)
    return params


def build_request(
    method: str,
    url: URLTypes,
    *,
    base_url: str | URL = "",
    params: QueryParamTypes | None = None,
    headers: HeaderTypes | None = None,
    cookies: CookieTypes | None = None,
    default_params: QueryParamTypes | None = None,
    default_headers: HeaderTypes | None = None,
    default_cookies: CookieTypes | None = None,
    content: typing.Any = None,
    data: typing.Any = None,
    json: typing.Any = None,
    files: typing.Any = None,
) -> Request:
    url = _merge_url(base_url, url)
    headers = _merge_headers(default_headers, headers)
    cookies = _merge_cookies(default_cookies, cookies)
    params = _merge_queryparams(default_params, params)
    return Request(
        method,
        url,
        content=content,
        data=data,
        files=files,
        json=json,
        params=params,
        headers=headers,
        cookies=cookies,
    )
'''


HTT_INIT = '''\
"""HTTP request model and offline request builder."""

from featurelifted._client_merge import build_request
from featurelifted._exceptions import CookieConflict, InvalidURL, RequestNotRead
from featurelifted._models import Cookies, Headers, Request
from featurelifted._urls import QueryParams, URL

__all__ = [
    "URL",
    "QueryParams",
    "Headers",
    "Cookies",
    "Request",
    "build_request",
    "InvalidURL",
    "CookieConflict",
    "RequestNotRead",
]
'''


def _trim_httpx_utils(text: str) -> str:
    """Drop unused Timer/sniffio async helpers from the request-model closure."""
    timer_idx = text.find("\nclass Timer:")
    if timer_idx != -1:
        text = text[:timer_idx] + "\n"
    return text.replace("import sniffio\n\n", "")


def _patch_pydantic_validators(text: str) -> str:
    """Drop dataclasses bridge from validator discovery."""
    text = text.replace(
        "    from featurelifted.dataclasses import is_builtin_dataclass, make_dataclass_validator\n\n",
        "",
    )
    text = text.replace(
        "    if is_builtin_dataclass(type_):\n"
        "        yield from make_dataclass_validator(type_, config)\n"
        "        return\n",
        "",
    )
    return text


def _patch_pydantic_fields(text: str) -> str:
    """Avoid schema.py import during ModelField.infer."""
    text = text.replace(
        "        from featurelifted.schema import get_annotation_from_field_info\n\n",
        "",
    )
    text = text.replace(
        "        annotation = get_annotation_from_field_info(annotation, field_info, name, config.validate_assignment)\n\n",
        "\n",
    )
    return text


def _patch_pydantic_json(text: str) -> str:
    """Drop color/network encoders not needed for validation-core tests."""
    text = text.replace("from featurelifted.color import Color\n", "")
    text = text.replace("from featurelifted.networks import NameEmail\n", "")
    text = text.replace("    Color: str,\n", "")
    text = text.replace("    NameEmail: str,\n", "")
    return text


def _patch_pydantic_main(text: str) -> str:
    """Remove JSON Schema dependency from the validation-core closure."""
    text = text.replace("from featurelifted.schema import default_ref_template, model_schema\n", "")
    stub = '''    @classmethod
    def schema(cls, by_alias: bool = True, ref_template: str = 'default') -> 'DictStrAny':
        raise NotImplementedError('JSON Schema generation is excluded from this task')

    @classmethod
    def schema_json(cls, *, by_alias: bool = True, ref_template: str = 'default', **dumps_kwargs: Any) -> str:
        raise NotImplementedError('JSON Schema generation is excluded from this task')

'''
    text = re.sub(
        r"    @classmethod\n    def schema\(cls, by_alias: bool = True, ref_template: str = default_ref_template\).*?"
        r"    @classmethod\n    def __get_validators__",
        stub + "    @classmethod\n    def __get_validators__",
        text,
        count=1,
        flags=re.DOTALL,
    )
    return text


PYDANTIC_CORE_FILES = [
    "pydantic/version.py",
    "pydantic/errors.py",
    "pydantic/utils.py",
    "pydantic/typing.py",
    "pydantic/json.py",
    "pydantic/datetime_parse.py",
    "pydantic/config.py",
    "pydantic/error_wrappers.py",
    "pydantic/validators.py",
    "pydantic/types.py",
    "pydantic/class_validators.py",
    "pydantic/fields.py",
    "pydantic/annotated_types.py",
    "pydantic/parse.py",
    "pydantic/main.py",
]


PYDANTIC_INIT = '''\
"""Pydantic v1 validation core extracted for FeatureLiftBench."""

from featurelifted.class_validators import root_validator, validator
from featurelifted.config import Extra
from featurelifted.error_wrappers import ValidationError
from featurelifted.fields import Field
from featurelifted.main import BaseModel, create_model

__all__ = [
    "BaseModel",
    "create_model",
    "Field",
    "ValidationError",
    "validator",
    "root_validator",
    "Extra",
]
'''


def build_pydantic(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, PYDANTIC_CORE_FILES, package="pydantic")
    main_path = output / "featurelifted" / "main.py"
    main_path.write_text(
        _patch_pydantic_main(main_path.read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    json_path = output / "featurelifted" / "json.py"
    json_path.write_text(
        _patch_pydantic_json(json_path.read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    fields_path = output / "featurelifted" / "fields.py"
    fields_path.write_text(
        _patch_pydantic_fields(fields_path.read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    validators_path = output / "featurelifted" / "validators.py"
    validators_path.write_text(
        _patch_pydantic_validators(validators_path.read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    write_init(output, PYDANTIC_INIT)


def build_pydantic_copy_all(task_dir: Path, output: Path) -> None:
    """Copy the full Pydantic v1 package for copy-all baseline calibration."""
    repo_root = task_dir / "repo"
    rel_files = _discover_package_files(repo_root, "pydantic")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, rel_files, package="pydantic")
    write_init(output, PYDANTIC_INIT)


DATEUTIL_CORE_FILES = [
    "dateutil/_common.py",
    "dateutil/easter.py",
    "dateutil/rrule.py",
]


DATEUTIL_INIT = '''\
"""iCalendar recurrence core extracted for FeatureLiftBench."""

from featurelifted.rrule import (
    DAILY,
    FR,
    HOURLY,
    MINUTELY,
    MO,
    MONTHLY,
    SA,
    SECONDLY,
    SU,
    TH,
    TU,
    WE,
    WEEKLY,
    YEARLY,
    rrule,
    rruleset,
    rrulestr,
)

__all__ = [
    "rrule",
    "rruleset",
    "rrulestr",
    "YEARLY",
    "MONTHLY",
    "WEEKLY",
    "DAILY",
    "HOURLY",
    "MINUTELY",
    "SECONDLY",
    "MO",
    "TU",
    "WE",
    "TH",
    "FR",
    "SA",
    "SU",
]
'''


def _patch_dateutil_rrule(text: str) -> str:
    text = re.sub(r"from six import advance_iterator, integer_types\n", "", text)
    text = re.sub(r"from six\.moves import _thread, range\n", "", text)
    shim = (
        "import threading\n\n"
        "integer_types = int\n\n\n"
        "def advance_iterator(iterator):\n"
        "    return next(iterator)\n\n\n"
        "class _MinimalParser:\n"
        "    @staticmethod\n"
        "    def parse(value, ignoretz=True, tzinfos=None):\n"
        "        value = value.strip()\n"
        "        if not value:\n"
        "            raise ValueError('empty date')\n"
        "        if value.endswith('Z'):\n"
        "            value = value[:-1]\n"
        "        if 'T' in value:\n"
        "            return datetime.datetime.strptime(value[:15], '%Y%m%dT%H%M%S')\n"
        "        if len(value) >= 8 and value[:8].isdigit():\n"
        "            return datetime.datetime.strptime(value[:8], '%Y%m%d')\n"
        "        raise ValueError(f'unsupported date format: {value!r}')\n\n\n"
        "parser = _MinimalParser()\n"
        "from featurelifted import easter\n\n"
    )
    text = text.replace("import datetime\n", "import datetime\n" + shim, 1)
    text = text.replace("_thread.allocate_lock()", "threading.Lock()")
    lazy_parser_block = (
        "        global parser\n"
        "        if not parser:\n"
        "            from featurelifted import parser\n"
    )
    text = text.replace(lazy_parser_block, "")
    text = text.replace(
        "                if not parser and (rdatevals or exdatevals):\n"
        "                    from featurelifted import parser\n",
        "",
    )
    text = text.replace(
        "            if not easter:\n"
        "                from featurelifted import easter\n",
        "",
    )
    text = re.sub(r"^        global parser\n", "", text, flags=re.MULTILINE)
    text = re.sub(r"^        global easter\n", "", text, flags=re.MULTILINE)
    text = text.replace(
        "                if tzids is None:\n"
        "                    from . import tz\n"
        "                    tzlookup = tz.gettz\n",
        "                if tzids is None:\n"
        "                    raise ValueError('TZID not supported in this closure')\n",
    )
    text = re.sub(r"^easter = None\nparser = None\n\n", "", text, flags=re.MULTILINE)
    return text


def build_dateutil(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, DATEUTIL_CORE_FILES, package="dateutil")
    rrule_path = output / "featurelifted" / "rrule.py"
    rrule_path.write_text(
        _patch_dateutil_rrule(rrule_path.read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    write_init(output, DATEUTIL_INIT)


DATEUTIL_RELATIVEDELTA_CORE_FILES = [
    "dateutil/_common.py",
    "dateutil/relativedelta.py",
]


DATEUTIL_RELATIVEDELTA_INIT = '''\
"""Relative date arithmetic core extracted for FeatureLiftBench."""

from featurelifted.relativedelta import (
    FR,
    MO,
    relativedelta,
    SA,
    SU,
    TH,
    TU,
    WE,
)

__all__ = [
    "relativedelta",
    "MO",
    "TU",
    "WE",
    "TH",
    "FR",
    "SA",
    "SU",
]
'''


def _patch_dateutil_relativedelta(text: str) -> str:
    text = re.sub(r"from six import integer_types\n", "integer_types = int\n", text)
    return text


def build_dateutil_relativedelta(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, DATEUTIL_RELATIVEDELTA_CORE_FILES, package="dateutil")
    rd_path = output / "featurelifted" / "relativedelta.py"
    rd_path.write_text(
        _patch_dateutil_relativedelta(rd_path.read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    write_init(output, DATEUTIL_RELATIVEDELTA_INIT)


def build_dateutil_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files = _discover_package_files(repo_root, "dateutil")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, rel_files, package="dateutil")
    write_init(output, DATEUTIL_INIT)


def build_dateutil_relativedelta_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files = _discover_package_files(repo_root, "dateutil")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, rel_files, package="dateutil")
    write_init(output, DATEUTIL_RELATIVEDELTA_INIT)


PENDULUM_PARSE_FORMAT_PATHS = [
    "pendulum/constants.py",
    "pendulum/day.py",
    "pendulum/exceptions.py",
    "pendulum/utils/__init__.py",
    "pendulum/utils/_compat.py",
    "pendulum/_helpers.py",
    "pendulum/helpers.py",
    "pendulum/duration.py",
    "pendulum/date.py",
    "pendulum/time.py",
    "pendulum/datetime.py",
    "pendulum/interval.py",
    "pendulum/mixins/__init__.py",
    "pendulum/mixins/default.py",
    "pendulum/formatting/__init__.py",
    "pendulum/formatting/formatter.py",
    "pendulum/parsing/__init__.py",
    "pendulum/parsing/iso8601.py",
    "pendulum/parsing/exceptions/__init__.py",
    "pendulum/parser.py",
    "pendulum/tz/__init__.py",
    "pendulum/tz/exceptions.py",
    "pendulum/tz/timezone.py",
    "pendulum/locales/__init__.py",
    "pendulum/locales/locale.py",
    "pendulum/locales/en/__init__.py",
    "pendulum/locales/en/custom.py",
    "pendulum/locales/en/locale.py",
]

PENDULUM_TZ_INIT = '''\
"""Minimal timezone helpers for parse/format slice (UTC and fixed offsets only)."""

from __future__ import annotations

from functools import cache

from featurelifted.tz.timezone import UTC
from featurelifted.tz.timezone import FixedTimezone
from featurelifted.tz.timezone import Timezone

_tz_cache: dict[int, FixedTimezone] = {}


@cache
def fixed_timezone(offset: int) -> FixedTimezone:
    if offset in _tz_cache:
        return _tz_cache[offset]
    tz = FixedTimezone(offset)
    _tz_cache[offset] = tz
    return tz


def local_timezone() -> Timezone | FixedTimezone:
    return UTC


__all__ = ["UTC", "FixedTimezone", "Timezone", "fixed_timezone", "local_timezone"]
'''

PENDULUM_PARSE_FORMAT_INIT = '''\
"""Pendulum parse/format/duration core for FeatureLiftBench."""

from __future__ import annotations

import datetime as _datetime

from featurelifted.date import Date
from featurelifted.datetime import DateTime
from featurelifted.duration import Duration
from featurelifted.parsing.exceptions import ParserError
from featurelifted.parser import parse
from featurelifted.time import Time
from featurelifted.tz import UTC
from featurelifted.tz import fixed_timezone
from featurelifted.tz.timezone import FixedTimezone
from featurelifted.tz.timezone import Timezone

__all__ = [
    "UTC",
    "Date",
    "DateTime",
    "Duration",
    "ParserError",
    "Time",
    "datetime",
    "duration",
    "fixed_timezone",
    "parse",
]


_LOCALE = "en"


def get_locale() -> str:
    return _LOCALE


def set_locale(locale: str) -> None:
    global _LOCALE
    _LOCALE = locale


def _safe_timezone(
    obj: str | float | _datetime.tzinfo | Timezone | FixedTimezone | None,
    dt: _datetime.datetime | None = None,
) -> Timezone | FixedTimezone:
    if isinstance(obj, (Timezone, FixedTimezone)):
        return obj
    if obj is None:
        return UTC
    if isinstance(obj, (int, float)):
        return fixed_timezone(int(obj * 60 * 60))
    if isinstance(obj, _datetime.tzinfo):
        if obj.tzname(None) == "UTC":
            return UTC
        offset = obj.utcoffset(dt)
        if offset is None:
            offset = _datetime.timedelta(0)
        return fixed_timezone(int(offset.total_seconds()))
    obj = str(obj)
    if obj.lower() == "utc":
        return UTC
    if obj.replace(".", "", 1).isdigit():
        return fixed_timezone(int(float(obj) * 60 * 60))
    raise ValueError(f"Named timezone {obj!r} not supported in this slice")


def datetime(
    year: int,
    month: int,
    day: int,
    hour: int = 0,
    minute: int = 0,
    second: int = 0,
    microsecond: int = 0,
    tz: str | float | Timezone | FixedTimezone | _datetime.tzinfo | None = UTC,
    fold: int = 1,
    raise_on_unknown_times: bool = False,
) -> DateTime:
    return DateTime.create(
        year,
        month,
        day,
        hour=hour,
        minute=minute,
        second=second,
        microsecond=microsecond,
        tz=tz,
        fold=fold,
        raise_on_unknown_times=raise_on_unknown_times,
    )


def duration(
    days: float = 0,
    seconds: float = 0,
    microseconds: float = 0,
    milliseconds: float = 0,
    minutes: float = 0,
    hours: float = 0,
    weeks: float = 0,
    years: float = 0,
    months: float = 0,
) -> Duration:
    return Duration(
        days=days,
        seconds=seconds,
        microseconds=microseconds,
        milliseconds=milliseconds,
        minutes=minutes,
        hours=hours,
        weeks=weeks,
        years=years,
        months=months,
    )
'''


def _apply_pendulum_submission_patches(output: Path) -> None:
    featurelifted = output / "featurelifted"
    for path in featurelifted.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        text = text.replace("pendulum.", "featurelifted.")
        text = text.replace('"pendulum.locales.', '"featurelifted.locales.')
        text = text.replace("'pendulum.locales.", "'featurelifted.locales.")
        path.write_text(text, encoding="utf-8")
    tz_init = featurelifted / "tz" / "__init__.py"
    tz_init.write_text(PENDULUM_TZ_INIT, encoding="utf-8")
    parsing_init = featurelifted / "parsing" / "__init__.py"
    text = parsing_init.read_text(encoding="utf-8")
    text = text.replace(
        'with_extensions = os.getenv("PENDULUM_EXTENSIONS", "1") == "1"',
        "with_extensions = False",
    )
    parsing_init.write_text(text, encoding="utf-8")
    parser_path = featurelifted / "parser.py"
    parser_text = parser_path.read_text(encoding="utf-8")
    parser_text = parser_text.replace(
        'with_extensions = os.getenv("PENDULUM_EXTENSIONS", "1") == "1"',
        "with_extensions = False",
    )
    parser_path.write_text(parser_text, encoding="utf-8")


def build_pendulum(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, PENDULUM_PARSE_FORMAT_PATHS, package="pendulum")
    _apply_pendulum_submission_patches(output)
    write_init(output, PENDULUM_PARSE_FORMAT_INIT)


def build_pendulum_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files = _discover_package_files(repo_root, "pendulum")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, rel_files, package="pendulum")
    _apply_pendulum_submission_patches(output)
    write_init(output, PENDULUM_PARSE_FORMAT_INIT)


JSONPATH_CORE_FILES = [
    "jsonpath_ng/jsonpath.py",
    "jsonpath_ng/parser.py",
    "jsonpath_ng/lexer.py",
    "jsonpath_ng/exceptions.py",
    "jsonpath_ng/ext/__init__.py",
    "jsonpath_ng/ext/parser.py",
    "jsonpath_ng/ext/filter.py",
    "jsonpath_ng/ext/arithmetic.py",
    "jsonpath_ng/ext/iterable.py",
    "jsonpath_ng/ext/string.py",
]


JSONPATH_INIT = '''\
"""JSONPath expression core extracted for FeatureLiftBench."""

from featurelifted.ext.parser import parse
from featurelifted.jsonpath import JSONPath, DatumInContext

__all__ = ["parse", "JSONPath", "DatumInContext"]
'''


def _patch_jsonpath_ply(text: str) -> str:
    for mod in ("jsonpath_ng", "featurelifted"):
        text = text.replace(f"import {mod}._ply.lex", "import ply.lex as _ply_lex")
        text = text.replace(f"{mod}._ply.lex.lex", "_ply_lex.lex")
        text = text.replace(f"import {mod}._ply.yacc", "import ply.yacc as _ply_yacc")
        text = text.replace(f"{mod}._ply.yacc.yacc", "_ply_yacc.yacc")
    return text


def _patch_jsonpath_parent_imports(text: str) -> str:
    import re

    text = text.replace("from .. import lexer", "import featurelifted.lexer as lexer")
    text = text.replace("from .. import parser", "import featurelifted.parser as parser")
    text = re.sub(
        r"from \.\. import ([^\n]+)",
        r"from featurelifted.jsonpath import \1",
        text,
    )
    return text


def _apply_jsonpath_submission_patches(output: Path, *, patch_ply: bool) -> None:
    featurelifted = output / "featurelifted"
    if patch_ply:
        for name in ("lexer.py", "parser.py"):
            path = featurelifted / name
            path.write_text(_patch_jsonpath_ply(path.read_text(encoding="utf-8")), encoding="utf-8")
    else:
        for path in featurelifted.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            if "jsonpath_ng" in text:
                path.write_text(text.replace("jsonpath_ng", "featurelifted"), encoding="utf-8")

    ext_pkg = featurelifted / "ext"
    for path in ext_pkg.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        text = _patch_jsonpath_parent_imports(text)
        if patch_ply:
            text = _patch_jsonpath_ply(text)
        path.write_text(text, encoding="utf-8")

    (ext_pkg / "__init__.py").write_text(
        '"""Extended JSONPath (internals in parser.py)."""\n',
        encoding="utf-8",
    )
    write_init(output, JSONPATH_INIT)


def build_jsonpath_ng(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, JSONPATH_CORE_FILES, package="jsonpath_ng")
    _apply_jsonpath_submission_patches(output, patch_ply=True)


def build_jsonpath_ng_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files = _discover_package_files(repo_root, "jsonpath_ng")
    rel_files = [p for p in rel_files if "/bin/" not in p]
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, rel_files, package="jsonpath_ng")
    _apply_jsonpath_submission_patches(output, patch_ply=False)


CONFIGOBJ_SUPPORT_FILES = [
    "configobj/validate.py",
    "configobj/_version.py",
]


CONFIGOBJ_INIT = '''\
"""ConfigObj round-trip and configspec validation core."""

from featurelifted.core import *  # noqa: F403
from featurelifted.validate import Validator

__all__ = (
    "DEFAULT_INDENT_TYPE",
    "DEFAULT_INTERPOLATION",
    "ConfigObjError",
    "NestingError",
    "ParseError",
    "DuplicateError",
    "ConfigspecError",
    "ConfigObj",
    "SimpleVal",
    "InterpolationError",
    "InterpolationLoopError",
    "MissingInterpolationOption",
    "RepeatSectionError",
    "ReloadError",
    "UnreprError",
    "UnknownType",
    "flatten_errors",
    "get_extra_values",
    "Validator",
)
'''


def _patch_configobj_interpolation(text: str) -> str:
    return text.replace(
        "if val is not None and not isinstance(val, Section):",
        "if val is not None and not (hasattr(val, 'scalars') and hasattr(val, 'sections')):",
    )


def _split_configobj_source(text: str) -> tuple[str, str, str]:
    errors_start = text.index("class UnknownType(Exception):")
    interp_start = text.index("class InterpolationEngine(object):")
    section_start = text.index("class Section(dict):")
    header = text[:errors_start]
    errors = text[errors_start:interp_start]
    interpolation = text[interp_start:section_start]
    core_tail = text[section_start:]
    # Drop legacy compiler/unrepr helpers from the compact oracle errors module.
    errors = re.sub(
        r"def getObj\(s\):.*?^_builder = Builder\(\)\n\n",
        "",
        errors,
        count=1,
        flags=re.DOTALL | re.MULTILINE,
    )
    errors = re.sub(
        r"def unrepr\(s\):.*?return ast\.literal_eval\(s\)\n\n",
        "",
        errors,
        count=1,
        flags=re.DOTALL | re.MULTILINE,
    )
    errors_src = "import ast\n\n" + errors
    interpolation_src = (
        "import re\n\n"
        "from featurelifted.errors import (\n"
        "    InterpolationError,\n"
        "    InterpolationLoopError,\n"
        "    MissingInterpolationOption,\n"
        ")\n\n"
        + interpolation
    )
    core_src = (
        header
        + "from featurelifted.errors import *  # noqa: F403\n"
        + "from featurelifted.interpolation import interpolation_engines\n"
        + "from featurelifted._version import __version__\n\n"
        + core_tail
    )
    core_src = rewrite_source(core_src.replace("from ._version import __version__\n", ""), "configobj")
    return errors_src, interpolation_src, core_src


def build_configobj(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    init_path = repo_root / "configobj" / "__init__.py"
    if not init_path.is_file():
        raise FileNotFoundError(f"missing configobj package init: {init_path}")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, CONFIGOBJ_SUPPORT_FILES, package="configobj")
    errors_src, interpolation_src, core_src = _split_configobj_source(
        init_path.read_text(encoding="utf-8"),
    )
    pkg = output / "featurelifted"
    pkg.mkdir(parents=True, exist_ok=True)
    (pkg / "errors.py").write_text(errors_src, encoding="utf-8")
    (pkg / "interpolation.py").write_text(
        _patch_configobj_interpolation(interpolation_src),
        encoding="utf-8",
    )
    (pkg / "core.py").write_text(core_src, encoding="utf-8")
    write_init(output, CONFIGOBJ_INIT)


def build_configobj_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files = _discover_package_files(repo_root, "configobj")
    _append_repo_test_files(repo_root, rel_files)
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, rel_files, package="configobj")
    init_path = output / "featurelifted" / "__init__.py"
    if init_path.is_file():
        text = rewrite_source(init_path.read_text(encoding="utf-8"), "configobj")
        text = text.replace("from featurelifted.validate", "from featurelifted.validate")
        init_path.write_text(text, encoding="utf-8")


WEBSOCKETS_CORE_FILES = [
    "websockets/datastructures.py",
    "websockets/headers.py",
    "websockets/http11.py",
    "websockets/streams.py",
    "websockets/typing.py",
    "websockets/version.py",
    "websockets/utils.py",
]


WEBSOCKETS_EXCEPTIONS = '''\
"""Handshake-related exceptions extracted from websockets."""

from __future__ import annotations


class WebSocketException(Exception):
    """Base class for websockets handshake exceptions."""


class InvalidHandshake(WebSocketException):
    """Base class for opening handshake failures."""


class SecurityError(InvalidHandshake):
    """Raised when a handshake message breaks a security rule."""


class InvalidMessage(InvalidHandshake):
    """Raised when a handshake request or response is malformed."""


class InvalidHeader(InvalidHandshake):
    """Raised when an HTTP header doesn't have a valid format or value."""

    def __init__(self, name: str, value: str | None = None) -> None:
        self.name = name
        self.value = value

    def __str__(self) -> str:
        if self.value is None:
            return f"missing {self.name} header"
        if self.value == "":
            return f"empty {self.name} header"
        return f"invalid {self.name} header: {self.value}"


class InvalidHeaderFormat(InvalidHeader):
    """Raised when an HTTP header cannot be parsed."""

    def __init__(self, name: str, error: str, header: str, pos: int) -> None:
        super().__init__(name, f"{error} at {pos} in {header}")


class InvalidHeaderValue(InvalidHeader):
    """Raised when an HTTP header has a wrong value."""


class InvalidOrigin(InvalidHeader):
    """Raised when the Origin header in a request isn't allowed."""

    def __init__(self, origin: str | None) -> None:
        super().__init__("Origin", origin)


class InvalidUpgrade(InvalidHeader):
    """Raised when the Upgrade or Connection header isn't correct."""


class NegotiationError(InvalidHandshake):
    """Raised when negotiating an extension or a subprotocol fails."""


class DuplicateParameter(NegotiationError):
    def __init__(self, name: str) -> None:
        self.name = name

    def __str__(self) -> str:
        return f"duplicate parameter: {self.name}"


class InvalidParameterName(NegotiationError):
    def __init__(self, name: str) -> None:
        self.name = name

    def __str__(self) -> str:
        return f"invalid parameter name: {self.name}"


class InvalidParameterValue(NegotiationError):
    def __init__(self, name: str, value: str | None) -> None:
        self.name = name
        self.value = value

    def __str__(self) -> str:
        if self.value is None:
            return f"missing value for parameter {self.name}"
        if self.value == "":
            return f"empty value for parameter {self.name}"
        return f"invalid value for parameter {self.name}: {self.value}"
'''


WEBSOCKETS_HANDSHAKE = '''\
"""Validate WebSocket handshake request headers."""

from __future__ import annotations

import base64
import binascii
import re
from collections.abc import Sequence
from typing import cast

from featurelifted.datastructures import MultipleValuesError
from featurelifted.exceptions import (
    InvalidHeader,
    InvalidHeaderValue,
    InvalidOrigin,
    InvalidUpgrade,
)
from featurelifted.headers import parse_connection, parse_upgrade
from featurelifted.http11 import Request
from featurelifted.typing import ConnectionOption, Origin, UpgradeProtocol
from featurelifted.utils import accept_key


def validate_handshake_request(
    request: Request,
    *,
    origins: Sequence[Origin | re.Pattern[str] | None] | None = None,
) -> str:
    """Validate handshake headers and return the Sec-WebSocket-Accept value."""
    headers = request.headers

    connection: list[ConnectionOption] = sum(
        [parse_connection(value) for value in headers.get_all("Connection")],
        [],
    )
    if not any(value.lower() == "upgrade" for value in connection):
        raise InvalidUpgrade(
            "Connection", ", ".join(connection) if connection else None
        )

    upgrade: list[UpgradeProtocol] = sum(
        [parse_upgrade(value) for value in headers.get_all("Upgrade")],
        [],
    )
    if not (len(upgrade) == 1 and upgrade[0].lower() == "websocket"):
        raise InvalidUpgrade("Upgrade", ", ".join(upgrade) if upgrade else None)

    try:
        key = headers["Sec-WebSocket-Key"]
    except KeyError:
        raise InvalidHeader("Sec-WebSocket-Key") from None
    except MultipleValuesError:
        raise InvalidHeader("Sec-WebSocket-Key", "multiple values") from None
    try:
        raw_key = base64.b64decode(key.encode(), validate=True)
    except binascii.Error as exc:
        raise InvalidHeaderValue("Sec-WebSocket-Key", key) from exc
    if len(raw_key) != 16:
        raise InvalidHeaderValue("Sec-WebSocket-Key", key)

    try:
        version = headers["Sec-WebSocket-Version"]
    except KeyError:
        raise InvalidHeader("Sec-WebSocket-Version") from None
    except MultipleValuesError:
        raise InvalidHeader("Sec-WebSocket-Version", "multiple values") from None
    if version != "13":
        raise InvalidHeaderValue("Sec-WebSocket-Version", version)

    try:
        origin = headers.get("Origin")
    except MultipleValuesError:
        raise InvalidHeader("Origin", "multiple values") from None
    if origin is not None:
        origin = cast(Origin, origin)
    if origins is not None:
        for origin_or_regex in origins:
            if origin_or_regex == origin or (
                isinstance(origin_or_regex, re.Pattern)
                and origin is not None
                and origin_or_regex.fullmatch(origin) is not None
            ):
                break
        else:
            raise InvalidOrigin(origin)

    return accept_key(key)
'''


WEBSOCKETS_INIT = '''\
"""WebSocket HTTP upgrade handshake parsing core."""

from featurelifted.datastructures import Headers, MultipleValuesError
from featurelifted.exceptions import (
    InvalidHandshake,
    InvalidHeader,
    InvalidHeaderFormat,
    InvalidHeaderValue,
    InvalidMessage,
    InvalidOrigin,
    InvalidUpgrade,
    SecurityError,
)
from featurelifted.handshake import validate_handshake_request
from featurelifted.http11 import Request, Response
from featurelifted.headers import (
    build_extension,
    build_host,
    build_subprotocol,
    parse_connection,
    parse_extension,
    parse_subprotocol,
    parse_upgrade,
)
from featurelifted.utils import accept_key, generate_key

__all__ = (
    "Headers",
    "MultipleValuesError",
    "InvalidHandshake",
    "InvalidHeader",
    "InvalidHeaderFormat",
    "InvalidHeaderValue",
    "InvalidMessage",
    "InvalidOrigin",
    "InvalidUpgrade",
    "SecurityError",
    "Request",
    "Response",
    "parse_connection",
    "parse_upgrade",
    "parse_extension",
    "parse_subprotocol",
    "build_host",
    "build_extension",
    "build_subprotocol",
    "validate_handshake_request",
    "accept_key",
    "generate_key",
)
'''


def build_websockets(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, WEBSOCKETS_CORE_FILES, package="websockets")
    pkg = output / "featurelifted"
    (pkg / "exceptions.py").write_text(WEBSOCKETS_EXCEPTIONS, encoding="utf-8")
    (pkg / "handshake.py").write_text(WEBSOCKETS_HANDSHAKE, encoding="utf-8")
    write_init(output, WEBSOCKETS_INIT)


def build_websockets_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files = _discover_package_files(repo_root, "websockets")
    rel_files = [
        p
        for p in rel_files
        if not p.endswith("/__main__.py")
        and "/cli.py" not in p
        and not p.endswith("speedups.pyi")
    ]
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, rel_files, package="websockets")
    pkg = output / "featurelifted"
    (pkg / "exceptions.py").write_text(WEBSOCKETS_EXCEPTIONS, encoding="utf-8")
    (pkg / "handshake.py").write_text(WEBSOCKETS_HANDSHAKE, encoding="utf-8")
    write_init(output, WEBSOCKETS_INIT)


CRONITER_INIT = '''\
"""Cron expression parse and next/prev iteration core."""

from featurelifted.errors import (
    CroniterBadCronError,
    CroniterBadDateError,
    CroniterBadTypeRangeError,
    CroniterError,
    CroniterNotAlphaError,
    CroniterUnsupportedSyntaxError,
)
from featurelifted.iterator import croniter
from featurelifted.utils import datetime_to_timestamp

__all__ = (
    "croniter",
    "datetime_to_timestamp",
    "CroniterError",
    "CroniterBadTypeRangeError",
    "CroniterBadCronError",
    "CroniterUnsupportedSyntaxError",
    "CroniterBadDateError",
    "CroniterNotAlphaError",
)
'''


def _patch_croniter_source(text: str, *, trim_hash: bool = False) -> str:
    text = re.sub(
        r"# as pytz is optional.*?\nimport pytz  # noqa\n",
        "",
        text,
        count=1,
        flags=re.DOTALL,
    )
    if trim_hash:
        text = text.replace("import binascii\n", "")
        text = text.replace("import random\n", "")
        text = re.sub(
            r"hash_expression_re = re\.compile\(\n.*?\)\n",
            "",
            text,
            count=1,
            flags=re.DOTALL,
        )
    return text


def _split_croniter_source(text: str) -> tuple[str, str, str, str]:
    text = _patch_croniter_source(text, trim_hash=True)
    errors_start = text.index("class CroniterError")
    croniter_start = text.index("class croniter")
    croniter_range_start = text.index("\ndef croniter_range")

    constants_header = (
        "from __future__ import absolute_import, print_function, division\n\n"
        "import copy\n"
        "import re\n\n"
        "try:\n"
        "    from collections import OrderedDict\n"
        "except ImportError:\n"
        "    OrderedDict = dict\n\n"
    )
    constants_body = text[text.index("M_ALPHAS"):errors_start]
    constants_body = constants_body.replace(
        "EXPRESSIONS = {}\n",
        "EXPRESSIONS = {}\n\nEXPANDERS = OrderedDict()\n",
    )
    constants_src = constants_header + constants_body

    errors_src = text[errors_start:croniter_start]
    utils_src = (
        "from __future__ import absolute_import, print_function, division\n\n"
        "import datetime\n\n"
        + text[text.index("def timedelta_to_seconds"):errors_start]
    )

    iterator_src = text[croniter_start:croniter_range_start]
    iterator_src = re.sub(
        r"\n    @classmethod\n    def is_valid\(.*?return cls\.match_range\(.*?\)\n",
        "\n",
        iterator_src,
        count=1,
        flags=re.DOTALL,
    )
    iterator_src = re.sub(
        r"\n    @classmethod\n    def match_range\(.*?return \(max\(tdp, tdt\).*?\n",
        "\n",
        iterator_src,
        count=1,
        flags=re.DOTALL,
    )
    iterator_src = (
        "from __future__ import absolute_import, print_function, division\n\n"
        "import calendar\n"
        "import copy\n"
        "import datetime\n"
        "import inspect\n"
        "import math\n"
        "import re\n"
        "import sys\n"
        "import traceback as _traceback\n"
        "from time import time\n\n"
        "from dateutil.relativedelta import relativedelta\n"
        "from dateutil.tz import tzutc\n\n"
        "from featurelifted.constants import (\n"
        "    ALPHAS,\n"
        "    DOW_ALPHAS,\n"
        "    EXPRESSIONS,\n"
        "    EXPANDERS,\n"
        "    M_ALPHAS,\n"
        "    MONTHS,\n"
        "    VALID_LEN_EXPRESSION,\n"
        "    WEEKDAYS,\n"
        "    only_int_re,\n"
        "    re_star,\n"
        "    special_dow_re,\n"
        "    star_or_int_re,\n"
        "    step_search_re,\n"
        ")\n"
        "from featurelifted.errors import (\n"
        "    CroniterBadCronError,\n"
        "    CroniterBadDateError,\n"
        "    CroniterError,\n"
        "    CroniterNotAlphaError,\n"
        ")\n"
        "from featurelifted.utils import datetime_to_timestamp, timedelta_to_seconds\n\n"
        + iterator_src
    )
    iterator_src = rewrite_source(iterator_src, "croniter")
    return constants_src, errors_src, utils_src, iterator_src


def build_croniter(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    source_path = repo_root / "croniter" / "croniter.py"
    if not source_path.is_file():
        raise FileNotFoundError(f"missing croniter source: {source_path}")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    constants_src, errors_src, utils_src, iterator_src = _split_croniter_source(
        source_path.read_text(encoding="utf-8"),
    )
    pkg = output / "featurelifted"
    pkg.mkdir(parents=True, exist_ok=True)
    (pkg / "constants.py").write_text(constants_src, encoding="utf-8")
    (pkg / "errors.py").write_text(errors_src, encoding="utf-8")
    (pkg / "utils.py").write_text(utils_src, encoding="utf-8")
    (pkg / "iterator.py").write_text(iterator_src, encoding="utf-8")
    write_init(output, CRONITER_INIT)


def build_croniter_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files = _discover_package_files(repo_root, "croniter")
    _append_repo_test_files(repo_root, rel_files)
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, rel_files, package="croniter")
    cron_path = output / "featurelifted" / "croniter.py"
    if cron_path.is_file():
        cron_path.write_text(
            _patch_croniter_source(cron_path.read_text(encoding="utf-8"), trim_hash=False),
            encoding="utf-8",
        )
    init_path = output / "featurelifted" / "__init__.py"
    if init_path.is_file():
        text = init_path.read_text(encoding="utf-8")
        text = text.replace("from .croniter import", "from featurelifted.croniter import")
        init_path.write_text(text, encoding="utf-8")


MAKO_PKG = "mako"

MAKO_LEXER_EXPRESSION_PATHS = [
    "mako/exceptions.py",
    "mako/compat.py",
    "mako/util.py",
    "mako/_ast_util.py",
    "mako/pyparser.py",
    "mako/ast.py",
    "mako/filters.py",
    "mako/pygen.py",
    "mako/parsetree.py",
    "mako/lexer.py",
]

MAKO_LEXER_EXPRESSION_INIT = '''\
"""Mako template lexer and expression parse core."""

from featurelifted.ast import ArgumentList, FunctionDecl, PythonCode, PythonFragment
from featurelifted.exceptions import CompileException, MakoException, SyntaxException
from featurelifted.lexer import Lexer
from featurelifted import parsetree

__all__ = [
    "Lexer",
    "parsetree",
    "PythonCode",
    "PythonFragment",
    "FunctionDecl",
    "ArgumentList",
    "MakoException",
    "SyntaxException",
    "CompileException",
]
'''


def build_mako(task_dir: Path, output: Path) -> None:
    copy_tree(task_dir / "repo", output, MAKO_LEXER_EXPRESSION_PATHS, package=MAKO_PKG)
    write_init(output, MAKO_LEXER_EXPRESSION_INIT)


def build_mako_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files = _discover_package_files(repo_root, MAKO_PKG)
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, rel_files, package=MAKO_PKG)
    write_init(output, MAKO_LEXER_EXPRESSION_INIT)


VOLUPTUOUS_CORE_FILES = [
    "voluptuous/error.py",
    "voluptuous/schema_builder.py",
]

VOLUPTUOUS_VALIDATORS_TRIM = '''\
"""Core composed validators for schema validation."""

from __future__ import annotations

import typing
from decimal import InvalidOperation

from featurelifted.error import AllInvalid, AnyInvalid, CoerceInvalid, InInvalid, Invalid
from featurelifted.schema_builder import Schema  # noqa: F401

Enum: typing.Union[type, None]
try:
    from enum import Enum
except ImportError:
    Enum = None


class Coerce(object):
    def __init__(
        self,
        type: typing.Union[type, typing.Callable],
        msg: typing.Optional[str] = None,
    ) -> None:
        self.type = type
        self.msg = msg
        self.type_name = type.__name__

    def __call__(self, v):
        try:
            return self.type(v)
        except (ValueError, TypeError, InvalidOperation):
            msg = self.msg or ("expected %s" % self.type_name)
            if not self.msg and Enum and issubclass(self.type, Enum):
                msg += " or one of %s" % str([e.value for e in self.type])[1:-1]
            raise CoerceInvalid(msg)

    def __repr__(self):
        return "Coerce(%s, msg=%r)" % (self.type_name, self.msg)


class _WithSubValidators(object):
    def __init__(
        self, *validators, msg=None, required=False, discriminant=None, **kwargs
    ) -> None:
        self.validators = validators
        self.msg = msg
        self.required = required
        self.discriminant = discriminant

    def __voluptuous_compile__(self, schema: Schema) -> typing.Callable:
        self._compiled = []
        old_required = schema.required
        self.schema = schema
        for v in self.validators:
            schema.required = self.required
            self._compiled.append(schema._compile(v))
        schema.required = old_required
        return self._run

    def _run(self, path: typing.List[typing.Hashable], value):
        if self.discriminant is not None:
            self._compiled = [
                self.schema._compile(v)
                for v in self.discriminant(value, self.validators)
            ]
        return self._exec(self._compiled, value, path)

    def __call__(self, v):
        return self._exec((Schema(val) for val in self.validators), v)

    def __repr__(self):
        return "%s(%s, msg=%r)" % (
            self.__class__.__name__,
            ", ".join(repr(v) for v in self.validators),
            self.msg,
        )

    def _exec(
        self,
        funcs: typing.Iterable,
        v,
        path: typing.Optional[typing.List[typing.Hashable]] = None,
    ):
        raise NotImplementedError()


class Any(_WithSubValidators):
    def _exec(self, funcs, v, path=None):
        error = None
        for func in funcs:
            try:
                if path is None:
                    return func(v)
                return func(path, v)
            except Invalid as e:
                if error is None or len(e.path) > len(error.path):
                    error = e
        else:
            if error:
                raise error if self.msg is None else AnyInvalid(self.msg, path=path)
            raise AnyInvalid(self.msg or "no valid value found", path=path)


Or = Any


class All(_WithSubValidators):
    def _exec(self, funcs, v, path=None):
        try:
            for func in funcs:
                if path is None:
                    v = func(v)
                else:
                    v = func(path, v)
        except Invalid as e:
            raise e if self.msg is None else AllInvalid(self.msg, path=path)
        return v


And = All


class In(object):
    def __init__(
        self,
        container: typing.Container | typing.Iterable,
        msg: typing.Optional[str] = None,
    ) -> None:
        self.container = container
        self.msg = msg

    def __call__(self, v):
        try:
            check = v not in self.container
        except TypeError:
            check = True
        if check:
            try:
                raise InInvalid(
                    self.msg or f"value must be one of {sorted(self.container)}"
                )
            except TypeError:
                raise InInvalid(
                    self.msg
                    or f"value must be one of {sorted(self.container, key=str)}"
                )
        return v

    def __repr__(self):
        return "In(%s)" % (self.container,)
'''


VOLUPTUOUS_INIT = '''\
"""Voluptuous schema validation core."""

from featurelifted.error import Invalid, MultipleInvalid, SchemaError
from featurelifted.schema_builder import (
    ALLOW_EXTRA,
    Extra,
    Optional,
    PREVENT_EXTRA,
    REMOVE_EXTRA,
    Required,
    Schema,
)
from featurelifted.validators import All, Any, Coerce, In

__all__ = [
    "ALLOW_EXTRA",
    "All",
    "Any",
    "Coerce",
    "Extra",
    "In",
    "Invalid",
    "MultipleInvalid",
    "Optional",
    "PREVENT_EXTRA",
    "REMOVE_EXTRA",
    "Required",
    "Schema",
    "SchemaError",
]
'''


def build_voluptuous(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, VOLUPTUOUS_CORE_FILES, package="voluptuous")
    pkg = output / "featurelifted"
    (pkg / "validators.py").write_text(VOLUPTUOUS_VALIDATORS_TRIM, encoding="utf-8")
    write_init(output, VOLUPTUOUS_INIT)


def build_voluptuous_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files = _discover_package_files(repo_root, "voluptuous")
    rel_files = [p for p in rel_files if "/humanize.py" not in p]
    _append_repo_test_files(repo_root, rel_files)
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, rel_files, package="voluptuous")
    init_path = output / "featurelifted" / "__init__.py"
    if init_path.is_file():
        text = init_path.read_text(encoding="utf-8")
        text = text.replace("from featurelifted.schema_builder import *", "")
        text = text.replace("from featurelifted.util import *", "")
        text = text.replace("from featurelifted.validators import *", "")
        text = text.replace("from featurelifted.error import *", "")
        init_path.write_text(VOLUPTUOUS_INIT.rstrip() + "\n", encoding="utf-8")


SORTEDLIST_INDEX_METHODS = frozenset({"_expand", "_loc", "_pos", "_build_index"})
SORTEDLIST_DELETE_METHODS = frozenset({"_delete"})
SORTEDLIST_INVARIANT_METHODS = frozenset({"_check"})

SORTEDLIST_SHARED_HEADER = '''\
"""Sorted list support code extracted from sortedcontainers."""

from bisect import bisect_left, bisect_right, insort
from collections.abc import MutableSequence, Sequence
from functools import reduce, wraps
from itertools import chain, repeat, starmap
from math import log
from operator import add, eq, ge, gt, iadd, le, lt, ne
from reprlib import recursive_repr as _stdlib_recursive_repr
from sys import hexversion
from textwrap import dedent

if hexversion < 0x03000000:
    from itertools import imap as map  # noqa: F401
    from itertools import izip as zip  # noqa: F401
    try:
        from thread import get_ident
    except ImportError:
        from dummy_thread import get_ident
else:
    try:
        from _thread import get_ident
    except ImportError:
        from _dummy_thread import get_ident


def recursive_repr(fillvalue="..."):
    """Decorator to make a repr function return fillvalue for a recursive call."""

    def decorating_function(user_function):
        repr_running = set()

        @wraps(user_function)
        def wrapper(self):
            key = id(self), get_ident()
            if key in repr_running:
                return fillvalue
            repr_running.add(key)
            try:
                result = user_function(self)
            finally:
                repr_running.discard(key)
            return result

        return wrapper

    return decorating_function

'''

SORTEDLIST_INIT = '''\
"""Sorted list core extracted from sortedcontainers."""

from featurelifted.sortedlist import SortedList

__all__ = ["SortedList"]
'''

SORTEDLIST_COPY_ALL_INIT = '''\
"""Sorted containers package (copy-all baseline)."""

from featurelifted.sorteddict import SortedDict, SortedItemsView, SortedKeysView, SortedValuesView
from featurelifted.sortedlist import SortedKeyList, SortedList, SortedListWithKey
from featurelifted.sortedset import SortedSet

__all__ = [
    "SortedList",
    "SortedKeyList",
    "SortedListWithKey",
    "SortedDict",
    "SortedKeysView",
    "SortedItemsView",
    "SortedValuesView",
    "SortedSet",
]
'''


def _truncate_sortedlist_source(text: str) -> str:
    for marker in ("\nclass SortedKeyList", "\ndef identity"):
        if marker in text:
            return text.split(marker, 1)[0].rstrip() + "\n"
    return text.rstrip() + "\n"


def _indent_class_body(segment: str, spaces: int = 4) -> str:
    lines = segment.splitlines()
    if not lines:
        return segment
    prefix = " " * spaces
    return "\n".join([prefix + lines[0], *lines[1:]])


def _class_body_segments(source: str, class_name: str) -> tuple[list[str], list[str], list[str], list[str]]:
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            index_parts: list[str] = []
            delete_parts: list[str] = []
            invariant_parts: list[str] = []
            main_parts: list[str] = []
            for item in node.body:
                if isinstance(item, ast.Expr) and isinstance(item.value, ast.Constant):
                    continue
                segment = ast.get_source_segment(source, item)
                if segment is None:
                    continue
                if isinstance(item, ast.FunctionDef):
                    if item.name in SORTEDLIST_INDEX_METHODS:
                        index_parts.append(segment)
                    elif item.name in SORTEDLIST_DELETE_METHODS:
                        delete_parts.append(segment)
                    elif item.name in SORTEDLIST_INVARIANT_METHODS:
                        invariant_parts.append(segment)
                    else:
                        main_parts.append(segment)
                else:
                    main_parts.append(segment)
            return index_parts, delete_parts, invariant_parts, main_parts
    raise ValueError(f"class not found: {class_name}")


def _sortedlist_oracle_modules(repo_root: Path) -> dict[str, str]:
    source_path = repo_root / "sortedcontainers" / "sortedlist.py"
    source = _truncate_sortedlist_source(source_path.read_text(encoding="utf-8"))
    index_parts, delete_parts, invariant_parts, main_parts = _class_body_segments(
        source, "SortedList"
    )

    index_module = (
        SORTEDLIST_SHARED_HEADER
        + "\n\nclass SortedListIndexMixin:\n\n"
        + "\n\n".join(_indent_class_body(part) for part in index_parts)
        + "\n"
    )
    delete_module = (
        SORTEDLIST_SHARED_HEADER
        + "\n\nclass SortedListDeleteMixin:\n\n"
        + "\n\n".join(_indent_class_body(part) for part in delete_parts)
        + "\n"
    )
    invariant_module = (
        SORTEDLIST_SHARED_HEADER
        + "\n\nclass SortedListInvariantMixin:\n\n"
        + "\n\n".join(_indent_class_body(part) for part in invariant_parts)
        + "\n"
    )
    sortedlist_module = (
        SORTEDLIST_SHARED_HEADER
        + "\nfrom featurelifted._delete_ops import SortedListDeleteMixin\n"
        + "from featurelifted._index import SortedListIndexMixin\n"
        + "from featurelifted._invariants import SortedListInvariantMixin\n\n"
        + "class SortedList(SortedListIndexMixin, SortedListDeleteMixin, SortedListInvariantMixin, MutableSequence):\n"
        + '    """Sorted list is a sorted mutable sequence."""\n\n'
        + "    DEFAULT_LOAD_FACTOR = 1000\n\n"
        + "\n\n".join(_indent_class_body(part) for part in main_parts)
        + "\n"
    )
    return {
        "_index.py": index_module,
        "_delete_ops.py": delete_module,
        "_invariants.py": invariant_module,
        "sortedlist.py": sortedlist_module,
    }


def build_sortedcontainers(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    for rel_path, content in _sortedlist_oracle_modules(repo_root).items():
        write_module(output, rel_path, content)
    write_init(output, SORTEDLIST_INIT)


def build_sortedcontainers_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files = _discover_package_files(repo_root, "sortedcontainers")
    _append_repo_test_files(repo_root, rel_files)
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, rel_files, package="sortedcontainers")
    write_init(output, SORTEDLIST_COPY_ALL_INIT)


CATTRS_CORE_FILES = [
    "cattrs/_compat.py",
    "cattrs/_generics.py",
    "cattrs/converters.py",
    "cattrs/disambiguators.py",
    "cattrs/dispatch.py",
    "cattrs/errors.py",
    "cattrs/fns.py",
    "cattrs/gen/__init__.py",
    "cattrs/gen/_consts.py",
    "cattrs/gen/_shared.py",
    "cattrs/gen/_generics.py",
    "cattrs/gen/_lc.py",
    "cattrs/gen/typeddicts.py",
]

CATTRS_INIT = '''\
"""cattrs structure/unstructure core."""

from featurelifted.converters import BaseConverter, Converter, UnstructureStrategy
from featurelifted.errors import (
    ClassValidationError,
    ForbiddenExtraKeysError,
    StructureHandlerNotFoundError,
)
from featurelifted.gen import override

__all__ = [
    "BaseConverter",
    "ClassValidationError",
    "Converter",
    "ForbiddenExtraKeysError",
    "StructureHandlerNotFoundError",
    "UnstructureStrategy",
    "global_converter",
    "override",
    "register_structure_hook",
    "register_unstructure_hook",
    "structure",
    "unstructure",
]

global_converter = Converter()

unstructure = global_converter.unstructure
structure = global_converter.structure
register_structure_hook = global_converter.register_structure_hook
register_unstructure_hook = global_converter.register_unstructure_hook
'''


def build_cattrs(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, CATTRS_CORE_FILES, package="cattrs")
    write_init(output, CATTRS_INIT)


def build_cattrs_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files = _discover_package_files(repo_root, "cattrs")
    _append_repo_test_files(repo_root, rel_files)
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, rel_files, package="cattrs")
    write_init(output, CATTRS_INIT)


CERBERUS_CORE_FILES = [
    "cerberus/platform.py",
    "cerberus/utils.py",
    "cerberus/errors.py",
    "cerberus/schema.py",
    "cerberus/validator.py",
]

CERBERUS_INIT = '''\
"""Cerberus schema validation core."""

from featurelifted.schema import SchemaError
from featurelifted.utils import TypeDefinition
from featurelifted.validator import DocumentError, Validator

__all__ = [
    "DocumentError",
    "SchemaError",
    "TypeDefinition",
    "Validator",
]
'''


def build_cerberus(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, CERBERUS_CORE_FILES, package="cerberus")
    write_init(output, CERBERUS_INIT)


DATACLASSES_JSON_CORE_FILES = [
    "dataclasses_json/__init__.py",
    "dataclasses_json/__version__.py",
    "dataclasses_json/api.py",
    "dataclasses_json/core.py",
    "dataclasses_json/cfg.py",
    "dataclasses_json/utils.py",
    "dataclasses_json/stringcase.py",
    "dataclasses_json/undefined.py",
]

DATACLASSES_JSON_INIT = '''\
"""Dataclass JSON serde core."""

from featurelifted.api import DataClassJsonMixin, dataclass_json
from featurelifted.cfg import Exclude, LetterCase, config, global_config
from featurelifted.undefined import CatchAll, Undefined, UndefinedParameterError

__all__ = [
    "CatchAll",
    "DataClassJsonMixin",
    "Exclude",
    "LetterCase",
    "Undefined",
    "UndefinedParameterError",
    "config",
    "dataclass_json",
    "global_config",
]
'''


def _patch_dataclasses_json_api(text: str) -> str:
    text = re.sub(r"from featurelifted\.mm import[^\n]*\n", "", text)
    text = re.sub(r"from dataclasses_json\.mm import[^\n]*\n", "", text)
    text = re.sub(r", SchemaType", "", text)
    text = re.sub(r", build_schema", "", text)
    if "JsonData" not in text.split("Fields = ", 1)[0]:
        text = text.replace(
            "Fields = List[Tuple[str, Any]]\n",
            "JsonData = Union[str, bytes, bytearray]\n\nFields = List[Tuple[str, Any]]\n",
        )
    text = re.sub(
        r"\n    @classmethod\n    def schema\(cls.*?unknown=unknown\)\n",
        "\n",
        text,
        flags=re.DOTALL,
    )
    text = text.replace(
        "    cls.schema = classmethod(DataClassJsonMixin.schema.__func__)  # type: ignore[attr-defined]\n",
        "",
    )
    return text


def _patch_dataclasses_json_cfg(text: str) -> str:
    text = text.replace(
        "from marshmallow.fields import Field as MarshmallowField  # type: ignore\n",
        "",
    )
    if "Any" not in text.split("from typing import", 1)[-1].split("\n", 1)[0]:
        text = text.replace("from typing import ", "from typing import Any, ", 1)
    text = text.replace("MarshmallowField", "Any")
    return text


def _patch_dataclasses_json_undefined(text: str) -> str:
    text = text.replace(
        "from marshmallow.exceptions import ValidationError  # type: ignore\n",
        "",
    )
    text = text.replace(
        "class UndefinedParameterError(ValidationError):",
        "class UndefinedParameterError(Exception):",
    )
    return text


def _apply_dataclasses_json_patches(output: Path) -> None:
    patches = {
        "api.py": _patch_dataclasses_json_api,
        "cfg.py": _patch_dataclasses_json_cfg,
        "undefined.py": _patch_dataclasses_json_undefined,
    }
    for name, patch_fn in patches.items():
        path = output / "featurelifted" / name
        if path.is_file():
            path.write_text(patch_fn(path.read_text(encoding="utf-8")), encoding="utf-8")


def build_dataclasses_json(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, DATACLASSES_JSON_CORE_FILES, package="dataclasses_json")
    _apply_dataclasses_json_patches(output)
    write_init(output, DATACLASSES_JSON_INIT)


def build_dataclasses_json_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files = _discover_package_files(repo_root, "dataclasses_json")
    rel_files = [p for p in rel_files if not p.endswith("/mm.py")]
    tests_root = repo_root / "tests"
    if tests_root.is_dir():
        for path in sorted(tests_root.rglob("*.py")):
            rel = path.relative_to(repo_root).as_posix()
            if rel not in rel_files:
                rel_files.append(rel)
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, rel_files, package="dataclasses_json")
    _apply_dataclasses_json_patches(output)
    write_init(output, DATACLASSES_JSON_INIT)


def build_cerberus_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files = _discover_package_files(repo_root, "cerberus")
    benchmarks_root = repo_root / "cerberus" / "benchmarks"
    if benchmarks_root.is_dir():
        for path in sorted(benchmarks_root.rglob("*.py")):
            rel = path.relative_to(repo_root).as_posix()
            if rel not in rel_files:
                rel_files.append(rel)
    _append_repo_test_files(repo_root, rel_files)
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, rel_files, package="cerberus")
    write_init(output, CERBERUS_INIT)


PYTHON_FRONTMATTER_CORE_FILES = [
    "frontmatter/__init__.py",
    "frontmatter/default_handlers.py",
    "frontmatter/util.py",
    "frontmatter/py.typed",
]


def build_python_frontmatter(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, PYTHON_FRONTMATTER_CORE_FILES, package="frontmatter")


def build_python_frontmatter_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files = _discover_package_files(repo_root, "frontmatter")
    for extra_root in ("tests", "examples"):
        extra = repo_root / extra_root
        if extra.is_dir():
            for path in sorted(extra.rglob("*.py")):
                rel = path.relative_to(repo_root).as_posix()
                if rel not in rel_files:
                    rel_files.append(rel)
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, rel_files, package="frontmatter")


BIDICT_CORE_FILES = [
    "bidict/__init__.py",
    "bidict/_abc.py",
    "bidict/_base.py",
    "bidict/_bidict.py",
    "bidict/_dup.py",
    "bidict/_exc.py",
    "bidict/_frozen.py",
    "bidict/_iter.py",
    "bidict/_orderedbase.py",
    "bidict/_orderedbidict.py",
    "bidict/_typing.py",
]

BIDICT_INIT = '''\
"""Bidirectional mapping core."""

from featurelifted._abc import BidirectionalMapping, MutableBidirectionalMapping
from featurelifted._bidict import MutableBidict, bidict
from featurelifted._dup import (
    DROP_NEW,
    DROP_OLD,
    ON_DUP_DEFAULT,
    ON_DUP_DROP_OLD,
    ON_DUP_RAISE,
    RAISE,
    OnDup,
    OnDupAction,
)
from featurelifted._exc import (
    BidictException,
    DuplicationError,
    KeyAndValueDuplicationError,
    KeyDuplicationError,
    ValueDuplicationError,
)
from featurelifted._frozen import frozenbidict
from featurelifted._iter import inverted
from featurelifted._orderedbidict import OrderedBidict

__all__ = [
    "BidictException",
    "BidirectionalMapping",
    "DROP_NEW",
    "DROP_OLD",
    "DuplicationError",
    "KeyAndValueDuplicationError",
    "KeyDuplicationError",
    "MutableBidict",
    "MutableBidirectionalMapping",
    "ON_DUP_DEFAULT",
    "ON_DUP_DROP_OLD",
    "ON_DUP_RAISE",
    "OnDup",
    "OnDupAction",
    "OrderedBidict",
    "RAISE",
    "ValueDuplicationError",
    "bidict",
    "frozenbidict",
    "inverted",
]
'''


PATHVALIDATE_CORE_FILES = [
    "pathvalidate/__version__.py",
    "pathvalidate/error.py",
    "pathvalidate/handler.py",
    "pathvalidate/_base.py",
    "pathvalidate/_common.py",
    "pathvalidate/_const.py",
    "pathvalidate/_types.py",
    "pathvalidate/_filename.py",
    "pathvalidate/_filepath.py",
]

PATHVALIDATE_INIT = '''\
"""Path filename and filepath sanitization core."""

from featurelifted._const import Platform
from featurelifted._filename import (
    FileNameSanitizer,
    FileNameValidator,
    is_valid_filename,
    sanitize_filename,
    validate_filename,
)
from featurelifted._filepath import (
    FilePathSanitizer,
    FilePathValidator,
    is_valid_filepath,
    sanitize_filepath,
    validate_filepath,
)
from featurelifted.error import (
    ErrorReason,
    InvalidCharError,
    NullNameError,
    ReservedNameError,
    ValidationError,
)

__all__ = [
    "ErrorReason",
    "FileNameSanitizer",
    "FileNameValidator",
    "FilePathSanitizer",
    "FilePathValidator",
    "InvalidCharError",
    "NullNameError",
    "Platform",
    "ReservedNameError",
    "ValidationError",
    "is_valid_filename",
    "is_valid_filepath",
    "sanitize_filename",
    "sanitize_filepath",
    "validate_filename",
    "validate_filepath",
]
'''


PYTHON_MULTIPART_INIT = '''\
"""Multipart form-data parse core (offline bytes)."""

from featurelifted.base import BaseParser
from featurelifted.decoders import Base64Decoder, QuotedPrintableDecoder
from featurelifted.exceptions import DecodeError, FileError, FormParserError, MultipartParseError
from featurelifted.form import FormParser, create_form_parser, parse_form
from featurelifted.headers import parse_options_header
from featurelifted.models import Field, File
from featurelifted.multipart_parse import MultipartParser

__all__ = [
    "BaseParser",
    "Base64Decoder",
    "DecodeError",
    "Field",
    "File",
    "FileError",
    "FormParser",
    "FormParserError",
    "MultipartParseError",
    "MultipartParser",
    "QuotedPrintableDecoder",
    "create_form_parser",
    "parse_form",
    "parse_options_header",
]
'''


def _patch_python_multipart_text(text: str) -> str:
    text = text.replace("from .decoders import", "from featurelifted.decoders import")
    text = text.replace("from .exceptions import", "from featurelifted.exceptions import")
    return text


def _multipart_only_form_parser(text: str) -> str:
    text = re.sub(
        r'\n        if content_type == "application/octet-stream":.*?\n        elif content_type == "multipart/form-data":',
        '\n        if content_type == "multipart/form-data":',
        text,
        count=1,
        flags=re.DOTALL,
    )
    return text


def _split_python_multipart_source(text: str) -> dict[str, str]:
    text = _patch_python_multipart_text(text)
    parseparam = text.index("def _parseparam")
    field = text.index("class Field:")
    base = text.index("class BaseParser:")
    octet = text.index("class OctetStreamParser(")
    multipart = text.index("class MultipartParser(")
    form = text.index("class FormParser:")
    create = text.index("def create_form_parser(")
    main = len(text)

    constants = (
        "from __future__ import annotations\n\n"
        "from enum import IntEnum\n"
        "from typing import Literal, TypeAlias\n\n"
        + text[text.index("class MultipartState"):parseparam]
        + "\n\nCallbackName: TypeAlias = Literal[\n"
        '    "start",\n'
        '    "data",\n'
        '    "end",\n'
        '    "part_begin",\n'
        '    "part_data",\n'
        '    "part_end",\n'
        '    "header_begin",\n'
        '    "header_field",\n'
        '    "header_value",\n'
        '    "header_end",\n'
        '    "headers_finished",\n'
        "]\n"
    )

    headers = "from __future__ import annotations\n\n" + text[parseparam:field]

    models = (
        "from __future__ import annotations\n\n"
        "import logging\n"
        "import os\n"
        "import shutil\n"
        "import sys\n"
        "import tempfile\n"
        "from io import BufferedRandom, BytesIO\n"
        "from typing import cast\n\n"
        "_missing = object()\n\n"
        + text[field:base]
    )

    base_parser = (
        "from __future__ import annotations\n\n"
        "import logging\n"
        "from collections.abc import Callable\n"
        "from typing import Any, cast\n\n"
        "from featurelifted.constants import CallbackName\n\n"
        + text[base:octet]
    )
    base_parser = base_parser.replace(
        "self.callbacks: QuerystringCallbacks | OctetStreamCallbacks | MultipartCallbacks = {}",
        "self.callbacks: dict[str, Callable[..., Any]] = {}",
    )

    multipart_parse = (
        "from __future__ import annotations\n\n"
        "import logging\n"
        "from numbers import Number\n"
        "from typing import cast\n\n"
        "from featurelifted.base import BaseParser\n"
        "from featurelifted.constants import (\n"
        "    CallbackName,\n"
        "    CR,\n"
        "    DEFAULT_MAX_HEADER_COUNT,\n"
        "    DEFAULT_MAX_HEADER_SIZE,\n"
        "    FLAG_LAST_BOUNDARY,\n"
        "    FLAG_PART_BOUNDARY,\n"
        "    HYPHEN,\n"
        "    LF,\n"
        "    MAX_BOUNDARY_LENGTH,\n"
        "    MultipartState,\n"
        "    SPACE,\n"
        "    TOKEN_CHARS,\n"
        "    TOKEN_CHARS_SET,\n"
        ")\n"
        "from featurelifted.exceptions import FormParserError, MultipartParseError\n\n"
        + text[multipart:form]
    )

    form_src = _multipart_only_form_parser(text[form:main])
    form_src = (
        "from __future__ import annotations\n\n"
        "import logging\n"
        "from collections.abc import Callable\n"
        "from typing import TYPE_CHECKING, Any\n\n"
        "from featurelifted.constants import (\n"
        "    DEFAULT_MAX_HEADER_COUNT,\n"
        "    DEFAULT_MAX_HEADER_SIZE,\n"
        ")\n"
        "from featurelifted.decoders import Base64Decoder, QuotedPrintableDecoder\n"
        "from featurelifted.exceptions import FormParserError\n"
        "from featurelifted.headers import parse_options_header\n"
        "from featurelifted.models import Field, File\n"
        "from featurelifted.multipart_parse import MultipartParser\n\n"
        + form_src
    )

    return {
        "constants.py": constants,
        "headers.py": headers,
        "models.py": models,
        "base.py": base_parser,
        "multipart_parse.py": multipart_parse,
        "form.py": form_src,
    }


def build_python_multipart(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    pkg_root = repo_root / "python_multipart"
    multipart_path = pkg_root / "multipart.py"
    if not multipart_path.is_file():
        raise FileNotFoundError(f"missing python_multipart source: {multipart_path}")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    for rel in ("exceptions.py", "decoders.py"):
        src = pkg_root / rel
        write_module(output, rel, rewrite_source(src.read_text(encoding="utf-8"), "python_multipart"))
    modules = _split_python_multipart_source(multipart_path.read_text(encoding="utf-8"))
    for name, body in modules.items():
        write_module(output, name, body)
    write_init(output, PYTHON_MULTIPART_INIT)


def build_python_multipart_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files = [
        "python_multipart/__init__.py",
        "python_multipart/multipart.py",
        "python_multipart/decoders.py",
        "python_multipart/exceptions.py",
    ]
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, rel_files, package="python_multipart")
    tests_root = repo_root / "tests"
    if tests_root.is_dir():
        shutil.copytree(
            tests_root,
            output / "tests",
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "test_data"),
        )
    copy_all_init = '''\
"""python-multipart copy-all baseline."""

from featurelifted.decoders import Base64Decoder, QuotedPrintableDecoder
from featurelifted.exceptions import DecodeError, FileError, FormParserError, MultipartParseError
from featurelifted.multipart import (
    BaseParser,
    Field,
    File,
    FormParser,
    MultipartParser,
    create_form_parser,
    parse_form,
    parse_options_header,
)

__all__ = [
    "BaseParser",
    "Base64Decoder",
    "DecodeError",
    "Field",
    "File",
    "FileError",
    "FormParser",
    "FormParserError",
    "MultipartParseError",
    "MultipartParser",
    "QuotedPrintableDecoder",
    "create_form_parser",
    "parse_form",
    "parse_options_header",
]
'''
    write_init(output, copy_all_init)


XMLTODICT_INIT = '''\
"""XML to ordered dict parse/unparse core."""

from featurelifted.exceptions import ParsingInterrupted
from featurelifted.parse import parse
from featurelifted.unparse import unparse

__all__ = ["parse", "unparse", "ParsingInterrupted"]
'''


def _split_xmltodict_source(text: str) -> dict[str, str]:
    sax_start = text.index("class _DictSAXHandler")
    parse_start = text.index("def parse(")
    convert_start = text.index("def _convert_value_to_string")
    emit_start = text.index("def _emit(")
    main_start = text.index("if __name__ == '__main__'")

    exceptions_src = text[text.index("class ParsingInterrupted"):sax_start]

    sax_src = (
        "from xml.sax.xmlreader import AttributesImpl\n\n"
        + text[sax_start:parse_start]
    )

    parse_src = (
        "from inspect import isgenerator\n"
        "from xml.parsers import expat\n\n"
        "from featurelifted.sax_handler import _DictSAXHandler\n\n"
        + text[parse_start:convert_start]
    )

    validation_src = text[convert_start:emit_start]

    unparse_src = (
        "import codecs\n"
        "from io import StringIO\n"
        "from xml.sax.saxutils import XMLGenerator, escape\n"
        "from xml.sax.xmlreader import AttributesImpl\n\n"
        "from featurelifted.validation import (\n"
        "    _convert_value_to_string,\n"
        "    _process_namespace,\n"
        "    _validate_comment,\n"
        "    _validate_name,\n"
        ")\n\n"
        + text[emit_start:main_start]
    )

    return {
        "exceptions.py": exceptions_src,
        "sax_handler.py": sax_src,
        "parse.py": parse_src,
        "validation.py": validation_src,
        "unparse.py": unparse_src,
    }


def build_xmltodict(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    source_path = repo_root / "xmltodict.py"
    if not source_path.is_file():
        raise FileNotFoundError(f"missing xmltodict source: {source_path}")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    modules = _split_xmltodict_source(source_path.read_text(encoding="utf-8"))
    pkg = output / "featurelifted"
    pkg.mkdir(parents=True, exist_ok=True)
    for name, body in modules.items():
        (pkg / name).write_text(body, encoding="utf-8")
    write_init(output, XMLTODICT_INIT)


def build_xmltodict_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    source_path = repo_root / "xmltodict.py"
    if not source_path.is_file():
        raise FileNotFoundError(f"missing xmltodict source: {source_path}")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    pkg = output / "featurelifted"
    pkg.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, pkg / "xmltodict.py")
    copy_all_init = '''\
"""xmltodict copy-all baseline."""

from featurelifted.xmltodict import ParsingInterrupted, parse, unparse

__all__ = ["parse", "unparse", "ParsingInterrupted"]
'''
    write_init(output, copy_all_init)
    tests_root = repo_root / "tests"
    if tests_root.is_dir():
        shutil.copytree(
            tests_root,
            output / "tests",
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )


MSGPACK_CORE_FILES = [
    "msgpack/exceptions.py",
    "msgpack/ext.py",
    "msgpack/fallback.py",
]

MSGPACK_INIT = '''\
"""MessagePack pack/unpack core (pure-Python fallback path)."""

from featurelifted.exceptions import (  # noqa: F401
    BufferFull,
    ExtraData,
    FormatError,
    OutOfData,
    PackException,
    PackOverflowError,
    PackValueError,
    StackError,
    UnpackException,
    UnpackValueError,
)
from featurelifted.ext import ExtType, Timestamp
from featurelifted.fallback import Packer, Unpacker, unpackb

__all__ = [
    "BufferFull",
    "ExtType",
    "ExtraData",
    "FormatError",
    "OutOfData",
    "PackException",
    "PackOverflowError",
    "PackValueError",
    "Packer",
    "StackError",
    "Timestamp",
    "UnpackException",
    "UnpackValueError",
    "Unpacker",
    "dump",
    "dumps",
    "load",
    "loads",
    "pack",
    "packb",
    "unpack",
    "unpackb",
]


def pack(o, stream, **kwargs):
    """Pack object ``o`` and write it to ``stream``."""
    packer = Packer(**kwargs)
    stream.write(packer.pack(o))


def packb(o, **kwargs):
    """Pack object ``o`` and return packed bytes."""
    return Packer(**kwargs).pack(o)


def unpack(stream, **kwargs):
    """Unpack an object from ``stream``."""
    data = stream.read()
    return unpackb(data, **kwargs)


load = unpack
loads = unpackb
dump = pack
dumps = packb
'''


def build_msgpack(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, MSGPACK_CORE_FILES, package="msgpack")
    write_init(output, MSGPACK_INIT)


def build_msgpack_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files: list[str] = []
    for path in sorted(repo_root.rglob("*.py")):
        rel = path.relative_to(repo_root).as_posix()
        rel_files.append(rel)
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, rel_files, package="msgpack")
    init_src = (repo_root / "msgpack" / "__init__.py").read_text(encoding="utf-8")
    init_src = rewrite_source(init_src, "msgpack")
    init_src = init_src.replace(
        'if os.environ.get("MSGPACK_PUREPYTHON"):\n'
        "    from .fallback import Packer, Unpacker, unpackb\n"
        "else:\n"
        "    try:\n"
        "        from ._cmsgpack import Packer, Unpacker, unpackb\n"
        "    except ImportError:\n"
        "        from .fallback import Packer, Unpacker, unpackb\n",
        "from featurelifted.fallback import Packer, Unpacker, unpackb\n",
    )
    init_src = init_src.replace("import os\n\n", "")
    init_src = init_src.replace("from .exceptions", "from featurelifted.exceptions")
    init_src = init_src.replace("from .ext", "from featurelifted.ext")
    write_init(output, init_src)


TABULATE_INIT = '''\
"""Pretty-print tabular data (table formatting core)."""

from featurelifted.formats import tabulate_formats
from featurelifted.layout import simple_separated_format
from featurelifted.render import tabulate

__all__ = ["tabulate", "tabulate_formats", "simple_separated_format"]
'''

TABULATE_COPY_ALL_INIT = '''\
"""tabulate copy-all baseline."""

from featurelifted.tabulate_core import simple_separated_format, tabulate, tabulate_formats

__all__ = ["tabulate", "tabulate_formats", "simple_separated_format"]
'''

_TABULATE_LAYOUT_INJECT = (
    "import featurelifted.formats as _formats\n"
    "globals().update({k: getattr(_formats, k) for k in dir(_formats) if not k.startswith('__')})\n\n"
)

_TABULATE_RENDER_INJECT = (
    "import featurelifted.formats as _formats\n"
    "import featurelifted.layout as _layout\n"
    "globals().update({k: getattr(_formats, k) for k in dir(_formats) if not k.startswith('__')})\n"
    "globals().update({k: getattr(_layout, k) for k in dir(_layout) if not k.startswith('__')})\n\n"
)


def _split_tabulate_source(text: str) -> tuple[str, str, str]:
    main_idx = text.index("if __name__")
    text = text[:main_idx].rstrip() + "\n"
    layout_start = text.index("_multiline_codes = re.compile")
    render_start = text.index("def tabulate(")
    formats = re.sub(r"^__all__\s*=.*\n", "", text[:layout_start], count=1, flags=re.MULTILINE)
    layout = text[layout_start:render_start]
    render = text[render_start:]
    return formats, layout, render


def build_tabulate(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    source_path = repo_root / "tabulate" / "__init__.py"
    if not source_path.is_file():
        raise FileNotFoundError(f"missing tabulate source: {source_path}")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    formats, layout, render = _split_tabulate_source(source_path.read_text(encoding="utf-8"))
    pkg = output / "featurelifted"
    pkg.mkdir(parents=True, exist_ok=True)
    (pkg / "formats.py").write_text(formats, encoding="utf-8")
    (pkg / "layout.py").write_text(_TABULATE_LAYOUT_INJECT + layout, encoding="utf-8")
    (pkg / "render.py").write_text(_TABULATE_RENDER_INJECT + render, encoding="utf-8")
    write_init(output, TABULATE_INIT)


def build_tabulate_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    source_path = repo_root / "tabulate" / "__init__.py"
    if not source_path.is_file():
        raise FileNotFoundError(f"missing tabulate source: {source_path}")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    pkg = output / "featurelifted"
    pkg.mkdir(parents=True, exist_ok=True)
    text = source_path.read_text(encoding="utf-8")
    main_idx = text.index("if __name__")
    core = text[:main_idx].rstrip() + "\n"
    (pkg / "tabulate_core.py").write_text(core, encoding="utf-8")
    write_init(output, TABULATE_COPY_ALL_INIT)
    tests_root = repo_root / "test"
    if tests_root.is_dir():
        shutil.copytree(
            tests_root,
            output / "tests",
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )


def build_pathvalidate(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, PATHVALIDATE_CORE_FILES, package="pathvalidate")
    write_init(output, PATHVALIDATE_INIT)


def build_pathvalidate_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files = _discover_package_files(repo_root, "pathvalidate")
    rel_files = [
        p
        for p in rel_files
        if not p.endswith(("click.py", "argparse.py"))
    ]
    tests_root = repo_root / "test"
    if tests_root.is_dir():
        for path in sorted(tests_root.rglob("*.py")):
            rel = path.relative_to(repo_root).as_posix()
            if rel not in rel_files:
                rel_files.append(rel)
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, rel_files, package="pathvalidate")
    write_init(output, PATHVALIDATE_INIT)


ENVIRONS_PKG = "src/environs"

ENVIRONS_SUPPORT_FILES = [
    "src/environs/exceptions.py",
    "src/environs/types.py",
    "src/environs/fields.py",
]

ENVIRONS_INIT = '''\
"""Typed environment variable parsing core."""

import marshmallow as ma

from featurelifted.env import Env
from featurelifted.exceptions import (
    EnvError,
    EnvSealedError,
    EnvValidationError,
    ParserConflictError,
)

validate = ma.validate
ValidationError = ma.ValidationError

__all__ = [
    "Env",
    "EnvError",
    "EnvSealedError",
    "EnvValidationError",
    "ParserConflictError",
    "ValidationError",
    "validate",
]
'''


def _patch_environs_env_source(text: str) -> str:
    text = re.sub(r"from dotenv\.main import[^\n]+\n", "", text)
    text = re.sub(r"import inspect\n", "", text)
    text = re.sub(
        r"\n    try:\n        from dj_database_url import DBConfig\n    except ImportError:\n        pass\n",
        "\n",
        text,
    )
    text = text.replace(
        '__all__ = ["Env", "EnvError", "FileAwareEnv", "ValidationError", "env"]',
        (
            '__all__ = ["Env", "EnvError", "EnvSealedError", '
            '"EnvValidationError", "ParserConflictError", "ValidationError", "validate"]'
        ),
    )
    text = re.sub(
        r"\ndef _dj_db_url_parser[\s\S]*?\n\n\nclass Env:",
        "\n\nclass Env:",
        text,
        count=1,
    )
    text = re.sub(
        r"\n    dj_db_url = _func2method\(_dj_db_url_parser, \"dj_db_url\"\)\n"
        r"    dj_email_url = _func2method\(_dj_email_url_parser, \"dj_email_url\"\)\n"
        r"    dj_cache_url = _func2method\(_dj_cache_url_parser, \"dj_cache_url\"\)\n",
        "\n",
        text,
    )
    text = re.sub(
        r"\n    def read_env\([\s\S]*?\n        return is_env_loaded\n",
        "\n",
        text,
        count=1,
    )
    text = re.sub(
        r"\n    def _load_dotenv\([\s\S]*?\n                self\._environ\[key\] = value\n",
        "\n",
        text,
        count=1,
    )
    text = re.sub(
        r"\n\nclass FileAwareEnv[\s\S]*?\n\n\n# Singleton instance[\s\S]*?env = Env\(\)\n?",
        "\n",
        text,
        count=1,
    )
    return text


def build_environs(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, ENVIRONS_SUPPORT_FILES, package=ENVIRONS_PKG)
    env_src = repo_root / "src" / "environs" / "__init__.py"
    env_text = rewrite_source(env_src.read_text(encoding="utf-8"), "environs")
    env_text = _patch_environs_env_source(env_text)
    write_module(output, "env.py", env_text)
    write_init(output, ENVIRONS_INIT)


def build_environs_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files = _discover_package_files(repo_root, "environs")
    tests_root = repo_root / "tests"
    if tests_root.is_dir():
        for path in sorted(tests_root.rglob("*.py")):
            rel = path.relative_to(repo_root).as_posix()
            if rel not in rel_files:
                rel_files.append(rel)
    rel_files = [p for p in rel_files if p != f"{ENVIRONS_PKG}/__init__.py"]
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, rel_files, package=ENVIRONS_PKG)
    env_src = repo_root / "src" / "environs" / "__init__.py"
    env_text = rewrite_source(env_src.read_text(encoding="utf-8"), "environs")
    env_text = _patch_environs_env_source(env_text)
    write_module(output, "env.py", env_text)
    write_init(output, ENVIRONS_INIT)


CACHETOOLS_PKG = "src/cachetools"

CACHETOOLS_CORE_FILES = [
    "src/cachetools/keys.py",
    "src/cachetools/_cached.py",
]

CACHETOOLS_INIT = '''\
"""Cache eviction core (LRU/TTL/LFU caches and memoizing decorators)."""

from featurelifted._caches import Cache, LFUCache, LRUCache, TTLCache, cached
from featurelifted.keys import hashkey, typedkey

__all__ = [
    "Cache",
    "LFUCache",
    "LRUCache",
    "TTLCache",
    "cached",
    "hashkey",
    "typedkey",
]
'''

CACHETOOLS_COPY_ALL_INIT = '''\
"""Cachetools copy-all baseline."""

from featurelifted._caches import (
    Cache,
    FIFOCache,
    LFUCache,
    LRUCache,
    RRCache,
    TLRUCache,
    TTLCache,
    cached,
    cachedmethod,
)
from featurelifted.keys import hashkey, methodkey, typedkey, typedmethodkey

__all__ = [
    "Cache",
    "FIFOCache",
    "LFUCache",
    "LRUCache",
    "RRCache",
    "TLRUCache",
    "TTLCache",
    "cached",
    "cachedmethod",
    "hashkey",
    "methodkey",
    "typedkey",
    "typedmethodkey",
]
'''


def build_cachetools(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, CACHETOOLS_CORE_FILES, package=CACHETOOLS_PKG)
    caches_src = repo_root / "src" / "cachetools" / "__init__.py"
    content = rewrite_source(caches_src.read_text(encoding="utf-8"), "cachetools")
    write_module(output, "_caches.py", content)
    write_init(output, CACHETOOLS_INIT)


def build_cachetools_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files = _discover_package_files(repo_root, "cachetools")
    tests_root = repo_root / "tests"
    if tests_root.is_dir():
        for path in sorted(tests_root.rglob("*.py")):
            rel = path.relative_to(repo_root).as_posix()
            if rel not in rel_files:
                rel_files.append(rel)
    rel_files = [p for p in rel_files if p != f"{CACHETOOLS_PKG}/__init__.py"]
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, rel_files, package=CACHETOOLS_PKG)
    caches_src = repo_root / "src" / "cachetools" / "__init__.py"
    content = rewrite_source(caches_src.read_text(encoding="utf-8"), "cachetools")
    write_module(output, "_caches.py", content)
    write_init(output, CACHETOOLS_COPY_ALL_INIT)


URLLIB3_INIT = '''\
"""urllib3 Retry policy core (offline, no HTTP I/O)."""

from featurelifted.exceptions import (
    ConnectTimeoutError,
    InvalidHeader,
    MaxRetryError,
    ReadTimeoutError,
    ResponseError,
)
from featurelifted.retry import RequestHistory, Retry

__all__ = [
    "ConnectTimeoutError",
    "InvalidHeader",
    "MaxRetryError",
    "ReadTimeoutError",
    "RequestHistory",
    "ResponseError",
    "Retry",
]
'''


def _urllib3_repo_root(task_dir: Path) -> Path:
    return task_dir / "repo" / "src" / "urllib3"


def _patch_urllib3_retry_source(text: str) -> str:
    text = text.replace("from typing_extensions import Self", "from typing import Self")
    text = text.replace("from ..exceptions import", "from featurelifted.exceptions import")
    text = text.replace("from .util import reraise", "from featurelifted.util import reraise")
    text = re.sub(
        r"if typing\.TYPE_CHECKING:.*?from \.\.response import BaseHTTPResponse\n",
        "",
        text,
        flags=re.DOTALL,
    )
    text = text.replace(
        "from ..connectionpool import ConnectionPool\n",
        "",
    )
    return text


def _patch_urllib3_util_imports(text: str) -> str:
    text = text.replace("from ..exceptions import", "from featurelifted.exceptions import")
    text = re.sub(r"^\s*import urllib3\s*$", "", text, flags=re.MULTILINE)
    return text


def build_urllib3_retry(task_dir: Path, output: Path) -> None:
    repo_pkg = _urllib3_repo_root(task_dir)
    if not repo_pkg.is_dir():
        raise FileNotFoundError(f"missing urllib3 snapshot: {repo_pkg}")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    exceptions_src = (repo_pkg / "exceptions.py").read_text(encoding="utf-8")
    util_src = (repo_pkg / "util" / "util.py").read_text(encoding="utf-8")
    retry_src = _patch_urllib3_retry_source(
        (repo_pkg / "util" / "retry.py").read_text(encoding="utf-8"),
    )
    write_module(output, "exceptions.py", exceptions_src)
    write_module(output, "util.py", util_src)
    write_module(output, "retry.py", retry_src)
    write_init(output, URLLIB3_INIT)


def build_urllib3_copy_all(task_dir: Path, output: Path) -> None:
    repo_pkg = _urllib3_repo_root(task_dir)
    if not repo_pkg.is_dir():
        raise FileNotFoundError(f"missing urllib3 snapshot: {repo_pkg}")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    exceptions_src = rewrite_source(
        (repo_pkg / "exceptions.py").read_text(encoding="utf-8"),
        "urllib3",
    )
    write_module(output, "exceptions.py", exceptions_src)
    util_dst = output / "featurelifted" / "util"
    util_dst.mkdir(parents=True, exist_ok=True)
    for path in sorted((repo_pkg / "util").glob("*.py")):
        content = _patch_urllib3_util_imports(path.read_text(encoding="utf-8"))
        if path.name == "retry.py":
            content = _patch_urllib3_retry_source(content)
            content = content.replace(
                "from featurelifted.util import reraise",
                "from featurelifted.util.util import reraise",
            )
        content = rewrite_source(content, "urllib3")
        (util_dst / path.name).write_text(content, encoding="utf-8")
    write_init(
        output,
        URLLIB3_INIT.replace(
            "from featurelifted.retry import RequestHistory, Retry",
            "from featurelifted.util.retry import RequestHistory, Retry",
        ),
    )


INTERVALTREE_CORE_FILES = [
    "intervaltree/interval.py",
    "intervaltree/intervaltree.py",
    "intervaltree/node.py",
]

INTERVALTREE_INIT = '''\
"""Interval tree core: add/remove/overlap/chop queries."""

from featurelifted.interval import Interval
from featurelifted.intervaltree import IntervalTree

__all__ = ["Interval", "IntervalTree"]
'''


def build_intervaltree(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, INTERVALTREE_CORE_FILES, package="intervaltree")
    write_init(output, INTERVALTREE_INIT)


def build_intervaltree_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files = _discover_package_files(repo_root, "intervaltree")
    tests_root = repo_root / "test"
    if tests_root.is_dir():
        for path in sorted(tests_root.rglob("*.py")):
            rel = path.relative_to(repo_root).as_posix()
            if rel not in rel_files:
                rel_files.append(rel)
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, rel_files, package="intervaltree")
    write_init(output, INTERVALTREE_INIT)


def build_bidict(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, BIDICT_CORE_FILES, package="bidict")
    write_init(output, BIDICT_INIT)


DYNACONF_SETTINGS_MERGE_CORE = [
    "dynaconf/constants.py",
    "dynaconf/default_settings.py",
    "dynaconf/nodes.py",
    "dynaconf/base.py",
    "dynaconf/validator.py",
    "dynaconf/utils/__init__.py",
    "dynaconf/utils/parse_conf.py",
    "dynaconf/utils/functional.py",
    "dynaconf/utils/files.py",
    "dynaconf/utils/boxing.py",
    "dynaconf/utils/inspect.py",
    "dynaconf/strategies/__init__.py",
    "dynaconf/strategies/filtering.py",
    "dynaconf/loaders/__init__.py",
    "dynaconf/loaders/base.py",
    "dynaconf/loaders/env_loader.py",
    "dynaconf/loaders/toml_loader.py",
]

DYNACONF_VENDOR_DIRS = [
    "dynaconf/vendor/box",
    "dynaconf/vendor/toml",
    "dynaconf/vendor/tomllib",
    "dynaconf/vendor/ruamel",
    "dynaconf/vendor/dotenv",
]

DYNACONF_SETTINGS_MERGE_INIT = '''\
"""Dynaconf layered settings merge core."""

from featurelifted.base import LazySettings
from featurelifted.base import LazySettings as Dynaconf
from featurelifted.utils import object_merge

__all__ = ["Dynaconf", "LazySettings", "object_merge"]
'''


def _dynaconf_vendor_files(repo_root: Path) -> list[str]:
    files: list[str] = []
    for rel_dir in DYNACONF_VENDOR_DIRS:
        root = repo_root / rel_dir
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*")):
            if path.is_file() and path.suffix in {".py", ".typed", ".pyi"}:
                files.append(path.relative_to(repo_root).as_posix())
    return files


def _patch_dynaconf_submission(output: Path) -> None:
    for path in output.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        text = rewrite_source(text, "dynaconf")
        if "vendor" in path.parts:
            text = text.replace("dynaconf", "featurelifted")
        path.write_text(text, encoding="utf-8")
    loaders_init = output / "featurelifted" / "loaders" / "__init__.py"
    text = loaders_init.read_text(encoding="utf-8")
    text = text.replace("from featurelifted.loaders import yaml_loader\n", "")
    text = text.replace('{"ext": ct.YAML_EXTENSIONS, "name": "YAML", "loader": yaml_loader},\n', "")
    loaders_init.write_text(text, encoding="utf-8")
    base_path = output / "featurelifted" / "base.py"
    base_text = base_path.read_text(encoding="utf-8")
    base_text = base_text.replace("from featurelifted.loaders import yaml_loader\n", "")
    base_path.write_text(base_text, encoding="utf-8")
    default_settings = output / "featurelifted" / "default_settings.py"
    ds_text = default_settings.read_text(encoding="utf-8")
    ds_text = ds_text.replace("from featurelifted.vendor.dotenv import load_dotenv\n", "")
    ds_text = ds_text.replace(
        "def start_dotenv(obj=None, root_path=None):\n    # load_from_dotenv_if_installed",
        "def start_dotenv(obj=None, root_path=None):\n    return\n    # load_from_dotenv_if_installed",
    )
    default_settings.write_text(ds_text, encoding="utf-8")
    write_module(
        output,
        "validator_conditions.py",
        '"""Stubbed validator conditions for env-merge oracle."""\n\n'
        "def identity(value):\n    return value\n",
    )
    write_module(output, "loaders/json_loader.py", "def load(*args, **kwargs):\n    return None\n")
    write_module(output, "loaders/ini_loader.py", "def load(*args, **kwargs):\n    return None\n")
    write_module(
        output,
        "loaders/py_loader.py",
        "def load(*args, **kwargs):\n    return None\n\ndef import_from_filename(*args, **kwargs):\n    return None\n",
    )
    env_loader = output / "featurelifted" / "loaders" / "env_loader.py"
    if env_loader.is_file():
        el_text = env_loader.read_text(encoding="utf-8")
        el_text = re.sub(
            r"DOTENV_IMPORTED = False\nwith suppress\(ImportError, FileNotFoundError\):\n"
            r"    from featurelifted\.vendor\.dotenv import cli as dotenv_cli\n\n"
            r"    DOTENV_IMPORTED = True\n",
            "DOTENV_IMPORTED = False\n",
            el_text,
            count=1,
        )
        env_loader.write_text(el_text, encoding="utf-8")


def build_dynaconf_settings_merge(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files = DYNACONF_SETTINGS_MERGE_CORE + _dynaconf_vendor_files(repo_root)
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, rel_files, package="dynaconf")
    _patch_dynaconf_submission(output)
    write_init(output, DYNACONF_SETTINGS_MERGE_INIT)


def build_dynaconf_settings_merge_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files = _discover_package_files(repo_root, "dynaconf")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, rel_files, package="dynaconf")
    _patch_dynaconf_submission(output)
    write_init(output, DYNACONF_SETTINGS_MERGE_INIT)


PHONENUMBERS_PARSE_FORMAT_CORE = [
    "phonenumbers/__init__.py",
    "phonenumbers/phonenumber.py",
    "phonenumbers/phonenumberutil.py",
    "phonenumbers/phonemetadata.py",
    "phonenumbers/re_util.py",
    "phonenumbers/util.py",
    "phonenumbers/unicode_util.py",
    "phonenumbers/data/region_US.py",
    "phonenumbers/data/region_GB.py",
    "phonenumbers/data/alt_format_44.py",
]

PHONENUMBERS_DATA_INIT = '''\
"""Trimmed region metadata for US and GB."""

from ..phonemetadata import PhoneMetadata

_AVAILABLE_REGION_CODES = ["GB", "US"]
_AVAILABLE_NONGEO_COUNTRY_CODES: list[int] = []


def _load_region(code):
    __import__("region_%s" % code, globals(), locals(), fromlist=["PHONE_METADATA_%s" % code], level=1)


for _region_code in _AVAILABLE_REGION_CODES:
    PhoneMetadata.register_region_loader(_region_code, _load_region)

from .alt_format_44 import PHONE_ALT_FORMAT_44

_ALT_NUMBER_FORMATS = {44: PHONE_ALT_FORMAT_44}

_COUNTRY_CODE_TO_REGION_CODE = {1: ("US",), 44: ("GB",)}
'''

PHONENUMBERS_PARSE_FORMAT_INIT = '''\
"""Phone number parse and format core."""

from featurelifted.phonenumber import PhoneNumber
from featurelifted.phonenumberutil import (
    NumberParseException,
    PhoneNumberFormat,
    format_number,
    is_valid_number,
    parse,
)

__all__ = [
    "PhoneNumber",
    "PhoneNumberFormat",
    "NumberParseException",
    "parse",
    "format_number",
    "is_valid_number",
]
'''


def _patch_phonenumbers_submission(output: Path) -> None:
    data_init = output / "featurelifted" / "data" / "__init__.py"
    data_init.parent.mkdir(parents=True, exist_ok=True)
    data_init.write_text(PHONENUMBERS_DATA_INIT, encoding="utf-8")
    pkg_init = output / "featurelifted" / "__init__.py"
    text = pkg_init.read_text(encoding="utf-8")
    text = text.replace("from .data import _COUNTRY_CODE_TO_REGION_CODE", "")
    text = text.replace(
        "COUNTRY_CODE_TO_REGION_CODE = _COUNTRY_CODE_TO_REGION_CODE",
        "COUNTRY_CODE_TO_REGION_CODE = {1: ('US',), 44: ('GB',)}",
    )
    pkg_init.write_text(text, encoding="utf-8")


def build_phonenumbers_parse_format(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, PHONENUMBERS_PARSE_FORMAT_CORE, package="phonenumbers")
    _patch_phonenumbers_submission(output)
    write_init(output, PHONENUMBERS_PARSE_FORMAT_INIT)


def build_phonenumbers_parse_format_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files = _discover_package_files(repo_root, "phonenumbers")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, rel_files, package="phonenumbers")
    write_init(output, PHONENUMBERS_PARSE_FORMAT_INIT)


PASSLIB_HASH_CONTEXT_CORE = [
    "passlib/context.py",
    "passlib/registry.py",
    "passlib/exc.py",
    "passlib/ifc.py",
    "passlib/handlers/__init__.py",
    "passlib/handlers/pbkdf2.py",
    "passlib/utils/__init__.py",
    "passlib/utils/handlers.py",
    "passlib/utils/decor.py",
    "passlib/utils/binary.py",
    "passlib/utils/compat",
    "passlib/crypto/__init__.py",
    "passlib/crypto/digest.py",
]

PASSLIB_HASH_CONTEXT_INIT = '''\
"""Passlib CryptContext hash/verify core."""

from featurelifted.context import CryptContext, LazyCryptContext

__all__ = ["CryptContext", "LazyCryptContext"]
'''


def _patch_passlib_submission(output: Path) -> None:
    for path in output.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        text = text.replace("passlib.ifc", "featurelifted.ifc")
        text = text.replace("import passlib", "import featurelifted")
        text = text.replace("from passlib", "from featurelifted")
        path.write_text(text, encoding="utf-8")


def build_passlib_hash_context(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, PASSLIB_HASH_CONTEXT_CORE, package="passlib")
    _patch_passlib_submission(output)
    write_init(output, PASSLIB_HASH_CONTEXT_INIT)


def build_passlib_hash_context_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files = _discover_package_files(repo_root, "passlib")
    tests_root = repo_root / "passlib" / "tests"
    if tests_root.is_dir():
        for path in sorted(tests_root.rglob("*.py")):
            rel = path.relative_to(repo_root).as_posix()
            if rel not in rel_files:
                rel_files.append(rel)
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, rel_files, package="passlib")
    _patch_passlib_submission(output)
    write_init(output, PASSLIB_HASH_CONTEXT_INIT)


PYDANTIC_SETTINGS_ENV_CORE = [
    "pydantic_settings/__init__.py",
    "pydantic_settings/exceptions.py",
    "pydantic_settings/version.py",
    "pydantic_settings/utils.py",
    "pydantic_settings/main.py",
    "pydantic_settings/sources/__init__.py",
    "pydantic_settings/sources/base.py",
    "pydantic_settings/sources/types.py",
    "pydantic_settings/sources/utils.py",
    "pydantic_settings/sources/providers/__init__.py",
    "pydantic_settings/sources/providers/env.py",
    "pydantic_settings/sources/providers/dotenv.py",
]

PYDANTIC_SETTINGS_SOURCES_INIT = '''\
"""Pydantic settings sources (env core)."""

from .base import (
    DefaultSettingsSource,
    InitSettingsSource,
    PydanticBaseEnvSettingsSource,
    PydanticBaseSettingsSource,
    get_subcommand,
)
from .providers.dotenv import DotEnvSettingsSource
from .providers.env import EnvSettingsSource
from .types import (
    ENV_FILE_SENTINEL,
    DotenvFiltering,
    DotenvType,
    EnvPrefixTarget,
    ForceDecode,
    NoDecode,
    PathType,
    PydanticModel,
)

__all__ = [
    "ENV_FILE_SENTINEL",
    "DefaultSettingsSource",
    "DotenvFiltering",
    "DotenvType",
    "EnvPrefixTarget",
    "DotEnvSettingsSource",
    "EnvSettingsSource",
    "ForceDecode",
    "InitSettingsSource",
    "NoDecode",
    "PathType",
    "PydanticBaseEnvSettingsSource",
    "PydanticBaseSettingsSource",
    "PydanticModel",
    "get_subcommand",
]
'''

PYDANTIC_SETTINGS_PROVIDERS_INIT = '''\
"""Env and dotenv settings providers."""

from .dotenv import DotEnvSettingsSource
from .env import EnvSettingsSource

__all__ = ["DotEnvSettingsSource", "EnvSettingsSource"]
'''

PYDANTIC_SETTINGS_ENV_INIT = '''\
"""Pydantic settings env source core."""

from featurelifted.exceptions import SettingsError
from featurelifted.main import BaseSettings, SettingsConfigDict

__all__ = ["BaseSettings", "SettingsConfigDict", "SettingsError"]
'''


def _patch_pydantic_settings_submission(output: Path) -> None:
    write_module(output, "sources/__init__.py", PYDANTIC_SETTINGS_SOURCES_INIT)
    write_module(output, "sources/providers/__init__.py", PYDANTIC_SETTINGS_PROVIDERS_INIT)
    main_path = output / "featurelifted" / "main.py"
    text = main_path.read_text(encoding="utf-8")
    text = re.sub(
        r"from \.sources import \([\s\S]*?\)\n",
        "from .sources import (\n"
        "    DefaultSettingsSource,\n"
        "    DotEnvSettingsSource,\n"
        "    EnvSettingsSource,\n"
        "    InitSettingsSource,\n"
        "    PydanticBaseSettingsSource,\n"
        "    get_subcommand,\n"
        ")\n"
        "from .sources.types import ENV_FILE_SENTINEL, DotenvType, PathType\n",
        text,
        count=1,
    )
    if "\nclass CliApp:" in text:
        text = text.split("\nclass CliApp:")[0].rstrip() + "\n"
    text = re.sub(
        r"    @staticmethod\n    def _settings_warn_unused_config_keys\([\s\S]*?(?=\n    model_config: ClassVar)",
        "    @staticmethod\n    def _settings_warn_unused_config_keys(sources, model_config):\n        return\n\n",
        text,
        count=1,
    )
    text = text.replace(
        "        return init_settings, env_settings, dotenv_settings, file_secret_settings",
        "        return env_settings, init_settings",
    )
    text = re.sub(
        r"        file_secret_settings = SecretsSettingsSource\([\s\S]*?\)\n",
        "",
        text,
        count=1,
    )
    text = re.sub(
        r"        custom_cli_sources = \[source for source in sources if isinstance\(source, CliSettingsSource\)\][\s\S]*?"
        r"            custom_cli_sources\[0\]\(args=cli_parse_args\)  # type: ignore\n\n",
        "",
        text,
        count=1,
    )
    text = text.replace(
        "            dotenv_settings=dotenv_settings,\n            file_secret_settings=file_secret_settings,",
        "            dotenv_settings=dotenv_settings,\n            file_secret_settings=init_settings,",
    )
    main_path.write_text(text, encoding="utf-8")


def build_pydantic_settings_env_source(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, PYDANTIC_SETTINGS_ENV_CORE, package="pydantic_settings")
    _patch_pydantic_settings_submission(output)
    write_init(output, PYDANTIC_SETTINGS_ENV_INIT)


def build_pydantic_settings_env_source_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files = _discover_package_files(repo_root, "pydantic_settings")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, rel_files, package="pydantic_settings")
    _patch_pydantic_settings_submission(output)
    write_init(output, PYDANTIC_SETTINGS_ENV_INIT)


CHAMELEON_TEMPLATE_COMPILE_CORE = [
    "chameleon/exc.py",
    "chameleon/types.py",
    "chameleon/config.py",
    "chameleon/utils.py",
    "chameleon/astutil.py",
    "chameleon/nodes.py",
    "chameleon/namespaces.py",
    "chameleon/tokenize.py",
    "chameleon/parser.py",
    "chameleon/compiler.py",
    "chameleon/codegen.py",
    "chameleon/program.py",
    "chameleon/template.py",
    "chameleon/tal.py",
    "chameleon/tales.py",
    "chameleon/i18n.py",
    "chameleon/metal.py",
    "chameleon/loader.py",
    "chameleon/zpt/__init__.py",
    "chameleon/zpt/template.py",
    "chameleon/zpt/program.py",
]

CHAMELEON_TEMPLATE_COMPILE_INIT = '''\
"""Chameleon ZPT template compile core."""

from featurelifted.exc import TemplateError
from featurelifted.zpt.template import PageTemplate

__all__ = ["TemplateError", "PageTemplate"]
'''


def build_chameleon_template_compile(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, CHAMELEON_TEMPLATE_COMPILE_CORE, package="chameleon")
    write_init(output, CHAMELEON_TEMPLATE_COMPILE_INIT)


def build_chameleon_template_compile_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files = _discover_package_files(repo_root, "chameleon")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, rel_files, package="chameleon")
    write_init(output, CHAMELEON_TEMPLATE_COMPILE_INIT)


BOLTONS_ITERUTILS_CORE = ["boltons/iterutils.py"]

BOLTONS_ITERUTILS_INIT = '''\
"""Boltons iterutils iterator toolkit."""

from featurelifted.iterutils import (
    bucketize,
    chunked,
    get_path,
    pairwise,
    partition,
    remap,
    unique,
    windowed,
)

__all__ = [
    "bucketize",
    "chunked",
    "get_path",
    "pairwise",
    "partition",
    "remap",
    "unique",
    "windowed",
]
'''


def _copy_namespaced_files(
    repo_root: Path,
    output: Path,
    rel_paths: list[str],
) -> None:
    pkg_root = output / "featurelifted"
    pkg_root.mkdir(parents=True, exist_ok=True)
    for rel in rel_paths:
        src = repo_root / rel
        if not src.is_file():
            raise FileNotFoundError(src)
        dst = pkg_root / Path(rel)
        dst.parent.mkdir(parents=True, exist_ok=True)
        top = rel.split("/", 1)[0]
        text = src.read_text(encoding="utf-8")
        if top == "hyperframe":
            text = re.sub(r"^(\s*)from \.", r"\1from featurelifted.hyperframe.", text, flags=re.MULTILINE)
            text = text.replace("from hyperframe.", "from featurelifted.hyperframe.")
        elif top == "h2":
            text = re.sub(r"^(\s*)from \.", r"\1from featurelifted.h2.", text, flags=re.MULTILINE)
            text = text.replace("from hyperframe.", "from featurelifted.hyperframe.")
        else:
            text = rewrite_source(text, top)
        dst.write_text(text, encoding="utf-8")


H2_FRAME_ORACLE_FILES = [
    "hyperframe/__init__.py",
    "hyperframe/frame.py",
    "hyperframe/flags.py",
    "hyperframe/exceptions.py",
    "h2/__init__.py",
    "h2/frame_buffer.py",
    "h2/errors.py",
    "h2/exceptions.py",
]

H2_FRAME_INIT = '''\
"""HTTP/2 frame parse/build core (hyperframe + FrameBuffer)."""

from featurelifted.h2.exceptions import (
    FrameDataMissingError,
    FrameTooLargeError,
    ProtocolError,
)
from featurelifted.h2.frame_buffer import FrameBuffer
from featurelifted.hyperframe.exceptions import (
    InvalidDataError,
    InvalidFrameError,
    InvalidPaddingError,
    UnknownFrameError,
)
from featurelifted.hyperframe.frame import (
    AltSvcFrame,
    ContinuationFrame,
    DataFrame,
    Frame,
    GoAwayFrame,
    HeadersFrame,
    PingFrame,
    PriorityFrame,
    PushPromiseFrame,
    RstStreamFrame,
    SettingsFrame,
    WindowUpdateFrame,
)

__all__ = [
    "Frame",
    "DataFrame",
    "HeadersFrame",
    "ContinuationFrame",
    "SettingsFrame",
    "PingFrame",
    "GoAwayFrame",
    "RstStreamFrame",
    "WindowUpdateFrame",
    "PushPromiseFrame",
    "PriorityFrame",
    "AltSvcFrame",
    "FrameBuffer",
    "ProtocolError",
    "FrameTooLargeError",
    "FrameDataMissingError",
    "InvalidDataError",
    "InvalidFrameError",
    "InvalidPaddingError",
    "UnknownFrameError",
]
'''


def build_h2_frame(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    _copy_namespaced_files(repo_root, output, H2_FRAME_ORACLE_FILES)
    write_module(
        output,
        "h2/_exports.py",
        '"""HTTP/2 frame export helpers."""\n\n'
        "from featurelifted.hyperframe.frame import Frame as H2Frame\n\n"
        "Frame = H2Frame\n\n"
        '__all__ = ["Frame", "H2Frame"]\n',
    )
    write_init(output, H2_FRAME_INIT)


def build_h2_frame_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files: list[str] = []
    for pkg in ("h2", "hyperframe"):
        rel_files.extend(_discover_package_files(repo_root, pkg))
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    _copy_namespaced_files(repo_root, output, rel_files)
    write_init(output, H2_FRAME_INIT)


REFERENCING_CORE_FILES = [
    "referencing/__init__.py",
    "referencing/_attrs.py",
    "referencing/_core.py",
    "referencing/exceptions.py",
    "referencing/jsonschema.py",
    "referencing/typing.py",
]

REFERENCING_INIT = '''\
"""JSON Schema $ref resolution core."""

from featurelifted._core import Anchor, Registry, Resource, Specification
from featurelifted.exceptions import NoSuchAnchor, PointerToNowhere, Unresolvable
from featurelifted.jsonschema import (
    DRAFT202012,
    DRAFT201909,
    DRAFT7,
    DRAFT6,
    DRAFT4,
    DRAFT3,
    UnknownDialect,
    specification_with,
)

__all__ = [
    "Anchor",
    "Registry",
    "Resource",
    "Specification",
    "NoSuchAnchor",
    "PointerToNowhere",
    "Unresolvable",
    "DRAFT202012",
    "DRAFT201909",
    "DRAFT7",
    "DRAFT6",
    "DRAFT4",
    "DRAFT3",
    "UnknownDialect",
    "specification_with",
]
'''


def build_referencing(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, REFERENCING_CORE_FILES, package="referencing")
    write_init(output, REFERENCING_INIT)


def build_referencing_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files = _discover_package_files(repo_root, "referencing")
    tests_root = repo_root / "referencing" / "tests"
    if tests_root.is_dir():
        for path in sorted(tests_root.rglob("*.py")):
            rel = path.relative_to(repo_root).as_posix()
            if rel not in rel_files:
                rel_files.append(rel)
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, rel_files, package="referencing")
    write_init(output, REFERENCING_INIT)


WSPROTO_FRAME_CORE_FILES = [
    "wsproto/frame_protocol.py",
    "wsproto/extensions.py",
    "wsproto/events.py",
    "wsproto/utilities.py",
    "wsproto/typing.py",
]

WSPROTO_FRAME_INIT = '''\
"""WebSocket frame protocol core."""

from featurelifted.frame_protocol import CloseReason, Frame, FrameProtocol, Opcode, ParseFailed

__all__ = [
    "FrameProtocol",
    "Opcode",
    "ParseFailed",
    "CloseReason",
    "Frame",
]
'''


def build_wsproto_frame(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, WSPROTO_FRAME_CORE_FILES, package="wsproto")
    write_init(output, WSPROTO_FRAME_INIT)


def build_wsproto_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    wsproto_files = _discover_package_files(repo_root, "wsproto")
    h11_files = _discover_package_files(repo_root, "h11")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, wsproto_files, package="wsproto")
    pkg_root = output / "featurelifted"
    for rel in h11_files:
        src = repo_root / rel
        dst = pkg_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(rewrite_source(src.read_text(encoding="utf-8"), "h11"), encoding="utf-8")
    write_init(output, WSPROTO_FRAME_INIT)


ASTROID_ORACLE_SKIP_PARTS = frozenset({"brain", "__pycache__", "contrib"})
ASTROID_ORACLE_SKIP_FILES = frozenset(
    {
        "inference.py",
        "test_utils.py",
    }
)


def _astroid_oracle_files(repo_root: Path) -> list[str]:
    rel_files: list[str] = []
    package_root = repo_root / "astroid"
    for path in sorted(package_root.rglob("*.py")):
        rel = path.relative_to(repo_root).as_posix()
        if any(part in ASTROID_ORACLE_SKIP_PARTS for part in Path(rel).parts):
            continue
        if path.name in ASTROID_ORACLE_SKIP_FILES:
            continue
        if rel == "astroid/__init__.py":
            continue
        rel_files.append(rel)
    return rel_files


def _patch_astroid_manager(text: str) -> str:
    text = text.replace(
        "from astroid.interpreter._import import spec, util\n",
        "",
    )
    text = text.replace(
        "        from astroid.inference_tip import clear_inference_tip_cache\n"
        "        from astroid.interpreter.objectmodel import ObjectModel\n",
        "        from astroid.inference_tip import clear_inference_tip_cache\n",
    )
    return text


def _patch_astroid_modutils(text: str) -> str:
    import_line = "from featurelifted.interpreter._import import spec, util\n"
    if import_line not in text:
        return text
    text = text.replace(import_line, "")
    marker = "EXT_LIB_DIRS = {sysconfig.get_path(\"purelib\"), sysconfig.get_path(\"platlib\")}\n"
    if marker in text:
        text = text.replace(marker, marker + import_line)
    else:
        text += "\n" + import_line
    return text


ASTROID_NODES_INIT = '''\
"""Astroid parse and nodes subset."""

from featurelifted.nodes import node_classes, scoped_nodes  # noqa: F401

from featurelifted.builder import extract_node, parse
from featurelifted import nodes
from featurelifted.nodes import (
    AsyncFunctionDef,
    ClassDef,
    FunctionDef,
    Match,
    Module,
    NodeNG,
)

__all__ = [
    "parse",
    "extract_node",
    "nodes",
    "Module",
    "ClassDef",
    "FunctionDef",
    "AsyncFunctionDef",
    "Match",
    "NodeNG",
]
'''


def build_astroid_nodes(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files = _astroid_oracle_files(repo_root)
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, rel_files, package="astroid")
    manager = output / "featurelifted" / "manager.py"
    manager.write_text(_patch_astroid_manager(manager.read_text(encoding="utf-8")), encoding="utf-8")
    modutils = output / "featurelifted" / "modutils.py"
    modutils.write_text(_patch_astroid_modutils(modutils.read_text(encoding="utf-8")), encoding="utf-8")
    write_init(output, ASTROID_NODES_INIT)


def build_astroid_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files = _discover_package_files(repo_root, "astroid")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, rel_files, package="astroid")
    manager = output / "featurelifted" / "manager.py"
    if manager.is_file():
        manager.write_text(_patch_astroid_manager(manager.read_text(encoding="utf-8")), encoding="utf-8")
    modutils = output / "featurelifted" / "modutils.py"
    if modutils.is_file():
        modutils.write_text(_patch_astroid_modutils(modutils.read_text(encoding="utf-8")), encoding="utf-8")
    write_init(output, ASTROID_NODES_INIT)


def build_boltons_iterutils(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, BOLTONS_ITERUTILS_CORE, package="boltons")
    write_init(output, BOLTONS_ITERUTILS_INIT)


def build_boltons_iterutils_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files = _discover_package_files(repo_root, "boltons")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, rel_files, package="boltons")
    write_init(output, BOLTONS_ITERUTILS_INIT)


def rewrite_dotted_source(text: str, dotted: str, flat: str = "featurelifted") -> str:
    escaped = re.escape(dotted)
    text = re.sub(rf"^(\s*)from {escaped}\.", rf"\1from {flat}.", text, flags=re.MULTILINE)
    text = re.sub(rf"^(\s*)from {escaped}\b", rf"\1from {flat}", text, flags=re.MULTILINE)
    text = re.sub(rf"^(\s*)import {escaped}\.", rf"\1import {flat}.", text, flags=re.MULTILINE)
    text = re.sub(rf"^(\s*)import {escaped}\b", rf"\1import {flat}", text, flags=re.MULTILINE)
    text = text.replace(f"{dotted}.", f"{flat}.")
    return text


def copy_tree_dotted(
    src_root: Path,
    dst_root: Path,
    rel_paths: list[str],
    *,
    path_prefix: str,
    dotted: str,
) -> None:
    if dst_root.exists():
        shutil.rmtree(dst_root)
    dst_root.mkdir(parents=True, exist_ok=True)
    for rel in rel_paths:
        src = src_root / rel
        if not src.exists():
            raise FileNotFoundError(f"missing source path: {src}")
        dst = dst_root / rel.replace(f"{path_prefix}/", "featurelifted/", 1)
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            continue
        content = rewrite_dotted_source(src.read_text(encoding="utf-8"), dotted)
        dst.write_text(content, encoding="utf-8")
    for rel in rel_paths:
        src = src_root / rel
        if src.is_dir():
            dst = dst_root / rel.replace(f"{path_prefix}/", "featurelifted/", 1)
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            for path in dst.rglob("*.py"):
                path.write_text(
                    rewrite_dotted_source(path.read_text(encoding="utf-8"), dotted),
                    encoding="utf-8",
                )
            for path in dst.rglob("*.txt"):
                if path.suffix == ".txt":
                    continue


BLEACH_SANITIZE_CORE = [
    "bleach/sanitizer.py",
    "bleach/html5lib_shim.py",
    "bleach/utils.py",
    "bleach/_vendor/parse.py",
    "bleach/_vendor/html5lib",
]

BLEACH_SANITIZE_INIT = '''\
"""Bleach HTML sanitizer core."""

from featurelifted.sanitizer import (
    ALLOWED_ATTRIBUTES,
    ALLOWED_PROTOCOLS,
    ALLOWED_STYLES,
    ALLOWED_TAGS,
    Cleaner,
)


def clean(
    text,
    tags=ALLOWED_TAGS,
    attributes=ALLOWED_ATTRIBUTES,
    styles=ALLOWED_STYLES,
    protocols=ALLOWED_PROTOCOLS,
    strip=False,
    strip_comments=True,
):
    cleaner = Cleaner(
        tags=tags,
        attributes=attributes,
        styles=styles,
        protocols=protocols,
        strip=strip,
        strip_comments=strip_comments,
    )
    return cleaner.clean(text)


__all__ = [
    "clean",
    "Cleaner",
    "ALLOWED_TAGS",
    "ALLOWED_ATTRIBUTES",
    "ALLOWED_STYLES",
    "ALLOWED_PROTOCOLS",
]
'''


def build_bleach_sanitize(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, BLEACH_SANITIZE_CORE, package="bleach")
    write_init(output, BLEACH_SANITIZE_INIT)


def build_bleach_sanitize_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files = _discover_package_files(repo_root, "bleach")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, rel_files, package="bleach")
    write_init(output, BLEACH_SANITIZE_INIT)


RUAMEL_YAML_CORE: list[str] = []


def _ruamel_yaml_core_files(repo_root: Path) -> list[str]:
    yaml_root = repo_root / "ruamel" / "yaml"
    return sorted(
        f"ruamel/yaml/{path.name}"
        for path in yaml_root.glob("*.py")
        if path.name != "cyaml.py"
    )

RUAMEL_YAML_INIT = '''\
"""ruamel.yaml round-trip core."""

from featurelifted.comments import CommentedMap, CommentedSeq
from featurelifted.main import YAML, round_trip_dump, round_trip_load

version_info = (0, 18, 6)
__version__ = "0.18.6"

__all__ = [
    "YAML",
    "round_trip_load",
    "round_trip_dump",
    "CommentedMap",
    "CommentedSeq",
    "version_info",
    "__version__",
]
'''


def build_ruamel_yaml_roundtrip(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    manifest_path = task_dir / "evaluation" / "oracle_manifest.json"
    rel_files = _ruamel_yaml_core_files(repo_root)
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        rel_files = manifest.get("required_source_files") or rel_files
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree_dotted(repo_root, output, rel_files, path_prefix="ruamel/yaml", dotted="ruamel.yaml")
    write_init(output, RUAMEL_YAML_INIT)


def build_ruamel_yaml_roundtrip_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files: list[str] = []
    for path in sorted(repo_root.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        rel_files.append(path.relative_to(repo_root).as_posix())
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    for rel in rel_files:
        src = repo_root / rel
        if rel.startswith("ruamel/yaml/"):
            dst_rel = rel.replace("ruamel/yaml/", "featurelifted/", 1)
        elif rel.startswith("ruamel/contrib/yaml_mirror/"):
            dst_rel = rel.replace("ruamel/contrib/yaml_mirror/", "featurelifted/contrib/yaml_mirror/", 1)
        else:
            continue
        dst = output / dst_rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        text = rewrite_dotted_source(src.read_text(encoding="utf-8"), "ruamel.yaml", "featurelifted")
        text = rewrite_source(text, "ruamel")
        dst.write_text(text, encoding="utf-8")
    write_init(output, RUAMEL_YAML_INIT)


MARKDOWN_EXTENSIONS_CORE = [
    "markdown/__init__.py",
    "markdown/__meta__.py",
    "markdown/blockparser.py",
    "markdown/blockprocessors.py",
    "markdown/core.py",
    "markdown/extensions/__init__.py",
    "markdown/extensions/tables.py",
    "markdown/extensions/footnotes.py",
    "markdown/htmlparser.py",
    "markdown/inlinepatterns.py",
    "markdown/postprocessors.py",
    "markdown/preprocessors.py",
    "markdown/serializers.py",
    "markdown/treeprocessors.py",
    "markdown/util.py",
]

MARKDOWN_EXTENSIONS_INIT = '''\
"""Python-Markdown core with tables and footnotes."""

from featurelifted.core import Markdown, markdown, markdownFromFile

__all__ = ["Markdown", "markdown", "markdownFromFile"]
'''


def build_markdown_extensions(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, MARKDOWN_EXTENSIONS_CORE, package="markdown")
    core_path = output / "featurelifted" / "core.py"
    text = core_path.read_text(encoding="utf-8")
    text = text.replace(
        "entry_points = [ep for ep in util.get_installed_extensions() if ep.name == ext_name]",
        "entry_points = []",
    )
    text = text.replace(
        "module = importlib.import_module(ext_name)",
        "ext_name = ext_name if ext_name.startswith('featurelifted.') else 'featurelifted.extensions.' + ext_name.rsplit('.', 1)[-1]\n            module = importlib.import_module(ext_name)",
    )
    core_path.write_text(text, encoding="utf-8")
    write_init(output, MARKDOWN_EXTENSIONS_INIT)


def build_markdown_extensions_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files = _discover_package_files(repo_root, "markdown")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, rel_files, package="markdown")
    core_path = output / "featurelifted" / "core.py"
    if core_path.is_file():
        text = core_path.read_text(encoding="utf-8")
        text = text.replace(
            "entry_points = [ep for ep in util.get_installed_extensions() if ep.name == ext_name]",
            "entry_points = []",
        )
        text = text.replace(
            "module = importlib.import_module(ext_name)",
            "ext_name = ext_name if ext_name.startswith('featurelifted.') else 'featurelifted.extensions.' + ext_name.rsplit('.', 1)[-1]\n            module = importlib.import_module(ext_name)",
        )
        core_path.write_text(text, encoding="utf-8")
    write_init(output, MARKDOWN_EXTENSIONS_INIT)


PARSO_PARSE_CORE = [
    "parso/__init__.py",
    "parso/_compatibility.py",
    "parso/cache.py",
    "parso/file_io.py",
    "parso/grammar.py",
    "parso/normalizer.py",
    "parso/parser.py",
    "parso/tree.py",
    "parso/utils.py",
    "parso/pgen2/__init__.py",
    "parso/pgen2/generator.py",
    "parso/pgen2/grammar_parser.py",
    "parso/python/__init__.py",
    "parso/python/errors.py",
    "parso/python/grammar310.txt",
    "parso/python/grammar311.txt",
    "parso/python/grammar312.txt",
    "parso/python/grammar36.txt",
    "parso/python/grammar37.txt",
    "parso/python/grammar38.txt",
    "parso/python/grammar39.txt",
    "parso/python/parser.py",
    "parso/python/prefix.py",
    "parso/python/token.py",
    "parso/python/tokenize.py",
    "parso/python/tree.py",
]

PARSO_PARSE_INIT = '''\
"""Parso Python parser core."""

from featurelifted.parser import ParserSyntaxError
from featurelifted.grammar import Grammar, load_grammar
from featurelifted.utils import split_lines, python_bytes_to_unicode


def parse(code=None, **kwargs):
    version = kwargs.pop("version", None)
    grammar = load_grammar(version=version)
    return grammar.parse(code, **kwargs)


__all__ = [
    "parse",
    "load_grammar",
    "Grammar",
    "ParserSyntaxError",
    "split_lines",
    "python_bytes_to_unicode",
]
'''


def build_parso_python_parse(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, PARSO_PARSE_CORE, package="parso")
    grammar_path = output / "featurelifted" / "grammar.py"
    text = grammar_path.read_text(encoding="utf-8")
    text = text.replace("from featurelifted.python.diff import DiffParser\n", "")
    text = text.replace("from featurelifted.python import pep8\n", "")
    text = text.replace(
        "    _default_normalizer_config: NormalizerConfig = pep8.PEP8NormalizerConfig()",
        "    _default_normalizer_config: NormalizerConfig | None = None",
    )
    text = text.replace("            diff_parser=DiffParser", "            diff_parser=None")
    grammar_path.write_text(text, encoding="utf-8")
    write_init(output, PARSO_PARSE_INIT)


def _parso_repo_files(repo_root: Path) -> list[str]:
    rel_files: list[str] = []
    for path in sorted(repo_root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix not in {".py", ".txt"}:
            continue
        if "__pycache__" in path.parts:
            continue
        rel_files.append(path.relative_to(repo_root).as_posix())
    return rel_files


def build_parso_python_parse_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files = _parso_repo_files(repo_root)
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    for rel in rel_files:
        src = repo_root / rel
        if rel.startswith("parso/"):
            dst_rel = rel.replace("parso/", "featurelifted/", 1)
            package = "parso"
        elif rel.startswith("parso_extra/"):
            dst_rel = rel.replace("parso_extra/", "featurelifted_extra/", 1)
            package = "parso"
        else:
            continue
        dst = output / dst_rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.suffix == ".py":
            dst.write_text(rewrite_source(src.read_text(encoding="utf-8"), package), encoding="utf-8")
        else:
            shutil.copy2(src, dst)
    grammar_path = output / "featurelifted" / "grammar.py"
    if grammar_path.is_file():
        text = grammar_path.read_text(encoding="utf-8")
        text = text.replace("from featurelifted.python.diff import DiffParser\n", "")
        text = text.replace("from featurelifted.python import pep8\n", "")
        text = text.replace(
            "    _default_normalizer_config: NormalizerConfig = pep8.PEP8NormalizerConfig()",
            "    _default_normalizer_config: NormalizerConfig | None = None",
        )
        text = text.replace("            diff_parser=DiffParser", "            diff_parser=None")
        grammar_path.write_text(text, encoding="utf-8")
    write_init(output, PARSO_PARSE_INIT)


DEEPDIFF_COMPARE_CORE = [
    "deepdiff/diff.py",
    "deepdiff/helper.py",
    "deepdiff/model.py",
    "deepdiff/base.py",
    "deepdiff/path.py",
    "deepdiff/lfucache.py",
    "deepdiff/serialization.py",
    "deepdiff/distance.py",
    "deepdiff/deephash.py",
    "deepdiff/colored_view.py",
    "deepdiff/_multiprocessing.py",
]

DEEPDIFF_COMPARE_INIT = '''\
"""DeepDiff structural comparison core."""

from featurelifted.diff import DeepDiff
from featurelifted.path import extract, parse_path

__all__ = ["DeepDiff", "extract", "parse_path"]
'''


def build_deepdiff_deep_compare(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, DEEPDIFF_COMPARE_CORE, package="deepdiff")
    write_init(output, DEEPDIFF_COMPARE_INIT)


def _ensure_deepdiff_repo_contrib(task_dir: Path) -> None:
    """Add copy-all penalty modules under repo/deepdiff/contrib/."""
    repo_root = task_dir / "repo" / "deepdiff"
    contrib = repo_root / "contrib"
    contrib.mkdir(parents=True, exist_ok=True)
    site = Path("/Users/chz/anaconda3/lib/python3.12/site-packages/deepdiff")
    for name in ("search.py", "delta.py", "commands.py", "serialization.py"):
        src = site / name
        dst = contrib / name
        if src.is_file() and not dst.exists():
            shutil.copy2(src, dst)



def build_deepdiff_deep_compare_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files = _discover_package_files(repo_root, "deepdiff")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, rel_files, package="deepdiff")
    write_init(output, DEEPDIFF_COMPARE_INIT)


HUMANIZE_NATURALTIME_CORE = [
    "humanize/time.py",
    "humanize/i18n.py",
    "humanize/number.py",
    "humanize/_version.py",
]

HUMANIZE_NATURALTIME_INIT = '''\
"""Humanize natural time/delta core."""

from featurelifted.time import (
    naturaldate,
    naturalday,
    naturaldelta,
    naturaltime,
    precisedelta,
)

__all__ = [
    "naturaldate",
    "naturalday",
    "naturaldelta",
    "naturaltime",
    "precisedelta",
]
'''


def build_humanize_naturaltime(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, HUMANIZE_NATURALTIME_CORE, package="humanize")
    write_init(output, HUMANIZE_NATURALTIME_INIT)


def build_humanize_naturaltime_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files = _discover_package_files(repo_root, "humanize")
    locale_root = repo_root / "humanize" / "locale"
    if locale_root.is_dir():
        for path in sorted(locale_root.rglob("*.po")):
            rel = path.relative_to(repo_root).as_posix()
            if rel not in rel_files:
                rel_files.append(rel)
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, rel_files, package="humanize")
    write_init(output, HUMANIZE_NATURALTIME_INIT)


ISODATE_DURATION_CORE = [
    "isodate/duration.py",
    "isodate/isoduration.py",
    "isodate/isoerror.py",
    "isodate/isodatetime.py",
    "isodate/isodates.py",
    "isodate/isotime.py",
    "isodate/isostrf.py",
    "isodate/isotzinfo.py",
    "isodate/tzinfo.py",
]

ISODATE_DURATION_INIT = '''\
"""ISO8601 duration parse/format core."""

from featurelifted.duration import Duration
from featurelifted.isoerror import ISO8601Error
from featurelifted.isoduration import duration_isoformat, parse_duration

__all__ = [
    "Duration",
    "ISO8601Error",
    "duration_isoformat",
    "parse_duration",
]
'''


def build_isodate_duration(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, ISODATE_DURATION_CORE, package="isodate")
    write_init(output, ISODATE_DURATION_INIT)


def build_isodate_duration_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files = _discover_package_files(repo_root, "isodate")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, rel_files, package="isodate")
    write_init(output, ISODATE_DURATION_INIT)


RFC3986_URI_CORE = [
    "rfc3986/uri.py",
    "rfc3986/parseresult.py",
    "rfc3986/api.py",
    "rfc3986/misc.py",
    "rfc3986/normalizers.py",
    "rfc3986/_mixin.py",
    "rfc3986/compat.py",
    "rfc3986/exceptions.py",
    "rfc3986/abnf_regexp.py",
    "rfc3986/builder.py",
    "rfc3986/validators.py",
]

RFC3986_URI_INIT = '''\
"""RFC3986 URI parse/build/normalize core."""

from featurelifted.api import (
    URIReference,
    is_valid_uri,
    normalize_uri,
    uri_reference,
)
from featurelifted.builder import URIBuilder

__all__ = [
    "URIBuilder",
    "URIReference",
    "is_valid_uri",
    "normalize_uri",
    "uri_reference",
]
'''


def build_rfc3986_uri(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, RFC3986_URI_CORE, package="rfc3986")
    _apply_rfc3986_submission_patches(output, oracle=True)
    write_init(output, RFC3986_URI_INIT)


def _apply_rfc3986_submission_patches(output: Path, *, oracle: bool) -> None:
    builder_path = output / "featurelifted" / "builder.py"
    builder_text = builder_path.read_text(encoding="utf-8")
    builder_text = builder_text.replace(
        "from . import uri_reference\n",
        "from featurelifted.api import uri_reference\n",
    )
    builder_path.write_text(builder_text, encoding="utf-8")
    if not oracle:
        return
    api_path = output / "featurelifted" / "api.py"
    text = api_path.read_text(encoding="utf-8")
    text = text.replace("from .iri import IRIReference\n", "")
    text = text.replace(
        "def iri_reference(iri, encoding=\"utf-8\"):\n"
        "    \"\"\"Parse a IRI string into an IRIReference.\n"
        "\n"
        "    This is a convenience function. You could achieve the same end by using\n"
        "    ``IRIReference.from_string(iri)``.\n"
        "\n"
        "    :param str iri: The IRI which needs to be parsed into a reference.\n"
        "    :param str encoding: The encoding of the string provided\n"
        "    :returns: A parsed IRI\n"
        "    :rtype: :class:`IRIReference`\n"
        "    \"\"\"\n"
        "    return IRIReference.from_string(iri, encoding)\n"
        "\n"
        "\n",
        "",
    )
    api_path.write_text(text, encoding="utf-8")


def build_rfc3986_uri_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files = _discover_package_files(repo_root, "rfc3986")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, rel_files, package="rfc3986")
    _apply_rfc3986_submission_patches(output, oracle=False)
    write_init(output, RFC3986_URI_INIT)


PYTHON_BOX_CONFIG_CORE = [
    "box/box.py",
    "box/config_box.py",
    "box/exceptions.py",
]

PYTHON_BOX_CONFIG_INIT = '''\
"""ConfigBox dot-access config core."""

from featurelifted.box import Box
from featurelifted.config_box import ConfigBox
from featurelifted.exceptions import BoxError, BoxKeyError, BoxTypeError, BoxValueError, BoxWarning

__all__ = [
    "Box",
    "ConfigBox",
    "BoxError",
    "BoxKeyError",
    "BoxTypeError",
    "BoxValueError",
    "BoxWarning",
]
'''

BOX_CONVERTERS_STUB = '''\
"""Minimal converters stub for ConfigBox oracle closure."""

BOX_PARAMETERS = {}


def _from_json(*args, **kwargs):
    raise NotImplementedError


def _from_msgpack(*args, **kwargs):
    raise NotImplementedError


def _from_toml(*args, **kwargs):
    raise NotImplementedError


def _from_toon(*args, **kwargs):
    raise NotImplementedError


def _from_yaml(*args, **kwargs):
    raise NotImplementedError


def _to_json(*args, **kwargs):
    raise NotImplementedError


def _to_msgpack(*args, **kwargs):
    raise NotImplementedError


def _to_toml(*args, **kwargs):
    raise NotImplementedError


def _to_toon(*args, **kwargs):
    raise NotImplementedError


def _to_yaml(*args, **kwargs):
    raise NotImplementedError


msgpack_available = False
toon_available = False
toml_read_library = None
toml_write_library = None
yaml_available = False
'''


def _apply_python_box_submission_patches(output: Path) -> None:
    converters = output / "featurelifted" / "converters.py"
    converters.write_text(BOX_CONVERTERS_STUB, encoding="utf-8")
    box_path = output / "featurelifted" / "box.py"
    text = box_path.read_text(encoding="utf-8")
    text = text.replace("import box\n", "import featurelifted as box\n")
    box_path.write_text(text, encoding="utf-8")


def build_python_box_config(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, PYTHON_BOX_CONFIG_CORE, package="box")
    _apply_python_box_submission_patches(output)
    write_init(output, PYTHON_BOX_CONFIG_INIT)


def build_python_box_config_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files = _discover_package_files(repo_root, "box")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, rel_files, package="box")
    box_path = output / "featurelifted" / "box.py"
    text = box_path.read_text(encoding="utf-8")
    text = text.replace("import box\n", "import featurelifted as box\n")
    box_path.write_text(text, encoding="utf-8")
    write_init(output, PYTHON_BOX_CONFIG_INIT)


ARROW_PARSE_FORMAT_CORE = [
    "arrow/parser.py",
    "arrow/formatter.py",
    "arrow/arrow.py",
    "arrow/factory.py",
    "arrow/api.py",
    "arrow/constants.py",
    "arrow/util.py",
    "arrow/locales.py",
]

ARROW_PARSE_FORMAT_INIT = '''\
"""Arrow parse/format/humanize core (English locale)."""

from featurelifted.api import Arrow, get

__all__ = ["Arrow", "get"]
'''


def _trim_arrow_locales(locales_path: Path) -> None:
    lines = locales_path.read_text(encoding="utf-8").splitlines(keepends=True)
    end = 0
    for idx, line in enumerate(lines):
        if line.startswith("class ItalianLocale"):
            end = idx
            break
    if end:
        locales_path.write_text("".join(lines[:end]), encoding="utf-8")


def _apply_arrow_submission_patches(output: Path) -> None:
    locales = output / "featurelifted" / "locales.py"
    if locales.is_file():
        _trim_arrow_locales(locales)


def build_arrow_parse_format(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, ARROW_PARSE_FORMAT_CORE, package="arrow")
    _apply_arrow_submission_patches(output)
    write_init(output, ARROW_PARSE_FORMAT_INIT)


def build_arrow_parse_format_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files = _discover_package_files(repo_root, "arrow")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, rel_files, package="arrow")
    write_init(output, ARROW_PARSE_FORMAT_INIT)


def build_bidict_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files = _discover_package_files(repo_root, "bidict")
    tests_root = repo_root / "tests"
    if tests_root.is_dir():
        for path in sorted(tests_root.rglob("*.py")):
            rel = path.relative_to(repo_root).as_posix()
            if rel not in rel_files:
                rel_files.append(rel)
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, rel_files, package="bidict")
    write_init(output, BIDICT_INIT)


EMAIL_VALIDATOR_CORE_FILES = [
    "email_validator/exceptions.py",
    "email_validator/rfc_constants.py",
    "email_validator/syntax.py",
    "email_validator/types.py",
    "email_validator/validate_email.py",
]

EMAIL_VALIDATOR_INIT = '''\
"""Email syntax validation core (offline, no deliverability)."""

from featurelifted.exceptions import EmailNotValidError, EmailSyntaxError, EmailUndeliverableError
from featurelifted.types import ValidatedEmail
from featurelifted.validate_email import validate_email

__all__ = [
    "validate_email",
    "ValidatedEmail",
    "EmailNotValidError",
    "EmailSyntaxError",
    "EmailUndeliverableError",
    "ALLOW_SMTPUTF8",
    "ALLOW_EMPTY_LOCAL",
    "ALLOW_QUOTED_LOCAL",
    "ALLOW_DOMAIN_LITERAL",
    "ALLOW_DISPLAY_NAME",
    "STRICT",
    "GLOBALLY_DELIVERABLE",
    "CHECK_DELIVERABILITY",
    "TEST_ENVIRONMENT",
    "DEFAULT_TIMEOUT",
    "SPECIAL_USE_DOMAIN_NAMES",
]

ALLOW_SMTPUTF8 = True
ALLOW_EMPTY_LOCAL = False
ALLOW_QUOTED_LOCAL = False
ALLOW_DOMAIN_LITERAL = False
ALLOW_DISPLAY_NAME = False
STRICT = False
GLOBALLY_DELIVERABLE = True
CHECK_DELIVERABILITY = False
TEST_ENVIRONMENT = False
DEFAULT_TIMEOUT = 15

SPECIAL_USE_DOMAIN_NAMES = [
    "arpa",
    "invalid",
    "local",
    "localhost",
    "onion",
    "test",
]
'''


def _patch_email_validator_submission(output: Path) -> None:
    path = output / "featurelifted" / "validate_email.py"
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        "from typing import Optional, TYPE_CHECKING\nimport unicodedata\n\n"
        "from .exceptions import EmailSyntaxError\n"
        "from .types import ValidatedEmail\n"
        "from .syntax import split_email, validate_email_local_part, validate_email_domain_name, validate_email_domain_literal, validate_email_length\n"
        "from .rfc_constants import CASE_INSENSITIVE_MAILBOX_NAMES\n\n"
        "if TYPE_CHECKING:\n"
        "    import dns.resolver\n"
        "    _Resolver = dns.resolver.Resolver\n"
        "else:\n"
        "    _Resolver = object\n",
        "from typing import Any, Optional\nimport unicodedata\n\n"
        "from .exceptions import EmailSyntaxError\n"
        "from .types import ValidatedEmail\n"
        "from .syntax import split_email, validate_email_local_part, validate_email_domain_name, validate_email_domain_literal, validate_email_length\n"
        "from .rfc_constants import CASE_INSENSITIVE_MAILBOX_NAMES\n\n"
        "_Resolver = Any\n",
    )
    text = text.replace(
        "    if check_deliverability and not test_environment:\n"
        "        # Validate the email address's deliverability using DNS\n"
        "        # and update the returned ValidatedEmail object with metadata.\n\n"
        "        if is_domain_literal:\n"
        "            # There is nothing to check --- skip deliverability checks.\n"
        "            return ret\n\n"
        "        # Lazy load `deliverability` as it is slow to import (due to dns.resolver)\n"
        "        from .deliverability import validate_email_deliverability\n"
        "        deliverability_info = validate_email_deliverability(\n"
        "            ret.ascii_domain, ret.domain, timeout, dns_resolver\n"
        "        )\n"
        "        mx = deliverability_info.get(\"mx\")\n"
        "        if mx is not None:\n"
        "            ret.mx = mx\n"
        "        ret.mx_fallback_type = deliverability_info.get(\"mx_fallback_type\")\n",
        "    if check_deliverability and not test_environment:\n"
        "        raise EmailSyntaxError(\n"
        "            \"Deliverability checks are not available in this feature slice; \"\n"
        "            \"pass check_deliverability=False.\"\n"
        "        )\n",
    )
    path.write_text(text, encoding="utf-8")


def build_email_validator(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, EMAIL_VALIDATOR_CORE_FILES, package="email_validator")
    write_init(output, EMAIL_VALIDATOR_INIT)
    _patch_email_validator_submission(output)


def build_email_validator_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files = _discover_package_files(repo_root, "email_validator")
    rel_files = [
        p
        for p in rel_files
        if not p.endswith("/deliverability.py")
        and not p.endswith("/__main__.py")
    ]
    tests_root = repo_root / "tests"
    if tests_root.is_dir():
        for path in sorted(tests_root.rglob("*.py")):
            rel = path.relative_to(repo_root).as_posix()
            if rel not in rel_files:
                rel_files.append(rel)
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, rel_files, package="email_validator")
    write_init(output, EMAIL_VALIDATOR_INIT)
    _patch_email_validator_submission(output)


JSONPOINTER_ESCAPE = '''\
"""RFC 6901 escape helpers."""


def escape(s: str) -> str:
    return s.replace("~", "~0").replace("/", "~1")


def unescape(s: str) -> str:
    return s.replace("~1", "/").replace("~0", "~")
'''

JSONPOINTER_ERRORS = '''\
"""JSON Pointer exceptions."""

_nothing = object()


class JsonPointerException(Exception):
    pass


class EndOfList:
    """Result of accessing element '-' of a list."""

    def __init__(self, list_) -> None:
        self.list_ = list_

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.list_!r})"
'''

JSONPOINTER_INIT = '''\
"""JSON Pointer resolve/set core (RFC 6901)."""

from featurelifted._errors import EndOfList, JsonPointerException, _nothing
from featurelifted._escape import escape, unescape
from featurelifted._pointer import JsonPointer, resolve_pointer, set_pointer

__all__ = [
    "EndOfList",
    "JsonPointer",
    "JsonPointerException",
    "escape",
    "resolve_pointer",
    "set_pointer",
    "unescape",
]
'''


def _jsonpointer_pointer_module(repo_root: Path) -> str:
    src = (repo_root / "jsonpointer.py").read_text(encoding="utf-8")
    start = src.index("import copy")
    body = src[start:]
    cut = body.index("\ndef escape(s):")
    body = body[:cut].rstrip() + "\n"
    body = body.replace(
        "_nothing = object()\n\n\n",
        "",
    )
    body = body.replace(
        "class JsonPointerException(Exception):\n    pass\n\n\nclass EndOfList:\n"
        '    """Result of accessing element "-" of a list"""\n\n'
        "    def __init__(self, list_):\n"
        "        self.list_ = list_\n\n"
        "    def __repr__(self):\n"
        "        return '{cls}({lst})'.format(cls=self.__class__.__name__,\n"
        "                                     lst=repr(self.list_))\n\n\n",
        "",
    )
    return (
        '"""JsonPointer resolution and mutation."""\n\n'
        "from featurelifted._errors import EndOfList, JsonPointerException, _nothing\n"
        "from featurelifted._escape import escape, unescape\n\n"
        + body
    )


DOTENV_PKG = "src/dotenv"

DOTENV_CORE_FILES = [
    "src/dotenv/parser.py",
    "src/dotenv/variables.py",
    "src/dotenv/main.py",
]

DOTENV_INIT = '''\
"""Dotenv file parsing and key management."""

from featurelifted.main import dotenv_values, find_dotenv, get_key, load_dotenv, set_key, unset_key

__all__ = [
    "dotenv_values",
    "find_dotenv",
    "get_key",
    "load_dotenv",
    "set_key",
    "unset_key",
]
'''

DOTENV_COPY_ALL_INIT = '''\
"""Copy-all python-dotenv baseline."""

from featurelifted.main import *  # noqa: F403
from featurelifted.parser import *  # noqa: F403
from featurelifted.variables import *  # noqa: F403
'''


def build_python_dotenv(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, DOTENV_CORE_FILES, package=DOTENV_PKG)
    write_init(output, DOTENV_INIT)


def _rewrite_dotenv_test_imports(text: str) -> str:
    text = rewrite_source(text, "dotenv")
    text = text.replace("import dotenv", "import featurelifted as dotenv")
    text = text.replace("from dotenv.", "from featurelifted.")
    return text


def build_python_dotenv_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files = _discover_package_files(repo_root, "dotenv")
    rel_files = [
        p
        for p in rel_files
        if not p.endswith(("/cli.py", "/ipython.py", "/__main__.py"))
    ]
    tests_root = repo_root / "tests"
    if tests_root.is_dir():
        for path in sorted(tests_root.rglob("*.py")):
            rel = path.relative_to(repo_root).as_posix()
            if rel not in rel_files:
                rel_files.append(rel)
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, rel_files, package=DOTENV_PKG)
    for rel in rel_files:
        if not rel.startswith("tests/") or not rel.endswith(".py"):
            continue
        dst = output / rel.replace("tests/", "featurelifted/tests/", 1)
        if dst.is_file():
            dst.write_text(
                _rewrite_dotenv_test_imports(dst.read_text(encoding="utf-8")),
                encoding="utf-8",
            )
    write_init(output, DOTENV_COPY_ALL_INIT)


def build_jsonpointer(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    write_module(output, "_escape.py", JSONPOINTER_ESCAPE)
    write_module(output, "_errors.py", JSONPOINTER_ERRORS)
    write_module(output, "_pointer.py", _jsonpointer_pointer_module(repo_root))
    write_init(output, JSONPOINTER_INIT)


def _rewrite_jsonpointer_flat_imports(text: str) -> str:
    text = text.replace("from jsonpointer import", "from featurelifted.jsonpointer import")
    text = text.replace("import jsonpointer", "import featurelifted.jsonpointer as jsonpointer")
    return text


def build_jsonpointer_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    pointer_src = (repo_root / "jsonpointer.py").read_text(encoding="utf-8")
    write_module(output, "jsonpointer.py", pointer_src)
    for rel in ("tests.py", "setup.py", "doc/conf.py"):
        src = repo_root / rel
        if not src.is_file():
            continue
        text = _rewrite_jsonpointer_flat_imports(src.read_text(encoding="utf-8"))
        write_module(output, Path(rel).name, text)
    write_init(
        output,
        '"""Copy-all jsonpointer baseline."""\n\nfrom featurelifted.jsonpointer import *  # noqa: F403\n',
    )


YARL_INIT = '''\
"""Yarl URL model core (offline, no aiohttp/network)."""

from featurelifted._query import Query, QueryVariable, SimpleQuery
from featurelifted._url import URL, cache_clear, cache_configure, cache_info

__all__ = (
    "URL",
    "SimpleQuery",
    "QueryVariable",
    "Query",
    "cache_clear",
    "cache_configure",
    "cache_info",
)
'''


def build_yarl(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    paths = [
        "yarl/_parse.py",
        "yarl/_path.py",
        "yarl/_query.py",
        "yarl/_quoters.py",
        "yarl/_quoting.py",
        "yarl/_quoting_py.py",
        "yarl/_url.py",
    ]
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, paths, package="yarl")
    write_init(output, YARL_INIT)


def build_yarl_copy_all(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files = _discover_package_files(repo_root, "yarl")
    tests_root = repo_root / "tests"
    if tests_root.is_dir():
        for path in sorted(tests_root.rglob("*.py")):
            rel = path.relative_to(repo_root).as_posix()
            if rel not in rel_files:
                rel_files.append(rel)
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, rel_files, package="yarl")
    write_init(output, YARL_INIT)


def build_httpx_copy_all(task_dir: Path, output: Path) -> None:
    """Copy the full HTTPX package for copy-all baseline calibration."""
    repo_root = task_dir / "repo"
    rel_files = _discover_package_files(repo_root, "httpx")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, rel_files, package="httpx")
    write_module(output, "_client_merge.py", HTT_CLIENT_MERGE)
    write_init(output, HTT_INIT)
    models_path = output / "featurelifted" / "_models.py"
    if models_path.is_file():
        models_path.write_text(
            _trim_httpx_models(models_path.read_text(encoding="utf-8")),
            encoding="utf-8",
        )
    content_path = output / "featurelifted" / "_content.py"
    if content_path.is_file():
        content_path.write_text(
            _trim_httpx_content(content_path.read_text(encoding="utf-8")),
            encoding="utf-8",
        )
    utils_path = output / "featurelifted" / "_utils.py"
    if utils_path.is_file():
        utils_path.write_text(
            _trim_httpx_utils(utils_path.read_text(encoding="utf-8")),
            encoding="utf-8",
        )


def build_httpx(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    paths = [
        "httpx/_urlparse.py",
        "httpx/_urls.py",
        "httpx/_types.py",
        "httpx/_utils.py",
        "httpx/_exceptions.py",
        "httpx/_content.py",
        "httpx/_multipart.py",
        "httpx/_models.py",
    ]
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, paths, package="httpx")
    models_path = output / "featurelifted" / "_models.py"
    models_path.write_text(
        _trim_httpx_models(models_path.read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    content_path = output / "featurelifted" / "_content.py"
    content_path.write_text(
        _trim_httpx_content(content_path.read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    utils_path = output / "featurelifted" / "_utils.py"
    utils_path.write_text(
        _trim_httpx_utils(utils_path.read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    write_module(output, "_client_merge.py", HTT_CLIENT_MERGE)
    write_init(output, HTT_INIT)


def build_h11(task_dir: Path, output: Path) -> None:
    repo_pkg = task_dir / "repo" / "h11"
    if not repo_pkg.is_dir():
        raise SystemExit(f"missing repo snapshot: {repo_pkg}")
    paths = _discover_package_paths(task_dir / "repo", "h11")
    copy_tree(task_dir / "repo", output, paths, package="h11")
    write_init(output, H11_INIT)


def build_redis(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    paths = [
        "redis/_parsers/__init__.py",
        "redis/_parsers/resp2.py",
        "redis/_parsers/resp3.py",
        "redis/_parsers/encoders.py",
        "redis/_parsers/socket.py",
        "redis/exceptions.py",
        "redis/typing.py",
    ]
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(repo_root, output, paths, package="redis")
    write_module(output, "utils.py", REDIS_UTILS_MINIMAL)
    write_module(output, "_parsers/base.py", REDIS_PARSER_BASE)
    write_init(output, REDIS_PARSER_INIT)
    parsers_init = output / "featurelifted" / "_parsers" / "__init__.py"
    parsers_init.write_text(
        "from featurelifted._parsers.base import BaseParser, PushNotificationsParser, _RESPBase\n"
        "from featurelifted._parsers.encoders import Encoder\n"
        "from featurelifted._parsers.resp2 import _RESP2Parser\n"
        "from featurelifted._parsers.resp3 import _RESP3Parser\n\n"
        '__all__ = ["BaseParser", "Encoder", "_RESP2Parser", "_RESP3Parser", "PushNotificationsParser"]\n',
        encoding="utf-8",
    )
    resp3_path = output / "featurelifted" / "_parsers" / "resp3.py"
    resp3_text = resp3_path.read_text(encoding="utf-8")
    resp3_text = resp3_text.replace(
        "from .base import (\n    AsyncPushNotificationsParser,\n    PushNotificationsParser,\n    _AsyncRESPBase,\n    _RESPBase,\n)",
        "from .base import PushNotificationsParser, _RESPBase",
    )
    if "class _AsyncRESP3Parser" in resp3_text:
        resp3_text = resp3_text.split("class _AsyncRESP3Parser", 1)[0].rstrip() + "\n"
    resp3_path.write_text(resp3_text, encoding="utf-8")
    resp2_path = output / "featurelifted" / "_parsers" / "resp2.py"
    resp2_text = resp2_path.read_text(encoding="utf-8")
    resp2_text = resp2_text.replace(
        "from .base import _AsyncRESPBase, _RESPBase",
        "from .base import _RESPBase",
    )
    if "class _AsyncRESP2Parser" in resp2_text:
        resp2_text = resp2_text.split("class _AsyncRESP2Parser", 1)[0].rstrip() + "\n"
    resp2_path.write_text(resp2_text, encoding="utf-8")


MANIFEST_TASK_PACKAGES = {
    "iniconfig__parse_config__001": "iniconfig",
    "python_slugify__slugify_core__001": "slugify",
    "python_pathspec__gitignore_match__001": "pathspec",
    "tomlkit__roundtrip_document__001": "tomlkit",
    "pyyaml__safe_load_dump__001": "yaml",
    "pluggy__hook_call_order__001": "pluggy",
    "packaging__requirement_marker_specifier__001": "packaging",
    "markdown_it__commonmark_render__001": "markdown_it",
    "click__option_parser__001": "click",
    "jsonschema__validator_core__001": "jsonschema",
    "faker__provider_core__001": "faker",
    "lark__grammar_loader_core__001": "lark",
    "rich__markup_parse_core__001": "rich",
    "marshmallow__schema_core__001": "marshmallow",
    "babel__plural_core__001": "babel",
    "pluggy__hook_specs_core__001": "pluggy",
    "networkx__dag_topo_core__001": "networkx",
    "json5__parse_core__001": "json5",
}

EXCLUDED_PATH_PARTS = frozenset(
    {
        "tests",
        "testing",
        "benchmarks",
        "__pycache__",
        ".github",
        ".vscode",
        "cli",
    }
)


def _append_repo_test_files(repo_root: Path, rel_files: list[str]) -> None:
    """Include upstream test modules in copy-all baselines (not runtime package)."""
    for path in sorted(repo_root.rglob("*.py")):
        rel = path.relative_to(repo_root).as_posix()
        parts = set(Path(rel).parts)
        if not (parts & {"tests", "testing", "test"}):
            continue
        if rel not in rel_files:
            rel_files.append(rel)


def _find_package_root(repo_root: Path, package: str) -> Path:
    for candidate in (repo_root / package, repo_root / "src" / package):
        if candidate.is_dir():
            return candidate
    raise FileNotFoundError(f"package directory not found for {package!r} under {repo_root}")


def _discover_package_files(repo_root: Path, package: str) -> list[str]:
    package_root = _find_package_root(repo_root, package)
    rel_files: list[str] = []
    for path in sorted(package_root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix not in {".py", ".typed", ".pyi"}:
            continue
        rel = path.relative_to(repo_root).as_posix()
        if any(part in EXCLUDED_PATH_PARTS for part in Path(rel).parts):
            continue
        rel_files.append(rel)
    return rel_files


def _load_manifest(task_dir: Path) -> tuple[list[str], str]:
    manifest_path = task_dir / "evaluation" / "oracle_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    package = manifest.get("source_package_name") or MANIFEST_TASK_PACKAGES.get(task_dir.name, "")
    rel_files = manifest.get("required_source_files") or manifest.get("source_files") or []
    if not package:
        metadata = json.loads((task_dir / "metadata.json").read_text(encoding="utf-8"))
        source = metadata.get("source", {})
        if isinstance(source, dict):
            package = str(source.get("name", "")).replace("-", "_")
            if package == "PyYAML":
                package = "yaml"
            if package == "markdown-it-py":
                package = "markdown_it"
            if package == "python-pathspec":
                package = "pathspec"
            if package == "python-slugify":
                package = "slugify"
    if not rel_files:
        rel_files = _discover_package_files(task_dir / "repo", package)
    return rel_files, package


def _destination_rel_path(rel_path: str, package: str) -> Path:
    parts = Path(rel_path).parts
    if package not in parts:
        raise ValueError(f"package {package!r} not found in manifest path {rel_path!r}")
    idx = parts.index(package)
    subpath = Path(*parts[idx + 1 :])
    return Path("featurelifted") / subpath


def build_from_manifest(task_dir: Path, output: Path) -> None:
    repo_root = task_dir / "repo"
    rel_files, package = _load_manifest(task_dir)
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)

    for rel in rel_files:
        src = repo_root / rel
        if not src.exists():
            raise FileNotFoundError(f"missing source path: {src}")
        dst = output / _destination_rel_path(rel, package)
        if src.is_dir():
            dst.mkdir(parents=True, exist_ok=True)
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.suffix == ".py":
            content = rewrite_source(src.read_text(encoding="utf-8"), package)
            dst.write_text(content, encoding="utf-8")
        elif src.suffix in {".dat"}:
            shutil.copy2(src, dst)
        else:
            dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    for path in output.rglob("*.py"):
        path.write_text(rewrite_source(path.read_text(encoding="utf-8"), package), encoding="utf-8")

    post_process = MANIFEST_POST_PROCESS.get(task_dir.name)
    if post_process:
        post_process(output)


def _patch_packaging_public_exports(output: Path) -> None:
    init_path = output / "featurelifted" / "__init__.py"
    base = init_path.read_text(encoding="utf-8")
    exports = (
        "\nfrom featurelifted.markers import InvalidMarker, Marker, default_environment\n"
        "from featurelifted.requirements import InvalidRequirement, Requirement\n"
        "from featurelifted.specifiers import InvalidSpecifier, Specifier, SpecifierSet\n"
        "from featurelifted.version import InvalidVersion, Version\n"
    )
    init_path.write_text(base.rstrip() + exports, encoding="utf-8")


def _patch_pathspec_public_exports(output: Path) -> None:
    init_path = output / "featurelifted" / "__init__.py"
    base = init_path.read_text(encoding="utf-8")
    exports = (
        "\nfrom featurelifted.patterns.gitignore.base import GitIgnorePatternError\n"
    )
    init_path.write_text(base.rstrip() + exports, encoding="utf-8")


def _patch_coverage_report_imports(output: Path) -> None:
    path = output / "featurelifted" / "xmlreport.py"
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        "from featurelifted import __version__, files",
        "from featurelifted.version import __version__\nfrom featurelifted import files",
    )
    path.write_text(text, encoding="utf-8")


FAKER_CONFIG = '''\
from importlib import import_module

DEFAULT_LOCALE = "en_US"

META_PROVIDERS_MODULES = [
    "featurelifted.providers",
]

PROVIDERS = [
    "featurelifted.providers.person",
    "featurelifted.providers.address",
    "featurelifted.providers.phone_number",
]

AVAILABLE_LOCALES = ["en_US"]
'''

FAKER_INIT = '''\
"""Faker en_US person/address/phone providers."""

from featurelifted.proxy import Faker

__all__ = ["Faker"]
'''

MARSHMALLOW_INIT = '''\
"""Marshmallow schema load/dump core."""

from featurelifted.constants import EXCLUDE, INCLUDE, RAISE, missing
from featurelifted.decorators import (
    post_dump,
    post_load,
    pre_dump,
    pre_load,
    validates,
    validates_schema,
)
from featurelifted.exceptions import ValidationError
from featurelifted.schema import Schema, SchemaOpts

from . import fields

__all__ = [
    "EXCLUDE",
    "INCLUDE",
    "RAISE",
    "Schema",
    "SchemaOpts",
    "ValidationError",
    "fields",
    "missing",
    "post_dump",
    "post_load",
    "pre_dump",
    "pre_load",
    "validates",
    "validates_schema",
]
'''

BABEL_INIT = '''\
"""Babel plural rules subset."""

from featurelifted.core import Locale
from featurelifted.plural import PluralRule

__all__ = ["Locale", "PluralRule"]
'''


def _patch_faker_oracle(output: Path) -> None:
    (output / "featurelifted" / "config.py").write_text(FAKER_CONFIG, encoding="utf-8")
    write_init(output, FAKER_INIT)


def _patch_marshmallow_oracle(output: Path) -> None:
    write_init(output, MARSHMALLOW_INIT)


def _patch_babel_oracle(output: Path) -> None:
    localedata = output / "featurelifted" / "localedata.py"
    text = localedata.read_text(encoding="utf-8")
    if "_is_locale_alias" not in text:
        text = text.replace(
            "def merge(dict1, dict2):",
            "def _is_locale_alias(obj):\n"
            "    return getattr(type(obj), '__name__', None) == 'Alias' and hasattr(obj, 'keys')\n\n\n"
            "def merge(dict1, dict2):",
        )
        text = text.replace("isinstance(val1, Alias)", "_is_locale_alias(val1)")
        text = text.replace("isinstance(data, Alias)", "_is_locale_alias(data)")
        text = text.replace("isinstance(val, Alias)", "_is_locale_alias(val)")
        localedata.write_text(text, encoding="utf-8")
    write_init(output, BABEL_INIT)


MANIFEST_POST_PROCESS = {
    "packaging__requirement_marker_specifier__001": _patch_packaging_public_exports,
    "python_pathspec__gitignore_match__001": _patch_pathspec_public_exports,
    "coverage__report_core__001": _patch_coverage_report_imports,
    "faker__provider_core__001": _patch_faker_oracle,
    "marshmallow__schema_core__001": _patch_marshmallow_oracle,
    "babel__plural_core__001": _patch_babel_oracle,
}


TASK_PROFILES = {
    "sqlparse__parse_format_core__001": "parse_format",
    "sqlparse__parse_split_core__001": "parse_split",
    "sqlparse__token_tree_core__001": "token_tree",
    "sqlparse__format_filters_core__001": "format_filters",
    "coverage__glob_matcher_core__001": "glob_matcher",
    "coverage__config_merge_core__001": "config_merge",
    "coverage__source_selection_core__001": "source_selection",
    "coverage__path_remap_core__001": "path_remap",
    "coverage__report_core__001": "report_core",
    "jinja2__lexer_parser_core__001": "lexer_parser",
    "jinja2__compile_render_core__001": "compile_render",
    "jinja2__loader_inheritance_core__001": "loader_inheritance",
    "jinja2__filters_tests_core__001": "filters_tests",
    "jinja2__extensions_core__001": "extensions",
    "pytest__mark_expression_core__001": "mark_expression",
    "pytest__skipif_eval_core__001": "skipif_eval",
    "pytest__ini_markers_core__001": "ini_markers",
    "pytest__fixture_resolve_core__001": "fixture_resolve",
    "vibe_app__pricing_rules_core__001": "pricing_rules",
    "vibe_app__yaml_config_bootstrap__001": "yaml_config",
    "vibe_app__csv_transform_core__001": "csv_transform",
    "vibe_app__rules_engine_core__001": "rules_engine",
    "vibe_app__session_registry_core__001": "session_registry",
    "vibe_app__orm_query_ast_core__001": "orm_query",
    "vibe_app__plugin_registry_core__001": "plugin_registry",
    "pygments__lexer_core__001": "lexer_core",
    "pygments__formatter_core__001": "formatter_core",
    "lark__parse_tree_core__001": "parse_tree_core",
    "lark__visitor_transform_core__001": "visitor_transform_core",
    "attrs__validators_core__001": "validators_core",
    "werkzeug__routing_core__001": "routing",
    "typer__command_parser_core__001": "command_parser",
    "importlib_metadata__entry_points_core__001": "entry_points",
    "h11__message_parse_core__001": "message_parse",
    "redis__resp_parser_core__001": "resp_parser",
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task_dir", type=Path)
    parser.add_argument(
        "--profile",
        default=None,
        choices=[
            "parse_format",
            "parse_split",
            "token_tree",
            "format_filters",
            "glob_matcher",
            "config_merge",
            "source_selection",
            "path_remap",
            "report_core",
            "lexer_parser",
            "compile_render",
            "loader_inheritance",
            "filters_tests",
            "extensions",
            "mark_expression",
            "skipif_eval",
            "ini_markers",
            "fixture_resolve",
            "pricing_rules",
            "yaml_config",
            "csv_transform",
            "rules_engine",
            "session_registry",
            "orm_query",
            "plugin_registry",
            "lexer_core",
            "formatter_core",
            "parse_tree_core",
            "visitor_transform_core",
            "validators_core",
            "routing",
            "command_parser",
            "entry_points",
            "message_parse",
            "resp_parser",
        ],
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Submission root (default: benchmark/submissions/<task_id>/oracle)",
    )
    parser.add_argument(
        "--variant",
        choices=["oracle", "copy_all"],
        default="oracle",
        help="Submission variant (default: oracle compact closure)",
    )
    args = parser.parse_args()
    task_dir = args.task_dir.resolve()
    task_id = task_dir.name
    if args.output is not None:
        output = args.output.resolve()
    else:
        subdir = "copy_all" if args.variant == "copy_all" else "oracle"
        output = (SUBMISSIONS_DIR / task_id / subdir).resolve()

    if task_id in MANIFEST_TASK_PACKAGES:
        build_from_manifest(task_dir, output)
        print(f"Wrote oracle submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("jsonpath_ng__"):
        if output.name == "copy_all" or args.variant == "copy_all":
            build_jsonpath_ng_copy_all(task_dir, output)
        else:
            build_jsonpath_ng(task_dir, output)
        print(f"Wrote submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("configobj__"):
        if output.name == "copy_all" or args.variant == "copy_all":
            build_configobj_copy_all(task_dir, output)
        else:
            build_configobj(task_dir, output)
        print(f"Wrote submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("websockets__"):
        if output.name == "copy_all" or args.variant == "copy_all":
            build_websockets_copy_all(task_dir, output)
        else:
            build_websockets(task_dir, output)
        print(f"Wrote submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("croniter__"):
        if output.name == "copy_all" or args.variant == "copy_all":
            build_croniter_copy_all(task_dir, output)
        else:
            build_croniter(task_dir, output)
        print(f"Wrote submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("mako__"):
        if output.name == "copy_all" or args.variant == "copy_all":
            build_mako_copy_all(task_dir, output)
        else:
            build_mako(task_dir, output)
        print(f"Wrote submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("voluptuous__"):
        if output.name == "copy_all" or args.variant == "copy_all":
            build_voluptuous_copy_all(task_dir, output)
        else:
            build_voluptuous(task_dir, output)
        print(f"Wrote submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("sortedcontainers__"):
        if output.name == "copy_all" or args.variant == "copy_all":
            build_sortedcontainers_copy_all(task_dir, output)
        else:
            build_sortedcontainers(task_dir, output)
        print(f"Wrote submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("cerberus__"):
        if output.name == "copy_all" or args.variant == "copy_all":
            build_cerberus_copy_all(task_dir, output)
        else:
            build_cerberus(task_dir, output)
        print(f"Wrote submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("dataclasses_json__"):
        if output.name == "copy_all" or args.variant == "copy_all":
            build_dataclasses_json_copy_all(task_dir, output)
        else:
            build_dataclasses_json(task_dir, output)
        print(f"Wrote submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("cattrs__"):
        if output.name == "copy_all" or args.variant == "copy_all":
            build_cattrs_copy_all(task_dir, output)
        else:
            build_cattrs(task_dir, output)
        print(f"Wrote oracle submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("python_multipart__"):
        if output.name == "copy_all" or args.variant == "copy_all":
            build_python_multipart_copy_all(task_dir, output)
        else:
            build_python_multipart(task_dir, output)
        print(f"Wrote submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("xmltodict__"):
        if output.name == "copy_all":
            build_xmltodict_copy_all(task_dir, output)
        else:
            build_xmltodict(task_dir, output)
        print(f"Wrote oracle submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("msgpack__"):
        if output.name == "copy_all" or args.variant == "copy_all":
            build_msgpack_copy_all(task_dir, output)
        else:
            build_msgpack(task_dir, output)
        print(f"Wrote submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("python_frontmatter__"):
        if output.name == "copy_all" or args.variant == "copy_all":
            build_python_frontmatter_copy_all(task_dir, output)
        else:
            build_python_frontmatter(task_dir, output)
        print(f"Wrote submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("urllib3__"):
        if output.name == "copy_all":
            build_urllib3_copy_all(task_dir, output)
        else:
            build_urllib3_retry(task_dir, output)
        print(f"Wrote oracle submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("intervaltree__"):
        if output.name == "copy_all" or args.variant == "copy_all":
            build_intervaltree_copy_all(task_dir, output)
        else:
            build_intervaltree(task_dir, output)
        print(f"Wrote submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("bidict__"):
        if output.name == "copy_all":
            build_bidict_copy_all(task_dir, output)
        else:
            build_bidict(task_dir, output)
        print(f"Wrote oracle submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("environs__"):
        if output.name == "copy_all":
            build_environs_copy_all(task_dir, output)
        else:
            build_environs(task_dir, output)
        print(f"Wrote oracle submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("cachetools__"):
        if output.name == "copy_all":
            build_cachetools_copy_all(task_dir, output)
        else:
            build_cachetools(task_dir, output)
        print(f"Wrote oracle submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("email_validator__"):
        if output.name == "copy_all":
            build_email_validator_copy_all(task_dir, output)
        else:
            build_email_validator(task_dir, output)
        print(f"Wrote oracle submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("tabulate__"):
        if output.name == "copy_all" or args.variant == "copy_all":
            build_tabulate_copy_all(task_dir, output)
        else:
            build_tabulate(task_dir, output)
        print(f"Wrote submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("pathvalidate__"):
        if output.name == "copy_all" or args.variant == "copy_all":
            build_pathvalidate_copy_all(task_dir, output)
        else:
            build_pathvalidate(task_dir, output)
        print(f"Wrote submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("python_dotenv__"):
        if output.name == "copy_all" or args.variant == "copy_all":
            build_python_dotenv_copy_all(task_dir, output)
        else:
            build_python_dotenv(task_dir, output)
        print(f"Wrote submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("jsonpointer__"):
        if output.name == "copy_all":
            build_jsonpointer_copy_all(task_dir, output)
        else:
            build_jsonpointer(task_dir, output)
        print(f"Wrote oracle submission to {output / 'featurelifted'}")
        return

    if task_id == "python_dateutil__relativedelta_core__001":
        if output.name == "copy_all" or args.variant == "copy_all":
            build_dateutil_relativedelta_copy_all(task_dir, output)
        else:
            build_dateutil_relativedelta(task_dir, output)
        print(f"Wrote submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("python_dateutil__"):
        if output.name == "copy_all" or args.variant == "copy_all":
            build_dateutil_copy_all(task_dir, output)
        else:
            build_dateutil(task_dir, output)
        print(f"Wrote submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("pendulum__"):
        if output.name == "copy_all" or args.variant == "copy_all":
            build_pendulum_copy_all(task_dir, output)
        else:
            build_pendulum(task_dir, output)
        print(f"Wrote submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("boltons__iterutils"):
        if output.name == "copy_all" or args.variant == "copy_all":
            build_boltons_iterutils_copy_all(task_dir, output)
        else:
            build_boltons_iterutils(task_dir, output)
        print(f"Wrote submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("h2__frame_parse"):
        if output.name == "copy_all" or args.variant == "copy_all":
            build_h2_frame_copy_all(task_dir, output)
        else:
            build_h2_frame(task_dir, output)
        print(f"Wrote submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("referencing__json_schema_refs"):
        if output.name == "copy_all" or args.variant == "copy_all":
            build_referencing_copy_all(task_dir, output)
        else:
            build_referencing(task_dir, output)
        print(f"Wrote submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("wsproto__frame_parse"):
        if output.name == "copy_all" or args.variant == "copy_all":
            build_wsproto_copy_all(task_dir, output)
        else:
            build_wsproto_frame(task_dir, output)
        print(f"Wrote submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("astroid__nodes"):
        if output.name == "copy_all" or args.variant == "copy_all":
            build_astroid_copy_all(task_dir, output)
        else:
            build_astroid_nodes(task_dir, output)
        print(f"Wrote submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("bleach__sanitize"):
        if output.name == "copy_all" or args.variant == "copy_all":
            build_bleach_sanitize_copy_all(task_dir, output)
        else:
            build_bleach_sanitize(task_dir, output)
        print(f"Wrote submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("ruamel_yaml__roundtrip"):
        if output.name == "copy_all" or args.variant == "copy_all":
            build_ruamel_yaml_roundtrip_copy_all(task_dir, output)
        else:
            build_ruamel_yaml_roundtrip(task_dir, output)
        print(f"Wrote submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("markdown__extensions"):
        if output.name == "copy_all" or args.variant == "copy_all":
            build_markdown_extensions_copy_all(task_dir, output)
        else:
            build_markdown_extensions(task_dir, output)
        print(f"Wrote submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("parso__python_parse"):
        if output.name == "copy_all" or args.variant == "copy_all":
            build_parso_python_parse_copy_all(task_dir, output)
        else:
            build_parso_python_parse(task_dir, output)
        print(f"Wrote submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("deepdiff__deep_compare"):
        if output.name == "copy_all" or args.variant == "copy_all":
            build_deepdiff_deep_compare_copy_all(task_dir, output)
        else:
            build_deepdiff_deep_compare(task_dir, output)
        print(f"Wrote submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("dynaconf__settings_merge"):
        if output.name == "copy_all" or args.variant == "copy_all":
            build_dynaconf_settings_merge_copy_all(task_dir, output)
        else:
            build_dynaconf_settings_merge(task_dir, output)
        print(f"Wrote submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("phonenumbers__parse_format"):
        if output.name == "copy_all" or args.variant == "copy_all":
            build_phonenumbers_parse_format_copy_all(task_dir, output)
        else:
            build_phonenumbers_parse_format(task_dir, output)
        print(f"Wrote submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("passlib__hash_context"):
        if output.name == "copy_all" or args.variant == "copy_all":
            build_passlib_hash_context_copy_all(task_dir, output)
        else:
            build_passlib_hash_context(task_dir, output)
        print(f"Wrote submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("pydantic_settings__env_source"):
        if output.name == "copy_all" or args.variant == "copy_all":
            build_pydantic_settings_env_source_copy_all(task_dir, output)
        else:
            build_pydantic_settings_env_source(task_dir, output)
        print(f"Wrote submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("chameleon__template_compile"):
        if output.name == "copy_all" or args.variant == "copy_all":
            build_chameleon_template_compile_copy_all(task_dir, output)
        else:
            build_chameleon_template_compile(task_dir, output)
        print(f"Wrote submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("humanize__naturaltime"):
        if output.name == "copy_all" or args.variant == "copy_all":
            build_humanize_naturaltime_copy_all(task_dir, output)
        else:
            build_humanize_naturaltime(task_dir, output)
        print(f"Wrote submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("isodate__duration"):
        if output.name == "copy_all" or args.variant == "copy_all":
            build_isodate_duration_copy_all(task_dir, output)
        else:
            build_isodate_duration(task_dir, output)
        print(f"Wrote submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("rfc3986__uri"):
        if output.name == "copy_all" or args.variant == "copy_all":
            build_rfc3986_uri_copy_all(task_dir, output)
        else:
            build_rfc3986_uri(task_dir, output)
        print(f"Wrote submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("python_box__config"):
        if output.name == "copy_all" or args.variant == "copy_all":
            build_python_box_config_copy_all(task_dir, output)
        else:
            build_python_box_config(task_dir, output)
        print(f"Wrote submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("arrow__parse_format"):
        if output.name == "copy_all" or args.variant == "copy_all":
            build_arrow_parse_format_copy_all(task_dir, output)
        else:
            build_arrow_parse_format(task_dir, output)
        print(f"Wrote submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("pydantic_v1__"):
        if output.name == "copy_all" or args.variant == "copy_all":
            build_pydantic_copy_all(task_dir, output)
        else:
            build_pydantic(task_dir, output)
        print(f"Wrote submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("httpx__"):
        if output.name == "copy_all" or args.variant == "copy_all":
            build_httpx_copy_all(task_dir, output)
        else:
            build_httpx(task_dir, output)
        print(f"Wrote submission to {output / 'featurelifted'}")
        return

    if task_id.startswith("yarl__"):
        if output.name == "copy_all" or args.variant == "copy_all":
            build_yarl_copy_all(task_dir, output)
        else:
            build_yarl(task_dir, output)
        print(f"Wrote submission to {output / 'featurelifted'}")
        return

    profile = args.profile or TASK_PROFILES.get(task_id)
    if profile is None:
        raise SystemExit(f"unknown task_id, pass --profile explicitly: {task_id}")
    output.mkdir(parents=True, exist_ok=True)

    if task_id.startswith("sqlparse__"):
        build_sqlparse(task_dir, profile, output)
    elif task_id.startswith("coverage__"):
        build_coverage(task_dir, profile, output)
    elif task_id.startswith("vibe_app__"):
        build_vibe_app(task_dir, profile, output)
    elif task_id.startswith("jinja2__"):
        build_jinja2(task_dir, profile, output)
    elif task_id.startswith("pytest__"):
        build_pytest(task_dir, profile, output)
    elif task_id.startswith("pygments__"):
        build_pygments(task_dir, profile, output)
    elif task_id.startswith("lark__"):
        build_lark(task_dir, profile, output)
    elif task_id.startswith("attrs__"):
        build_attrs(task_dir, profile, output)
    elif task_id.startswith("werkzeug__"):
        build_werkzeug(task_dir, output)
    elif task_id.startswith("typer__"):
        build_typer(task_dir, output)
    elif task_id.startswith("importlib_metadata__"):
        build_importlib_metadata(task_dir, output)
    elif task_id.startswith("h11__"):
        build_h11(task_dir, output)
    elif task_id.startswith("redis__"):
        build_redis(task_dir, output)
    else:
        raise SystemExit(f"unsupported task family for auto-oracle: {task_id}")

    print(f"Wrote oracle submission to {output / 'featurelifted'}")


if __name__ == "__main__":
    main()
