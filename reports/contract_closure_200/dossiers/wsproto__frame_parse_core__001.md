# wsproto__frame_parse_core__001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `10/19`

## Required API

- `featurelifted.frame_protocol` (module)
- `featurelifted.frame_protocol.CloseReason` (class) `(*values)`
- `featurelifted.frame_protocol.FrameProtocol` (class) `(client: 'bool', extensions: 'list[Extension]') -> 'None'`
- `featurelifted.frame_protocol.FrameProtocol.close` (method) `(self, code: 'int | None' = None, reason: 'str | None' = None) -> 'bytearray'`
- `featurelifted.frame_protocol.FrameProtocol.receive_bytes` (method) `(self, data: 'bytes') -> 'None'`
- `featurelifted.frame_protocol.FrameProtocol.received_frames` (method) `(self) -> 'Generator[Frame, None, None]'`
- `featurelifted.frame_protocol.ParseFailed` (exception)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: parse and serialize text/binary WebSocket frames. Required observable cases include client receives unmasked text; binary frame extended payload length.
- **B002**: The extracted feature must support this observable behavior: client/server masking rules and XOR payload decoding. Required observable cases include client receives unmasked text; client send data; server decodes masked client frame; role masking validation.
- **B003**: The extracted feature must support this observable behavior: fragmented message reassembly across continuation frames. Required observable cases include fragmented message reassembly; reserved bit set on data frame.
- **B004**: The extracted feature must support this observable behavior: ping/pong/close control frames with close codes. Required observable cases include close frame code and reason; close frame rejects one byte payload; reserved bit set on data frame.
- **B005**: The package exposes the required task API paths `featurelifted.frame_protocol`, `featurelifted.frame_protocol.CloseReason`, `featurelifted.frame_protocol.FrameProtocol`, `featurelifted.frame_protocol.FrameProtocol.close`, `featurelifted.frame_protocol.FrameProtocol.receive_bytes`, `featurelifted.frame_protocol.FrameProtocol.received_frames`, `featurelifted.frame_protocol.ParseFailed` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_client_receives_unmasked_text`

- mapping: `B001, B002`
- API: `featurelifted.frame_protocol`
- risk: `none`
- A001 `assert` L10: `frame.payload == 'hello'`

### `public_tests/test_public_api.py::test_client_send_data`

- mapping: `B002`
- API: `featurelifted.frame_protocol`
- risk: `none`
- A001 `assert` L16: `out[0] & 15 == 1`

### `hidden_tests/test_hidden_behavior.py::test_server_decodes_masked_client_frame`

- mapping: `B002`
- API: `featurelifted.frame_protocol`
- risk: `none`
- A001 `assert` L18: `frame.payload == 'abc'`

### `hidden_tests/test_hidden_behavior.py::test_fragmented_message_reassembly`

- mapping: `B003`
- API: `featurelifted.frame_protocol`
- risk: `none`
- A001 `assert` L26: `frames[0].payload == 'hello'`
- A002 `assert` L27: `frames[1].payload == 'wor'`
- A003 `assert` L28: `frames[1].message_finished is False`

### `hidden_tests/test_hidden_behavior.py::test_close_frame_code_and_reason`

- mapping: `B004`
- API: `featurelifted.frame_protocol`
- risk: `none`
- A001 `assert` L38: `code == 1000`
- A002 `assert` L39: `reason == 'bye'`

### `hidden_tests/test_hidden_behavior.py::test_binary_frame_extended_payload_length`

- mapping: `B001`
- API: `featurelifted.frame_protocol`
- risk: `none`
- A001 `assert` L48: `len(frame.payload) == 200`

### `hidden_tests/test_hidden_behavior.py::test_close_frame_rejects_one_byte_payload`

- mapping: `B004`
- API: `featurelifted.frame_protocol`
- risk: `exact_error_text, exception_semantics`
- A001 `raises` L55: `pytest.raises(ParseFailed, match='1 byte payload')`

### `hidden_tests/test_hidden_behavior.py::test_reserved_bit_set_on_data_frame`

- mapping: `B003, B004`
- API: `featurelifted.frame_protocol`
- risk: `exact_error_text, exception_semantics`
- A001 `raises` L62: `pytest.raises(ParseFailed, match='Reserved bit')`

### `hidden_tests/test_hidden_behavior.py::test_role_masking_validation`

- mapping: `B002`
- API: `featurelifted.frame_protocol`
- risk: `exception_semantics`
- A001 `raises` L69: `pytest.raises(ParseFailed)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.frame_protocol`
- risk: `none`
- A001 `assert` L9: `frame_protocol is not None`
- A002 `assert` L10: `isinstance(getattr(frame_protocol, 'CloseReason'), type)`
- A003 `assert` L11: `isinstance(getattr(frame_protocol, 'FrameProtocol'), type)`
- A004 `assert` L12: `hasattr(getattr(frame_protocol, 'FrameProtocol'), 'close')`
- A005 `assert` L13: `hasattr(getattr(frame_protocol, 'FrameProtocol'), 'receive_bytes')`
- A006 `assert` L14: `hasattr(getattr(frame_protocol, 'FrameProtocol'), 'received_frames')`
- A007 `assert` L15: `issubclass(getattr(frame_protocol, 'ParseFailed'), BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `wsproto`
- source entrypoints: `wsproto.frame_protocol.FrameProtocol, wsproto.frame_protocol.Opcode, wsproto.frame_protocol.ParseFailed`
- oracle source files: `none`
- runtime dependencies: `none`
- oracle notes: Oracle is frame_protocol closure; repo includes wsproto and h11 for copy-all penalty.
