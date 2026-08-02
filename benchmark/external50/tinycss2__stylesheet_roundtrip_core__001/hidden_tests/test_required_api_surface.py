from featurelifted import parse_stylesheet, serialize
from featurelifted.ast import AtRule, ParseError, QualifiedRule


def test_required_api_surface() -> None:
    assert callable(parse_stylesheet)
    assert callable(serialize)
    assert QualifiedRule is not None and AtRule is not None and ParseError is not None
