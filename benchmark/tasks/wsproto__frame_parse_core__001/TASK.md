# FeatureLift Task: WebSocket frame protocol

Extract wsproto RFC6455 frame parsing, masking, fragmentation, and control frames without HTTP handshake or connection lifecycle.

## Target API

- Import: `from featurelifted.frame_protocol import FrameProtocol, Opcode, ParseFailed, CloseReason, Frame`
- Callable: `featurelifted.frame_protocol.FrameProtocol`
- Signature: `FrameProtocol(client: bool, extensions: list) -> FrameProtocol`

## Excluded Behavior

- HTTP/1.1 upgrade handshake (h11 integration)
- WSConnection state machine and extensions negotiation I/O
- original wsproto import at runtime

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `wsproto`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — parse and serialize text/binary WebSocket frames
- **B002** — client/server masking rules and XOR payload decoding
- **B003** — fragmented message reassembly across continuation frames
- **B004** — ping/pong/close control frames with close codes
- **B005** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B006** — the submitted package does not import forbidden upstream packages: wsproto
<!-- featureliftbench:behavior-clauses:end -->
