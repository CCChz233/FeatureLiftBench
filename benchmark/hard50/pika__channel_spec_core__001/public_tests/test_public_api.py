from __future__ import annotations

from featurelifted.frame import Heartbeat, Method, decode_frame
from featurelifted.spec import Basic


def test_heartbeat_roundtrip() -> None:
    payload = Heartbeat().marshal()
    consumed, framed = decode_frame(payload)
    assert consumed == len(payload)
    assert isinstance(framed, Heartbeat)


def test_basic_ack_roundtrip() -> None:
    payload = Method(1, Basic.Ack(delivery_tag=7, multiple=True)).marshal()
    consumed, framed = decode_frame(payload)
    assert consumed == len(payload)
    assert framed.channel_number == 1
    assert framed.method.NAME == "Basic.Ack"
    assert framed.method.delivery_tag == 7
    assert framed.method.multiple is True
