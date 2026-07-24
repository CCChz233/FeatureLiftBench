"""Constitution API-surface coverage generated from public_spec."""

from featurelifted import (
    Lexer,
    parsetree,
    PythonCode,
    PythonFragment,
    SyntaxException,
    CompileException,
)


def test_required_api_surface():
    assert isinstance(Lexer, type)
    assert hasattr(Lexer, 'parse')
    assert parsetree is not None
    assert isinstance(PythonCode, type)
    assert isinstance(PythonFragment, type)
    assert PythonFragment is not None
    assert PythonFragment is not None
    assert issubclass(SyntaxException, BaseException)
    assert issubclass(CompileException, BaseException)
