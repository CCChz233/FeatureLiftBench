# blinker__signal_registry_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `5/12`

## Required API

- `featurelifted.ANY` (constant)
- `featurelifted.Namespace` (class) `(*args, **kwargs)`
- `featurelifted.Signal` (class) `(doc=None)`
- `featurelifted.Signal.connect` (method) `(self, receiver, sender=<object object>, weak=True)`
- `featurelifted.Signal.send` (method) `(self, sender=None, **kwargs)`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: connect, disconnect, connected_to, and receiver iteration. Required observable cases include sender filtering and responses; namespace identity; weak receiver cleanup; connected to scope and disconnect.
- **B002**: The extracted feature must support this observable behavior: ANY and sender-specific dispatch. Required observable cases include sender filtering and responses; namespace identity; weak receiver cleanup; connected to scope and disconnect.
- **B003**: The extracted feature must support this observable behavior: weak receiver cleanup after garbage collection. Required observable cases include sender filtering and responses; namespace identity; weak receiver cleanup; connected to scope and disconnect.
- **B004**: The extracted feature must support this observable behavior: Namespace returns one stable Signal per name. Required observable cases include sender filtering and responses; namespace identity; weak receiver cleanup; connected to scope and disconnect.
- **B005**: The package exposes the required task API paths `featurelifted.ANY`, `featurelifted.Namespace`, `featurelifted.Signal`, `featurelifted.Signal.connect`, `featurelifted.Signal.send` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_sender_filtering_and_responses`

- mapping: `B001, B002, B003, B004`
- API: `featurelifted.Signal`
- risk: `none`
- A001 `assert` L9: `signal.send('chosen', value=3) == [(any_receiver, 3), (only_receiver, 'only')]`
- A002 `assert` L10: `signal.send('other', value=4) == [(any_receiver, 4)]`

### `public_tests/test_public_contract.py::test_namespace_identity`

- mapping: `B001, B002, B003, B004`
- API: `featurelifted.Namespace`
- risk: `none`
- A001 `assert` L14: `namespace.signal('ready') is namespace.signal('ready')`
- A002 `assert` L15: `namespace.signal('ready') is not namespace.signal('done')`

### `hidden_tests/test_hidden_contract.py::test_weak_receiver_cleanup`

- mapping: `B001, B002, B003, B004`
- API: `featurelifted.Signal`
- risk: `none`
- A001 `assert` L10: `len(signal.send(None)) == 1`
- A002 `assert` L12: `signal.send(None) == []`

### `hidden_tests/test_hidden_contract.py::test_connected_to_scope_and_disconnect`

- mapping: `B001, B002, B003, B004`
- API: `featurelifted.Signal`
- risk: `none`
- A001 `assert` L20: `calls == ['x']`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.ANY, featurelifted.Namespace, featurelifted.Signal`
- risk: `none`
- A001 `assert` L11: `ANY is not None`
- A002 `assert` L12: `isinstance(Namespace, type)`
- A003 `assert` L13: `isinstance(Signal, type)`
- A004 `assert` L14: `hasattr(Signal, 'connect')`
- A005 `assert` L15: `hasattr(Signal, 'send')`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `blinker`
- source entrypoints: `blinker.base.Signal, blinker.base.Namespace, blinker.base.ANY`
- oracle source files: `blinker.base.Signal, blinker.base.Namespace, blinker.base.ANY`
- runtime dependencies: `none`
- oracle notes: Entrypoints are maintainer-private provenance and are never Agent-visible in Main.
- behavior contract lacks a completed review_status
