from __future__ import annotations

import re
from pathlib import Path


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\\s*(?:from configupdater\\b|import configupdater\\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path


from io import StringIO

from featurelifted import ConfigUpdater


def test_multiple_sections_roundtrip() -> None:
    text = "[a]\nx=1\n\n[b]\n# note\ny=2\n"
    cu = ConfigUpdater()
    cu.read_string(text)
    cu["b"]["y"].value = "9"
    buf = StringIO()
    cu.write(buf)
    out = buf.getvalue()
    assert "# note" in out
    assert "y = 9" in out
    assert "[a]" in out and "[b]" in out
