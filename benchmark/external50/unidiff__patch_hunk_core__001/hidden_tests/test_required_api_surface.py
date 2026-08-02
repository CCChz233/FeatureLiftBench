from featurelifted import Hunk, PatchSet, PatchedFile, UnidiffParseError


def test_required_api_surface() -> None:
    assert PatchSet is not None and PatchedFile is not None
    assert Hunk is not None and UnidiffParseError is not None
