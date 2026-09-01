# FeatureLift Task: AMQP frame codec

Build a standalone `featurelifted` package that encodes and decodes AMQP frames like Pika `frame`/`spec`, including heartbeats and `Basic.Ack`, without connecting to a broker.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    frame,
    spec,
)
```

## Required API Details

- `frame.decode_frame(data_in, offset=0)`
- `frame.Heartbeat()` class constructor
  - `frame.Heartbeat.marshal(self)`
- `frame.Method(channel_number, method)` class constructor
  - `frame.Method.marshal(self)`
- `frame.ProtocolHeader(major=None, minor=None, revision=None)` class constructor
  - `frame.ProtocolHeader.marshal(self)`
- `spec.Basic.Ack(delivery_tag=0, multiple=False)` class constructor

## Required Behavior

- `Heartbeat().marshal()` round-trips through `decode_frame` to a `Heartbeat` instance and consumes the full payload.
- `Method(channel, Basic.Ack(delivery_tag, multiple)).marshal()` round-trips through `decode_frame` preserving channel number, delivery tag, and multiple flag.
- `ProtocolHeader().marshal()` starts with `b"AMQP"` and `decode_frame` returns a `ProtocolHeader`.
- `decode_frame(b"")` returns `(0, None)`.
- The package exposes `decode_frame`, `Heartbeat`, `Method`, `ProtocolHeader`, and `Basic.Ack`.
- The submitted package source does not import the forbidden upstream package `pika`.

## Constraints

- Forbidden imports: `pika`.
- Do not implement BlockingConnection.
- Do not implement live broker.
- Do not implement runtime import of pika.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — `Heartbeat().marshal()` round-trips through `decode_frame` to a `Heartbeat` instance and consumes the full payload.
- **B002** — `Method(channel, Basic.Ack(delivery_tag, multiple)).marshal()` round-trips through `decode_frame` preserving channel number, delivery tag, and multiple flag.
- **B003** — `ProtocolHeader().marshal()` starts with `b"AMQP"` and `decode_frame` returns a `ProtocolHeader`.
- **B004** — `decode_frame(b"")` returns `(0, None)`.
- **B005** — The package exposes `decode_frame`, `Heartbeat`, `Method`, `ProtocolHeader`, and `Basic.Ack`.
- **B006** — The submitted package source does not import the forbidden upstream package `pika`.
<!-- featureliftbench:behavior-clauses:end -->
