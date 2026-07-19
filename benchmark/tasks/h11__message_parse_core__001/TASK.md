# FeatureLift Task: HTTP/1.1 message parse and state machine

Extract h11 Connection state machine for parsing and framing HTTP/1.1 request/response messages.

## Target API

- Import: `from featurelifted import Connection, CLIENT, SERVER, Request, Response, Data, EndOfMessage, NEED_DATA, RemoteProtocolError`
- Callable: `featurelifted.Connection`
- Signature: `Connection(our_role, max_incomplete_event_size=16384)`

## Excluded Behavior

- socket I/O and TLS
- HTTP/2 or WebSocket upgrades beyond state flags
- original project tests

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `h11`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — parse request and response start-lines and headers
- **B002** — frame bodies with content-length and chunked encoding
- **B003** — drive client/server role state transitions
- **B004** — surface protocol errors for malformed messages
- **B005** — serialize events back to wire bytes
- **B006** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B007** — the submitted package does not import forbidden upstream packages: h11
<!-- featureliftbench:behavior-clauses:end -->
