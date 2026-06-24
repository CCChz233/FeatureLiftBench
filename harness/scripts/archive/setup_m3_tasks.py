#!/usr/bin/env python3
"""Scaffold M3 Extreme tasks: jinja2 x4 + pytest x3."""

from __future__ import annotations

import json
import shutil
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
JINJA_SRC = Path("/tmp/flb-clones/jinja")
PYTEST_SRC = Path("/tmp/flb-clones/pytest")

JINJA_COMMIT = "15206881c006c79667fe5154fe80c01c65410679"
PYTEST_COMMIT = "b55ab2aabb68c0ce94c3903139b062d0c2790152"

MARKUPSAFE_LOCK = ""
EMPTY_LOCK = ""

JINJA_BASE = {
    "source": {
        "name": "jinja2",
        "url": "https://github.com/pallets/jinja",
        "commit": JINJA_COMMIT,
        "license": "BSD-3-Clause",
    },
    "language": "python",
    "difficulty": "hard",
    "tags": [
        "extreme",
        "multi-task-repo",
        "functional-discriminator",
        "template-engine",
        "pure-python",
        "multi-module",
    ],
    "environment": {
        "python": "3.12",
        "network": False,
        "timeout_seconds": 120,
        "dependency_lock": "requirements.lock",
        "allowed_dependencies": ["MarkupSafe"],
        "forbidden_dependencies": ["jinja2", "Jinja2"],
        "forbidden_imports": ["jinja2", "jinja"],
    },
    "tests": {"public": "public_tests/", "hidden": "hidden_tests/", "command": "pytest"},
}

PYTEST_BASE = {
    "source": {
        "name": "pytest",
        "url": "https://github.com/pytest-dev/pytest",
        "commit": PYTEST_COMMIT,
        "license": "MIT",
    },
    "language": "python",
    "difficulty": "hard",
    "tags": [
        "extreme",
        "multi-task-repo",
        "functional-discriminator",
        "test-framework",
        "pure-python",
        "multi-module",
    ],
    "environment": {
        "python": "3.12",
        "network": False,
        "timeout_seconds": 60,
        "dependency_lock": "requirements.lock",
        "allowed_dependencies": [],
        "forbidden_dependencies": ["pytest"],
        "forbidden_imports": ["pytest", "_pytest"],
    },
    "tests": {"public": "public_tests/", "hidden": "hidden_tests/", "command": "pytest"},
}


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")


def _copy_repo(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(
        src,
        dst,
        ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", ".pytest_cache"),
    )


def _task_skeleton(task_dir: Path, metadata: dict, *, lock: str, forbidden: str) -> None:
    _write(task_dir / "metadata.json", json.dumps(metadata, indent=2) + "\n")
    _write(task_dir / "requirements.lock", lock)
    _write(task_dir / "evaluation/forbidden_imports.txt", forbidden.strip() + "\n")
    (task_dir / "public_tests").mkdir(parents=True, exist_ok=True)
    (task_dir / "hidden_tests").mkdir(parents=True, exist_ok=True)
    (task_dir / "evaluation").mkdir(parents=True, exist_ok=True)


def setup_jinja_repo(task_dir: Path) -> None:
    _copy_repo(JINJA_SRC, task_dir / "repo")


def setup_pytest_repo(task_dir: Path) -> None:
    _copy_repo(PYTEST_SRC, task_dir / "repo")


def setup_jinja_tasks() -> None:
    tasks = {
        "jinja2__lexer_parser_core__001": {
            "feature": {
                "name": "Jinja2 lexer and parser core",
                "description": "Extract Jinja2 template lexing and parsing into AST nodes as a standalone package.",
                "source_entrypoints": [
                    "jinja2.lexer.Lexer",
                    "jinja2.lexer.TokenStream",
                    "jinja2.parser.Parser",
                    "jinja2.environment.Environment.lex",
                    "jinja2.environment.Environment.parse",
                    "jinja2.nodes",
                ],
                "included_behaviors": [
                    "tokenize template source into token streams",
                    "parse templates into AST node trees",
                    "support block, variable, comment, and statement delimiters",
                    "preserve syntax error reporting with line numbers",
                ],
                "excluded_behaviors": [
                    "template compilation and rendering",
                    "loaders and template inheritance",
                    "filters, tests, extensions, async mode",
                    "CLI, original tests, docs, packaging metadata",
                ],
            },
            "entanglement": {
                "level": "high",
                "types": [
                    "parser_state_coupling",
                    "data_model_coupling",
                    "implicit_dependency_coupling",
                ],
                "description": "Lexer and parser behavior spans tokenization state, AST node hierarchy, and environment-driven delimiter configuration.",
                "signals": [
                    "lexer token cache and delimiter configuration",
                    "parser tag stack and nested block state",
                    "AST node tree used by compiler but required for parse output",
                ],
            },
            "output": {
                "package": "featurelifted",
                "import": "from featurelifted import Environment, nodes",
                "callable": "featurelifted.Environment.parse",
                "signature": "parse(source: str, name: str | None = None, filename: str | None = None) -> nodes.Template",
            },
            "oracle_manifest": {
                "source_files": [
                    "src/jinja2/exceptions.py",
                    "src/jinja2/utils.py",
                    "src/jinja2/_identifier.py",
                    "src/jinja2/constants.py",
                    "src/jinja2/lexer.py",
                    "src/jinja2/nodes.py",
                    "src/jinja2/parser.py",
                    "src/jinja2/environment.py",
                ],
                "notes": "Lexer/parser closure only. Compiler, runtime, loaders, filters excluded.",
            },
            "public_test": '''
                from featurelifted import Environment
                from featurelifted import nodes


                def test_parse_variable_output() -> None:
                    env = Environment()
                    tree = env.parse("Hello {{ name }}!")
                    assert isinstance(tree, nodes.Template)
                    assert len(tree.body) == 2
                    assert isinstance(tree.body[1], nodes.Output)


                def test_lex_returns_token_types() -> None:
                    env = Environment()
                    tokens = list(env.lex("{% if x %}y{% endif %}"))
                    types = [t[1] for t in tokens if t[1] != "eof"]
                    assert "block_begin" in types
                    assert "name" in types
            ''',
            "hidden_test": '''
                from featurelifted import Environment
                from featurelifted import nodes
                from featurelifted.lexer import Lexer
                from featurelifted.parser import Parser


                def test_parse_for_loop_structure() -> None:
                    env = Environment()
                    tree = env.parse("{% for item in seq %}{{ item }}{% endfor %}")
                    for_node = tree.body[0]
                    assert isinstance(for_node, nodes.For)
                    assert isinstance(for_node.body[0], nodes.Output)


                def test_lexer_module_required_for_raw_blocks() -> None:
                    env = Environment()
                    lexer = Lexer(env)
                    stream = lexer.tokenize("{% raw %}{{ x }}{% endraw %}")
                    values = [token.value for token in stream if token.value]
                    assert "{{ x }}" in values


                def test_parser_module_required_for_if_elif() -> None:
                    env = Environment()
                    tree = Parser(env, "{% if a %}1{% elif b %}2{% else %}3{% endif %}").parse()
                    if_node = tree.body[0]
                    assert isinstance(if_node, nodes.If)
                    assert len(if_node.elif_) == 1
            ''',
            "design": "Narrow jinja2 extraction to lex+parse AST. Module probes target lexer and parser.",
        },
        "jinja2__compile_render_core__001": {
            "feature": {
                "name": "Jinja2 compile and render core",
                "description": "Extract Jinja2 template compilation and rendering as a standalone package.",
                "source_entrypoints": [
                    "jinja2.environment.Environment.from_string",
                    "jinja2.environment.Environment.compile",
                    "jinja2.environment.Template.render",
                    "jinja2.compiler",
                    "jinja2.runtime",
                ],
                "included_behaviors": [
                    "compile template source to executable code",
                    "render templates with context variables",
                    "support if/for/set/macro blocks and expressions",
                    "preserve undefined variable behavior with default Undefined",
                ],
                "excluded_behaviors": [
                    "loaders and extends/include inheritance graph",
                    "async rendering",
                    "extensions, bytecode cache, i18n",
                    "CLI, original tests, docs, packaging metadata",
                ],
            },
            "entanglement": {
                "level": "high",
                "types": [
                    "parser_state_coupling",
                    "framework_coupling",
                    "data_model_coupling",
                ],
                "description": "Compile/render couples parser output, compiler code generation, runtime context, and default filters/tests registration.",
                "signals": [
                    "compiler id-tracking and optimizer passes",
                    "runtime Context and exported variable handling",
                    "environment owns lexer, parser, compiler pipeline",
                ],
            },
            "output": {
                "package": "featurelifted",
                "import": "from featurelifted import Environment",
                "callable": "featurelifted.Environment.from_string",
                "signature": "from_string(source: str, globals: dict | None = None) -> Template",
            },
            "oracle_manifest": {
                "source_files": [
                    "src/jinja2/exceptions.py",
                    "src/jinja2/utils.py",
                    "src/jinja2/_identifier.py",
                    "src/jinja2/constants.py",
                    "src/jinja2/defaults.py",
                    "src/jinja2/async_utils.py",
                    "src/jinja2/lexer.py",
                    "src/jinja2/nodes.py",
                    "src/jinja2/parser.py",
                    "src/jinja2/visitor.py",
                    "src/jinja2/idtracking.py",
                    "src/jinja2/optimizer.py",
                    "src/jinja2/compiler.py",
                    "src/jinja2/runtime.py",
                    "src/jinja2/filters.py",
                    "src/jinja2/tests.py",
                    "src/jinja2/environment.py",
                ],
                "notes": "Compile/render closure without loaders or extensions.",
            },
            "public_test": '''
                from featurelifted import Environment


                def test_render_simple_interpolation() -> None:
                    env = Environment()
                    tmpl = env.from_string("Hello {{ name }}!")
                    assert tmpl.render(name="World") == "Hello World!"


                def test_render_if_for_blocks() -> None:
                    env = Environment()
                    tmpl = env.from_string(
                        "{% for n in items %}{% if n %}{{ n }}{% endif %}{% endfor %}"
                    )
                    assert tmpl.render(items=[1, 0, 2]) == "12"
            ''',
            "hidden_test": '''
                from featurelifted import Environment
                from featurelifted.compiler import generate
                from featurelifted.runtime import Context


                def test_macro_render_and_caller() -> None:
                    env = Environment()
                    tmpl = env.from_string(
                        "{% macro greet(name) %}Hi {{ name }}{% endmacro %}{{ greet('Ann') }}"
                    )
                    assert tmpl.render() == "Hi Ann"


                def test_compiler_module_required_for_set_block() -> None:
                    env = Environment()
                    tree = env.parse("{% set x = 1 %}{{ x + 1 }}")
                    source = generate(tree, env, None, None)
                    assert "x" in source


                def test_runtime_context_exported_vars() -> None:
                    env = Environment()
                    tmpl = env.from_string("{% set x = 5 %}{{ x }}")
                    assert tmpl.render() == "5"
            ''',
            "design": "Compile/render without loaders. Probes target compiler and runtime modules.",
        },
        "jinja2__loader_inheritance_core__001": {
            "feature": {
                "name": "Jinja2 loader and inheritance core",
                "description": "Extract Jinja2 template loading and extends/block inheritance rendering.",
                "source_entrypoints": [
                    "jinja2.loaders.BaseLoader",
                    "jinja2.loaders.DictLoader",
                    "jinja2.environment.Environment.get_template",
                    "jinja2.environment.Template.render",
                ],
                "included_behaviors": [
                    "load templates via DictLoader and BaseLoader subclasses",
                    "resolve extends chains and block overrides",
                    "render nested block inheritance across multiple templates",
                    "support trim_blocks for layout templates",
                ],
                "excluded_behaviors": [
                    "PackageLoader zip/import paths beyond DictLoader",
                    "async rendering, extensions, bytecode cache",
                    "CLI, original tests, docs, packaging metadata",
                ],
            },
            "entanglement": {
                "level": "high",
                "types": [
                    "resource_coupling",
                    "framework_coupling",
                    "data_model_coupling",
                ],
                "description": "Loader/inheritance couples template lookup, compile pipeline, and block resolution across multiple sources.",
                "signals": [
                    "loader get_source and template cache",
                    "extends/import include graph in parser/compiler",
                    "block super() resolution at render time",
                ],
            },
            "output": {
                "package": "featurelifted",
                "import": "from featurelifted import Environment, DictLoader",
                "callable": "featurelifted.Environment.get_template",
                "signature": "get_template(name: str) -> Template",
            },
            "oracle_manifest": {
                "source_files": [
                    "src/jinja2/loaders.py",
                    "src/jinja2/environment.py",
                    "src/jinja2/compiler.py",
                    "src/jinja2/runtime.py",
                    "src/jinja2/parser.py",
                    "src/jinja2/lexer.py",
                    "src/jinja2/nodes.py",
                ],
                "notes": "Loader + inheritance closure includes compile/render stack and DictLoader.",
            },
            "public_test": '''
                from featurelifted import DictLoader
                from featurelifted import Environment


                LAYOUT = "|{% block body %}base{% endblock %}|"
                CHILD = '{% extends "layout" %}{% block body %}child{% endblock %}'


                def test_extends_overrides_block() -> None:
                    env = Environment(
                        loader=DictLoader({"layout": LAYOUT, "child": CHILD}),
                        trim_blocks=True,
                    )
                    assert env.get_template("child").render() == "|child|"
            ''',
            "hidden_test": '''
                from featurelifted import DictLoader
                from featurelifted import Environment
                from featurelifted.loaders import BaseLoader


                MULTI = {
                    "layout": "|{% block a %}A{% endblock %}{% block b %}B{% endblock %}|",
                    "mid": '{% extends "layout" %}{% block a %}a{% endblock %}',
                    "leaf": '{% extends "mid" %}{% block b %}b{% endblock %}',
                }


                def test_multi_level_inheritance() -> None:
                    env = Environment(loader=DictLoader(MULTI), trim_blocks=True)
                    assert env.get_template("leaf").render() == "|ab|"


                def test_loader_module_required_for_missing_template() -> None:
                    env = Environment(loader=DictLoader({}))
                    try:
                        env.get_template("missing")
                    except Exception as exc:
                        assert "missing" in exc.__class__.__name__.lower() or "not found" in str(exc).lower()
                    else:
                        raise AssertionError("expected TemplateNotFound")


                def test_base_loader_subclass_get_source() -> None:
                    class OneShot(BaseLoader):
                        def get_source(self, environment, template):
                            return "static", None, lambda: True

                    env = Environment(loader=OneShot())
                    assert env.get_template("x").render() == "static"
            ''',
            "design": "Loader + extends with bundled DictLoader fixtures. Probes loaders module.",
            "fixtures": {
                "layout.jinja": "|{% block body %}base{% endblock %}|",
                "child.jinja": '{% extends "layout.jinja" %}{% block body %}child{% endblock %}',
            },
        },
        "jinja2__filters_tests_core__001": {
            "feature": {
                "name": "Jinja2 filters and tests core",
                "description": "Extract Jinja2 built-in filters, tests, and template usage via Environment.",
                "source_entrypoints": [
                    "jinja2.filters.FILTERS",
                    "jinja2.tests.TESTS",
                    "jinja2.environment.Environment.call_filter",
                    "jinja2.environment.Environment.call_test",
                ],
                "included_behaviors": [
                    "apply built-in filters in templates and via call_filter",
                    "evaluate built-in tests in templates and via call_test",
                    "support common filters: capitalize, default, length, join, map, select",
                    "support common tests: defined, undefined, even, odd, number, string",
                ],
                "excluded_behaviors": [
                    "custom extension filters",
                    "async filter variants",
                    "loaders and template inheritance beyond from_string",
                    "CLI, original tests, docs, packaging metadata",
                ],
            },
            "entanglement": {
                "level": "high",
                "types": [
                    "framework_coupling",
                    "implicit_dependency_coupling",
                    "data_model_coupling",
                ],
                "description": "Filters/tests registry integrates with Environment, runtime Undefined, and template compilation.",
                "signals": [
                    "DEFAULT_FILTERS/DEFAULT_TESTS wired through defaults.py",
                    "filters depend on runtime Undefined and MarkupSafe",
                    "call_filter/call_test require compiled expression path",
                ],
            },
            "output": {
                "package": "featurelifted",
                "import": "from featurelifted import Environment",
                "callable": "featurelifted.Environment.call_filter",
                "signature": "call_filter(name: str, value: object, *args, **kwargs) -> object",
            },
            "oracle_manifest": {
                "source_files": [
                    "src/jinja2/filters.py",
                    "src/jinja2/tests.py",
                    "src/jinja2/runtime.py",
                    "src/jinja2/environment.py",
                    "src/jinja2/defaults.py",
                ],
                "notes": "Filters/tests with compile/render support for template usage.",
            },
            "public_test": '''
                from featurelifted import Environment


                def test_capitalize_filter_in_template() -> None:
                    env = Environment()
                    tmpl = env.from_string('{{ "hello"|capitalize }}')
                    assert tmpl.render() == "Hello"


                def test_call_filter_directly() -> None:
                    env = Environment()
                    assert env.call_filter("upper", "abc") == "ABC"
            ''',
            "hidden_test": '''
                from featurelifted import Environment
                from featurelifted import filters
                from featurelifted import tests as jinja_tests


                def test_default_filter_with_boolean() -> None:
                    env = Environment()
                    tmpl = env.from_string("{{ false|default('no', true) }}")
                    assert tmpl.render() == "no"


                def test_defined_test_in_template() -> None:
                    env = Environment()
                    tmpl = env.from_string("{% if x is defined %}yes{% else %}no{% endif %}")
                    assert tmpl.render() == "no"
                    assert tmpl.render(x=1) == "yes"


                def test_filters_module_required_for_join() -> None:
                    env = Environment()
                    assert env.call_filter("join", ["a", "b"], ":") == "a:b"
                    assert "join" in filters.FILTERS


                def test_tests_module_required_for_even() -> None:
                    env = Environment()
                    assert env.call_test("even", 4) is True
                    assert "even" in jinja_tests.TESTS
            ''',
            "design": "Filters/tests with module probes on filters.py and tests.py.",
        },
    }

    for task_id, spec in tasks.items():
        task_dir = ROOT / "benchmark" / "tasks" / task_id
        metadata = {
            "task_id": task_id,
            **JINJA_BASE,
            "feature": spec["feature"],
            "entanglement": spec["entanglement"],
            "output": spec["output"],
        }
        _task_skeleton(task_dir, metadata, lock=MARKUPSAFE_LOCK, forbidden="jinja2\njinja")
        setup_jinja_repo(task_dir)
        _write(task_dir / "evaluation/oracle_manifest.json", json.dumps(spec["oracle_manifest"], indent=2) + "\n")
        _write(task_dir / "public_tests/test_public_api.py", spec["public_test"])
        _write(task_dir / "hidden_tests/test_hidden_behavior.py", spec["hidden_test"])
        if fixtures := spec.get("fixtures"):
            for name, content in fixtures.items():
                _write(task_dir / "template_fixtures" / name, content + "\n")
        design = f"""# Task Design: {task_id}

Status: draft

## Why This Task

{spec["design"]}

## Source

| Field | Value |
| --- | --- |
| Source repo | `{JINJA_BASE["source"]["url"]}` |
| Commit | `{JINJA_COMMIT}` |
| License | BSD-3-Clause |
| Difficulty | hard |
| Tags | extreme, multi-task-repo, functional-discriminator |

## Output API

```python
{spec["output"]["import"]}
```

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| core module | see hidden tests | see hidden tests |
"""
        _write(ROOT / "docs/task_designs" / f"{task_id}.md", design)


def setup_pytest_tasks() -> None:
    tasks = {
        "pytest__mark_expression_core__001": {
            "feature": {
                "name": "pytest mark expression evaluator",
                "description": "Extract pytest -m mark expression compile/evaluate logic as a standalone package.",
                "source_entrypoints": [
                    "_pytest.mark.expression.Expression",
                    "_pytest.mark.expression.Expression.compile",
                    "_pytest.mark.expression.Expression.evaluate",
                ],
                "included_behaviors": [
                    "parse and compile mark expressions with and/or/not",
                    "evaluate expressions against a matcher callback",
                    "support identifier kwargs syntax for parameterized markers",
                    "empty expression evaluates to False",
                ],
                "excluded_behaviors": [
                    "full pytest collection and test running",
                    "keyword -k matching",
                    "marker registration and strict markers",
                    "CLI, original tests, docs, packaging metadata",
                ],
            },
            "entanglement": {
                "level": "high",
                "types": [
                    "parser_state_coupling",
                    "framework_coupling",
                    "implicit_dependency_coupling",
                ],
                "description": "Mark expressions compile to Python bytecode evaluated against pytest marker matching hooks.",
                "signals": [
                    "custom scanner/parser for marker grammar",
                    "MatcherAdapter bridges eval() to marker names",
                    "used by pytest -m but standalone logic lives in one module",
                ],
            },
            "output": {
                "package": "featurelifted",
                "import": "from featurelifted import Expression, ParseError",
                "callable": "featurelifted.Expression.compile",
                "signature": "compile(input: str) -> Expression",
            },
            "oracle_manifest": {
                "source_files": ["src/_pytest/mark/expression.py"],
                "notes": "Standalone mark expression module only.",
            },
            "public_test": '''
                from featurelifted import Expression


                def test_empty_expression_is_false() -> None:
                    assert not Expression.compile("").evaluate(lambda name: True)


                def test_and_or_logic() -> None:
                    matcher = {"fast": True, "slow": False}.__getitem__
                    assert Expression.compile("fast and not slow").evaluate(matcher)
            ''',
            "hidden_test": '''
                from featurelifted import Expression
                from featurelifted import expression as expr_mod


                def test_kwargs_matcher() -> None:
                    def matcher(name, **kwargs):
                        return name == "req" and kwargs.get("version") == 2

                    assert Expression.compile('req(version=2)').evaluate(matcher)


                def test_expression_module_scanner() -> None:
                    from featurelifted.expression import Scanner, TokenType

                    scanner = Scanner("a and b")
                    assert scanner.current.type is TokenType.IDENT
            ''',
            "design": "Standalone -m expression evaluator from _pytest/mark/expression.py.",
        },
        "pytest__skipif_eval_core__001": {
            "feature": {
                "name": "pytest skipif condition evaluator",
                "description": "Extract pytest skipif/xfail condition evaluation semantics as a standalone package.",
                "source_entrypoints": [
                    "_pytest.skipping.evaluate_condition",
                ],
                "included_behaviors": [
                    "evaluate string conditions via compile/eval with allowed globals",
                    "evaluate boolean conditions directly",
                    "merge markeval_namespace mappings into eval globals",
                    "return (result, reason) tuple with default reason for string conditions",
                ],
                "excluded_behaviors": [
                    "full skip/xfail mark application during test run",
                    "pytest item/collector integration",
                    "xfail strict/run/raises handling",
                    "CLI, original tests, docs, packaging metadata",
                ],
            },
            "entanglement": {
                "level": "high",
                "types": [
                    "framework_coupling",
                    "config_environment_coupling",
                    "implicit_dependency_coupling",
                ],
                "description": "Skipif evaluation uses dynamic eval with config, platform, and custom namespace hooks from pytest runtime.",
                "signals": [
                    "string conditions compiled at evaluation time",
                    "globals merge os/sys/platform/config namespaces",
                    "tied to Mark metadata but usable standalone",
                ],
            },
            "output": {
                "package": "featurelifted",
                "import": "from featurelifted import Mark, EvalContext, evaluate_condition",
                "callable": "featurelifted.evaluate_condition",
                "signature": "evaluate_condition(context: EvalContext, mark: Mark, condition: object) -> tuple[bool, str]",
            },
            "oracle_manifest": {
                "source_files": ["src/_pytest/skipping.py"],
                "notes": "evaluate_condition subset extracted from skipping.py with local Mark/EvalContext types.",
            },
            "public_test": '''
                import sys

                from featurelifted import EvalContext
                from featurelifted import Mark
                from featurelifted import evaluate_condition


                def test_string_condition_true() -> None:
                    ctx = EvalContext()
                    mark = Mark("skipif", {"reason": "win32"})
                    result, reason = evaluate_condition(ctx, mark, "sys.platform == 'win32'")
                    assert result == (sys.platform == "win32")
                    assert reason == "win32"


                def test_boolean_condition() -> None:
                    ctx = EvalContext()
                    mark = Mark("skipif", {"reason": "disabled"})
                    assert evaluate_condition(ctx, mark, True) == (True, "disabled")
            ''',
            "hidden_test": '''
                import sys

                from featurelifted import EvalContext
                from featurelifted import Mark
                from featurelifted import evaluate_condition


                def test_markeval_namespace_merged() -> None:
                    ctx = EvalContext(markeval_namespace=[{"flag": True}])
                    mark = Mark("skipif", {})
                    result, _ = evaluate_condition(ctx, mark, "flag")
                    assert result is True


                def test_obj_globals_merged() -> None:
                    ctx = EvalContext(obj_globals={"value": 42})
                    mark = Mark("skipif", {})
                    result, _ = evaluate_condition(ctx, mark, "value == 42")
                    assert result is True


                def test_invalid_syntax_raises() -> None:
                    import pytest

                    ctx = EvalContext()
                    mark = Mark("skipif", {})
                    with pytest.raises(Exception):
                        evaluate_condition(ctx, mark, "1 and")
            ''',
            "design": "evaluate_condition subset from skipping.py with EvalContext/Mark adapters.",
        },
        "pytest__ini_markers_core__001": {
            "feature": {
                "name": "pytest ini markers parsing",
                "description": "Extract pytest ini markers linelist parsing and marker line normalization.",
                "source_entrypoints": [
                    "_pytest.config.Config.getini",
                    "_pytest.config.Config.addinivalue_line",
                    "_pytest.mark.__init__.pytest_addoption",
                ],
                "included_behaviors": [
                    "parse multiline ini markers values into linelist entries",
                    "append marker lines preserving order",
                    "split marker lines into name and description",
                    "strip whitespace from linelist entries",
                ],
                "excluded_behaviors": [
                    "full Config initialization and plugin loading",
                    "strict marker validation at collection",
                    "conftest and pyproject discovery",
                    "CLI --markers display",
                ],
            },
            "entanglement": {
                "level": "high",
                "types": [
                    "config_environment_coupling",
                    "global_state_registry_coupling",
                ],
                "description": "Ini marker definitions accumulate via config linelist merging across plugins and pytest.ini.",
                "signals": [
                    "linelist ini type coerces multiline strings",
                    "addinivalue_line appends to cached marker registry",
                    "marker names/descriptions parsed for --markers output",
                ],
            },
            "output": {
                "package": "featurelifted",
                "import": "from featurelifted import MarkerRegistry, parse_linelist, split_marker_line",
                "callable": "featurelifted.MarkerRegistry.from_ini",
                "signature": "from_ini(value: str | list[str]) -> MarkerRegistry",
            },
            "oracle_manifest": {
                "source_files": ["src/_pytest/config/__init__.py", "src/_pytest/mark/__init__.py"],
                "notes": "Subset extracted into ini_markers module mirroring linelist + marker line parsing.",
            },
            "public_test": '''
                from featurelifted import MarkerRegistry
                from featurelifted import parse_linelist


                def test_parse_multiline_markers() -> None:
                    raw = """
                        a1: web test
                        a2: smoke
                    """
                    lines = parse_linelist(raw)
                    reg = MarkerRegistry.from_lines(lines)
                    assert reg.names() == ["a1", "a2"]
                    assert reg.description("a1") == "web test"


                def test_append_marker_line() -> None:
                    reg = MarkerRegistry()
                    reg.add_line("slow: slow tests")
                    reg.add_line("fast")
                    assert reg.description("slow") == "slow tests"
                    assert reg.description("fast") == ""
            ''',
            "hidden_test": '''
                from featurelifted import MarkerRegistry
                from featurelifted import parse_linelist
                from featurelifted import split_marker_line


                def test_linelist_strips_blank_lines() -> None:
                    assert parse_linelist("a\\nb\\n\\n c ") == ["a", "b", "c"]


                def test_split_marker_line_whitespace() -> None:
                    name, desc = split_marker_line("  a1 :  whitespace marker  ")
                    assert name == "a1"
                    assert desc == "whitespace marker"


                def test_registry_module_order_preserved() -> None:
                    reg = MarkerRegistry.from_ini(["z: last", "a: first"])
                    assert reg.names() == ["z", "a"]
            ''',
            "design": "Ini markers linelist parsing subset from pytest config/mark modules.",
        },
    }

    for task_id, spec in tasks.items():
        task_dir = ROOT / "benchmark" / "tasks" / task_id
        metadata = {
            "task_id": task_id,
            **PYTEST_BASE,
            "feature": spec["feature"],
            "entanglement": spec["entanglement"],
            "output": spec["output"],
        }
        _task_skeleton(task_dir, metadata, lock=EMPTY_LOCK, forbidden="pytest\n_pytest")
        setup_pytest_repo(task_dir)
        _write(task_dir / "evaluation/oracle_manifest.json", json.dumps(spec["oracle_manifest"], indent=2) + "\n")
        _write(task_dir / "public_tests/test_public_api.py", spec["public_test"])
        _write(task_dir / "hidden_tests/test_hidden_behavior.py", spec["hidden_test"])
        design = f"""# Task Design: {task_id}

Status: draft

## Why This Task

{spec["design"]}

## Source

| Field | Value |
| --- | --- |
| Source repo | `{PYTEST_BASE["source"]["url"]}` |
| Commit | `{PYTEST_COMMIT}` |
| License | MIT |
| Difficulty | hard |
| Tags | extreme, multi-task-repo, functional-discriminator |

## Output API

```python
{spec["output"]["import"]}
```
"""
        _write(ROOT / "docs/task_designs" / f"{task_id}.md", design)


def main() -> None:
    if not JINJA_SRC.is_dir() or not PYTEST_SRC.is_dir():
        raise SystemExit("Clone jinja and pytest to /tmp/flb-clones first")
    setup_jinja_tasks()
    setup_pytest_tasks()
    print("M3 task scaffolding complete.")


if __name__ == "__main__":
    main()
