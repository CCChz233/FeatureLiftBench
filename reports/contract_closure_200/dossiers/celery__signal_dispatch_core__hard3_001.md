# celery__signal_dispatch_core__hard3_001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `6/8`

## Required API

- `featurelifted.Signal` (class) `(name: 'str' = 'signal') -> 'None'`
- `featurelifted.Signal.connect` (method) `(self, receiver: 'Callable[..., Any]', sender: 'Any' = None, dispatch_uid: 'Any' = None, weak: 'bool' = True) -> 'Callable[..., Any]'`
- `featurelifted.Signal.send` (method) `(self, sender: 'Any' = None, **kwargs) -> 'list[tuple[Any, Any]]'`

## Public Behaviors

- **B001**: When connect registers a receiver, dispatch invokes it once unless dispatch_uid intentionally deduplicates the registration.
- **B002**: When a receiver is registered for a sender, dispatch invokes it only for matching sender values while sender-agnostic receivers still run.
- **B003**: When a signal is dispatched, the returned list preserves receiver order and pairs each receiver with its response or captured exception.
- **B004**: When a weakly referenced receiver is garbage-collected, later dispatches omit and clean up that dead receiver.
- **B005**: The package exposes the required task API paths `featurelifted.Signal`, `featurelifted.Signal.connect`, `featurelifted.Signal.send` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_signal_send_invokes_receiver`

- mapping: `B001, B004`
- API: `featurelifted.Signal`
- risk: `none`
- A001 `assert` L10: `seen == [1]`

### `hidden_tests/test_hidden_contract.py::test_sender_filtering`

- mapping: `B002`
- API: `featurelifted.Signal`
- risk: `none`
- A001 `assert` L19: `hits == ['all', 'all', 'one']`

### `hidden_tests/test_hidden_contract.py::test_dispatch_uid_allows_duplicate_callables`

- mapping: `B001, B003`
- API: `featurelifted.Signal`
- risk: `none`
- A001 `assert` L28: `seen == [1, 2]`

### `hidden_tests/test_hidden_contract.py::test_exception_capture_in_send`

- mapping: `B003`
- API: `featurelifted.Signal`
- risk: `none`
- A001 `assert` L39: `isinstance(responses[0][1], RuntimeError)`

### `hidden_tests/test_hidden_contract.py::test_weak_receiver_cleanup`

- mapping: `B004`
- API: `featurelifted.Signal`
- risk: `none`
- A001 `assert` L53: `sig.send() == []`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.Signal`
- risk: `none`
- A001 `assert` L9: `isinstance(Signal, type)`
- A002 `assert` L10: `hasattr(Signal, 'connect')`
- A003 `assert` L11: `hasattr(Signal, 'send')`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `celery`
- source entrypoints: `celery.utils.dispatch.signal.Signal`
- oracle source files: `repo/celery/utils/dispatch/signal.py`
- runtime dependencies: `none`
- oracle notes: Signal dispatch subset without broker runtime.
