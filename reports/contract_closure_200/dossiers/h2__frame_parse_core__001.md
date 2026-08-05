# h2__frame_parse_core__001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `7/32`

## Required API

- `featurelifted.h2.exceptions` (module)
- `featurelifted.h2.exceptions.FrameTooLargeError` (exception)
- `featurelifted.h2.exceptions.ProtocolError` (exception)
- `featurelifted.h2.frame_buffer` (module)
- `featurelifted.h2.frame_buffer.FrameBuffer` (class) `(server: 'bool' = False) -> 'None'`
- `featurelifted.h2.frame_buffer.FrameBuffer.add_data` (method) `(self, data: 'bytes') -> 'None'`
- `featurelifted.h2.frame_buffer.FrameBuffer.max_frame_size` (attribute)
- `featurelifted.hyperframe.exceptions` (module)
- `featurelifted.hyperframe.exceptions.InvalidDataError` (exception)
- `featurelifted.hyperframe.frame` (module)
- `featurelifted.hyperframe.frame.ContinuationFrame` (class) `(stream_id: 'int', data: 'bytes' = b'', **kwargs: 'Any') -> 'None'`
- `featurelifted.hyperframe.frame.ContinuationFrame.data` (attribute)
- `featurelifted.hyperframe.frame.ContinuationFrame.flags` (attribute)
- `featurelifted.hyperframe.frame.ContinuationFrame.serialize` (method) `(self) -> 'bytes'`
- `featurelifted.hyperframe.frame.DataFrame` (class) `(stream_id: 'int', data: 'bytes' = b'', **kwargs: 'Any') -> 'None'`
- `featurelifted.hyperframe.frame.DataFrame.data` (attribute)
- `featurelifted.hyperframe.frame.DataFrame.serialize` (method) `(self) -> 'bytes'`
- `featurelifted.hyperframe.frame.Frame` (class) `(stream_id: 'int', flags: 'Iterable[str]' = ()) -> 'None'`
- `featurelifted.hyperframe.frame.HeadersFrame` (class) `(stream_id: 'int', data: 'bytes' = b'', **kwargs: 'Any') -> 'None'`
- `featurelifted.hyperframe.frame.HeadersFrame.data` (attribute)
- `featurelifted.hyperframe.frame.HeadersFrame.serialize` (method) `(self) -> 'bytes'`
- `featurelifted.hyperframe.frame.PingFrame` (class) `(stream_id: 'int' = 0, opaque_data: 'bytes' = b'', **kwargs: 'Any') -> 'None'`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: parse and serialize HTTP/2 frames (DATA, HEADERS, PING, SETTINGS, etc.). Required observable cases include ping frame roundtrip; data frame via frame buffer; ping stream id must be zero; frame buffer rejects bad preamble; frame buffer enforces max frame size.
- **B002**: The extracted feature must support this observable behavior: FrameBuffer incremental parsing with continuation reassembly. Required observable cases include continuation reassembly.
- **B003**: The extracted feature must support this observable behavior: HTTP/2 connection preamble validation for server mode. Required observable cases include frame buffer rejects bad preamble.
- **B004**: The extracted feature must support this observable behavior: frame size limits and typed protocol errors. Required observable cases include frame buffer enforces max frame size.
- **B005**: The package exposes the required task API paths `featurelifted.h2.exceptions`, `featurelifted.h2.exceptions.FrameTooLargeError`, `featurelifted.h2.exceptions.ProtocolError`, `featurelifted.h2.frame_buffer`, `featurelifted.h2.frame_buffer.FrameBuffer`, `featurelifted.h2.frame_buffer.FrameBuffer.add_data`, `featurelifted.h2.frame_buffer.FrameBuffer.max_frame_size`, `featurelifted.hyperframe.exceptions`, `featurelifted.hyperframe.exceptions.InvalidDataError`, `featurelifted.hyperframe.frame`, `featurelifted.hyperframe.frame.ContinuationFrame`, `featurelifted.hyperframe.frame.ContinuationFrame.data`, and 10 listed members with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_ping_frame_roundtrip`

- mapping: `B001`
- API: `featurelifted.h2.frame_buffer, featurelifted.hyperframe.frame`
- risk: `none`
- A001 `assert` L12: `isinstance(frame, PingFrame)`
- A002 `assert` L13: `frame.stream_id == 0`

### `public_tests/test_public_api.py::test_data_frame_via_frame_buffer`

- mapping: `B001`
- API: `featurelifted.h2.frame_buffer, featurelifted.hyperframe.frame`
- risk: `none`
- A001 `assert` L23: `len(frames) == 1`
- A002 `assert` L24: `frames[0].data == b'hello'`

### `hidden_tests/test_hidden_behavior.py::test_ping_stream_id_must_be_zero`

- mapping: `B001`
- API: `featurelifted.h2.exceptions, featurelifted.h2.frame_buffer, featurelifted.hyperframe.exceptions, featurelifted.hyperframe.frame`
- risk: `exception_semantics`
- A001 `raises` L18: `pytest.raises(InvalidDataError)`

### `hidden_tests/test_hidden_behavior.py::test_frame_buffer_rejects_bad_preamble`

- mapping: `B001, B003`
- API: `featurelifted.h2.exceptions, featurelifted.h2.frame_buffer, featurelifted.hyperframe.exceptions, featurelifted.hyperframe.frame`
- risk: `exception_semantics`
- A001 `raises` L24: `pytest.raises(ProtocolError)`

### `hidden_tests/test_hidden_behavior.py::test_frame_buffer_enforces_max_frame_size`

- mapping: `B001, B004`
- API: `featurelifted.h2.exceptions, featurelifted.h2.frame_buffer, featurelifted.hyperframe.exceptions, featurelifted.hyperframe.frame`
- risk: `exception_semantics`
- A001 `raises` L33: `pytest.raises(FrameTooLargeError)`

### `hidden_tests/test_hidden_behavior.py::test_continuation_reassembly`

- mapping: `B002`
- API: `featurelifted.h2.exceptions, featurelifted.h2.frame_buffer, featurelifted.hyperframe.exceptions, featurelifted.hyperframe.frame`
- risk: `none`
- A001 `assert` L48: `len(out) == 1`
- A002 `assert` L49: `isinstance(out[0], HeadersFrame)`
- A003 `assert` L50: `out[0].data == b'part-apart-b'`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.h2, featurelifted.h2.exceptions, featurelifted.h2.frame_buffer, featurelifted.hyperframe, featurelifted.hyperframe.exceptions, featurelifted.hyperframe.frame`
- risk: `none`
- A001 `assert` L15: `getattr(h2, 'exceptions') is not None`
- A002 `assert` L16: `issubclass(getattr(getattr(h2, 'exceptions'), 'FrameTooLargeError'), BaseException)`
- A003 `assert` L17: `issubclass(getattr(getattr(h2, 'exceptions'), 'ProtocolError'), BaseException)`
- A004 `assert` L18: `getattr(h2, 'frame_buffer') is not None`
- A005 `assert` L19: `isinstance(getattr(getattr(h2, 'frame_buffer'), 'FrameBuffer'), type)`
- A006 `assert` L20: `hasattr(getattr(getattr(h2, 'frame_buffer'), 'FrameBuffer'), 'add_data')`
- A007 `assert` L21: `getattr(getattr(h2, 'frame_buffer'), 'FrameBuffer') is not None`
- A008 `assert` L22: `getattr(hyperframe, 'exceptions') is not None`
- A009 `assert` L23: `issubclass(getattr(getattr(hyperframe, 'exceptions'), 'InvalidDataError'), BaseException)`
- A010 `assert` L24: `getattr(hyperframe, 'frame') is not None`
- A011 `assert` L25: `isinstance(getattr(getattr(hyperframe, 'frame'), 'ContinuationFrame'), type)`
- A012 `assert` L26: `getattr(getattr(hyperframe, 'frame'), 'ContinuationFrame') is not None`
- A013 `assert` L27: `getattr(getattr(hyperframe, 'frame'), 'ContinuationFrame') is not None`
- A014 `assert` L28: `hasattr(getattr(getattr(hyperframe, 'frame'), 'ContinuationFrame'), 'serialize')`
- A015 `assert` L29: `isinstance(getattr(getattr(hyperframe, 'frame'), 'DataFrame'), type)`
- A016 `assert` L30: `getattr(getattr(hyperframe, 'frame'), 'DataFrame') is not None`
- A017 `assert` L31: `hasattr(getattr(getattr(hyperframe, 'frame'), 'DataFrame'), 'serialize')`
- A018 `assert` L32: `isinstance(getattr(getattr(hyperframe, 'frame'), 'Frame'), type)`
- A019 `assert` L33: `isinstance(getattr(getattr(hyperframe, 'frame'), 'HeadersFrame'), type)`
- A020 `assert` L34: `getattr(getattr(hyperframe, 'frame'), 'HeadersFrame') is not None`
- A021 `assert` L35: `hasattr(getattr(getattr(hyperframe, 'frame'), 'HeadersFrame'), 'serialize')`
- A022 `assert` L36: `isinstance(getattr(getattr(hyperframe, 'frame'), 'PingFrame'), type)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `h2, hyperframe`
- source entrypoints: `hyperframe.frame.Frame.parse_frame_header, hyperframe.frame.DataFrame.serialize, h2.frame_buffer.FrameBuffer`
- oracle source files: `none`
- runtime dependencies: `none`
- oracle notes: Oracle is hyperframe framing plus h2 FrameBuffer; repo includes full h2 and hyperframe for copy-all penalty.
