from __future__ import annotations

import pytest

from featurelifted.frame_protocol import CloseReason, FrameProtocol, ParseFailed


def test_server_decodes_masked_client_frame() -> None:
    fp = FrameProtocol(client=False, extensions=[])
    key = bytes([1, 2, 3, 4])
    payload = b"abc"
    masked = bytearray([0x81, 0x80 | len(payload)]) + bytearray(key)
    masked += bytearray(payload[i] ^ key[i % 4] for i in range(len(payload)))
    fp.receive_bytes(masked)
    frame = next(fp.received_frames())
    assert frame.payload == "abc"


def test_fragmented_message_reassembly() -> None:
    fp = FrameProtocol(client=True, extensions=[])
    fp.receive_bytes(b"\x01\x05hello")
    fp.receive_bytes(b"\x00\x03wor")
    frames = list(fp.received_frames())
    assert frames[0].payload == "hello"
    assert frames[1].payload == "wor"
    assert frames[1].message_finished is False


def test_close_frame_code_and_reason() -> None:
    sender = FrameProtocol(client=True, extensions=[])
    payload = sender.close(code=1000, reason="bye")
    receiver = FrameProtocol(client=False, extensions=[])
    receiver.receive_bytes(payload)
    frame = next(receiver.received_frames())
    code, reason = frame.payload
    assert code == 1000
    assert reason == "bye"


def test_role_masking_validation() -> None:
    fp = FrameProtocol(client=False, extensions=[])
    with pytest.raises(ParseFailed):
        fp.receive_bytes(b"\x81\x05hello")
        list(fp.received_frames())
