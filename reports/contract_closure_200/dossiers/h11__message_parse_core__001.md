# h11__message_parse_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `5/20`

## Required API

- `featurelifted.Connection` (class) `(our_role: Type[Sentinel], max_incomplete_event_size: int = 16384) -> None`
- `featurelifted.Connection.next_event` (method) `(self) -> Union[Event, Type[NEED_DATA], Type[PAUSED]]`
- `featurelifted.Connection.receive_data` (method) `(self, data: bytes) -> None`
- `featurelifted.CLIENT` (class) `(name: str, bases: Tuple[type, ...], namespace: Dict[str, Any], **kwds: Any) -> ~_T_Sentinel`
- `featurelifted.SERVER` (class) `(name: str, bases: Tuple[type, ...], namespace: Dict[str, Any], **kwds: Any) -> ~_T_Sentinel`
- `featurelifted.Request` (class) `(*, method: Union[bytes, str], headers: Union[Headers, List[Tuple[bytes, bytes]], List[Tuple[str, str]]], target: Union[bytes, str], http_version: Union[bytes, str] = b'1.1', _parsed: bool = False) -> None`
- `featurelifted.Response` (class) `(*, headers: Union[Headers, List[Tuple[bytes, bytes]], List[Tuple[str, str]]], status_code: int, http_version: Union[bytes, str] = b'1.1', reason: Union[bytes, str] = b'', _parsed: bool = False) -> None`
- `featurelifted.Data` (class) `(data: bytes, chunk_start: bool = False, chunk_end: bool = False) -> None`
- `featurelifted.EndOfMessage` (class) `(*, headers: Union[Headers, List[Tuple[bytes, bytes]], List[Tuple[str, str]], NoneType] = None, _parsed: bool = False) -> None`
- `featurelifted.NEED_DATA` (class) `(name: str, bases: Tuple[type, ...], namespace: Dict[str, Any], **kwds: Any) -> ~_T_Sentinel`
- `featurelifted.RemoteProtocolError` (exception)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: parse request and response start-lines and headers. Required observable cases include parse simple http request; client request serialization; malformed request raises.
- **B002**: The extracted feature must support this observable behavior: frame bodies with content-length and chunked encoding. Required observable cases include chunked response body.
- **B003**: The extracted feature must support this observable behavior: drive client/server role state transitions. Required observable cases include client request serialization; malformed request raises.
- **B004**: The extracted feature must support this observable behavior: surface protocol errors for malformed messages. Required observable cases include malformed request raises.
- **B005**: The extracted feature must support this observable behavior: serialize events back to wire bytes. Required observable cases include malformed request raises.
- **B006**: The package exposes the required task API paths `featurelifted.Connection`, `featurelifted.Connection.next_event`, `featurelifted.Connection.receive_data`, `featurelifted.CLIENT`, `featurelifted.SERVER`, `featurelifted.Request`, `featurelifted.Response`, `featurelifted.Data`, `featurelifted.EndOfMessage`, `featurelifted.NEED_DATA`, `featurelifted.RemoteProtocolError` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_parse_simple_http_request`

- mapping: `B001`
- API: `featurelifted.Connection, featurelifted.SERVER`
- risk: `none`
- A001 `assert` L23: `len(events) == 2`
- A002 `assert` L24: `events[0].method == b'GET'`
- A003 `assert` L25: `events[0].target == b'/hello'`
- A004 `assert` L26: `events[1].__class__.__name__ == 'EndOfMessage'`

### `public_tests/test_public_api.py::test_client_request_serialization`

- mapping: `B001, B003`
- API: `featurelifted.CLIENT, featurelifted.Connection, featurelifted.Request`
- risk: `none`
- A001 `assert` L32: `b'GET / HTTP/1.1' in payload`

### `hidden_tests/test_hidden_behavior.py::test_chunked_response_body`

- mapping: `B002`
- API: `featurelifted.CLIENT, featurelifted.Connection, featurelifted.Data, featurelifted.EndOfMessage, featurelifted.Response`
- risk: `none`
- A001 `assert` L31: `any((isinstance(e, Response) for e in events))`
- A002 `assert` L33: `b''.join((e.data for e in data_events)) == b'hello'`
- A003 `assert` L34: `any((isinstance(e, EndOfMessage) for e in events))`

### `hidden_tests/test_hidden_behavior.py::test_malformed_request_raises`

- mapping: `B001, B003, B004, B005`
- API: `featurelifted.Connection, featurelifted.RemoteProtocolError, featurelifted.SERVER`
- risk: `none`
- A001 `assert` L45: `raised`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B006`
- API: `featurelifted.CLIENT, featurelifted.Connection, featurelifted.Data, featurelifted.EndOfMessage, featurelifted.NEED_DATA, featurelifted.RemoteProtocolError, featurelifted.Request, featurelifted.Response, featurelifted.SERVER`
- risk: `none`
- A001 `assert` L17: `isinstance(Connection, type)`
- A002 `assert` L18: `hasattr(Connection, 'next_event')`
- A003 `assert` L19: `hasattr(Connection, 'receive_data')`
- A004 `assert` L20: `isinstance(CLIENT, type)`
- A005 `assert` L21: `isinstance(SERVER, type)`
- A006 `assert` L22: `isinstance(Request, type)`
- A007 `assert` L23: `isinstance(Response, type)`
- A008 `assert` L24: `isinstance(Data, type)`
- A009 `assert` L25: `isinstance(EndOfMessage, type)`
- A010 `assert` L26: `isinstance(NEED_DATA, type)`
- A011 `assert` L27: `issubclass(RemoteProtocolError, BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `h11`
- source entrypoints: `h11.Connection, h11.Request, h11.Response, h11.Data, h11.EndOfMessage`
- oracle source files: `none`
- runtime dependencies: `none`
