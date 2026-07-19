# FeatureLift Task: HTTP/2 frame parse and buffer

Extract hyperframe HTTP/2 frame serialization and h2 FrameBuffer reassembly without connection/stream state machines.

## Target API

- Import: `from featurelifted.hyperframe.frame import Frame, DataFrame, PingFrame, HeadersFrame, ContinuationFrame, SettingsFrame; from featurelifted.h2.frame_buffer import FrameBuffer; from featurelifted.h2.exceptions import ProtocolError, FrameTooLargeError; from featurelifted.hyperframe.exceptions import InvalidDataError, InvalidFrameError`
- Callable: `featurelifted.hyperframe.frame.Frame.parse_frame_header`
- Signature: `Frame.parse_frame_header(memoryview) -> tuple[Frame, int]`

## Excluded Behavior

- h2 connection and stream state machines
- HPACK header compression and flow control windows
- network sockets and asyncio integration
- original h2 or hyperframe imports at runtime

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `h2`, `hyperframe`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — parse and serialize HTTP/2 frames (DATA, HEADERS, PING, SETTINGS, etc.)
- **B002** — FrameBuffer incremental parsing with continuation reassembly
- **B003** — HTTP/2 connection preamble validation for server mode
- **B004** — frame size limits and typed protocol errors
- **B005** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B006** — the submitted package does not import forbidden upstream packages: h2, hyperframe
<!-- featureliftbench:behavior-clauses:end -->
