#!/usr/bin/env python3
"""Materialize External-50 W2 lower-risk tasks into benchmark/staging/."""

from __future__ import annotations

import importlib.util
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
PILOT = ROOT / "harness" / "scripts" / "materialize_external50_pilot.py"
W1 = ROOT / "harness" / "scripts" / "materialize_external50_w1.py"
PIN_ROOT = Path("/tmp/flb_w2_pins")
STAGING = ROOT / "benchmark" / "staging"

spec = importlib.util.spec_from_file_location("pilot_mat", PILOT)
pilot = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(pilot)

w1_spec = importlib.util.spec_from_file_location("w1_mat", W1)
w1 = importlib.util.module_from_spec(w1_spec)
assert w1_spec.loader is not None
w1_spec.loader.exec_module(w1)

copy_package_tree = w1.copy_package_tree
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
        ignore=shutil.ignore_patterns(
            "__pycache__", "*.pyc", ".flb_pin", "*.tar.gz", "wheels", ".git"
        ),
    )
    (task_dir / "evaluation").mkdir(parents=True)
    (task_dir / "public_tests").mkdir()
    (task_dir / "hidden_tests").mkdir()
    return task_dir


PINS: dict[str, dict[str, Any]] = {
    "toolz__compose_pipe_core__001": {
        "package": "toolz",
        "url": "https://github.com/pytoolz/toolz",
        "commit": "568c2b8393973cd172a466546c9d95779c452438",
        "tag": "1.1.0",
        "license": "BSD-3-Clause",
        "license_path": "LICENSE.txt",
        "src": PIN_ROOT / "toolz",
        "forbidden": "toolz",
        "lift": "Direct",
        "pkg_dir": lambda: PIN_ROOT / "toolz" / "toolz",
    },
    "anytree__tree_resolve_render_core__001": {
        "package": "anytree",
        "url": "https://github.com/c0fec0de/anytree",
        "commit": "2e0a1b956172654d75aff93277ce3d883355e0bf",
        "tag": "2.13.0",
        "license": "Apache-2.0",
        "license_path": "LICENSE",
        "src": PIN_ROOT / "anytree",
        "forbidden": "anytree",
        "lift": "Composite",
        "pkg_dir": lambda: PIN_ROOT / "anytree" / "src" / "anytree",
    },
    "parsimonious__grammar_visitor_core__001": {
        "package": "parsimonious",
        "url": "https://github.com/erikrose/parsimonious",
        "commit": "a33206834534df5bc1da341315c819f4312b8131",
        "tag": "0.10.0",
        "license": "MIT",
        "license_path": "LICENSE",
        "src": PIN_ROOT / "parsimonious",
        "forbidden": "parsimonious",
        "lift": "Adapted",
        "pkg_dir": lambda: PIN_ROOT / "parsimonious" / "parsimonious",
    },
    "typeguard__check_type_pipeline_core__001": {
        "package": "typeguard",
        "url": "https://github.com/agronholm/typeguard",
        "commit": "9f289c7fca68097542d3bde9d59496ad42e58251",
        "tag": "4.6.0",
        "license": "MIT",
        "license_path": "LICENSE",
        "src": PIN_ROOT / "typeguard",
        "forbidden": "typeguard",
        "lift": "Composite",
        "pkg_dir": lambda: PIN_ROOT / "typeguard" / "src" / "typeguard",
    },
    "pykwalify__map_seq_validate_core__001": {
        "package": "pykwalify",
        "url": "https://github.com/Grokzen/pykwalify",
        "commit": "4359ddf1edfe6cff13a183f3142c5970ed1dbbd7",
        "tag": "1.8.0",
        "license": "MIT",
        "license_path": "LICENSE",
        "src": PIN_ROOT / "pykwalify",
        "forbidden": "pykwalify",
        "lift": "Composite",
        "pkg_dir": lambda: PIN_ROOT / "pykwalify" / "pykwalify",
    },
    "strictyaml__schema_load_core__001": {
        "package": "strictyaml",
        "url": "https://github.com/crdoconnor/strictyaml",
        "commit": "f19d2815bb733e3bf709a34281a62a25ccdfdc3a",
        "tag": "1.7.3",
        "license": "MIT",
        "license_path": "LICENSE.txt",
        "src": PIN_ROOT / "strictyaml",
        "forbidden": "strictyaml",
        "lift": "Composite",
        "pkg_dir": lambda: PIN_ROOT / "strictyaml" / "strictyaml",
    },
    "premailer__inline_css_core__001": {
        "package": "premailer",
        "url": "https://github.com/peterbe/premailer",
        "commit": "f4ded0b9701c4985e7ff5c5beda83324c264ea62",
        "tag": "3.10.0-master",
        "license": "BSD-3-Clause",
        "license_path": "LICENSE",
        "src": PIN_ROOT / "premailer",
        "forbidden": "premailer",
        "lift": "Composite",
        "pkg_dir": lambda: PIN_ROOT / "premailer" / "premailer",
    },
    "textx__metamodel_model_core__001": {
        "package": "textX",
        "url": "https://github.com/textX/textX",
        "commit": "ff7327de0b3d7ae81d52d867eb0cdcb643b56e93",
        "tag": "v2.2.0",
        "license": "MIT",
        "license_path": "LICENSE.txt",
        "src": PIN_ROOT / "textX",
        "forbidden": "textx",
        "lift": "Composite",
        "pkg_dir": lambda: PIN_ROOT / "textX" / "textx",
    },
    "frictionless__schema_resource_validate_core__001": {
        "package": "frictionless",
        "url": "https://github.com/frictionlessdata/frictionless-py",
        "commit": "43a63e0be8f332f82177f62e0099e667a93bd77b",
        "tag": "v5.19.0",
        "license": "MIT",
        "license_path": "LICENSE.md",
        "src": PIN_ROOT / "frictionless",
        "forbidden": "frictionless",
        "lift": "Composite",
        "pkg_dir": lambda: PIN_ROOT / "frictionless" / "frictionless",
    },
    "libcst__parse_transform_core__001": {
        "package": "libcst",
        "url": "https://github.com/Instagram/LibCST",
        "commit": "c029c17bf45a3737fc8d1347001ab2422f42ae58",
        "tag": "v1.9.0",
        "license": "MIT",
        "license_path": "LICENSE",
        "src": PIN_ROOT / "libcst",
        "forbidden": "libcst",
        "lift": "Composite",
        # Native parser lives in the PyPI wheel (git tree alone cannot parse).
        "pkg_dir": lambda: PIN_ROOT / "libcst_wheel" / "libcst",
    },
    "unidiff__patch_hunk_core__001": {
        "package": "unidiff",
        "url": "https://github.com/matiasb/python-unidiff",
        "commit": "5ff054b218a345b6322bdd3cdd8ca4670ddcd6ad",
        "tag": "v1.0.0",
        "license": "MIT",
        "license_path": "LICENSE",
        "src": PIN_ROOT / "unidiff",
        "forbidden": "unidiff",
        "lift": "Composite",
        "pkg_dir": lambda: PIN_ROOT / "unidiff" / "unidiff",
    },
}


def materialize_toolz() -> Path:
    task_id = "toolz__compose_pipe_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["pkg_dir"](), ref, "toolz")
    # Direct surface: avoid broken curried/sandbox rewrites (`del toolz`).
    (ref / "__init__.py").write_text(
        '''"""Task-scoped toolz functoolz extract."""

from .functoolz import compose, curry, identity, pipe

__all__ = ["compose", "curry", "identity", "pipe"]
''',
        encoding="utf-8",
    )
    for drop in ("curried", "sandbox"):
        p = ref / drop
        if p.exists():
            shutil.rmtree(p)
    (task_dir / "requirements.lock").write_text("# no third-party dependencies\n", encoding="utf-8")
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("toolz\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "toolz",
            "required_source_files": ["toolz/functoolz.py", "toolz/__init__.py"],
            "runtime_dependencies": [],
            "notes": "Direct extract of compose/pipe/curry/identity.",
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        '''from __future__ import annotations

from featurelifted import compose, curry, identity, pipe


def test_compose_and_pipe() -> None:
    f = compose(lambda x: x + 1, lambda x: x * 2)
    assert f(3) == 7
    assert pipe(3, lambda x: x * 2, lambda x: x + 1) == 7


def test_curry_partial() -> None:
    add = curry(lambda a, b: a + b)
    assert add(1)(2) == 3
    assert add(1, 2) == 3


def test_identity() -> None:
    assert identity(42) == 42
    assert compose(identity, identity)(5) == 5
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        '''from __future__ import annotations

import re
from pathlib import Path

from featurelifted import compose, curry, identity, pipe


def test_compose_right_to_left() -> None:
    order: list[str] = []

    def a(x: int) -> int:
        order.append("a")
        return x + 1

    def b(x: int) -> int:
        order.append("b")
        return x * 2

    assert compose(a, b)(3) == 7
    assert order == ["b", "a"]


def test_pipe_left_to_right() -> None:
    order: list[str] = []

    def a(x: int) -> int:
        order.append("a")
        return x + 1

    def b(x: int) -> int:
        order.append("b")
        return x * 2

    assert pipe(3, a, b) == 8
    assert order == ["a", "b"]


def test_curry_kwargs() -> None:
    def f(a: int, b: int, c: int = 0) -> int:
        return a + b + c

    cf = curry(f)
    assert cf(1)(2) == 3
    assert cf(1, c=4)(2) == 7


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\\s*(?:from toolz\\b|import toolz\\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''from featurelifted import compose, curry, identity, pipe


def test_required_api_surface() -> None:
    assert callable(compose) and callable(pipe) and callable(identity)
    assert curry is not None
''',
        encoding="utf-8",
    )
    metadata = base_metadata(
        task_id,
        meta,
        feature={
            "name": "toolz compose pipe curry",
            "description": "Direct extract of toolz.functoolz compose/pipe/curry/identity.",
            "source_entrypoints": [
                "toolz.functoolz.compose",
                "toolz.functoolz.pipe",
                "toolz.functoolz.curry",
            ],
            "included_behaviors": [
                "compose right-to-left callable pipelines",
                "pipe left-to-right value pipelines",
                "curry partial application",
                "identity passthrough",
            ],
            "excluded_behaviors": ["cytoolz", "parallelism", "dicttoolz recipes"],
        },
        entanglement={
            "level": "low",
            "types": ["data_model_coupling"],
            "primary": "data_model_coupling",
            "description": "Pure function combinators.",
            "signals": ["compose", "pipe", "curry"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import compose, pipe, curry, identity",
            "callable": "compose",
            "signature": "compose(*funcs)",
        },
        public_spec={
            "title": "toolz compose pipe curry",
            "summary": "Extract a task-scoped subset of `toolz` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.compose", "kind": "function", "signature": "(*funcs)"},
                {"path": "featurelifted.pipe", "kind": "function", "signature": "(data, *funcs)"},
                {"path": "featurelifted.curry", "kind": "class"},
                {"path": "featurelifted.identity", "kind": "function", "signature": "(x)"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: compose right-to-left callable pipelines. Required observable cases include compose and pipe."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: pipe left-to-right value pipelines. Required observable cases include pipe left to right."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: curry partial application. Required observable cases include curry partial; curry kwargs."},
                {"id": "B004", "text": "identity returns its argument unchanged."},
                {"id": "B005", "text": "The package exposes compose/pipe/curry/identity with the kinds listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: toolz."},
            ],
            "exclusions": ["cytoolz", "parallelism", "original toolz import at runtime"],
            "forbidden": {"imports": ["toolz"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


def materialize_anytree() -> Path:
    task_id = "anytree__tree_resolve_render_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["pkg_dir"](), ref, "anytree")
    (task_dir / "requirements.lock").write_text("# no third-party dependencies\n", encoding="utf-8")
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("anytree\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "anytree",
            "required_source_files": [
                "src/anytree/node/nodemixin.py",
                "src/anytree/resolver.py",
                "src/anytree/render.py",
            ],
            "runtime_dependencies": [],
            "notes": "Composite Node + Resolver + RenderTree + PreOrderIter/findall.",
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        '''from __future__ import annotations

from featurelifted import (
    ChildResolverError,
    Node,
    PreOrderIter,
    RenderTree,
    Resolver,
    findall,
)


def test_build_and_preorder() -> None:
    root = Node("udo")
    marc = Node("marc", parent=root)
    Node("lian", parent=marc)
    assert [n.name for n in PreOrderIter(root)] == ["udo", "marc", "lian"]


def test_resolver_get() -> None:
    root = Node("udo")
    marc = Node("marc", parent=root)
    lian = Node("lian", parent=marc)
    r = Resolver("name")
    assert r.get(root, "/udo/marc/lian") is lian
    try:
        r.get(root, "/udo/missing")
        assert False, "expected ChildResolverError"
    except ChildResolverError:
        pass


def test_render_and_findall() -> None:
    root = Node("udo")
    Node("marc", parent=root)
    lines = [f"{row.pre}{row.node.name}" for row in RenderTree(root)]
    assert lines[0] == "udo"
    assert any("marc" in line for line in lines)
    found = findall(root, filter_=lambda n: n.name.startswith("m"))
    assert [n.name for n in found] == ["marc"]
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        '''from __future__ import annotations

import re
from pathlib import Path

from featurelifted import (
    Node,
    PreOrderIter,
    RenderTree,
    Resolver,
    ResolverError,
    findall,
)


def test_parent_children_mutation() -> None:
    root = Node("r")
    a = Node("a")
    a.parent = root
    assert a in root.children
    assert list(PreOrderIter(root))[1] is a


def test_resolver_relative_path() -> None:
    root = Node("r")
    a = Node("a", parent=root)
    b = Node("b", parent=a)
    r = Resolver("name")
    assert r.get(a, "b") is b


def test_render_row_fields() -> None:
    root = Node("r")
    Node("c", parent=root)
    rows = list(RenderTree(root))
    assert hasattr(rows[0], "pre") and hasattr(rows[0], "fill") and hasattr(rows[0], "node")


def test_findall_empty() -> None:
    root = Node("r")
    assert findall(root, filter_=lambda n: False) == ()


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\\s*(?:from anytree\\b|import anytree\\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path


def test_resolver_error_base() -> None:
    assert issubclass(ResolverError, Exception)
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''from featurelifted import Node, PreOrderIter, RenderTree, Resolver, findall


def test_required_api_surface() -> None:
    assert Node is not None and Resolver is not None and RenderTree is not None
    assert callable(PreOrderIter) and callable(findall)
''',
        encoding="utf-8",
    )
    metadata = base_metadata(
        task_id,
        meta,
        feature={
            "name": "anytree resolve render",
            "description": "Composite anytree Node + Resolver + RenderTree.",
            "source_entrypoints": [
                "anytree.Node",
                "anytree.Resolver",
                "anytree.RenderTree",
            ],
            "included_behaviors": [
                "build parent/child trees",
                "path resolve via Resolver",
                "ASCII RenderTree rows",
                "PreOrderIter and findall",
            ],
            "excluded_behaviors": ["dot export", "dict importer/exporter persistence"],
        },
        entanglement={
            "level": "medium",
            "types": ["data_model_coupling"],
            "primary": "data_model_coupling",
            "description": "Tree mutation, path resolve, and render share Node graph.",
            "signals": ["parent/children", "Resolver", "RenderTree"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import Node, Resolver, RenderTree",
            "callable": "Resolver.get",
            "signature": "get(node, path: str)",
        },
        public_spec={
            "title": "anytree tree resolve render",
            "summary": "Extract a task-scoped subset of `anytree` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.Node", "kind": "class"},
                {"path": "featurelifted.Resolver", "kind": "class"},
                {"path": "featurelifted.RenderTree", "kind": "class"},
                {"path": "featurelifted.PreOrderIter", "kind": "function"},
                {"path": "featurelifted.findall", "kind": "function"},
                {"path": "featurelifted.ChildResolverError", "kind": "class"},
                {"path": "featurelifted.ResolverError", "kind": "class"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: build parent/child trees and PreOrderIter. Required observable cases include build and preorder."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: Resolver path get and ChildResolverError. Required observable cases include resolver get."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: RenderTree yields Row(pre, fill, node) and findall filters. Required observable cases include render and findall."},
                {"id": "B004", "text": "parent assignment mutates children relationships."},
                {"id": "B005", "text": "The package exposes Node/Resolver/RenderTree/PreOrderIter/findall/ChildResolverError/ResolverError with the kinds listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: anytree."},
            ],
            "exclusions": ["dot export", "dict attachment persistence", "original anytree import at runtime"],
            "forbidden": {"imports": ["anytree"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


def materialize_parsimonious() -> Path:
    task_id = "parsimonious__grammar_visitor_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["pkg_dir"](), ref, "parsimonious")
    (task_dir / "requirements.lock").write_text("# no third-party dependencies\n", encoding="utf-8")
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("parsimonious\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "parsimonious",
            "required_source_files": [
                "parsimonious/grammar.py",
                "parsimonious/nodes.py",
                "parsimonious/exceptions.py",
            ],
            "runtime_dependencies": [],
            "notes": "Adapted Grammar + NodeVisitor documented workflow.",
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        '''from __future__ import annotations

from featurelifted import Grammar, NodeVisitor, ParseError


GRAMMAR = Grammar(
    r"""
expr = term (add term)*
add = "+"
term = ~"[0-9]+"
"""
)


class SumVisitor(NodeVisitor):
    def visit_expr(self, node, visited_children):
        first, rest = visited_children
        total = first
        for item in rest:
            total += item[1]
        return total

    def visit_term(self, node, visited_children):
        return int(node.text)

    def visit_add(self, node, visited_children):
        return node.text

    def generic_visit(self, node, visited_children):
        return visited_children or node


def test_parse_tree() -> None:
    tree = GRAMMAR.parse("1+2")
    assert tree.expr_name == "expr"


def test_visitor_eval() -> None:
    assert SumVisitor().visit(GRAMMAR.parse("1+2+3")) == 6


def test_parse_error() -> None:
    try:
        GRAMMAR.parse("x")
        assert False, "expected ParseError"
    except ParseError:
        pass
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        '''from __future__ import annotations

import re
from pathlib import Path

from featurelifted import Grammar, NodeVisitor, ParseError, VisitationError


def test_named_rule_access() -> None:
    g = Grammar(r"""
a = b
b = "x"
""")
    assert g["b"].parse("x").text == "x"


def test_visitation_error() -> None:
    g = Grammar(r'x = "a"')

    class Boom(NodeVisitor):
        def visit_x(self, node, visited_children):
            raise ValueError("boom")

        def generic_visit(self, node, visited_children):
            return visited_children or node

    try:
        Boom().visit(g.parse("a"))
        assert False
    except VisitationError:
        pass


def test_incomplete_or_bad_input() -> None:
    g = Grammar(r'x = "ab"')
    try:
        g.parse("a")
        assert False
    except ParseError:
        pass


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\\s*(?:from parsimonious\\b|import parsimonious\\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''from featurelifted import Grammar, NodeVisitor, ParseError, VisitationError


def test_required_api_surface() -> None:
    assert Grammar is not None and NodeVisitor is not None
    assert ParseError is not None and VisitationError is not None
''',
        encoding="utf-8",
    )
    metadata = base_metadata(
        task_id,
        meta,
        feature={
            "name": "parsimonious grammar visitor",
            "description": "Adapted Grammar parse + NodeVisitor evaluation.",
            "source_entrypoints": ["parsimonious.Grammar", "parsimonious.NodeVisitor"],
            "included_behaviors": [
                "PEG Grammar.parse to Node tree",
                "NodeVisitor evaluation",
                "ParseError and VisitationError",
            ],
            "excluded_behaviors": ["TokenGrammar-only workflows", "left-recursion hacks"],
        },
        entanglement={
            "level": "medium",
            "types": ["parser_state_coupling"],
            "primary": "parser_state_coupling",
            "description": "Grammar expression tree + visitor dispatch.",
            "signals": ["Grammar", "NodeVisitor", "ParseError"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import Grammar, NodeVisitor, ParseError",
            "callable": "Grammar.parse",
            "signature": "parse(text: str)",
        },
        public_spec={
            "title": "parsimonious grammar visitor",
            "summary": "Extract a task-scoped subset of `parsimonious` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.Grammar", "kind": "class"},
                {"path": "featurelifted.NodeVisitor", "kind": "class"},
                {"path": "featurelifted.ParseError", "kind": "class"},
                {"path": "featurelifted.VisitationError", "kind": "class"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: Grammar.parse builds a Node tree. Required observable cases include parse tree."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: NodeVisitor evaluates parse trees. Required observable cases include visitor eval."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: ParseError on bad input and VisitationError wrapping visitor exceptions. Required observable cases include parse error; visitation error."},
                {"id": "B004", "text": "Named rules are accessible via Grammar.__getitem__."},
                {"id": "B005", "text": "The package exposes Grammar/NodeVisitor/ParseError/VisitationError with the kinds listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: parsimonious."},
            ],
            "exclusions": ["TokenGrammar-only workflows", "original parsimonious import at runtime"],
            "forbidden": {"imports": ["parsimonious"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


def materialize_typeguard() -> Path:
    task_id = "typeguard__check_type_pipeline_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["pkg_dir"](), ref, "typeguard")
    (task_dir / "requirements.lock").write_text(
        "typing_extensions==4.15.0\n", encoding="utf-8"
    )
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("typeguard\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "typeguard",
            "required_source_files": ["src/typeguard/_checkers.py", "src/typeguard/__init__.py"],
            "runtime_dependencies": ["typing_extensions"],
            "notes": "Composite check_type nested collection/Union/Optional + CollectionCheckStrategy.",
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        '''from __future__ import annotations

from typing import Optional, Union

from featurelifted import CollectionCheckStrategy, TypeCheckError, check_type


def test_nested_collections() -> None:
    assert check_type([1, 2], list[int]) == [1, 2]
    assert check_type({"a": 1}, dict[str, int]) == {"a": 1}


def test_optional_union() -> None:
    assert check_type(None, Optional[int]) is None
    assert check_type(1, Union[int, str]) == 1


def test_type_check_error() -> None:
    all_items = CollectionCheckStrategy["ALL_ITEMS"]
    try:
        check_type([1, "a"], list[int], collection_check_strategy=all_items)
        assert False, "expected TypeCheckError"
    except TypeCheckError:
        pass


def test_collection_strategy() -> None:
    all_items = CollectionCheckStrategy["ALL_ITEMS"]
    assert (
        check_type(
            (1, 2, 3),
            tuple[int, ...],
            collection_check_strategy=all_items,
        )
        == (1, 2, 3)
    )
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        '''from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from featurelifted import CollectionCheckStrategy, TypeCheckError, check_type


def test_dict_nested_list() -> None:
    value = {"nums": [1, 2]}
    assert check_type(value, dict[str, list[int]]) == value


def test_first_item_strategy_can_miss() -> None:
    first = CollectionCheckStrategy["FIRST_ITEM"]
    all_items = CollectionCheckStrategy["ALL_ITEMS"]
    # FIRST_ITEM may accept heterogeneous lists that ALL_ITEMS rejects
    check_type([1, "x"], list[int], collection_check_strategy=first)
    try:
        check_type([1, "x"], list[int], collection_check_strategy=all_items)
        assert False
    except TypeCheckError:
        pass


def test_optional_reject() -> None:
    try:
        check_type("x", Optional[int])
        assert False
    except TypeCheckError:
        pass


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\\s*(?:from typeguard\\b|import typeguard\\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''from featurelifted import CollectionCheckStrategy, TypeCheckError, check_type


def test_required_api_surface() -> None:
    assert callable(check_type)
    assert TypeCheckError is not None
    assert CollectionCheckStrategy["ALL_ITEMS"] is not None
''',
        encoding="utf-8",
    )
    metadata = base_metadata(
        task_id,
        meta,
        allowed_dependencies=["typing_extensions"],
        feature={
            "name": "typeguard check_type pipeline",
            "description": "Composite typeguard check_type for nested collections/Unions.",
            "source_entrypoints": ["typeguard.check_type", "typeguard.TypeCheckError"],
            "included_behaviors": [
                "check_type for builtins and nested collections",
                "Optional/Union handling",
                "CollectionCheckStrategy FIRST_ITEM vs ALL_ITEMS",
                "TypeCheckError on mismatch",
            ],
            "excluded_behaviors": ["pytest plugin", "import hook instrumentation"],
        },
        entanglement={
            "level": "medium",
            "types": ["data_model_coupling"],
            "primary": "data_model_coupling",
            "description": "Nested type checkers compose across origins/args.",
            "signals": ["check_type", "CollectionCheckStrategy", "TypeCheckError"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import check_type, TypeCheckError",
            "callable": "check_type",
            "signature": "check_type(value, expected_type, *, collection_check_strategy=...)",
        },
        public_spec={
            "title": "typeguard check_type pipeline",
            "summary": "Extract a task-scoped subset of `typeguard` into a standalone `featurelifted` package.",
            "required_api": [
                {
                    "path": "featurelifted.check_type",
                    "kind": "function",
                    "signature": "(value, expected_type, *, collection_check_strategy=...)",
                },
                {"path": "featurelifted.TypeCheckError", "kind": "class"},
                {"path": "featurelifted.CollectionCheckStrategy", "kind": "class"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: check_type for nested list/dict. Required observable cases include nested collections."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: Optional/Union handling. Required observable cases include optional union."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: TypeCheckError on mismatch and CollectionCheckStrategy differences. Required observable cases include type check error; first item strategy can miss."},
                {"id": "B004", "text": "dict[str, list[int]] nesting is checked."},
                {"id": "B005", "text": "The package exposes check_type/TypeCheckError/CollectionCheckStrategy with the kinds listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: typeguard."},
            ],
            "exclusions": ["pytest plugin", "import hook", "original typeguard import at runtime"],
            "forbidden": {"imports": ["typeguard"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


def materialize_pykwalify() -> Path:
    task_id = "pykwalify__map_seq_validate_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["pkg_dir"](), ref, "pykwalify")
    (task_dir / "requirements.lock").write_text(
        "ruamel.yaml==0.18.6\npython-dateutil==2.9.0.post0\n",
        encoding="utf-8",
    )
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("pykwalify\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "pykwalify",
            "required_source_files": ["pykwalify/core.py", "pykwalify/rule.py", "pykwalify/errors.py"],
            "runtime_dependencies": ["ruamel.yaml", "python-dateutil"],
            "notes": "Composite Core map/seq schema validate from in-memory dicts.",
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        '''from __future__ import annotations

from featurelifted.core import Core
from featurelifted.errors import SchemaError


SCHEMA = {
    "type": "map",
    "mapping": {
        "name": {"type": "str", "required": True},
        "age": {"type": "int"},
        "tags": {"type": "seq", "sequence": [{"type": "str"}]},
    },
}


def test_validate_map_seq() -> None:
    data = {"name": "Ada", "age": 3, "tags": ["a", "b"]}
    assert Core(source_data=data, schema_data=SCHEMA).validate() == data


def test_required_key_error() -> None:
    try:
        Core(source_data={"age": 1}, schema_data=SCHEMA).validate()
        assert False, "expected SchemaError"
    except SchemaError:
        pass


def test_type_mismatch() -> None:
    try:
        Core(source_data={"name": "Ada", "age": "x"}, schema_data=SCHEMA).validate()
        assert False
    except SchemaError:
        pass
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        '''from __future__ import annotations

import re
from pathlib import Path

from featurelifted.core import Core
from featurelifted.errors import SchemaError


NESTED = {
    "type": "map",
    "mapping": {
        "items": {
            "type": "seq",
            "sequence": [
                {
                    "type": "map",
                    "mapping": {
                        "id": {"type": "int", "required": True},
                        "ok": {"type": "bool"},
                    },
                }
            ],
        }
    },
}


def test_nested_seq_map() -> None:
    data = {"items": [{"id": 1, "ok": True}, {"id": 2, "ok": False}]}
    assert Core(source_data=data, schema_data=NESTED).validate() == data


def test_nested_required_missing() -> None:
    try:
        Core(source_data={"items": [{"ok": True}]}, schema_data=NESTED).validate()
        assert False
    except SchemaError:
        pass


def test_bool_any() -> None:
    schema = {
        "type": "map",
        "mapping": {
            "flag": {"type": "bool"},
            "payload": {"type": "any"},
        },
    }
    data = {"flag": True, "payload": {"x": 1}}
    assert Core(source_data=data, schema_data=schema).validate() == data


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\\s*(?:from pykwalify\\b|import pykwalify\\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''from featurelifted.core import Core
from featurelifted.errors import SchemaError


def test_required_api_surface() -> None:
    assert Core is not None and SchemaError is not None
''',
        encoding="utf-8",
    )
    metadata = base_metadata(
        task_id,
        meta,
        allowed_dependencies=["ruamel.yaml", "python-dateutil"],
        feature={
            "name": "pykwalify map seq validate",
            "description": "Composite pykwalify Core map/seq schema validation.",
            "source_entrypoints": ["pykwalify.core.Core"],
            "included_behaviors": [
                "map/seq nested validate",
                "required keys",
                "type checks and SchemaError",
            ],
            "excluded_behaviors": ["YAML file path loading", "extensions ecosystem", "CLI"],
        },
        entanglement={
            "level": "medium",
            "types": ["data_model_coupling"],
            "primary": "data_model_coupling",
            "description": "Rule tree walks nested map/seq schemas.",
            "signals": ["Core.validate", "SchemaError", "map/seq"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted.core import Core",
            "callable": "Core.validate",
            "signature": "validate()",
        },
        public_spec={
            "title": "pykwalify map seq validate",
            "summary": "Extract a task-scoped subset of `pykwalify` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.core.Core", "kind": "class"},
                {"path": "featurelifted.errors.SchemaError", "kind": "class"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: validate map/seq schemas from in-memory dicts. Required observable cases include validate map seq."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: required key and type mismatch raise SchemaError. Required observable cases include required key error; type mismatch."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: nested seq of maps and bool/any types. Required observable cases include nested seq map; bool any."},
                {"id": "B004", "text": "Core(source_data=..., schema_data=...) is the in-memory entrypoint."},
                {"id": "B005", "text": "The package exposes featurelifted.core.Core and featurelifted.errors.SchemaError with the kinds listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: pykwalify."},
            ],
            "exclusions": ["YAML path loading", "extensions", "original pykwalify import at runtime"],
            "forbidden": {"imports": ["pykwalify"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


def materialize_strictyaml() -> Path:
    task_id = "strictyaml__schema_load_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["pkg_dir"](), ref, "strictyaml")
    (task_dir / "requirements.lock").write_text(
        "python-dateutil==2.9.0.post0\n", encoding="utf-8"
    )
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("strictyaml\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "strictyaml",
            "required_source_files": [
                "strictyaml/parser.py",
                "strictyaml/compound.py",
                "strictyaml/scalar.py",
            ],
            "runtime_dependencies": ["python-dateutil"],
            "notes": "Composite load + Map/Seq/scalar validators; ruamel vendored inside package.",
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        '''from __future__ import annotations

from featurelifted import (
    Bool,
    Int,
    Map,
    MapPattern,
    Optional,
    Seq,
    Str,
    YAMLValidationError,
    load,
)


def test_load_map_seq() -> None:
    schema = Map(
        {
            "name": Str(),
            "age": Int(),
            "tags": Seq(Str()),
            "enabled": Bool(),
            Optional("nick"): Str(),
        }
    )
    doc = load("name: Ada\\nage: 3\\ntags:\\n  - a\\n  - b\\nenabled: yes", schema)
    assert doc.data == {"name": "Ada", "age": 3, "tags": ["a", "b"], "enabled": True}


def test_validation_error() -> None:
    try:
        load("name: Ada\\nage: x", Map({"name": Str(), "age": Int()}))
        assert False, "expected YAMLValidationError"
    except YAMLValidationError:
        pass


def test_map_pattern() -> None:
    doc = load("a: 1\\nb: 2", MapPattern(Str(), Int()))
    assert doc.data == {"a": 1, "b": 2}
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        '''from __future__ import annotations

import re
from pathlib import Path

from featurelifted import Int, Map, Optional, Seq, Str, StrictYAMLError, YAMLValidationError, load


def test_optional_key_absent() -> None:
    schema = Map({"name": Str(), Optional("nick"): Str()})
    doc = load("name: Ada", schema)
    assert doc.data == {"name": "Ada"}


def test_nested_seq_map() -> None:
    schema = Map({"items": Seq(Map({"id": Int(), "label": Str()}))})
    doc = load("items:\\n  - id: 1\\n    label: a\\n  - id: 2\\n    label: b", schema)
    items = doc.data["items"]
    assert items[1]["label"] == "b"


def test_strict_error_hierarchy() -> None:
    assert issubclass(YAMLValidationError, StrictYAMLError)


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\\s*(?:from strictyaml\\b|import strictyaml\\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''from featurelifted import (
    Bool,
    Int,
    Map,
    MapPattern,
    Optional,
    Seq,
    Str,
    StrictYAMLError,
    YAMLValidationError,
    load,
)


def test_required_api_surface() -> None:
    assert callable(load)
    assert all(x is not None for x in (Map, Seq, Str, Int, Bool, Optional, MapPattern))
    assert YAMLValidationError is not None and StrictYAMLError is not None
''',
        encoding="utf-8",
    )
    metadata = base_metadata(
        task_id,
        meta,
        allowed_dependencies=["python-dateutil"],
        feature={
            "name": "strictyaml schema load",
            "description": "Composite strictyaml load + Map/Seq/scalar validators.",
            "source_entrypoints": ["strictyaml.load", "strictyaml.Map", "strictyaml.Seq"],
            "included_behaviors": [
                "load YAML string against schema",
                "Map/Seq/scalars/Optional/MapPattern",
                "YAMLValidationError on mismatch",
            ],
            "excluded_behaviors": ["external ruamel fancy types beyond vendored subset"],
        },
        entanglement={
            "level": "medium",
            "types": ["data_model_coupling"],
            "primary": "data_model_coupling",
            "description": "Schema combinators + loader produce typed YAML objects.",
            "signals": ["load", "Map/Seq", "YAMLValidationError"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import load, Map, Seq, Str, Int",
            "callable": "load",
            "signature": "load(yaml_string: str, schema, label: str = 'string')",
        },
        public_spec={
            "title": "strictyaml schema load",
            "summary": "Extract a task-scoped subset of `strictyaml` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.load", "kind": "function", "signature": "(yaml_string, schema, label='string')"},
                {"path": "featurelifted.Map", "kind": "class"},
                {"path": "featurelifted.Seq", "kind": "class"},
                {"path": "featurelifted.Str", "kind": "class"},
                {"path": "featurelifted.Int", "kind": "class"},
                {"path": "featurelifted.Bool", "kind": "class"},
                {"path": "featurelifted.Optional", "kind": "class"},
                {"path": "featurelifted.MapPattern", "kind": "class"},
                {"path": "featurelifted.YAMLValidationError", "kind": "class"},
                {"path": "featurelifted.StrictYAMLError", "kind": "class"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: load Map/Seq/Bool schemas to .data primitives. Required observable cases include load map seq."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: YAMLValidationError on type mismatch. Required observable cases include validation error."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: Optional keys and MapPattern. Required observable cases include optional key absent; map pattern."},
                {"id": "B004", "text": "YAMLValidationError is a StrictYAMLError subclass."},
                {"id": "B005", "text": "The package exposes load and declared validators/errors with the kinds listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: strictyaml."},
            ],
            "exclusions": ["external ruamel beyond vendored", "original strictyaml import at runtime"],
            "forbidden": {"imports": ["strictyaml"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


def materialize_premailer() -> Path:
    task_id = "premailer__inline_css_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["pkg_dir"](), ref, "premailer")
    (task_dir / "requirements.lock").write_text(
        "\n".join(
            [
                "lxml==5.2.1",
                "cssselect==1.2.0",
                "cssutils==2.15.0",
                "requests==2.32.3",
                "cachetools==5.3.3",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("premailer\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "premailer",
            "required_source_files": ["premailer/premailer.py"],
            "runtime_dependencies": ["lxml", "cssselect", "cssutils", "requests", "cachetools"],
            "notes": "Composite HTML+CSS inline via Premailer.transform; offline HTML strings only.",
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        '''from __future__ import annotations

from featurelifted import Premailer, transform


HTML = (
    "<html><head><style>a{color:red}</style></head>"
    '<body><a class="x" href="#">hi</a></body></html>'
)


def test_transform_inlines_style() -> None:
    out = transform(HTML)
    assert "color" in out and "red" in out
    assert "hi" in out


def test_premailer_remove_classes() -> None:
    out = Premailer(HTML, remove_classes=True).transform()
    assert "class=" not in out
    assert "color" in out


def test_keep_style_tags_option() -> None:
    out = Premailer(HTML, keep_style_tags=True).transform()
    assert "<style" in out.lower()
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        '''from __future__ import annotations

import re
from pathlib import Path

from featurelifted import Premailer, transform


def test_strip_important_default_keeps_or_strips() -> None:
    html = (
        "<html><head><style>p{color:blue !important}</style></head>"
        "<body><p>x</p></body></html>"
    )
    out = transform(html)
    assert "blue" in out and "x" in out


def test_multiple_rules() -> None:
    html = (
        "<html><head><style>a{color:red} a.b{font-weight:bold}</style></head>"
        '<body><a class="b" href="#">z</a></body></html>'
    )
    out = Premailer(html, remove_classes=True).transform()
    assert "z" in out
    assert "color" in out


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\\s*(?:from premailer\\b|import premailer\\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''from featurelifted import Premailer, transform


def test_required_api_surface() -> None:
    assert Premailer is not None and callable(transform)
''',
        encoding="utf-8",
    )
    metadata = base_metadata(
        task_id,
        meta,
        allowed_dependencies=["lxml", "cssselect", "cssutils", "requests", "cachetools"],
        feature={
            "name": "premailer inline css",
            "description": "Composite premailer HTML+CSS inlining via Premailer/transform.",
            "source_entrypoints": ["premailer.Premailer", "premailer.transform"],
            "included_behaviors": [
                "inline style tags into element style attributes",
                "remove_classes option",
                "keep_style_tags option",
            ],
            "excluded_behaviors": ["remote CSS URL fetching in tests", "networked base_url"],
        },
        entanglement={
            "level": "high",
            "types": ["parser_state_coupling"],
            "primary": "parser_state_coupling",
            "description": "HTML parse + CSS parse + style merge.",
            "signals": ["Premailer.transform", "cssutils", "lxml"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import Premailer, transform",
            "callable": "transform",
            "signature": "transform(html: str, **options) -> str",
        },
        public_spec={
            "title": "premailer inline css",
            "summary": "Extract a task-scoped subset of `premailer` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.Premailer", "kind": "class"},
                {"path": "featurelifted.Premailer.transform", "kind": "method", "signature": "() -> str"},
                {"path": "featurelifted.transform", "kind": "function", "signature": "(html: str, **options) -> str"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: transform inlines CSS color into HTML. Required observable cases include transform inlines style."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: remove_classes strips class attributes. Required observable cases include premailer remove classes."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: keep_style_tags retains style elements when set. Required observable cases include keep style tags option."},
                {"id": "B004", "text": "Multiple CSS rules can apply to anchors."},
                {"id": "B005", "text": "The package exposes Premailer and transform with the kinds listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: premailer."},
            ],
            "exclusions": ["remote CSS fetch in tests", "original premailer import at runtime"],
            "forbidden": {"imports": ["premailer"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


def materialize_textx() -> Path:
    task_id = "textx__metamodel_model_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["pkg_dir"](), ref, "textx")
    (task_dir / "requirements.lock").write_text(
        "Arpeggio==2.0.3\nclick==8.1.7\n", encoding="utf-8"
    )
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("textx\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "textx",
            "required_source_files": ["textx/metamodel.py", "textx/model.py", "textx/exceptions.py"],
            "runtime_dependencies": ["Arpeggio", "click"],
            "notes": "Composite metamodel_from_str + model_from_str.",
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        '''from __future__ import annotations

from featurelifted import metamodel_from_str
from featurelifted.exceptions import TextXSyntaxError


GRAMMAR = """
Model: 'hello' name=ID;
"""


def test_metamodel_and_model() -> None:
    mm = metamodel_from_str(GRAMMAR)
    model = mm.model_from_str("hello Ada")
    assert model.name == "Ada"


def test_syntax_error() -> None:
    mm = metamodel_from_str(GRAMMAR)
    try:
        mm.model_from_str("bye")
        assert False, "expected TextXSyntaxError"
    except TextXSyntaxError:
        pass


def test_nested_attributes() -> None:
    mm = metamodel_from_str(
        """
Model: 'person' name=ID age=INT;
"""
    )
    model = mm.model_from_str("person Bob 42")
    assert model.name == "Bob" and model.age == 42
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        '''from __future__ import annotations

import re
from pathlib import Path

from featurelifted import metamodel_from_str
from featurelifted.exceptions import TextXError, TextXSyntaxError


def test_list_of_objects() -> None:
    mm = metamodel_from_str(
        """
Model: items+=Item;
Item: 'item' name=ID;
"""
    )
    model = mm.model_from_str("item a item b")
    assert [i.name for i in model.items] == ["a", "b"]


def test_textx_error_hierarchy() -> None:
    assert issubclass(TextXSyntaxError, TextXError)


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\\s*(?:from textx\\b|import textx\\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''from featurelifted import metamodel_from_str
from featurelifted.exceptions import TextXError, TextXSyntaxError


def test_required_api_surface() -> None:
    assert callable(metamodel_from_str)
    assert TextXSyntaxError is not None and TextXError is not None
''',
        encoding="utf-8",
    )
    metadata = base_metadata(
        task_id,
        meta,
        allowed_dependencies=["Arpeggio", "click"],
        feature={
            "name": "textX metamodel model",
            "description": "Composite textX metamodel_from_str + model_from_str.",
            "source_entrypoints": ["textx.metamodel_from_str"],
            "included_behaviors": [
                "build metamodel from grammar string",
                "parse model instance attributes",
                "TextXSyntaxError on bad input",
            ],
            "excluded_behaviors": ["textX CLI", "scoping advanced features"],
        },
        entanglement={
            "level": "high",
            "types": ["parser_state_coupling"],
            "primary": "parser_state_coupling",
            "description": "Grammar metamodel and model parse are dual surfaces.",
            "signals": ["metamodel_from_str", "model_from_str", "Arpeggio"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import metamodel_from_str",
            "callable": "metamodel_from_str",
            "signature": "metamodel_from_str(grammar: str, **kwargs)",
        },
        public_spec={
            "title": "textX metamodel model",
            "summary": "Extract a task-scoped subset of `textX` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.metamodel_from_str", "kind": "function", "signature": "(grammar: str, **kwargs)"},
                {"path": "featurelifted.exceptions.TextXSyntaxError", "kind": "class"},
                {"path": "featurelifted.exceptions.TextXError", "kind": "class"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: metamodel_from_str + model_from_str attribute access. Required observable cases include metamodel and model."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: TextXSyntaxError on invalid model text. Required observable cases include syntax error."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: nested attributes and list of objects. Required observable cases include nested attributes; list of objects."},
                {"id": "B004", "text": "TextXSyntaxError is a TextXError subclass."},
                {"id": "B005", "text": "The package exposes metamodel_from_str and TextXSyntaxError/TextXError with the kinds listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: textx."},
            ],
            "exclusions": ["textX CLI", "original textx import at runtime"],
            "forbidden": {"imports": ["textx"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


def materialize_frictionless() -> Path:
    task_id = "frictionless__schema_resource_validate_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["pkg_dir"](), ref, "frictionless")
    # Absolute-import rewrite leaves bare ``return frictionless`` in platform.py.
    platform_py = ref / "platform.py"
    platform_py.write_text(
        platform_py.read_text(encoding="utf-8").replace(
            "        return frictionless\n",
            "        return featurelifted\n",
        ),
        encoding="utf-8",
    )
    # Drop embedded upstream tests from the agent package surface.
    for spec_dir in ref.rglob("__spec__"):
        if spec_dir.is_dir():
            shutil.rmtree(spec_dir)
    allowed = [
        "petl",
        "marko",
        "attrs",
        "jinja2",
        "PyYAML",
        "isodate",
        "rfc3986",
        "chardet",
        "pydantic",
        "requests",
        "humanize",
        "tabulate",
        "jsonschema",
        "simpleeval",
        "typer",
        "validators",
        "python-slugify",
        "python-dateutil",
        "typing_extensions",
    ]
    lock_lines = [
        "petl==1.7.22",
        "marko==2.2.3",
        "attrs==23.1.0",
        "jinja2==3.1.4",
        "PyYAML==6.0.1",
        "isodate==0.7.2",
        "rfc3986==2.0.0",
        "chardet==7.4.3",
        "pydantic==2.12.3",
        "requests==2.32.3",
        "humanize==4.15.0",
        "tabulate==0.9.0",
        "jsonschema==4.23.0",
        "simpleeval==1.0.7",
        "typer==0.27.0",
        "validators==0.35.0",
        "python-slugify==5.0.2",
        "python-dateutil==2.9.0.post0",
        "typing_extensions==4.15.0",
        "",
    ]
    (task_dir / "requirements.lock").write_text("\n".join(lock_lines), encoding="utf-8")
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("frictionless\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "frictionless",
            "required_source_files": [
                "frictionless/schema/schema.py",
                "frictionless/resource/resource.py",
                "frictionless/report/report.py",
            ],
            "runtime_dependencies": allowed,
            "notes": "Composite Schema + Resource.validate Report pipeline; inline data only.",
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        '''from __future__ import annotations

from featurelifted import Resource, Schema


SCHEMA_DESC = {
    "fields": [
        {"name": "id", "type": "integer"},
        {"name": "name", "type": "string"},
    ]
}


def test_schema_from_descriptor() -> None:
    schema = Schema.from_descriptor(SCHEMA_DESC)
    assert [f.name for f in schema.fields] == ["id", "name"]


def test_resource_validate_ok() -> None:
    schema = Schema.from_descriptor(SCHEMA_DESC)
    resource = Resource(data=[{"id": 1, "name": "a"}, {"id": 2, "name": "b"}], schema=schema)
    report = resource.validate()
    assert report.valid is True


def test_resource_validate_type_error() -> None:
    schema = Schema.from_descriptor(SCHEMA_DESC)
    resource = Resource(data=[{"id": "x", "name": "a"}], schema=schema)
    report = resource.validate()
    assert report.valid is False
    assert report.tasks and report.tasks[0].errors
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        '''from __future__ import annotations

import re
from pathlib import Path

from featurelifted import Resource, Schema


def test_required_field() -> None:
    schema = Schema.from_descriptor(
        {
            "fields": [
                {"name": "id", "type": "integer", "constraints": {"required": True}},
                {"name": "name", "type": "string"},
            ]
        }
    )
    report = Resource(data=[{"name": "a"}], schema=schema).validate()
    assert report.valid is False


def test_report_stats_errors() -> None:
    schema = Schema.from_descriptor(
        {"fields": [{"name": "id", "type": "integer"}, {"name": "name", "type": "string"}]}
    )
    report = Resource(data=[{"id": 1, "name": "ok"}], schema=schema).validate()
    assert report.valid is True
    assert report.stats["errors"] == 0


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\\s*(?:from frictionless\\b|import frictionless\\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''from featurelifted import Resource, Schema


def test_required_api_surface() -> None:
    assert Schema is not None and Resource is not None
    assert callable(Schema.from_descriptor)
''',
        encoding="utf-8",
    )
    metadata = base_metadata(
        task_id,
        meta,
        allowed_dependencies=allowed,
        timeout=120,
        feature={
            "name": "frictionless schema resource validate",
            "description": "Composite Schema + Resource.validate Report pipeline.",
            "source_entrypoints": [
                "frictionless.Schema",
                "frictionless.Resource",
            ],
            "included_behaviors": [
                "Schema.from_descriptor",
                "Resource inline data validate",
                "Report.valid and task errors",
            ],
            "excluded_behaviors": ["remote URL resources", "full checklist plugin ecosystem"],
        },
        entanglement={
            "level": "high",
            "types": ["data_model_coupling"],
            "primary": "data_model_coupling",
            "description": "Schema/resource/report compose validation pipeline.",
            "signals": ["Schema", "Resource.validate", "Report"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import Schema, Resource",
            "callable": "Resource.validate",
            "signature": "validate() -> Report",
        },
        public_spec={
            "title": "frictionless schema resource validate",
            "summary": "Extract a task-scoped subset of `frictionless` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.Schema", "kind": "class"},
                {"path": "featurelifted.Schema.from_descriptor", "kind": "method"},
                {"path": "featurelifted.Resource", "kind": "class"},
                {"path": "featurelifted.Resource.validate", "kind": "method", "signature": "() -> Report"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: Schema.from_descriptor builds fields. Required observable cases include schema from descriptor."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: Resource.validate returns Report.valid True/False. Required observable cases include resource validate ok; resource validate type error."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: required field constraints fail validation. Required observable cases include required field."},
                {"id": "B004", "text": "Report.stats exposes error counts on success."},
                {"id": "B005", "text": "The package exposes Schema and Resource with the kinds listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: frictionless."},
            ],
            "exclusions": ["remote URL resources", "original frictionless import at runtime"],
            "forbidden": {"imports": ["frictionless"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


def materialize_libcst() -> Path:
    task_id = "libcst__parse_transform_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["pkg_dir"](), ref, "libcst")
    (task_dir / "requirements.lock").write_text("PyYAML==6.0.3\n", encoding="utf-8")
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("libcst\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "libcst",
            "required_source_files": ["libcst/_parser/entrypoints.py", "libcst/_visitors.py"],
            "runtime_dependencies": ["PyYAML"],
            "notes": (
                "Composite parse_module + CSTTransformer + codegen. "
                "Reference uses PyPI wheel native parser (platform-specific .so)."
            ),
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        '''from __future__ import annotations

from featurelifted import CSTTransformer, ParserSyntaxError, parse_module


def test_parse_and_codegen() -> None:
    module = parse_module("x = 1\\n")
    assert "x = 1" in module.code


def test_transformer_rename() -> None:
    module = parse_module("x = 1\\n")

    class Rename(CSTTransformer):
        def leave_Name(self, original_node, updated_node):
            if original_node.value == "x":
                return updated_node.with_changes(value="y")
            return updated_node

    assert "y = 1" in module.visit(Rename()).code


def test_parser_syntax_error() -> None:
    try:
        parse_module("def (")
        assert False, "expected ParserSyntaxError"
    except ParserSyntaxError:
        pass
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        '''from __future__ import annotations

import re
from pathlib import Path

from featurelifted import CSTTransformer, RemovalSentinel, parse_module


def test_remove_statement() -> None:
    module = parse_module("a = 1\\nb = 2\\n")

    class DropA(CSTTransformer):
        def leave_SimpleStatementLine(self, original_node, updated_node):
            text = module.code_for_node(original_node)
            if text.strip().startswith("a"):
                return RemovalSentinel.REMOVE
            return updated_node

    out = module.visit(DropA()).code
    assert "a = 1" not in out
    assert "b = 2" in out


def test_code_for_node() -> None:
    module = parse_module("value = 3\\n")
    assert "value" in module.code


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\\s*(?:from libcst\\b|import libcst\\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''from featurelifted import CSTTransformer, ParserSyntaxError, RemovalSentinel, parse_module


def test_required_api_surface() -> None:
    assert callable(parse_module)
    assert CSTTransformer is not None
    assert ParserSyntaxError is not None
    assert RemovalSentinel is not None
''',
        encoding="utf-8",
    )
    metadata = base_metadata(
        task_id,
        meta,
        allowed_dependencies=["PyYAML"],
        feature={
            "name": "libcst parse transform",
            "description": "Composite libcst parse_module + CSTTransformer + codegen.",
            "source_entrypoints": ["libcst.parse_module", "libcst.CSTTransformer"],
            "included_behaviors": [
                "parse_module to Module with .code",
                "CSTTransformer leave_* rewrites",
                "ParserSyntaxError",
                "RemovalSentinel removals",
            ],
            "excluded_behaviors": ["metadata wrappers", "codemod CLI"],
        },
        entanglement={
            "level": "high",
            "types": ["parser_state_coupling"],
            "primary": "parser_state_coupling",
            "description": "Parse/transform/codegen CST pipeline.",
            "signals": ["parse_module", "CSTTransformer", "RemovalSentinel"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import parse_module, CSTTransformer",
            "callable": "parse_module",
            "signature": "parse_module(source: str) -> Module",
        },
        public_spec={
            "title": "libcst parse transform",
            "summary": "Extract a task-scoped subset of `libcst` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.parse_module", "kind": "function", "signature": "(source: str) -> Module"},
                {"path": "featurelifted.CSTTransformer", "kind": "class"},
                {"path": "featurelifted.ParserSyntaxError", "kind": "class"},
                {"path": "featurelifted.RemovalSentinel", "kind": "class"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: parse_module exposes Module.code. Required observable cases include parse and codegen."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: CSTTransformer can rename Name nodes. Required observable cases include transformer rename."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: ParserSyntaxError on invalid syntax and RemovalSentinel removals. Required observable cases include parser syntax error; remove statement."},
                {"id": "B004", "text": "Module.code roundtrips simple assignments."},
                {"id": "B005", "text": "The package exposes parse_module/CSTTransformer/ParserSyntaxError/RemovalSentinel with the kinds listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: libcst."},
            ],
            "exclusions": ["metadata wrappers", "codemod CLI", "original libcst import at runtime"],
            "forbidden": {"imports": ["libcst"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


def materialize_unidiff() -> Path:
    task_id = "unidiff__patch_hunk_core__001"
    meta = PINS[task_id]
    task_dir = _prepare(task_id, meta)
    ref = task_dir / "reference_solution" / "featurelifted"
    copy_package_tree(meta["pkg_dir"](), ref, "unidiff")
    (task_dir / "requirements.lock").write_text("# no third-party dependencies\n", encoding="utf-8")
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("unidiff\n", encoding="utf-8")
    write_json(
        task_dir / "evaluation" / "oracle_manifest.json",
        {
            "source_package_name": "unidiff",
            "required_source_files": ["unidiff/patch.py", "unidiff/__init__.py"],
            "runtime_dependencies": [],
            "notes": "Composite PatchSet + PatchedFile + Hunk model (W2 libcst native-blocked backup).",
        },
    )
    (task_dir / "public_tests" / "test_public_api.py").write_text(
        '''from __future__ import annotations

from featurelifted import LINE_TYPE_ADDED, LINE_TYPE_REMOVED, PatchSet, UnidiffParseError


SAMPLE = """--- a/file.py
+++ b/file.py
@@ -1,2 +1,3 @@
 def f():
-    return 1
+    return 2
+    # note
"""


def test_parse_patchset() -> None:
    ps = PatchSet(SAMPLE)
    assert len(ps) == 1
    assert ps[0].path == "file.py"
    assert len(ps[0]) == 1


def test_hunk_lines() -> None:
    hunk = PatchSet(SAMPLE)[0][0]
    added = [line.value for line in hunk if line.line_type == LINE_TYPE_ADDED]
    removed = [line.value for line in hunk if line.line_type == LINE_TYPE_REMOVED]
    assert any("return 2" in v for v in added)
    assert any("return 1" in v for v in removed)


def test_parse_error_short_hunk() -> None:
    bad = "--- a/x\\n+++ b/x\\n@@ -1,1 +1,1 @@\\n+only\\n"
    try:
        PatchSet(bad)
        assert False, "expected UnidiffParseError"
    except UnidiffParseError:
        pass
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden_behavior.py").write_text(
        '''from __future__ import annotations

import re
from pathlib import Path

from featurelifted import LINE_TYPE_CONTEXT, PatchSet, PatchedFile


MULTI = """--- a/a.py
+++ b/a.py
@@ -1,1 +1,1 @@
-old
+new
--- a/b.py
+++ b/b.py
@@ -1,1 +1,2 @@
 keep
+extra
"""


def test_multiple_files() -> None:
    ps = PatchSet(MULTI)
    assert len(ps) == 2
    assert {pf.path for pf in ps} == {"a.py", "b.py"}
    assert all(isinstance(pf, PatchedFile) for pf in ps)


def test_context_lines() -> None:
    sample = """--- a/file.py
+++ b/file.py
@@ -1,2 +1,3 @@
 def f():
-    return 1
+    return 2
+    # note
"""
    hunk = PatchSet(sample)[0][0]
    ctx = [line.value for line in hunk if line.line_type == LINE_TYPE_CONTEXT]
    assert any("def f" in v for v in ctx)


def test_added_removed_counts() -> None:
    ps = PatchSet(
        """--- a/file.py
+++ b/file.py
@@ -1,2 +1,3 @@
 def f():
-    return 1
+    return 2
+    # note
"""
    )
    pf = ps[0]
    assert pf.added > 0 and pf.removed > 0


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\\s*(?:from unidiff\\b|import unidiff\\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
''',
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_required_api_surface.py").write_text(
        '''from featurelifted import Hunk, PatchSet, PatchedFile, UnidiffParseError


def test_required_api_surface() -> None:
    assert PatchSet is not None and PatchedFile is not None
    assert Hunk is not None and UnidiffParseError is not None
''',
        encoding="utf-8",
    )
    metadata = base_metadata(
        task_id,
        meta,
        feature={
            "name": "unidiff patch hunk",
            "description": "Composite unidiff PatchSet + PatchedFile + Hunk line model.",
            "source_entrypoints": ["unidiff.PatchSet", "unidiff.PatchedFile", "unidiff.Hunk"],
            "included_behaviors": [
                "parse unified diff into PatchSet",
                "hunk added/removed/context lines",
                "UnidiffParseError on malformed hunks",
            ],
            "excluded_behaviors": ["git apply execution", "binary diffs"],
        },
        entanglement={
            "level": "medium",
            "types": ["parser_state_coupling"],
            "primary": "parser_state_coupling",
            "description": "Patch parse builds file/hunk/line object model.",
            "signals": ["PatchSet", "Hunk", "LINE_TYPE_*"],
        },
        output={
            "package": "featurelifted",
            "import": "from featurelifted import PatchSet, UnidiffParseError",
            "callable": "PatchSet",
            "signature": "PatchSet(diff: str)",
        },
        public_spec={
            "title": "unidiff patch hunk",
            "summary": "Extract a task-scoped subset of `unidiff` into a standalone `featurelifted` package.",
            "required_api": [
                {"path": "featurelifted.PatchSet", "kind": "class"},
                {"path": "featurelifted.PatchedFile", "kind": "class"},
                {"path": "featurelifted.Hunk", "kind": "class"},
                {"path": "featurelifted.UnidiffParseError", "kind": "class"},
                {"path": "featurelifted.LINE_TYPE_ADDED", "kind": "constant"},
                {"path": "featurelifted.LINE_TYPE_REMOVED", "kind": "constant"},
                {"path": "featurelifted.LINE_TYPE_CONTEXT", "kind": "constant"},
            ],
            "optional_api": [],
            "behaviors": [
                {"id": "B001", "text": "The extracted feature must support this observable behavior: PatchSet parses unified diffs into PatchedFile/Hunk. Required observable cases include parse patchset."},
                {"id": "B002", "text": "The extracted feature must support this observable behavior: hunk lines expose added/removed/context types. Required observable cases include hunk lines; context lines."},
                {"id": "B003", "text": "The extracted feature must support this observable behavior: UnidiffParseError on short hunks and multi-file patches. Required observable cases include parse error short hunk; multiple files."},
                {"id": "B004", "text": "PatchedFile exposes added/removed counts."},
                {"id": "B005", "text": "The package exposes PatchSet/PatchedFile/Hunk/UnidiffParseError/LINE_TYPE_* with the kinds listed in this contract."},
                {"id": "B006", "text": "the submitted package does not import forbidden upstream packages: unidiff."},
            ],
            "exclusions": ["git apply", "binary diffs", "original unidiff import at runtime"],
            "forbidden": {"imports": ["unidiff"], "paths": []},
        },
    )
    finalize_metadata(task_dir, metadata)
    make_archive_and_register(task_id, meta, task_dir / "repo")
    return task_dir


BUILDERS: dict[str, Callable[[], Path]] = {
    "toolz__compose_pipe_core__001": materialize_toolz,
    "anytree__tree_resolve_render_core__001": materialize_anytree,
    "parsimonious__grammar_visitor_core__001": materialize_parsimonious,
    "typeguard__check_type_pipeline_core__001": materialize_typeguard,
    "pykwalify__map_seq_validate_core__001": materialize_pykwalify,
    "strictyaml__schema_load_core__001": materialize_strictyaml,
    "premailer__inline_css_core__001": materialize_premailer,
    "textx__metamodel_model_core__001": materialize_textx,
    "frictionless__schema_resource_validate_core__001": materialize_frictionless,
    "libcst__parse_transform_core__001": materialize_libcst,
    "unidiff__patch_hunk_core__001": materialize_unidiff,
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
