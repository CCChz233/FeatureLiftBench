from featurelifted import decode, encode, register
from featurelifted.handlers import BaseHandler


def test_required_api_surface() -> None:
    assert callable(encode) and callable(decode) and callable(register)
    assert BaseHandler is not None
