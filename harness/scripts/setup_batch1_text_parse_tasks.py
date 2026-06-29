#!/usr/bin/env python3
"""Scaffold batch-1 text/parse staging tasks."""

from __future__ import annotations

import json
import shutil
import textwrap
from pathlib import Path
from typing import Any, Callable

_REPO = Path(__file__).resolve().parents[2]
SITE = Path("/Users/chz/anaconda3/lib/python3.12/site-packages")
STAGING = _REPO / "benchmark" / "staging"
DESIGNS = _REPO / "docs" / "task_designs"
SUBMISSIONS = _REPO / "benchmark" / "submissions"

BLEACH_ORACLE = [
    "bleach/sanitizer.py",
    "bleach/html5lib_shim.py",
    "bleach/utils.py",
    "bleach/_vendor/parse.py",
    "bleach/_vendor/html5lib",
]

RUAMEL_ORACLE = [
    f"ruamel/yaml/{path.name}"
    for path in sorted((SITE / "ruamel" / "yaml").glob("*.py"))
    if path.name != "cyaml.py"
]

MARKDOWN_ORACLE = [
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

PARSO_ORACLE = [
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

DEEPDIFF_ORACLE = [
    "deepdiff/diff.py",
    "deepdiff/helper.py",
    "deepdiff/model.py",
    "deepdiff/base.py",
    "deepdiff/path.py",
    "deepdiff/lfucache.py",
    "deepdiff/serialization.py",
    "deepdiff/distance.py",
]


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip("\n"), encoding="utf-8")


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _copy_pkg(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(
        src,
        dst,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"),
    )


def _scaffold_task(
    task_id: str,
    *,
    copy_repo: Callable[[], None],
    forbidden: str,
    manifest: dict[str, Any],
    metadata: dict[str, Any],
    design: str,
    public_tests: str,
    hidden_tests: str,
    naive_init: str,
) -> None:
    copy_repo()
    root = STAGING / task_id
    _write_json(root / "metadata.json", metadata)
    _write(root / "requirements.lock", "")
    _write(root / "evaluation/forbidden_imports.txt", f"{forbidden}\n")
    _write_json(root / "evaluation/oracle_manifest.json", manifest)
    _write(root / "public_tests/test_public_api.py", public_tests)
    _write(root / "hidden_tests/test_hidden_behavior.py", hidden_tests)
    _write(DESIGNS / f"{task_id}.md", design)
    _write(SUBMISSIONS / task_id / "naive" / "featurelifted" / "__init__.py", naive_init)
    print(f"scaffolded {task_id}")


def _copy_bleach_repo() -> None:
    dst = STAGING / "bleach__sanitize_core__001/repo/bleach"
    _copy_pkg(SITE / "bleach", dst)
    _copy_pkg(SITE / "bleach/_vendor", dst / "contrib/_vendor")


def main() -> None:
    _scaffold_task(
        "bleach__sanitize_core__001",
        copy_repo=_copy_bleach_repo,
        forbidden="bleach",
        manifest={
            "source_package_name": "bleach",
            "required_source_files": BLEACH_ORACLE,
            "runtime_dependencies": [],
            "notes": "Oracle sanitizer stack; repo includes linkifier for copy-all penalty.",
        },
        metadata={
            "task_id": "bleach__sanitize_core__001",
            "language": "python",
            "difficulty": "hard",
            "tags": [
                "batch-1",
                "bleach",
                "html-sanitizer",
                "hard-first",
                "functional-discriminator",
                "parser_state_coupling",
            ],
            "source": {
                "name": "bleach",
                "url": "https://github.com/mozilla/bleach",
                "commit": "4.1.0-installed-snapshot",
                "license": "Apache-2.0",
            },
            "feature": {
                "name": "HTML sanitizer clean core",
                "description": "Extract bleach clean/Cleaner HTML sanitization without importing bleach.",
                "source_entrypoints": ["bleach.clean", "bleach.sanitizer.Cleaner"],
                "included_behaviors": [
                    "XSS tag stripping",
                    "allowed attributes and protocols",
                    "strip and strip_comments modes",
                    "callable attribute filters",
                ],
                "excluded_behaviors": ["linkify", "upstream packaging", "original bleach import"],
            },
            "entanglement": {
                "level": "high",
                "types": ["parser_state_coupling", "data_model_coupling"],
                "primary": "parser_state_coupling",
                "description": "Sanitizer couples html5lib tokenizer, attribute policy, and Cleaner state.",
                "signals": [
                    "html5lib parser per Cleaner",
                    "protocol validation on href",
                    "strip vs escape modes",
                ],
            },
            "output": {
                "package": "featurelifted",
                "import": (
                    "import featurelifted; from featurelifted import clean, Cleaner, "
                    "ALLOWED_TAGS, ALLOWED_ATTRIBUTES, ALLOWED_PROTOCOLS"
                ),
                "callable": "featurelifted.clean",
                "signature": (
                    "clean(text, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, "
                    "styles=ALLOWED_STYLES, protocols=ALLOWED_PROTOCOLS, strip=False, "
                    "strip_comments=True) -> str"
                ),
            },
            "environment": {
                "python": "3.11",
                "network": False,
                "timeout_seconds": 60,
                "dependency_lock": "requirements.lock",
                "allowed_dependencies": [],
                "forbidden_dependencies": ["bleach"],
                "forbidden_imports": ["bleach"],
            },
            "tests": {"public": "public_tests/", "hidden": "hidden_tests/", "command": "pytest"},
        },
        design="""\
            # Task Design: `bleach__sanitize_core__001`

            Status: draft-spike

            ## Practical reuse

            1. **Reuse module** — Standalone HTML fragment sanitizer for user-generated content pipelines.
            2. **Who imports it** — Apps needing bleach-style `clean()` without vendoring linkifier stack.
            3. **Why not copy-all** — Curated snapshot includes linkifier/callbacks; compact closure keeps sanitizer + html5lib shim.

            ## Module Probes

            | Probe | Remove module | Hidden test(s) that must fail |
            | --- | --- | --- |
            | Sanitizer core | `featurelifted/sanitizer.py` | `test_strip_disallowed_script` |
            | Html5lib shim | `featurelifted/html5lib_shim.py` | `test_strip_mode_removes_tag` |
            | Vendor parse | `featurelifted/_vendor/parse.py` | `test_javascript_href_stripped` |

            ## Manual Oracle Closure Plan

            | Check | Target | Result |
            | --- | --- | --- |
            | Public tests | pass | |
            | Hidden tests | pass | |
            | ExtractionRatio | 0.20 – 0.60 | |
            | Copy-All delta | ≥ 0.25 | |

            ## Agent Calibration

            | Run | Model | Passed | ExtractionRatio | final_score | Notes |
            | --- | --- | --- | ---: | ---: | --- |
            | | | | | | Flash deferred |
            """,
        public_tests="""\
            from __future__ import annotations

            from featurelifted import clean


            def test_clean_strips_script() -> None:
                dirty = '<b>ok</b><script>alert(1)</script>'
                assert clean(dirty) == "<b>ok</b>&lt;script&gt;alert(1)&lt;/script&gt;"


            def test_clean_allows_safe_link() -> None:
                dirty = '<a href="https://example.com" title="x">link</a>'
                out = clean(dirty)
                assert 'href="https://example.com"' in out
                assert "link" in out


            def test_clean_escapes_unknown_tags() -> None:
                dirty = "<custom>text</custom>"
                assert clean(dirty) == "&lt;custom&gt;text&lt;/custom&gt;"
            """,
        hidden_tests="""\
            from __future__ import annotations

            import re
            from pathlib import Path

            from featurelifted import clean


            def test_strip_disallowed_script() -> None:
                dirty = '<b>keep</b><script>x</script>'
                assert clean(dirty, tags=["b"], strip=True) == "<b>keep</b>x"


            def test_strip_mode_removes_tag() -> None:
                dirty = "<b>bold</b> plain"
                assert clean(dirty, tags=[], strip=True) == "bold plain"


            def test_javascript_href_stripped() -> None:
                dirty = '<a href="javascript:alert(1)">x</a>'
                assert 'href=' not in clean(dirty)


            def test_strip_comments_removed() -> None:
                dirty = "<b>hi</b><!-- secret -->"
                assert clean(dirty, strip_comments=True) == "<b>hi</b>"


            def test_custom_attributes_callable() -> None:
                def allow_href(tag: str, name: str, value: str) -> bool:
                    return name == "href" and value.startswith("https://")

                dirty = '<a href="https://ok">y</a><a href="http://no">n</a>'
                out = clean(dirty, tags=["a"], attributes={"a": allow_href})
                assert 'href="https://ok"' in out
                assert "http://no" not in out


            def test_no_bleach_import_surface() -> None:
                import featurelifted

                pkg_root = Path(featurelifted.__file__).parent
                import_pattern = re.compile(r"^\\s*(?:from bleach|import bleach)\\b", re.MULTILINE)
                for path in pkg_root.rglob("*.py"):
                    text = path.read_text(encoding="utf-8")
                    assert not import_pattern.search(text)
            """,
        naive_init="""\
            \"\"\"Naive regex HTML cleaner.\"\"\"

            from __future__ import annotations

            import html as html_module
            import re

            ALLOWED_TAGS = [
                "a", "abbr", "acronym", "b", "blockquote", "code", "em", "i", "li", "ol", "strong", "ul",
            ]
            ALLOWED_ATTRIBUTES = {"a": ["href", "title"], "abbr": ["title"], "acronym": ["title"]}
            ALLOWED_STYLES: list[str] = []
            ALLOWED_PROTOCOLS = ["http", "https", "mailto"]

            _TAG_RE = re.compile(r"<(/?)([a-zA-Z0-9]+)(\\s[^>]*)?>")


            class Cleaner:
                def __init__(
                    self,
                    tags=None,
                    attributes=None,
                    styles=None,
                    protocols=None,
                    strip=False,
                    strip_comments=True,
                ):
                    self.tags = tags if tags is not None else ALLOWED_TAGS
                    self.attributes = attributes if attributes is not None else ALLOWED_ATTRIBUTES
                    self.styles = styles if styles is not None else ALLOWED_STYLES
                    self.protocols = protocols if protocols is not None else ALLOWED_PROTOCOLS
                    self.strip = strip
                    self.strip_comments = strip_comments

                def clean(self, text: str) -> str:
                    return clean(
                        text,
                        tags=self.tags,
                        attributes=self.attributes,
                        styles=self.styles,
                        protocols=self.protocols,
                        strip=self.strip,
                        strip_comments=self.strip_comments,
                    )


            def clean(
                text: str,
                tags=ALLOWED_TAGS,
                attributes=ALLOWED_ATTRIBUTES,
                styles=ALLOWED_STYLES,
                protocols=ALLOWED_PROTOCOLS,
                strip: bool = False,
                strip_comments: bool = True,
            ) -> str:
                del styles, protocols, attributes
                if strip_comments:
                    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)

                def repl(match: re.Match[str]) -> str:
                    closing, tag, attrs = match.group(1), match.group(2).lower(), match.group(3) or ""
                    if tag not in {t.lower() for t in tags}:
                        if strip:
                            return ""
                        return html_module.escape(match.group(0))
                    return f"</{tag}>" if closing else f"<{tag}{attrs}>"

                return _TAG_RE.sub(repl, text)
            """,
    )

    # ruamel_yaml
    def copy_ruamel() -> None:
        dst = STAGING / "ruamel_yaml__roundtrip_core__001/repo"
        yaml_dst = dst / "ruamel/yaml"
        _copy_pkg(SITE / "ruamel/yaml", yaml_dst)
        (yaml_dst / "cyaml.py").unlink(missing_ok=True)
        (dst / "ruamel/__init__.py").write_text("", encoding="utf-8")
        mirror_dst = dst / "ruamel/contrib/yaml_mirror"
        _copy_pkg(SITE / "ruamel/yaml", mirror_dst)
        (mirror_dst / "cyaml.py").unlink(missing_ok=True)

    _scaffold_task(
        "ruamel_yaml__roundtrip_core__001",
        copy_repo=copy_ruamel,
        forbidden="ruamel",
        manifest={
            "source_package_name": "ruamel.yaml",
            "required_source_files": RUAMEL_ORACLE,
            "runtime_dependencies": [],
            "notes": "Full ruamel.yaml Python modules except cyaml C extension.",
        },
        metadata={
            "task_id": "ruamel_yaml__roundtrip_core__001",
            "language": "python",
            "difficulty": "hard",
            "tags": ["batch-1", "ruamel-yaml", "roundtrip", "hard-first", "parser_state_coupling"],
            "source": {
                "name": "ruamel.yaml",
                "url": "https://sourceforge.net/projects/ruamel-yaml/",
                "commit": "0.18.6-installed-snapshot",
                "license": "MIT",
            },
            "feature": {
                "name": "YAML roundtrip with comments",
                "description": "Extract ruamel.yaml round-trip load/dump preserving comments and key order.",
                "source_entrypoints": ["ruamel.yaml.round_trip_load", "ruamel.yaml.round_trip_dump", "ruamel.yaml.YAML"],
                "included_behaviors": [
                    "round-trip load/dump preserves end-of-line comments",
                    "CommentedMap key order preserved",
                    "flow style and literal block scalars",
                ],
                "excluded_behaviors": ["C yaml acceleration", "jinja2 templating", "original ruamel import"],
            },
            "entanglement": {
                "level": "high",
                "types": ["parser_state_coupling", "data_model_coupling"],
                "primary": "parser_state_coupling",
                "description": "Round-trip YAML couples scanner comment tokens, CommentedMap model, and emitter layout.",
                "signals": ["CommentedMap comment slots", "RoundTripLoader/Dumper pairing", "scalar string quote preservation"],
            },
            "output": {
                "package": "featurelifted",
                "import": (
                    "import featurelifted; from featurelifted import YAML, round_trip_load, "
                    "round_trip_dump, CommentedMap"
                ),
                "callable": "featurelifted.round_trip_load",
                "signature": "round_trip_load(stream) -> CommentedMap",
            },
            "environment": {
                "python": "3.11",
                "network": False,
                "timeout_seconds": 60,
                "dependency_lock": "requirements.lock",
                "allowed_dependencies": [],
                "forbidden_dependencies": ["ruamel.yaml", "ruamel"],
                "forbidden_imports": ["ruamel"],
            },
            "tests": {"public": "public_tests/", "hidden": "hidden_tests/", "command": "pytest"},
        },
        design="""\
            # Task Design: `ruamel_yaml__roundtrip_core__001`

            Status: draft-spike

            ## Practical reuse

            1. **Reuse module** — Config round-trip preserving comments and ordering.
            2. **Who imports it** — Tools needing ruamel-style YAML editing without full packaging stack.
            3. **Why not copy-all** — Package is already compact; copy-all equals oracle for Python modules.

            ## Module Probes

            | Probe | Remove module | Hidden test(s) that must fail |
            | --- | --- | --- |
            | Comments model | `featurelifted/comments.py` | `test_eol_comment_preserved` |
            | Emitter | `featurelifted/emitter.py` | `test_flow_style_dump` |
            | Scanner | `featurelifted/scanner.py` | `test_literal_block_scalar` |

            ## Manual Oracle Closure Plan

            | Check | Target | Result |
            | --- | --- | --- |
            | Public tests | pass | |
            | Hidden tests | pass | |
            | ExtractionRatio | 0.20 – 0.60 | |
            | Copy-All delta | ≥ 0.25 | |

            ## Agent Calibration

            | Run | Model | Passed | ExtractionRatio | final_score | Notes |
            | --- | --- | --- | ---: | ---: | --- |
            | | | | | | Flash deferred |
            """,
        public_tests="""\
            from __future__ import annotations

            from featurelifted import YAML, CommentedMap


            def test_roundtrip_basic_mapping() -> None:
                text = "a: 1\\nb: two\\n"
                yaml = YAML()
                data = yaml.load(text)
                assert data["a"] == 1
                assert data["b"] == "two"
                from io import StringIO
                stream = StringIO()
                yaml.dump(data, stream)
                assert stream.getvalue().strip() == text.strip()


            def test_key_order_preserved() -> None:
                text = "z: 1\\na: 2\\n"
                data = YAML().load(text)
                assert list(data.keys()) == ["z", "a"]
            """,
        hidden_tests="""\
            from __future__ import annotations

            import re
            from io import StringIO
            from pathlib import Path

            from featurelifted import YAML, CommentedMap


            def test_eol_comment_preserved() -> None:
                text = "key: value  # note\\n"
                yaml = YAML()
                data = yaml.load(text)
                from io import StringIO
                stream = StringIO()
                yaml.dump(data, stream)
                assert "# note" in stream.getvalue()
                assert data["key"] == "value"


            def test_flow_style_dump() -> None:
                data = CommentedMap([("a", 1), ("b", 2)])
                data.fa.set_flow_style()
                from io import StringIO
                stream = StringIO()
                YAML().dump(data, stream)
                out = stream.getvalue()
                assert out.strip().startswith("{") or "[" in out


            def test_literal_block_scalar() -> None:
                text = "body: |\\n  line1\\n  line2\\n"
                data = YAML().load(text)
                assert data["body"] == "line1\\nline2\\n"
                from io import StringIO
                stream = StringIO()
                YAML().dump(data, stream)
                assert "|" in stream.getvalue()


            def test_anchor_alias_roundtrip() -> None:
                text = "base: &id\\n  x: 1\\nchild: *id\\n"
                data = YAML().load(text)
                assert data["child"]["x"] == 1


            def test_no_ruamel_import_surface() -> None:
                import featurelifted

                pkg_root = Path(featurelifted.__file__).parent
                import_pattern = re.compile(r"^\\s*(?:from ruamel|import ruamel)\\b", re.MULTILINE)
                for path in pkg_root.rglob("*.py"):
                    text = path.read_text(encoding="utf-8")
                    assert not import_pattern.search(text)
            """,
        naive_init="""\
            \"\"\"Naive key:value parser — no comments or flow style.\"\"\"

            from __future__ import annotations

            from collections import OrderedDict


            class CommentedMap(OrderedDict):
                pass


            def _parse_line(line: str) -> tuple[str, object] | None:
                if ":" not in line:
                    return None
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.split("#", 1)[0].strip()
                if value.isdigit():
                    return key, int(value)
                if value.startswith('"') and value.endswith('"'):
                    return key, value[1:-1]
                return key, value


            def round_trip_load(stream) -> CommentedMap:
                text = stream.read() if hasattr(stream, "read") else str(stream)
                data = CommentedMap()
                for line in text.splitlines():
                    parsed = _parse_line(line)
                    if parsed:
                        data[parsed[0]] = parsed[1]
                return data


            def round_trip_dump(data) -> str:
                lines = [f"{key}: {value}" for key, value in data.items()]
                return "\\n".join(lines) + "\\n"


            class YAML:
                def load(self, stream):
                    return round_trip_load(stream)

                def dump(self, data, stream):
                    stream.write(round_trip_dump(data))
            """,
    )

    # markdown
    def copy_markdown() -> None:
        md_dst = STAGING / "markdown__extensions_core__001/repo/markdown"
        _copy_pkg(SITE / "markdown", md_dst)
        _copy_pkg(SITE / "markdown/extensions", md_dst / "contrib/extensions_mirror")

    _scaffold_task(
        "markdown__extensions_core__001",
        copy_repo=copy_markdown,
        forbidden="markdown",
        manifest={
            "source_package_name": "markdown",
            "required_source_files": MARKDOWN_ORACLE,
            "runtime_dependencies": [],
            "notes": "Core markdown pipeline plus tables/footnotes extensions.",
        },
        metadata={
            "task_id": "markdown__extensions_core__001",
            "language": "python",
            "difficulty": "hard",
            "tags": ["batch-1", "markdown", "extensions", "hard-first", "parser_state_coupling"],
            "source": {
                "name": "Markdown",
                "url": "https://github.com/Python-Markdown/markdown",
                "commit": "3.7-installed-snapshot",
                "license": "BSD-3-Clause",
            },
            "feature": {
                "name": "Markdown tables and footnotes extensions",
                "description": "Extract python-markdown core with tables and footnotes extensions.",
                "source_entrypoints": [
                    "markdown.markdown",
                    "markdown.extensions.tables.TableExtension",
                    "markdown.extensions.footnotes.FootnoteExtension",
                ],
                "included_behaviors": [
                    "pipe table rendering",
                    "footnote reference and backlink HTML",
                    "extension registration on Markdown class",
                ],
                "excluded_behaviors": ["unrelated extensions", "CLI __main__", "original markdown import"],
            },
            "entanglement": {
                "level": "high",
                "types": ["parser_state_coupling", "framework_coupling"],
                "primary": "parser_state_coupling",
                "description": "Extensions hook block/tree processors and share Markdown instance registry state.",
                "signals": ["TableProcessor block regex", "FootnoteExtension footnote order", "build_block_parser registration"],
            },
            "output": {
                "package": "featurelifted",
                "import": "import featurelifted; from featurelifted import markdown, Markdown",
                "callable": "featurelifted.markdown",
                "signature": "markdown(text, extensions=None, extension_configs=None) -> str",
            },
            "environment": {
                "python": "3.11",
                "network": False,
                "timeout_seconds": 60,
                "dependency_lock": "requirements.lock",
                "allowed_dependencies": [],
                "forbidden_dependencies": ["markdown"],
                "forbidden_imports": ["markdown"],
            },
            "tests": {"public": "public_tests/", "hidden": "hidden_tests/", "command": "pytest"},
        },
        design="""\
            # Task Design: `markdown__extensions_core__001`

            Status: draft-spike

            ## Practical reuse

            1. **Reuse module** — Markdown renderer with tables/footnotes for docs sites.
            2. **Who imports it** — Static site tooling needing python-markdown extensions subset.
            3. **Why not copy-all** — Full extension pack inflates copy-all; oracle keeps core + 2 extensions.

            ## Module Probes

            | Probe | Remove module | Hidden test(s) that must fail |
            | --- | --- | --- |
            | Tables extension | `featurelifted/extensions/tables.py` | `test_table_header_align` |
            | Footnotes extension | `featurelifted/extensions/footnotes.py` | `test_footnote_backlink` |
            | Block processors | `featurelifted/blockprocessors.py` | `test_table_row_span` |

            ## Manual Oracle Closure Plan

            | Check | Target | Result |
            | --- | --- | --- |
            | Public tests | pass | |
            | Hidden tests | pass | |
            | ExtractionRatio | 0.20 – 0.60 | |
            | Copy-All delta | ≥ 0.25 | |

            ## Agent Calibration

            | Run | Model | Passed | ExtractionRatio | final_score | Notes |
            | --- | --- | --- | ---: | ---: | --- |
            | | | | | | Flash deferred |
            """,
        public_tests="""\
            from __future__ import annotations

            from featurelifted import markdown


            def test_simple_table() -> None:
                src = "| h1 | h2 |\\n| --- | --- |\\n| a | b |\\n"
                html = markdown(src, extensions=["tables"])
                assert "<table>" in html
                assert "<th>h1</th>" in html
                assert "<td>a</td>" in html


            def test_basic_footnote() -> None:
                src = "Text[^1]\\n\\n[^1]: note"
                html = markdown(src, extensions=["footnotes"])
                assert 'class="footnote"' in html or "footnote" in html
                assert "note" in html
            """,
        hidden_tests="""\
            from __future__ import annotations

            import re
            from pathlib import Path

            from featurelifted import markdown


            def test_table_header_align() -> None:
                src = (
                    "| left | center | right |\\n"
                    "| :--- | :---: | ---: |\\n"
                    "| l | c | r |\\n"
                )
                html = markdown(src, extensions=["tables"])
                assert "text-align: left" in html
                assert "text-align: center" in html
                assert "text-align: right" in html


            def test_footnote_backlink() -> None:
                src = "See[^fn]\\n\\n[^fn]: detail"
                html = markdown(src, extensions=["footnotes"])
                assert "footnote-backref" in html or "↩" in html


            def test_table_row_span() -> None:
                src = "| a | b |\\n| --- | --- |\\n| 1 | 2 |\\n| 3 | 4 |\\n"
                html = markdown(src, extensions=["tables"])
                assert html.count("<tr>") >= 3


            def test_multiple_footnotes_order() -> None:
                src = "A[^1] B[^2]\\n\\n[^2]: second\\n[^1]: first"
                html = markdown(src, extensions=["footnotes"])
                assert html.index("first") < html.index("second") or "first" in html


            def test_no_markdown_import_surface() -> None:
                import featurelifted

                pkg_root = Path(featurelifted.__file__).parent
                import_pattern = re.compile(r"^\\s*(?:from markdown|import markdown)\\b", re.MULTILINE)
                for path in pkg_root.rglob("*.py"):
                    text = path.read_text(encoding="utf-8")
                    assert not import_pattern.search(text)
            """,
        naive_init="""\
            \"\"\"Naive markdown — no tables/footnotes extensions.\"\"\"

            from __future__ import annotations

            import html
            import re


            def markdown(text: str, extensions=None, extension_configs=None) -> str:
                del extension_configs
                if extensions and ("tables" in extensions or "TableExtension" in str(extensions)):
                    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
                    if lines and lines[0].startswith("|"):
                        header = [cell.strip() for cell in lines[0].strip("|").split("|")]
                        body_rows = lines[2:] if len(lines) > 2 else []
                        out = ["<table>", "<thead><tr>"]
                        out.extend(f"<th>{cell}</th>" for cell in header)
                        out.append("</tr></thead><tbody>")
                        for row in body_rows:
                            cells = [cell.strip() for cell in row.strip("|").split("|")]
                            out.append("<tr>")
                            out.extend(f"<td>{cell}</td>" for cell in cells)
                            out.append("</tr>")
                        out.append("</tbody></table>")
                        return "\\n".join(out)
                if extensions and "footnotes" in extensions:
                    if "[^" in text:
                        return '<div class="footnote"><p>note</p></div>'
                out = html.escape(text)
                out = re.sub(r"\\*\\*(.+?)\\*\\*", r"<strong>\\1</strong>", out)
                out = re.sub(r"\\*(.+?)\\*", r"<em>\\1</em>", out)
                out = out.replace("\\n", "<br />\\n")
                return f"<p>{out}</p>"


            class Markdown:
                def __init__(self, *args, **kwargs):
                    pass

                def convert(self, text: str) -> str:
                    return markdown(text)
            """,
    )

    # parso
    def copy_parso() -> None:
        repo = STAGING / "parso__python_parse_core__001/repo"
        _copy_pkg(SITE / "parso", repo / "parso")
        _copy_pkg(SITE / "parso", repo / "parso_extra")

    _scaffold_task(
        "parso__python_parse_core__001",
        copy_repo=copy_parso,
        forbidden="parso",
        manifest={
            "source_package_name": "parso",
            "required_source_files": PARSO_ORACLE,
            "runtime_dependencies": [],
            "notes": "Core grammar/parser tree; copy-all adds diff/pep8 modules.",
        },
        metadata={
            "task_id": "parso__python_parse_core__001",
            "language": "python",
            "difficulty": "hard",
            "tags": ["batch-1", "parso", "python-parser", "hard-first", "parser_state_coupling"],
            "source": {
                "name": "parso",
                "url": "https://github.com/davidhalter/parso",
                "commit": "0.8.3-installed-snapshot",
                "license": "MIT",
            },
            "feature": {
                "name": "Python parser grammar core",
                "description": "Extract parso parse/load_grammar with error recovery and get_code roundtrip.",
                "source_entrypoints": ["parso.parse", "parso.load_grammar", "parso.Grammar.parse"],
                "included_behaviors": [
                    "parse Python source to syntax tree",
                    "get_code round-trip on nodes",
                    "iter_errors for multiple syntax issues",
                    "version-specific grammars",
                ],
                "excluded_behaviors": ["diff parser", "pep8 normalizer", "original parso import"],
            },
            "entanglement": {
                "level": "high",
                "types": ["parser_state_coupling", "data_model_coupling"],
                "primary": "parser_state_coupling",
                "description": "Parser couples pgen2 grammar, token stream, and Python AST node graph.",
                "signals": ["Grammar version selection", "error recovery in parser", "prefix/leaves on tree nodes"],
            },
            "output": {
                "package": "featurelifted",
                "import": "import featurelifted; from featurelifted import parse, load_grammar, Grammar",
                "callable": "featurelifted.parse",
                "signature": "parse(code=None, *, version=None, **kwargs)",
            },
            "environment": {
                "python": "3.11",
                "network": False,
                "timeout_seconds": 60,
                "dependency_lock": "requirements.lock",
                "allowed_dependencies": [],
                "forbidden_dependencies": ["parso"],
                "forbidden_imports": ["parso"],
            },
            "tests": {"public": "public_tests/", "hidden": "hidden_tests/", "command": "pytest"},
        },
        design="""\
            # Task Design: `parso__python_parse_core__001`

            Status: draft-spike

            ## Practical reuse

            1. **Reuse module** — Lightweight Python parser for tooling/linters.
            2. **Who imports it** — Jedi-like tools needing parso grammar without full jedi.
            3. **Why not copy-all** — diff/pep8 modules add weight beyond parse core.

            ## Module Probes

            | Probe | Remove module | Hidden test(s) that must fail |
            | --- | --- | --- |
            | Grammar loader | `featurelifted/grammar.py` | `test_parse_version_39` |
            | Python parser | `featurelifted/python/parser.py` | `test_iter_errors_multiple` |
            | Tree nodes | `featurelifted/python/tree.py` | `test_get_code_roundtrip` |

            ## Manual Oracle Closure Plan

            | Check | Target | Result |
            | --- | --- | --- |
            | Public tests | pass | |
            | Hidden tests | pass | |
            | ExtractionRatio | 0.20 – 0.60 | |
            | Copy-All delta | ≥ 0.25 | |

            ## Agent Calibration

            | Run | Model | Passed | ExtractionRatio | final_score | Notes |
            | --- | --- | --- | ---: | ---: | --- |
            | | | | | | Flash deferred |
            """,
        public_tests="""\
            from __future__ import annotations

            from featurelifted import parse


            def test_parse_simple_expr() -> None:
                module = parse("1 + 2", version="3.9")
                expr = module.children[0]
                assert expr.get_code().strip() == "1 + 2"


            def test_name_node_positions() -> None:
                module = parse("hello", version="3.9")
                name = module.children[0]
                assert name.start_pos == (1, 0)
                assert name.value == "hello"
            """,
        hidden_tests="""\
            from __future__ import annotations

            import re
            from pathlib import Path

            from featurelifted import load_grammar, parse


            def test_get_code_roundtrip() -> None:
                src = "def f(x):\\n    return x + 1\\n"
                module = parse(src, version="3.9")
                assert module.get_code() == src


            def test_iter_errors_multiple() -> None:
                grammar = load_grammar(version="3.9")
                module = grammar.parse("foo +\\nbar\\ncontinue")
                errors = list(grammar.iter_errors(module))
                assert len(errors) >= 2


            def test_parse_version_39() -> None:
                module = parse("match x:\\n    case 1: pass", version="3.10")
                assert module.get_code().startswith("match")


            def test_error_recovery_partial_tree() -> None:
                module = parse("def f(: pass", version="3.9")
                assert module.children


            def test_no_parso_import_surface() -> None:
                import featurelifted

                pkg_root = Path(featurelifted.__file__).parent
                import_pattern = re.compile(r"^\\s*(?:from parso|import parso)\\b", re.MULTILINE)
                for path in pkg_root.rglob("*.py"):
                    text = path.read_text(encoding="utf-8")
                    assert not import_pattern.search(text)
            """,
        naive_init="""\
            \"\"\"Naive ast.parse wrapper — no error recovery or get_code.\"\"\"

            from __future__ import annotations

            import ast


            class _Node:
                def __init__(self, value: str, start_pos=(1, 0)):
                    self.value = value
                    self.start_pos = start_pos
                    self.children: list[_Node] = []

                def get_code(self) -> str:
                    return self.value


            class _Module(_Node):
                pass


            def parse(code=None, **kwargs):
                del kwargs
                tree = ast.parse(code or "")
                mod = _Module(ast.unparse(tree))
                if tree.body:
                    stmt = tree.body[0]
                    if isinstance(stmt, ast.Expr):
                        mod.children = [_Node(ast.unparse(stmt.value))]
                    elif isinstance(stmt, ast.Pass):
                        mod.children = []
                    else:
                        mod.children = [_Node(ast.unparse(stmt))]
                return mod


            def load_grammar(version=None):
                return _Grammar()


            class Grammar:
                def parse(self, code, **kwargs):
                    return parse(code, version=version, **kwargs)

                def iter_errors(self, module):
                    return []


            class _Grammar(Grammar):
                pass
            """,
    )

    # deepdiff
    def copy_deepdiff() -> None:
        dst = STAGING / "deepdiff__deep_compare_core__001/repo/deepdiff"
        _copy_pkg(SITE / "deepdiff", dst)
        contrib = dst / "contrib"
        contrib.mkdir(parents=True, exist_ok=True)
        for name in ("search.py", "delta.py", "commands.py", "serialization.py"):
            shutil.copy2(SITE / "deepdiff" / name, contrib / name)

    _scaffold_task(
        "deepdiff__deep_compare_core__001",
        copy_repo=copy_deepdiff,
        forbidden="deepdiff",
        manifest={
            "source_package_name": "deepdiff",
            "required_source_files": DEEPDIFF_ORACLE,
            "runtime_dependencies": [],
            "notes": "DeepDiff core with path/exclude_paths; copy-all adds search/delta/commands.",
        },
        metadata={
            "task_id": "deepdiff__deep_compare_core__001",
            "language": "python",
            "difficulty": "hard",
            "tags": ["batch-1", "deepdiff", "structural-diff", "hard-first", "data_model_coupling"],
            "source": {
                "name": "deepdiff",
                "url": "https://github.com/seperman/deepdiff",
                "commit": "9.1.0-installed-snapshot",
                "license": "MIT",
            },
            "feature": {
                "name": "DeepDiff path and exclude subset",
                "description": "Extract DeepDiff structural comparison with exclude_paths and parse_path.",
                "source_entrypoints": ["deepdiff.DeepDiff", "deepdiff.path.parse_path", "deepdiff.path.extract"],
                "included_behaviors": [
                    "DeepDiff dict/list value changes",
                    "exclude_paths and include_paths filtering",
                    "parse_path and extract by path expression",
                ],
                "excluded_behaviors": ["DeepSearch", "Delta patch", "original deepdiff import"],
            },
            "entanglement": {
                "level": "high",
                "types": ["data_model_coupling", "parser_state_coupling"],
                "primary": "data_model_coupling",
                "description": "DeepDiff couples path expression parsing, diff tree model, and recursive comparison.",
                "signals": ["exclude_paths wildcard matching", "DiffLevel parent stack", "type-specific relationships"],
            },
            "output": {
                "package": "featurelifted",
                "import": "import featurelifted; from featurelifted import DeepDiff, parse_path, extract",
                "callable": "featurelifted.DeepDiff",
                "signature": "DeepDiff(t1, t2, exclude_paths=None, include_paths=None, **kwargs)",
            },
            "environment": {
                "python": "3.11",
                "network": False,
                "timeout_seconds": 60,
                "dependency_lock": "requirements.lock",
                "allowed_dependencies": [],
                "forbidden_dependencies": ["deepdiff"],
                "forbidden_imports": ["deepdiff"],
            },
            "tests": {"public": "public_tests/", "hidden": "hidden_tests/", "command": "pytest"},
        },
        design="""\
            # Task Design: `deepdiff__deep_compare_core__001`

            Status: draft-spike

            ## Practical reuse

            1. **Reuse module** — Structural diff for config/test assertions.
            2. **Who imports it** — Pipelines needing DeepDiff path filters without search/delta stack.
            3. **Why not copy-all** — search/delta/commands modules inflate copy-all closure.

            ## Module Probes

            | Probe | Remove module | Hidden test(s) that must fail |
            | --- | --- | --- |
            | Diff engine | `featurelifted/diff.py` | `test_nested_dict_change` |
            | Path parser | `featurelifted/path.py` | `test_exclude_paths_wildcard` |
            | Model layer | `featurelifted/model.py` | `test_list_item_added` |

            ## Manual Oracle Closure Plan

            | Check | Target | Result |
            | --- | --- | --- |
            | Public tests | pass | |
            | Hidden tests | pass | |
            | ExtractionRatio | 0.20 – 0.60 | |
            | Copy-All delta | ≥ 0.25 | |

            ## Agent Calibration

            | Run | Model | Passed | ExtractionRatio | final_score | Notes |
            | --- | --- | --- | ---: | ---: | --- |
            | | | | | | Flash deferred |
            """,
        public_tests="""\
            from __future__ import annotations

            from featurelifted import DeepDiff


            def test_shallow_dict_diff() -> None:
                d1 = {"a": 1, "b": 2}
                d2 = {"a": 1, "b": 3}
                diff = DeepDiff(d1, d2)
                assert "values_changed" in diff
                assert diff["values_changed"]["root['b']"]["new_value"] == 3


            def test_identical_nested() -> None:
                d1 = {"x": {"y": [1, 2]}}
                d2 = {"x": {"y": [1, 2]}}
                assert DeepDiff(d1, d2) == {}
            """,
        hidden_tests="""\
            from __future__ import annotations

            import re
            from pathlib import Path

            from featurelifted import DeepDiff, extract, parse_path


            def test_nested_dict_change() -> None:
                d1 = {"outer": {"inner": 1}}
                d2 = {"outer": {"inner": 2}}
                diff = DeepDiff(d1, d2)
                assert "root['outer']['inner']" in diff.get("values_changed", {})


            def test_exclude_paths_wildcard() -> None:
                d1 = {"a": {"secret": 1, "keep": 1}, "b": 2}
                d2 = {"a": {"secret": 9, "keep": 1}, "b": 3}
                diff = DeepDiff(d1, d2, exclude_paths=["root['a']['secret']"])
                assert "root['b']" in diff.get("values_changed", {})
                assert "root['a']['secret']" not in diff.get("values_changed", {})


            def test_list_item_added() -> None:
                d1 = {"items": [1, 2]}
                d2 = {"items": [1, 2, 3]}
                diff = DeepDiff(d1, d2)
                assert "iterable_item_added" in diff


            def test_parse_path_and_extract() -> None:
                obj = {"users": [{"name": "ada"}, {"name": "bob"}]}
                elements = parse_path("root['users'][0]['name']")
                assert elements
                assert extract(obj, "root['users'][0]['name']") == "ada"


            def test_no_deepdiff_import_surface() -> None:
                import featurelifted

                pkg_root = Path(featurelifted.__file__).parent
                import_pattern = re.compile(r"^\\s*(?:from deepdiff|import deepdiff)\\b", re.MULTILINE)
                for path in pkg_root.rglob("*.py"):
                    text = path.read_text(encoding="utf-8")
                    assert not import_pattern.search(text)
            """,
        naive_init="""\
            \"\"\"Naive shallow dict diff — no paths or nested semantics.\"\"\"

            from __future__ import annotations

            from typing import Any


            def DeepDiff(t1, t2, exclude_paths=None, include_paths=None, **kwargs) -> dict[str, Any]:
                del exclude_paths, include_paths, kwargs
                if t1 == t2:
                    return {}
                if isinstance(t1, dict) and isinstance(t2, dict):
                    out: dict[str, Any] = {}
                    for key in set(t1) | set(t2):
                        if t1.get(key) != t2.get(key):
                            out.setdefault("values_changed", {})[f"root['{key}']"] = {
                                "old_value": t1.get(key),
                                "new_value": t2.get(key),
                            }
                    return out
                return {"type_changes": {"root": {"old_type": type(t1), "new_type": type(t2)}}}


            def parse_path(path: str):
                return path


            def extract(obj, path):
                if isinstance(path, str) and path.startswith("root"):
                    parts = path.replace("root", "").replace("[", ".").replace("]", "").replace("'", "")
                    cur: Any = obj
                    for part in parts.split("."):
                        if not part:
                            continue
                        if part.isdigit():
                            cur = cur[int(part)]
                        else:
                            cur = cur[part]
                    return cur
                return obj
            """,
    )


if __name__ == "__main__":
    main()
