from __future__ import annotations

from featurelifted import HTMLRenderer, create_markdown


def test_emphasis_and_code() -> None:
    html = create_markdown()("**bold** and `code`")
    assert "<strong>bold</strong>" in html
    assert "<code>code</code>" in html


def test_strikethrough_plugin() -> None:
    plain = create_markdown()("~~gone~~")
    plugged = create_markdown(plugins=["strikethrough"])("~~gone~~")
    assert "<del>" not in plain
    assert "<del>" in plugged


def test_html_renderer_constructible() -> None:
    renderer = HTMLRenderer()
    assert isinstance(renderer, HTMLRenderer)
