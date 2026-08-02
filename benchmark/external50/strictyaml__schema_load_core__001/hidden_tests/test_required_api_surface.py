from featurelifted import (
    Bool,
    Int,
    Map,
    MapPattern,
    Optional,
    Seq,
    Str,
    StrictYAMLError,
    YAMLValidationError,
    load,
)


def test_required_api_surface() -> None:
    assert callable(load)
    assert all(x is not None for x in (Map, Seq, Str, Int, Bool, Optional, MapPattern))
    assert YAMLValidationError is not None and StrictYAMLError is not None
