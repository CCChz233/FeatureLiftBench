# FeatureLift Task: RESP2/RESP3 wire parser

Extract redis-py synchronous RESP2/RESP3 parsing and command encoding without network I/O.

## Target API

- Import: `from featurelifted._parsers import _RESP2Parser, _RESP3Parser, Encoder; from featurelifted.exceptions import ResponseError`
- Callable: `featurelifted._parsers._RESP2Parser.read_response`
- Signature: `read_response(disable_decoding=False, timeout=SENTINEL)`

## Excluded Behavior

- TCP/TLS connection management
- Redis command client and cluster logic
- pub/sub push notification handlers
- hiredis C extension parser

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `redis`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — parse RESP simple, bulk, and multi-bulk replies
- **B002** — decode bulk strings with optional byte preservation
- **B003** — map Redis error prefixes to exception classes
- **B004** — encode commands to RESP bulk arrays
- **B005** — buffer incremental socket reads via SocketBuffer
- **B006** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B007** — the submitted package does not import forbidden upstream packages: redis
<!-- featureliftbench:behavior-clauses:end -->
