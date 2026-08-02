from __future__ import annotations

from featurelifted import URL


def test_from_text_and_to_text() -> None:
    url = URL.from_text("https://example.com/a/b?x=1#frag")
    text = url.to_text()
    assert text.startswith("https://example.com/")
    assert "x=1" in text
    assert "#frag" in text


def test_replace_scheme_host() -> None:
    url = URL.from_text("http://old.test/path")
    updated = url.replace(scheme="https", host="new.test")
    assert updated.to_text().startswith("https://new.test")


def test_click_relative() -> None:
    base = URL.from_text("https://example.com/a/b/")
    clicked = base.click("../c")
    assert "/a/c" in clicked.to_text() or clicked.to_text().endswith("/a/c")
