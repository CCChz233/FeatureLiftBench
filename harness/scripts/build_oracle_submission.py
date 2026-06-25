#!/usr/bin/env python3
"""Build a featurelifted oracle submission by copying modules from a task repo snapshot."""

from __future__ import annotations

import argparse
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
    r"\b(?P<name>sqlparse|coverage|jinja2|_pytest|pytest|vibe_app|werkzeug|typer|importlib_metadata|h11|redis)\b"
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
    args = parser.parse_args()
    task_dir = args.task_dir.resolve()
    task_id = task_dir.name
    output = args.output or SUBMISSIONS_DIR / task_id / "oracle"
    output = output.resolve()

    if task_id in MANIFEST_TASK_PACKAGES:
        build_from_manifest(task_dir, output)
        print(f"Wrote oracle submission to {output / 'featurelifted'}")
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
