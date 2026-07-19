# FeatureLift Task: WebSocket HTTP upgrade handshake parsing

Extract websockets HTTP/1.1 handshake request parsing, header grammars (Connection, Upgrade, extensions, subprotocols), and handshake header validation without socket I/O or frame protocol.

## Target API

- Import: `import featurelifted; from featurelifted import Headers, Request, Response, accept_key, generate_key, validate_handshake_request; from featurelifted.headers import parse_connection, parse_upgrade, parse_extension, parse_subprotocol, build_subprotocol, validate_subprotocols, parse_authorization_basic, build_authorization_basic, build_www_authenticate_basic; from featurelifted.exceptions import InvalidHeaderFormat, InvalidHeaderValue, InvalidUpgrade, InvalidHeader, InvalidOrigin, SecurityError; from featurelifted.http11 import parse_headers; from featurelifted.streams import StreamReader`
- Callable: `featurelifted.validate_handshake_request`
- Signature: `validate_handshake_request(request, *, origins=None)`

## Excluded Behavior

- socket and asyncio/sync network I/O
- WebSocket frame encoding and masking
- ServerProtocol and ClientProtocol connection state machines
- extensions negotiation with permessage-deflate implementations
- CLI, docs, CI, and original tests
- original websockets package import at runtime

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `websockets`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — parse Connection and Upgrade header lists with OWS and empty elements
- **B002** — parse Sec-WebSocket-Extensions and Sec-WebSocket-Protocol grammars
- **B003** — parse WebSocket handshake HTTP requests from byte streams
- **B004** — case-insensitive Headers lookup with multiple values per name
- **B005** — validate handshake request headers including Sec-WebSocket-Key and Version
- **B006** — compute Sec-WebSocket-Accept from Sec-WebSocket-Key
- **B007** — raise typed errors for malformed headers and upgrade requests
- **B008** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B009** — the submitted package does not import forbidden upstream packages: websockets
<!-- featureliftbench:behavior-clauses:end -->
