#!/usr/bin/env python3
"""Build a featurelifted oracle submission by copying modules from a task repo snapshot."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "harness") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "harness"))

from featureliftbench.paths import SUBMISSIONS_DIR, VENDOR_WHEELS_DIR

IMPORT_RE = re.compile(
    r"\b(?P<name>sqlparse|coverage|jinja2|_pytest|pytest|vibe_app)\b"
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
    else:
        raise SystemExit(f"unknown coverage profile: {profile}")

    copy_tree(task_dir / "repo", output, paths, package="coverage")
    write_init(output, init)
    if profile == "source_selection":
        write_python_minimal(output)


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
    else:
        raise SystemExit(f"unknown pytest profile: {profile}")


TASK_PROFILES = {
    "sqlparse__parse_format_core__001": "parse_format",
    "sqlparse__parse_split_core__001": "parse_split",
    "sqlparse__token_tree_core__001": "token_tree",
    "sqlparse__format_filters_core__001": "format_filters",
    "coverage__glob_matcher_core__001": "glob_matcher",
    "coverage__config_merge_core__001": "config_merge",
    "coverage__source_selection_core__001": "source_selection",
    "coverage__path_remap_core__001": "path_remap",
    "jinja2__lexer_parser_core__001": "lexer_parser",
    "jinja2__compile_render_core__001": "compile_render",
    "jinja2__loader_inheritance_core__001": "loader_inheritance",
    "jinja2__filters_tests_core__001": "filters_tests",
    "pytest__mark_expression_core__001": "mark_expression",
    "pytest__skipif_eval_core__001": "skipif_eval",
    "pytest__ini_markers_core__001": "ini_markers",
    "vibe_app__pricing_rules_core__001": "pricing_rules",
    "vibe_app__yaml_config_bootstrap__001": "yaml_config",
    "vibe_app__csv_transform_core__001": "csv_transform",
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
            "lexer_parser",
            "compile_render",
            "loader_inheritance",
            "filters_tests",
            "mark_expression",
            "skipif_eval",
            "ini_markers",
            "pricing_rules",
            "yaml_config",
            "csv_transform",
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
    profile = args.profile or TASK_PROFILES.get(task_id)
    if profile is None:
        raise SystemExit(f"unknown task_id, pass --profile explicitly: {task_id}")
    output = args.output or SUBMISSIONS_DIR / task_id / "oracle"
    output = output.resolve()
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
    else:
        raise SystemExit(f"unsupported task family for auto-oracle: {task_id}")

    print(f"Wrote oracle submission to {output / 'featurelifted'}")


if __name__ == "__main__":
    main()
