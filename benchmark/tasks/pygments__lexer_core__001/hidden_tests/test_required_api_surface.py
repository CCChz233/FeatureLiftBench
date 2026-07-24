"""Constitution API-surface coverage generated from public_spec."""

from featurelifted import (
    lex,
    get_lexer_by_name,
    PythonLexer,
    token,
)


def test_required_api_surface():
    assert callable(lex)
    assert callable(get_lexer_by_name)
    assert isinstance(PythonLexer, type)
    assert token is not None
