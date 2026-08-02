from __future__ import annotations

import re
from pathlib import Path

from featurelifted import Int, Map, Optional, Seq, Str, StrictYAMLError, YAMLValidationError, load


def test_optional_key_absent() -> None:
    schema = Map({"name": Str(), Optional("nick"): Str()})
    doc = load("name: Ada", schema)
    assert doc.data == {"name": "Ada"}


def test_nested_seq_map() -> None:
    schema = Map({"items": Seq(Map({"id": Int(), "label": Str()}))})
    doc = load("items:\n  - id: 1\n    label: a\n  - id: 2\n    label: b", schema)
    items = doc.data["items"]
    assert items[1]["label"] == "b"


def test_strict_error_hierarchy() -> None:
    assert issubclass(YAMLValidationError, StrictYAMLError)


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\s*(?:from strictyaml\b|import strictyaml\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
