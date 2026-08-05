from __future__ import annotations

import re
from io import StringIO
from pathlib import Path

from featurelifted import CommentedMap, YAML


def test_eol_comment_preserved() -> None:
    text = "key: value  # note\n"
    yaml = YAML()
    data = yaml.load(text)
    stream = StringIO()
    yaml.dump(data, stream)
    assert "# note" in stream.getvalue()
    assert data["key"] == "value"


def test_flow_style_dump() -> None:
    data = CommentedMap([("a", 1), ("b", 2)])
    data.fa.set_flow_style()
    stream = StringIO()
    YAML().dump(data, stream)
    out = stream.getvalue()
    assert out.strip().startswith("{") or "[" in out


def test_literal_block_scalar() -> None:
    text = "body: |\n  line1\n  line2\n"
    data = YAML().load(text)
    assert data["body"] == "line1\nline2\n"
    stream = StringIO()
    YAML().dump(data, stream)
    assert "|" in stream.getvalue()


def test_anchor_alias_roundtrip() -> None:
    text = "base: &id\n  x: 1\nchild: *id\n"
    data = YAML().load(text)
    assert data["child"]["x"] == 1


def test_key_order_hidden() -> None:
    data = YAML().load("third: 3\nfirst: 1\nsecond: 2\n")
    assert list(data.keys()) == ["third", "first", "second"]


def test_no_ruamel_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    import_pattern = re.compile(
        r"^\s*(?:from (?:ruamel|_ruamel_yaml)|import (?:ruamel|_ruamel_yaml))\b",
        re.MULTILINE,
    )
    for path in pkg_root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert not import_pattern.search(text)
