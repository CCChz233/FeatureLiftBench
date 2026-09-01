from __future__ import annotations

from featurelifted import HTTPHeaders


def test_parse_content_type_and_length() -> None:
    headers = HTTPHeaders.parse("Content-Type: text/html\r\nContent-Length: 42\r\n")
    assert sorted(headers.items()) == [("Content-Length", "42"), ("Content-Type", "text/html")]


def test_set_cookie_get_list() -> None:
    headers = HTTPHeaders()
    headers.add("Set-Cookie", "A=B")
    headers.add("Set-Cookie", "C=D")
    assert headers.get_list("set-cookie") == ["A=B", "C=D"]
    assert headers["set-cookie"] == "A=B,C=D"
