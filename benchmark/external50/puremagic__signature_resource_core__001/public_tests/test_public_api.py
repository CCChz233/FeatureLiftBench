from io import BytesIO
from featurelifted import from_stream, from_string

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32


def test_string_and_stream_detection():
    assert from_string(PNG) == ".png"
    assert from_stream(BytesIO(PNG)) == ".png"


def test_mime_detection():
    assert from_string(PNG, mime=True) == "image/png"
