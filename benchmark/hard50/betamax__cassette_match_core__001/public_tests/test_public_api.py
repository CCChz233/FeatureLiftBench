from __future__ import annotations

import json

import requests

from featurelifted import Betamax, BetamaxError


def _write_cassette(directory, name: str, uri: str, body: str) -> None:
    payload = {
        "http_interactions": [
            {
                "request": {
                    "body": {"encoding": "utf-8", "string": ""},
                    "headers": {"Accept": ["*/*"]},
                    "method": "GET",
                    "uri": uri,
                },
                "response": {
                    "body": {"encoding": "utf-8", "string": body},
                    "headers": {
                        "Content-Type": ["text/plain"],
                        "Content-Length": [str(len(body))],
                    },
                    "status": {"code": 200, "message": "OK"},
                    "url": uri,
                },
                "recorded_at": "2020-01-01T00:00:00",
            }
        ],
        "recorded_with": "betamax/0.9.0",
    }
    (directory / f"{name}.json").write_text(json.dumps(payload), encoding="utf-8")


def test_replay_cassette_body(tmp_path) -> None:
    _write_cassette(tmp_path, "hello", "http://example.test/hello", "cassette-body")
    session = requests.Session()
    with Betamax(session, cassette_library_dir=str(tmp_path)).use_cassette(
        "hello", record="none"
    ):
        response = session.get("http://example.test/hello")
    assert response.status_code == 200
    assert response.text == "cassette-body"


def test_uri_mismatch_errors(tmp_path) -> None:
    _write_cassette(tmp_path, "hello", "http://example.test/hello", "cassette-body")
    session = requests.Session()
    raised = False
    try:
        with Betamax(session, cassette_library_dir=str(tmp_path)).use_cassette(
            "hello", record="none"
        ):
            session.get("http://example.test/other")
    except BetamaxError:
        raised = True
    assert raised


def test_missing_cassette_errors(tmp_path) -> None:
    session = requests.Session()
    raised = False
    try:
        with Betamax(session, cassette_library_dir=str(tmp_path)).use_cassette(
            "missing", record="none"
        ):
            pass
    except ValueError:
        raised = True
    assert raised
