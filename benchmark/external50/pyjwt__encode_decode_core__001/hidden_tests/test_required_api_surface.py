from featurelifted import decode, encode
from featurelifted.exceptions import ExpiredSignatureError, InvalidSignatureError, InvalidTokenError


def test_required_api_surface() -> None:
    assert callable(encode) and callable(decode)
    assert InvalidTokenError is not None
    assert ExpiredSignatureError is not None and InvalidSignatureError is not None
