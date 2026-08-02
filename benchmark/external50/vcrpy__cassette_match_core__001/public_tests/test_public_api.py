from __future__ import annotations

import urllib.request

from featurelifted import use_cassette

CASSETTE = """version: 1
interactions:
- request:
    body: null
    headers:
      Accept:
      - '*/*'
    method: GET
    uri: http://example.com/
  response:
    body:
      string: hello-vcr
    headers:
      Content-Type:
      - text/plain
    status:
      code: 200
      message: OK"""


def test_use_cassette_replay(tmp_path) -> None:
    path = tmp_path / "example.yaml"
    path.write_text(CASSETTE, encoding="utf-8")
    with use_cassette(str(path), record_mode="none"):
        resp = urllib.request.urlopen("http://example.com/")
        assert resp.read().decode() == "hello-vcr"


def test_vcr_factory() -> None:
    from featurelifted import VCR

    v = VCR(record_mode="none", match_on=["method", "uri"])
    assert v.record_mode == "none"
