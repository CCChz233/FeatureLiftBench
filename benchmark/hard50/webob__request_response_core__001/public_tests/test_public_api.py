from __future__ import annotations

from featurelifted import Request, Response


def test_blank_get_path_and_query() -> None:
    request = Request.blank("/search?q=lift")
    assert request.method == "GET"
    assert request.path_info == "/search"
    assert request.GET["q"] == "lift"


def test_headers_are_case_insensitive() -> None:
    request = Request.blank("/", headers={"X-Trace": "abc"})
    assert request.headers["x-trace"] == "abc"
    assert request.headers["X-Trace"] == "abc"


def test_blank_post_form_fields() -> None:
    request = Request.blank("/", POST={"name": "ada"})
    assert request.method == "POST"
    assert request.POST["name"] == "ada"


def test_json_response_body_and_status() -> None:
    response = Response(json={"ok": True})
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.json_body == {"ok": True}
