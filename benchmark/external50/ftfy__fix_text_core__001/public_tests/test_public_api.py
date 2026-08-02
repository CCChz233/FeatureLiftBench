from __future__ import annotations

from featurelifted import fix_text


def test_fix_latin1_mojibake() -> None:
    assert fix_text("cafÃ©") == "café"


def test_fix_em_dash_mojibake() -> None:
    assert fix_text("â€”") == "—"


def test_fix_identity_ascii() -> None:
    assert fix_text("plain text") == "plain text"
