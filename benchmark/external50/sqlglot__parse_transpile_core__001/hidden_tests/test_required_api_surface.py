from featurelifted import exp, parse, parse_one, transpile
from featurelifted.errors import ParseError


def test_required_api_surface() -> None:
    assert callable(parse_one) and callable(parse) and callable(transpile)
    assert exp.Select is not None and exp.Column is not None
    assert issubclass(ParseError, Exception)
