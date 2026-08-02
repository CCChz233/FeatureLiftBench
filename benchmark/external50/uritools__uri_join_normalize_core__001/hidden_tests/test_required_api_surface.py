from featurelifted import (
    SplitResult,
    uridecode,
    uriencode,
    urijoin,
    urinorm,
    urisplit,
    uriunsplit,
)


def test_required_api_surface() -> None:
    assert callable(urisplit)
    assert callable(uriunsplit)
    assert callable(urijoin)
    assert callable(urinorm)
    assert callable(uriencode)
    assert callable(uridecode)
    assert SplitResult is not None
