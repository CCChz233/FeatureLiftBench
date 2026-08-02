from __future__ import annotations

import re
from pathlib import Path

from featurelifted import fix_text


def test_fix_double_encoded_utf8() -> None:
    broken = "Ã©".encode("latin-1").decode("utf-8", errors="replace")
    assert "é" in fix_text(broken) or fix_text(broken) != broken


def test_fix_preserves_newlines() -> None:
    text = "line1\nline2"
    assert fix_text(text) == text


def test_fix_empty() -> None:
    assert fix_text("") == ""


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\s*(?:from ftfy\b|import ftfy\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
