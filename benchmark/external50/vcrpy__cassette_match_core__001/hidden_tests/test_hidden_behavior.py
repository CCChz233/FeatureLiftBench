from __future__ import annotations

import urllib.request

from featurelifted import VCR, use_cassette

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


def test_match_on_method_uri(tmp_path) -> None:
    path = tmp_path / "match.yaml"
    path.write_text(CASSETTE, encoding="utf-8")
    with VCR(record_mode="none", match_on=["method", "uri"]).use_cassette(str(path)):
        body = urllib.request.urlopen("http://example.com/").read()
        assert body == b"hello-vcr"


def test_cassette_path_record_mode_none(tmp_path) -> None:
    path = tmp_path / "replay.yaml"
    path.write_text(CASSETTE, encoding="utf-8")
    with use_cassette(str(path), record_mode="none") as cass:
        urllib.request.urlopen("http://example.com/")
        assert cass.play_count >= 1


def test_no_upstream_import_surface() -> None:
    import re
    from pathlib import Path
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(
        rf"^\s*(?:from vcr\b|import vcr\b)",
        re.MULTILINE,
    )
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
