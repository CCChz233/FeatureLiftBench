# FeatureLift Task: MessagePack pack/unpack core

Extract msgpack packb/unpackb, Packer/Unpacker streaming, ExtType/Timestamp extension types, and exception surface using the pure-Python fallback implementation without importing msgpack or compiled Cython extensions.

## Target API

- Import: `import featurelifted; from featurelifted import packb, unpackb, pack, unpack, dumps, loads, Packer, Unpacker, ExtType, Timestamp, ExtraData, FormatError`
- Callable: `featurelifted.packb`
- Signature: `packb(o, **kwargs) -> bytes`

## Excluded Behavior

- Cython _cmsgpack accelerated path and .pyx/.h build artifacts
- benchmark suite, docker images, docs, and upstream test harness
- original msgpack import at runtime

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `msgpack`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — packb/unpackb roundtrip for nil, bool, int, float, str, bytes, list, tuple, dict
- **B002** — Packer options: use_bin_type, use_single_float, default hook, datetime timestamps
- **B003** — Unpacker streaming feed/unpack, strict_map_key, raw/bin decoding, ext_hook
- **B004** — Timestamp extension type pack/unpack (32/64/96-bit encodings)
- **B005** — ExtType custom extension payloads
- **B006** — ExtraData, FormatError, StackError, OutOfData exception semantics
- **B007** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B008** — the submitted package does not import forbidden upstream packages: msgpack
<!-- featureliftbench:behavior-clauses:end -->
