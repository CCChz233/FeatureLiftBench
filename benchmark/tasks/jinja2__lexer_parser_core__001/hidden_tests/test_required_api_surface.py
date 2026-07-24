"""Constitution API-surface coverage generated from public_spec."""

from featurelifted import (
    Environment,
    nodes,
    lexer,
    parser,
)


def test_required_api_surface():
    assert isinstance(Environment, type)
    assert hasattr(Environment, 'parse')
    assert nodes is not None
    assert lexer is not None
    assert isinstance(getattr(lexer, 'Lexer'), type)
    assert hasattr(getattr(lexer, 'Lexer'), 'tokenize')
    assert parser is not None
    assert isinstance(getattr(parser, 'Parser'), type)
