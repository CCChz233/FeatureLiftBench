import pytest
from featurelifted import PureError, from_extension, magic_string


def test_extension_metadata_lookup():
    assert from_extension(".png") == "image/png"


def test_ranked_matches_and_unknown_input():
    matches = magic_string(b"%PDF-1.7\n")
    assert matches and matches[0].extension == ".pdf"
    with pytest.raises((PureError, ValueError)): magic_string(b"")


def test_required_api_surface():
    from featurelifted import PureError, from_extension, from_stream, from_string, magic_string
    assert all(callable(x) for x in (from_string, from_stream, magic_string, from_extension))
    assert issubclass(PureError, Exception)


def test_no_upstream_import_surface():
    import re
    from pathlib import Path
    import featurelifted
    pattern = re.compile(r"^\s*(?:from puremagic|import puremagic)\b", re.MULTILINE)
    for path in Path(featurelifted.__file__).parent.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8"))
