#!/usr/bin/env python3
"""Scaffold metadata, tests, manifests, and design notes for batch-4 tasks."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
TASKS = _REPO / "benchmark" / "tasks"
DESIGNS = _REPO / "docs" / "task_designs"

FAKER_MANIFEST = [
    "faker/__init__.py",
    "faker/config.py",
    "faker/exceptions.py",
    "faker/factory.py",
    "faker/generator.py",
    "faker/proxy.py",
    "faker/typing.py",
    "faker/utils/__init__.py",
    "faker/utils/checksums.py",
    "faker/utils/datasets.py",
    "faker/utils/decorators.py",
    "faker/utils/distribution.py",
    "faker/utils/loading.py",
    "faker/utils/text.py",
    "faker/providers/__init__.py",
    "faker/providers/person/__init__.py",
    "faker/providers/person/en/__init__.py",
    "faker/providers/person/en_US/__init__.py",
    "faker/providers/address/__init__.py",
    "faker/providers/address/en/__init__.py",
    "faker/providers/address/en_US/__init__.py",
    "faker/providers/phone_number/__init__.py",
    "faker/providers/phone_number/en_US/__init__.py",
    "faker/providers/date_time/__init__.py",
]

BABEL_MANIFEST = [
    "babel/__init__.py",
    "babel/core.py",
    "babel/plural.py",
    "babel/localedata.py",
    "babel/global.dat",
    "babel/locale-data/root.dat",
    "babel/locale-data/en.dat",
    "babel/locale-data/ru.dat",
    "babel/locale-data/fr.dat",
    "babel/locale-data/ja.dat",
    "babel/locale-data/pl.dat",
]


def discover_py_and_lark(repo: Path, package: str) -> list[str]:
    skip = {"__pycache__", "tools", "__pyinstaller"}
    files: list[str] = []
    root = repo / package
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix not in {".py", ".lark", ".typed", ".pyi"}:
            continue
        rel = path.relative_to(repo).as_posix()
        if any(part in skip for part in Path(rel).parts):
            continue
        files.append(rel)
    return files


TASK_SPECS: dict[str, dict] = {
    "faker__provider_core__001": {
        "commit": "40.23.0-installed-snapshot",
        "source_name": "Faker",
        "source_url": "https://github.com/joke2k/faker",
        "license": "MIT",
        "feature_name": "Single-locale Faker providers",
        "description": "Extract Faker factory and Generator wiring for en_US person, address, and phone_number providers with embedded locale data.",
        "entrypoints": [
            "faker.proxy.Faker",
            "faker.factory.Factory.create",
            "faker.providers.person.en_US",
            "faker.providers.address.en_US",
            "faker.providers.phone_number.en_US",
        ],
        "included": [
            "construct Faker with locale en_US and default person/address/phone providers",
            "generate deterministic fake names, addresses, and phone numbers with seed_instance",
            "resolve localized provider modules and locale resource data",
        ],
        "excluded": [
            "multi-locale weighting and proxy locale switching",
            "CLI, pytest plugin, and documentation",
            "providers beyond person, address, and phone_number",
        ],
        "entanglement": {
            "level": "high",
            "types": ["resource_coupling", "implicit_dependency_coupling", "global_state_registry_coupling"],
            "primary": "resource_coupling",
            "description": "Provider methods depend on locale-specific data tables loaded through dynamic provider discovery and import paths.",
            "signals": [
                "locale-scoped provider modules with embedded name/address lists",
                "factory provider registration and weighted sampling",
                "generator locale configuration",
            ],
        },
        "output_import": "from featurelifted import Faker",
        "callable": "featurelifted.Faker",
        "signature": "Faker(locale: str = 'en_US', providers: list[str] | None = None, **config)",
        "forbidden": ["faker"],
        "manifest": FAKER_MANIFEST,
        "manifest_package": "faker",
        "manifest_notes": "Oracle closure limited to en_US person/address/phone_number providers plus factory core.",
    },
    "lark__grammar_loader_core__001": {
        "commit": "1.3.1-installed-snapshot",
        "source_name": "lark",
        "source_url": "https://github.com/lark-parser/lark",
        "license": "MIT",
        "feature_name": "Grammar file loading",
        "description": "Extract Lark grammar loading from files and packages, including %import relative paths and packaged grammars/common.lark.",
        "entrypoints": [
            "lark.Lark",
            "lark.Lark.open",
            "lark.Lark.open_from_package",
            "lark.load_grammar.load_grammar",
        ],
        "included": [
            "load grammars from strings and files with Lark.open(rel_to=...)",
            "resolve relative %import directives across grammar files",
            "load packaged grammars via open_from_package and %import common.*",
            "parse inputs with lalr after grammar compilation",
        ],
        "excluded": [
            "standalone codegen tools and CLI",
            "serialization caches beyond compile-time loading",
            "original project tests",
        ],
        "entanglement": {
            "level": "high",
            "types": ["resource_coupling", "parser_state_coupling", "implicit_dependency_coupling"],
            "primary": "resource_coupling",
            "description": "Grammar compilation pulls in file-system and package-resource loaders, import paths, and lexer/parser construction.",
            "signals": [
                "multi-file grammar import graph",
                "package resource loader for grammars/common.lark",
                "grammar builder and parser frontend wiring",
            ],
        },
        "output_import": "from featurelifted import Lark",
        "callable": "featurelifted.Lark.open",
        "signature": "Lark.open(grammar_filename: str, rel_to: str | None = None, **options) -> Lark",
        "forbidden": ["lark"],
        "manifest": "discover:lark",
        "manifest_package": "lark",
        "manifest_notes": "Full lark runtime minus tools/; includes grammars/ resources for %import common.",
    },
    "rich__markup_parse_core__001": {
        "commit": "13.7.1-installed-snapshot",
        "source_name": "rich",
        "source_url": "https://github.com/Textualize/rich",
        "license": "MIT",
        "feature_name": "Console markup parsing",
        "description": "Extract Rich console markup rendering into Text spans, including escaping, nested styles, links, and error handling.",
        "entrypoints": [
            "rich.markup.render",
            "rich.markup.escape",
            "rich.text.Text.from_markup",
            "rich.errors.MarkupError",
        ],
        "included": [
            "render markup tags into Text with style spans",
            "escape square brackets for literal markup",
            "support nested/open/close tags and link metadata",
            "raise MarkupError on mismatched closing tags",
        ],
        "excluded": [
            "full Console rendering pipeline and terminal detection",
            "progress bars, tables, and layout renderables",
            "syntax highlighting and live displays",
        ],
        "entanglement": {
            "level": "high",
            "types": ["parser_state_coupling", "implicit_dependency_coupling", "data_model_coupling"],
            "primary": "parser_state_coupling",
            "description": "Markup parsing maintains style stacks, span lists, and emoji normalization while building Text objects.",
            "signals": [
                "tag open/close stack with implicit close",
                "style span accumulation on Text",
                "escaped bracket handling",
            ],
        },
        "output_import": "from featurelifted.markup import render, escape; from featurelifted.text import Text; from featurelifted.errors import MarkupError",
        "callable": "featurelifted.markup.render",
        "signature": "render(markup: str, style: str | Style = '', emoji: bool = True) -> Text",
        "forbidden": ["rich"],
        "manifest": "discover:rich",
        "manifest_package": "rich",
        "manifest_notes": "Markup rendering closure includes text/style/emoji support modules.",
    },
    "marshmallow__schema_core__001": {
        "commit": "4.3.0-installed-snapshot",
        "source_name": "marshmallow",
        "source_url": "https://github.com/marshmallow-code/marshmallow",
        "license": "MIT",
        "feature_name": "Schema load and dump",
        "description": "Extract Marshmallow Schema declaration, field validation, nested schemas, and load/dump round-trips.",
        "entrypoints": [
            "marshmallow.Schema",
            "marshmallow.fields",
            "marshmallow.ValidationError",
            "marshmallow.schema.Schema.load",
            "marshmallow.schema.Schema.dump",
        ],
        "included": [
            "declare Schema subclasses with typed fields",
            "load dict payloads with validation and nested schemas",
            "dump objects to dicts with field selection",
            "handle unknown=EXCLUDE and partial load validation errors",
        ],
        "excluded": [
            "flask-smorest and web framework integrations",
            "original project tests and packaging metadata",
            "schema class registry across entry points",
        ],
        "entanglement": {
            "level": "high",
            "types": ["data_model_coupling", "framework_coupling", "implicit_dependency_coupling"],
            "primary": "data_model_coupling",
            "description": "Schema load/dump couples field descriptors, nested schema graphs, error stores, and decorator hooks.",
            "signals": [
                "nested Schema and List(Field) graphs",
                "pre/post load and dump hooks",
                "ValidationError aggregation",
            ],
        },
        "output_import": "from featurelifted import Schema, fields, ValidationError, EXCLUDE, RAISE",
        "callable": "featurelifted.Schema.load",
        "signature": "Schema.load(data, *, many: bool = False, partial=None, unknown=RAISE)",
        "forbidden": ["marshmallow"],
        "manifest": "discover:marshmallow",
        "manifest_package": "marshmallow",
        "manifest_notes": "Full marshmallow runtime package (pure Python).",
    },
    "babel__plural_core__001": {
        "commit": "2.11.0-installed-snapshot",
        "source_name": "babel",
        "source_url": "https://github.com/python-babel/babel",
        "license": "BSD-3-Clause",
        "feature_name": "CLDR plural rules subset",
        "description": "Extract Babel plural rule parsing and locale plural_form selection backed by CLDR locale-data files.",
        "entrypoints": [
            "babel.plural.PluralRule",
            "babel.core.Locale",
            "babel.core.Locale.plural_form",
            "babel.localedata",
        ],
        "included": [
            "evaluate PluralRule expressions for numeric operands",
            "resolve Locale plural categories for en, ru, fr, ja, and pl",
            "load plural rules from packaged locale-data .dat resources",
        ],
        "excluded": [
            "gettext message catalogs and extraction",
            "number/date/currency formatting modules",
            "full CLDR locale-data tree",
        ],
        "entanglement": {
            "level": "high",
            "types": ["third_party_dependency_coupling", "resource_coupling", "data_model_coupling"],
            "primary": "third_party_dependency_coupling",
            "description": "Plural selection depends on CLDR locale-data pickles, plural expression parsing, and Locale metadata wiring.",
            "signals": [
                "locale-data .dat resource loading",
                "PluralRule expression AST evaluation",
                "Locale inheritance through parent locales",
            ],
        },
        "output_import": "from featurelifted import PluralRule, Locale",
        "callable": "featurelifted.Locale.parse",
        "signature": "Locale.parse(identifier: str) -> Locale",
        "forbidden": ["babel"],
        "allowed_dependencies": [],
        "manifest": BABEL_MANIFEST,
        "manifest_package": "babel",
        "manifest_notes": "Plural subset with core/localedata/plural and six locale-data files.",
    },
}


PUBLIC_TESTS = {
    "faker__provider_core__001": '''\
from __future__ import annotations

from featurelifted import Faker


def test_en_us_person_address_and_phone_are_seeded() -> None:
    fake = Faker("en_US")
    fake.seed_instance(12345)
    name = fake.name()
    address = fake.address()
    phone = fake.phone_number()
    assert isinstance(name, str) and " " in name
    assert isinstance(address, str) and "\\n" in address
    assert phone.startswith("(") or phone[0].isdigit()

    fake.seed_instance(12345)
    assert fake.name() == name
    assert fake.address() == address
    assert fake.phone_number() == phone
''',
    "lark__grammar_loader_core__001": '''\
from __future__ import annotations

from pathlib import Path

from featurelifted import Lark


def test_open_relative_import_and_common_import(tmp_path: Path) -> None:
    grammar_dir = tmp_path / "grammars"
    grammar_dir.mkdir()
    (grammar_dir / "tokens.lark").write_text('NUMBER: /[0-9]+/\\n', encoding="utf-8")
    (grammar_dir / "calc.lark").write_text(
        """start: sum
?sum: product | sum "+" product -> add
?product: atom | product "*" atom -> mul
?atom: NUMBER | "(" sum ")"
%import .tokens.NUMBER
%ignore " "
""",
        encoding="utf-8",
    )
    parser = Lark.open("calc.lark", rel_to=str(grammar_dir / "calc.lark"), parser="lalr")
    tree = parser.parse("1+2*3")
    assert "add" in tree.pretty()

    import featurelifted
    from featurelifted.load_grammar import FromPackageLoader

    loader = FromPackageLoader(featurelifted.__name__, ("grammars",))
    common_parser = Lark(
        "start: NUMBER\\n%import common.NUMBER",
        parser="lalr",
        import_paths=[loader],
    )
    assert common_parser.parse("42")
''',
    "rich__markup_parse_core__001": '''\
from __future__ import annotations

from featurelifted.markup import escape, render
from featurelifted.text import Text


def test_render_escape_and_from_markup() -> None:
    assert escape("plain [bold]") == "plain \\\\[bold]"

    text = render("[bold]Hello[/bold] [link=https://example.com]World[/link]")
    assert text.plain == "Hello World"
    assert any("bold" in str(span.style).lower() for span in text.spans)

    via_text = Text.from_markup("[italic]x[/italic]")
    assert via_text.plain == "x"
''',
    "marshmallow__schema_core__001": '''\
from __future__ import annotations

import pytest

from featurelifted import EXCLUDE, Schema, ValidationError, fields


class ProfileSchema(Schema):
    city = fields.Str(required=True)


class UserSchema(Schema):
    name = fields.Str(required=True)
    age = fields.Int(validate=lambda n: n >= 0)
    profile = fields.Nested(ProfileSchema)


def test_load_dump_nested_schema() -> None:
    schema = UserSchema()
    loaded = schema.load({"name": "Ada", "age": 3, "profile": {"city": "Paris"}})
    assert loaded["profile"]["city"] == "Paris"
    dumped = schema.dump(loaded)
    assert dumped["name"] == "Ada"

    with pytest.raises(ValidationError):
        schema.load({"age": 3, "profile": {"city": "Paris"}})
''',
    "babel__plural_core__001": '''\
from __future__ import annotations

from featurelifted import Locale, PluralRule


def test_plural_rule_and_english_locale() -> None:
    rule = PluralRule({"one": "n is 1"})
    assert rule(1) == "one"
    assert rule(5) == "other"

    en = Locale.parse("en")
    assert en.plural_form(1) == "one"
    assert en.plural_form(0) == "other"
''',
}

HIDDEN_TESTS = {
    "faker__provider_core__001": '''\
from __future__ import annotations

import re

from featurelifted import Faker


def test_only_en_us_locale_and_provider_formats() -> None:
    fake = Faker("en_US")
    fake.seed_instance(99)
    phone = fake.phone_number()
    assert re.search(r"\\d{3}", phone)
    assert len(phone) >= 10

    fake.seed_instance(7)
    first = fake.first_name()
    last = fake.last_name()
    assert first.isalpha()
    assert last.isalpha()

    fake.seed_instance(7)
    assert fake.first_name() == first
    assert fake.last_name() == last


def test_address_contains_city_state_zip_pattern() -> None:
    fake = Faker("en_US")
    fake.seed_instance(2024)
    address = fake.address()
    lines = address.split("\\n")
    assert len(lines) >= 2
    assert any(char.isdigit() for char in lines[-1])
''',
    "lark__grammar_loader_core__001": '''\
from __future__ import annotations

from pathlib import Path

import pytest

from featurelifted import Lark
from featurelifted.exceptions import GrammarError


def test_open_from_package_and_import_graph(tmp_path: Path) -> None:
    base = tmp_path / "pkg"
    grammars = base / "grammars"
    grammars.mkdir(parents=True)
    (grammars / "terminals.lark").write_text(
        'ESCAPED_STRING: /"[^"]*"/\\n%ignore " "\\n',
        encoding="utf-8",
    )
    (grammars / "main.lark").write_text(
        """start: greeting
greeting: "hi" | ESCAPED_STRING
%import .terminals.ESCAPED_STRING
""",
        encoding="utf-8",
    )
    parser = Lark.open(
        "grammars/main.lark",
        rel_to=str(base / "loader.py"),
        parser="lalr",
        import_paths=[str(base)],
    )
    assert parser.parse('"hello"')

    with pytest.raises(GrammarError):
        Lark('start: %import missing.rule\\n', parser="lalr")


def test_packaged_common_grammar_import() -> None:
    import featurelifted
    from featurelifted.load_grammar import FromPackageLoader

    loader = FromPackageLoader(featurelifted.__name__, ("grammars",))
    parser = Lark(
        """start: NUMBER "+" NUMBER
%import common.NUMBER
%ignore " "
""",
        parser="lalr",
        import_paths=[loader],
    )
    tree = parser.parse("2+3")
    assert len(tree.children) == 2
    assert str(tree.children[0]) == "2"
''',
    "rich__markup_parse_core__001": '''\
from __future__ import annotations

import pytest

from featurelifted.errors import MarkupError
from featurelifted.markup import render
from featurelifted.text import Text


def test_nested_styles_and_implicit_close() -> None:
    text = render("[bold]A[italic]B[/]C[/bold]")
    assert text.plain == "ABC"
    styles = [str(span.style) for span in text.spans]
    assert any("bold" in s.lower() for s in styles)
    assert any("italic" in s.lower() for s in styles)


def test_markup_errors_and_escaped_brackets() -> None:
    with pytest.raises(MarkupError):
        render("[bold]x[/italic]")

    with pytest.raises(MarkupError):
        render("[/italic]orphan")

    text = render("literal \\\\[bold] kept")
    assert "[bold]" in text.plain


def test_meta_link_handler_and_repr() -> None:
    text = render("[link=https://example.com/a?q=1]Docs[/link]")
    assert text.plain == "Docs"
    assert text.spans
    roundtrip = Text.from_markup(text.markup)
    assert roundtrip.plain == "Docs"
''',
    "marshmallow__schema_core__001": '''\
from __future__ import annotations

import pytest

from featurelifted import EXCLUDE, RAISE, Schema, ValidationError, fields
from featurelifted.decorators import post_load, validates_schema


class ItemSchema(Schema):
    qty = fields.Int(required=True)
    sku = fields.Str(required=True)


class OrderSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    items = fields.List(fields.Nested(ItemSchema), required=True)
    note = fields.Str(load_default="")

    @validates_schema
    def validate_items(self, data, **kwargs):
        if not data.get("items"):
            raise ValidationError("items required", "items")

    @post_load
    def add_total(self, data, **kwargs):
        data["total_qty"] = sum(item["qty"] for item in data["items"])
        return data


def test_unknown_exclude_post_load_and_nested_errors() -> None:
    schema = OrderSchema()
    loaded = schema.load(
        {
            "items": [{"sku": "A", "qty": 2}, {"sku": "B", "qty": 1}],
            "extra": True,
        }
    )
    assert loaded["total_qty"] == 3
    assert "extra" not in loaded

    with pytest.raises(ValidationError) as excinfo:
        schema.load({"items": [{"sku": "A", "qty": "nope"}]})
    assert "qty" in str(excinfo.value.messages)


def test_many_dump_partial_and_raise_unknown() -> None:
    class TagSchema(Schema):
        class Meta:
            unknown = RAISE

        name = fields.Str(required=True)

    schema = TagSchema()
    with pytest.raises(ValidationError):
        schema.load({"name": "x", "surprise": 1})

    many = TagSchema(many=True)
    dumped = many.dump([{"name": "a"}, {"name": "b"}])
    assert dumped == [{"name": "a"}, {"name": "b"}]
''',
    "babel__plural_core__001": '''\
from __future__ import annotations

import pytest

from featurelifted import Locale, PluralRule


def test_plural_rule_expression_edges() -> None:
    rule = PluralRule({"one": "n is 1", "few": "n in 2..4"})
    assert rule(1) == "one"
    assert rule(3) == "few"
    assert rule(5) == "other"

    with pytest.raises(ValueError):
        PluralRule({"bogus": "n is 1"})


def test_locale_plural_categories_multilingual() -> None:
    assert Locale.parse("ru").plural_form(21) == "one"
    assert Locale.parse("ru").plural_form(22) == "few"
    assert Locale.parse("fr").plural_form(0) == "one"
    assert Locale.parse("ja").plural_form(5) == "other"
    assert Locale.parse("pl").plural_form(22) == "few"
    assert Locale.parse("pl").plural_form(100) == "many"


def test_plural_rule_string_and_float_operands() -> None:
    rule = PluralRule.parse({"one": "n is 1"})
    assert rule(1) == "one"
    assert rule(1.0) == "one"
''',
}


DESIGN_NOTES = {
    "faker__provider_core__001": """# Task Design: faker__provider_core__001

Status: oracle-verified

## Why This Task

Covers locale-scoped provider data and factory wiring without multi-locale proxy complexity.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| en_US person data | `providers/person/en_US/__init__.py` | `test_only_en_us_locale_and_provider_formats` |
| Factory wiring | `factory.py` | `test_en_us_person_address_and_phone_are_seeded` |
| Weighted sampling | `utils/distribution.py` | `test_address_contains_city_state_zip_pattern` |
""",
    "lark__grammar_loader_core__001": """# Task Design: lark__grammar_loader_core__001

Status: oracle-verified

## Why This Task

Forces extraction of grammar import resolution and packaged `grammars/common.lark` resources.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Grammar loader | `load_grammar.py` | `test_open_from_package_and_import_graph` |
| Packaged grammars | `grammars/common.lark` | `test_packaged_common_grammar_import` |
| Parser frontend | `parser_frontends.py` | `test_open_relative_import_and_common_import` |
""",
    "rich__markup_parse_core__001": """# Task Design: rich__markup_parse_core__001

Status: oracle-verified

## Why This Task

Isolates console markup stack semantics without terminal Console rendering.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Markup parser | `markup.py` | `test_nested_styles_and_implicit_close` |
| Text spans | `text.py` | `test_meta_link_handler_and_repr` |
| Style normalization | `style.py` | `test_render_escape_and_from_markup` |
""",
    "marshmallow__schema_core__001": """# Task Design: marshmallow__schema_core__001

Status: oracle-verified

## Why This Task

Exercises schema graphs, nested fields, and decorator hooks central to Marshmallow.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Field types | `fields/__init__.py` | `test_load_dump_nested_schema` |
| Schema core | `schema.py` | `test_unknown_exclude_post_load_and_nested_errors` |
| Decorators | `decorators.py` | `test_unknown_exclude_post_load_and_nested_errors` |
""",
    "babel__plural_core__001": """# Task Design: babel__plural_core__001

Status: oracle-verified

## Why This Task

Covers CLDR plural operands, rule parsing, and locale-data resource loading.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Plural parser | `plural.py` | `test_plural_rule_expression_edges` |
| Locale data | `locale-data/ru.dat` | `test_locale_plural_categories_multilingual` |
| Locale core | `core.py` | `test_plural_rule_and_english_locale` |
""",
}


def write_task(task_id: str, spec: dict) -> None:
    task_dir = TASKS / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    (task_dir / "requirements.lock").write_text("", encoding="utf-8")

    manifest_files = spec["manifest"]
    if isinstance(manifest_files, str) and manifest_files.startswith("discover:"):
        pkg = manifest_files.split(":", 1)[1]
        manifest_files = discover_py_and_lark(task_dir / "repo", pkg)

    manifest = {
        "source_package_name": spec["manifest_package"],
        "required_source_files": manifest_files,
        "notes": spec["manifest_notes"],
    }
    eval_dir = task_dir / "evaluation"
    eval_dir.mkdir(exist_ok=True)
    (eval_dir / "oracle_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    (eval_dir / "forbidden_imports.txt").write_text(
        spec["forbidden"][0] + "\n",
        encoding="utf-8",
    )

    metadata = {
        "task_id": task_id,
        "language": "python",
        "difficulty": "hard",
        "tags": [
            "multi-task-repo",
            "functional-discriminator",
            "decoupling-discriminator",
            spec["entanglement"]["primary"],
            "pure-python",
        ],
        "source": {
            "name": spec["source_name"],
            "url": spec["source_url"],
            "commit": spec["commit"],
            "license": spec["license"],
        },
        "feature": {
            "name": spec["feature_name"],
            "description": spec["description"],
            "source_entrypoints": spec["entrypoints"],
            "included_behaviors": spec["included"],
            "excluded_behaviors": spec["excluded"],
        },
        "entanglement": spec["entanglement"],
        "output": {
            "package": "featurelifted",
            "import": spec["output_import"],
            "callable": spec["callable"],
            "signature": spec["signature"],
        },
        "environment": {
            "python": "3.11",
            "network": False,
            "timeout_seconds": 60,
            "dependency_lock": "requirements.lock",
            "allowed_dependencies": spec.get("allowed_dependencies", []),
            "forbidden_dependencies": spec["forbidden"],
            "forbidden_imports": spec["forbidden"],
        },
        "tests": {
            "public": "public_tests/",
            "hidden": "hidden_tests/",
            "command": "pytest",
        },
    }
    (task_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n",
        encoding="utf-8",
    )

    pub = task_dir / "public_tests"
    hid = task_dir / "hidden_tests"
    pub.mkdir(exist_ok=True)
    hid.mkdir(exist_ok=True)
    (pub / "test_public_api.py").write_text(PUBLIC_TESTS[task_id], encoding="utf-8")
    (hid / "test_hidden_behavior.py").write_text(HIDDEN_TESTS[task_id], encoding="utf-8")

    design = DESIGNS / f"{task_id}.md"
    design.write_text(DESIGN_NOTES[task_id], encoding="utf-8")


def main() -> None:
    for task_id, spec in TASK_SPECS.items():
        write_task(task_id, spec)
        print("scaffolded", task_id)


if __name__ == "__main__":
    main()
