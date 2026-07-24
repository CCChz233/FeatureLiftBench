"""Constitution API-surface coverage generated from public_spec."""

from featurelifted import (
    MarkerRegistry,
    parse_linelist,
    split_marker_line,
)


def test_required_api_surface():
    assert isinstance(MarkerRegistry, type)
    assert hasattr(MarkerRegistry, 'from_ini')
    assert hasattr(MarkerRegistry, 'names')
    assert callable(parse_linelist)
    assert callable(split_marker_line)
