# responses__request_matcher_core__hard3_001

- release: `frozen_python150`
- lift: `Composite`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `4/16`

## Required API

- `featurelifted.MockResponseRegistry` (class) `() -> 'None'`
- `featurelifted.MockResponseRegistry._responses` (attribute)
- `featurelifted.MockResponseRegistry.add` (method) `(self, response: 'MockResponse') -> 'MockResponse'`
- `featurelifted.MockResponseRegistry.call_history` (attribute)
- `featurelifted.MockResponseRegistry.find` (method) `(self, request: 'PreparedRequest') -> 'tuple[MockResponse | None, list[str]]'`
- `featurelifted.MockResponseRegistry.reset` (method) `(self) -> 'None'`
- `featurelifted.MockResponse` (class) `(url: 'str', method: 'str' = 'GET', status: 'int' = 200, body: 'Any' = '', match_querystring: 'bool' = False, headers: 'dict[str, str]' = <factory>, matchers: 'list[Callable[[PreparedRequest], tuple[bool, str]]]' = <factory>, call_count: 'int' = 0, once: 'bool' = False) -> None`
- `featurelifted.query_string_matcher` (function) `(params: 'dict[str, str]') -> 'Callable[[PreparedRequest], tuple[bool, str]]'`
- `featurelifted.header_matcher` (function) `(headers: 'dict[str, str]') -> 'Callable[[PreparedRequest], tuple[bool, str]]'`

## Public Behaviors

- **B001**: Register `MockResponse` objects and find the first matching `PreparedRequest`.
- **B002**: Support `query_string_matcher` and `header_matcher` helper matchers.
- **B003**: `once=True` responses are removed after the first successful match.
- **B004**: `reset()` clears registered responses and call history.
- **B005**: The package exposes the required task API paths `featurelifted.MockResponseRegistry`, `featurelifted.MockResponseRegistry._responses`, `featurelifted.MockResponseRegistry.add`, `featurelifted.MockResponseRegistry.call_history`, `featurelifted.MockResponseRegistry.find`, `featurelifted.MockResponseRegistry.reset`, `featurelifted.MockResponse`, `featurelifted.query_string_matcher`, `featurelifted.header_matcher` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_registry_finds_matching_response`

- mapping: `B003`
- API: `featurelifted.MockResponse, featurelifted.MockResponseRegistry`
- risk: `none`
- A001 `assert` L13: `response is not None`
- A002 `assert` L14: `response.body == 'ok'`

### `hidden_tests/test_hidden_contract.py::test_query_and_header_matchers_and_once_behavior`

- mapping: `B002, B003`
- API: `featurelifted.MockResponse, featurelifted.MockResponseRegistry, featurelifted.header_matcher, featurelifted.query_string_matcher`
- risk: `none`
- A001 `assert` L21: `first is not None`
- A002 `assert` L22: `second is None`
- A003 `assert` L23: `len(registry.call_history) == 2`

### `hidden_tests/test_hidden_contract.py::test_reset_clears_registry_and_history`

- mapping: `B001, B003, B004`
- API: `featurelifted.MockResponse, featurelifted.MockResponseRegistry`
- risk: `state_mutation`
- A001 `assert` L30: `registry._responses == []`
- A002 `assert` L31: `registry.call_history == []`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.MockResponse, featurelifted.MockResponseRegistry, featurelifted.header_matcher, featurelifted.query_string_matcher`
- risk: `none`
- A001 `assert` L12: `isinstance(MockResponseRegistry, type)`
- A002 `assert` L13: `MockResponseRegistry is not None`
- A003 `assert` L14: `hasattr(MockResponseRegistry, 'add')`
- A004 `assert` L15: `MockResponseRegistry is not None`
- A005 `assert` L16: `hasattr(MockResponseRegistry, 'find')`
- A006 `assert` L17: `hasattr(MockResponseRegistry, 'reset')`
- A007 `assert` L18: `isinstance(MockResponse, type)`
- A008 `assert` L19: `callable(query_string_matcher)`
- A009 `assert` L20: `callable(header_matcher)`

## Dependency / Oracle Evidence

- allowed dependencies: `certifi, charset-normalizer, idna, requests, urllib3`
- forbidden imports: `responses`
- source entrypoints: `responses.matchers, responses.registries.FirstMatchRegistry`
- oracle source files: `repo/responses/matchers.py, repo/responses/registries.py, repo/responses/__init__.py`
- runtime dependencies: `requests`
- oracle notes: Offline matcher/registry subset using requests.PreparedRequest.
