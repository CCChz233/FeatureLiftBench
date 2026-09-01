# FeatureLift Task: python json logger formatter

Extract a task-scoped subset of `python-json-logger` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    JsonFormatter,
)
```

## Required API Details

- `JsonFormatter(fmt: str | None = None, *, rename_fields: dict[str, str] | None = None, static_fields: dict[str, object] | None = None, **kwargs)` class constructor
- `JsonFormatter.format(record: logging.LogRecord) -> str`

## Required Behavior

- Given a logging.LogRecord and a format string naming `message` and `levelname`, JsonFormatter.format returns JSON text whose decoded object contains the rendered message and level name.
- Formatter configuration controls output fields: names selected by `fmt` are emitted, `rename_fields` moves a record field to the requested key and removes its old key, and `static_fields` adds the configured constant values.
- When `fmt` is `%(message)s %(name)s`, formatting a record named `worker` with message `boom` yields decoded JSON containing `{"message": "boom", "name": "worker"}`.
- Each call to JsonFormatter.format returns text that `json.loads` accepts as one JSON object for that record.
- The package exposes JsonFormatter with the kinds listed in this contract.
- Scanning every Python file in the submitted package finds no `import pythonjsonlogger` or `from pythonjsonlogger ...` statement.

## Constraints

- Forbidden imports: `pythonjsonlogger`.
- Do not implement SocketHandler networking.
- Do not implement original pythonjsonlogger import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — Given a logging.LogRecord and a format string naming `message` and `levelname`, JsonFormatter.format returns JSON text whose decoded object contains the rendered message and level name.
- **B002** — Formatter configuration controls output fields: names selected by `fmt` are emitted, `rename_fields` moves a record field to the requested key and removes its old key, and `static_fields` adds the configured constant values.
- **B003** — When `fmt` is `%(message)s %(name)s`, formatting a record named `worker` with message `boom` yields decoded JSON containing `{"message": "boom", "name": "worker"}`.
- **B004** — Each call to JsonFormatter.format returns text that `json.loads` accepts as one JSON object for that record.
- **B005** — The package exposes JsonFormatter with the kinds listed in this contract.
- **B006** — Scanning every Python file in the submitted package finds no `import pythonjsonlogger` or `from pythonjsonlogger ...` statement.
<!-- featureliftbench:behavior-clauses:end -->
