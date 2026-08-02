from featurelifted import jwt
from featurelifted.errors import ExpiredTokenError
from featurelifted.jwk import OctKey


def test_required_api_surface() -> None:
    assert jwt is not None
    assert OctKey is not None
    assert ExpiredTokenError is not None
