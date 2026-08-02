from __future__ import annotations

import re
from pathlib import Path


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\\s*(?:from jsonpickle\\b|import jsonpickle\\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path


from featurelifted import decode, encode


def test_unpicklable_false_dict_mode() -> None:
    class Thing:
        def __init__(self, name: str) -> None:
            self.name = name

    blob = encode(Thing("Ada"), unpicklable=False)
    data = decode(blob)
    assert data["name"] == "Ada"
