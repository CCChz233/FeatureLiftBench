from __future__ import annotations

from featurelifted import decode, encode, register
from featurelifted.handlers import BaseHandler


class Point:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


class PointHandler(BaseHandler):
    def flatten(self, obj, data):
        data["x"] = obj.x
        data["y"] = obj.y
        return data

    def restore(self, data):
        return Point(data["x"], data["y"])


def test_encode_decode_builtin() -> None:
    payload = {"a": [1, 2], "b": "x"}
    assert decode(encode(payload)) == payload


def test_custom_handler_roundtrip() -> None:
    register(Point, PointHandler)
    p = Point(3, 4)
    restored = decode(encode(p))
    assert isinstance(restored, Point)
    assert restored.x == 3 and restored.y == 4
