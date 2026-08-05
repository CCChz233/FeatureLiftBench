# referencing__json_schema_refs_core__001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `FAIL`
- tests/assertions: `6/16`

## Required API

- `featurelifted.Registry` (class) `(resources=HashTrieMap({}), anchors: 'HashTrieMap[tuple[URI, str], AnchorType[D]]' = HashTrieMap({}), uncrawled: 'HashTrieSet[URI]' = HashTrieSet({}), retrieve: 'Retrieve[D]' = <function _fail_to_retrieve>) -> None`
- `featurelifted.Registry.resolver` (method) `(self, base_uri: 'URI' = '') -> 'Resolver[D]'`
- `featurelifted.Resource` (class) `(contents: 'D', specification: 'Specification[D]') -> None`
- `featurelifted.Resource.from_contents` (method) `(contents: 'D', default_specification: 'Specification[D]' = None) -> 'Resource[D]'`
- `featurelifted.exceptions` (module)
- `featurelifted.exceptions.NoSuchAnchor` (exception)
- `featurelifted.exceptions.Unresolvable` (exception)
- `featurelifted.jsonschema` (module)
- `featurelifted.jsonschema.DRAFT202012` (constant)
- `featurelifted.jsonschema.UnknownDialect` (exception)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: Registry resource registration and base URI resolution. Required observable cases include external ref resolution; unresolvable external ref.
- **B002**: The extracted feature must support this observable behavior: $ref pointer and external URI chaining. Required observable cases include external ref resolution; fragment ref into defs; unresolvable external ref.
- **B003**: The extracted feature must support this observable behavior: $anchor and JSON Schema dialect specifications. Required observable cases include anchor lookup; unknown dialect and missing anchor.
- **B004**: The extracted feature must support this observable behavior: typed unresolvable and unknown dialect errors. Required observable cases include unknown dialect and missing anchor.
- **B005**: The package exposes the required task API paths `featurelifted.Registry`, `featurelifted.Registry.resolver`, `featurelifted.Resource`, `featurelifted.Resource.from_contents`, `featurelifted.exceptions`, `featurelifted.exceptions.NoSuchAnchor`, `featurelifted.exceptions.Unresolvable`, `featurelifted.jsonschema`, `featurelifted.jsonschema.DRAFT202012`, `featurelifted.jsonschema.UnknownDialect` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_external_ref_resolution`

- mapping: `B001, B002`
- API: `featurelifted.Registry, featurelifted.Registry.with_resources, featurelifted.jsonschema`
- risk: `none`
- A001 `assert` L18: `resolved.contents == {'type': 'integer'}`

### `hidden_tests/test_hidden_behavior.py::test_fragment_ref_into_defs`

- mapping: `B002`
- API: `featurelifted.Registry, featurelifted.Registry.with_resource, featurelifted.exceptions, featurelifted.jsonschema`
- risk: `none`
- A001 `assert` L20: `resolved.contents == {'type': 'string'}`

### `hidden_tests/test_hidden_behavior.py::test_anchor_lookup`

- mapping: `B003`
- API: `featurelifted.Registry, featurelifted.Registry.with_resource, featurelifted.exceptions, featurelifted.jsonschema`
- risk: `none`
- A001 `assert` L27: `resolved.contents['type'] == 'number'`

### `hidden_tests/test_hidden_behavior.py::test_unknown_dialect_and_missing_anchor`

- mapping: `B003, B004`
- API: `featurelifted.Registry, featurelifted.Registry.with_resource, featurelifted.Resource, featurelifted.Resource.from_contents, featurelifted.exceptions, featurelifted.jsonschema`
- risk: `exception_semantics`
- A001 `raises` L33: `pytest.raises(UnknownDialect)`
- A002 `raises` L38: `pytest.raises(NoSuchAnchor)`

### `hidden_tests/test_hidden_behavior.py::test_unresolvable_external_ref`

- mapping: `B001, B002`
- API: `featurelifted.Registry, featurelifted.Registry.with_resource, featurelifted.exceptions, featurelifted.jsonschema`
- risk: `exception_semantics`
- A001 `raises` L46: `pytest.raises(Unresolvable)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.Registry, featurelifted.Resource, featurelifted.exceptions, featurelifted.jsonschema`
- risk: `none`
- A001 `assert` L12: `isinstance(Registry, type)`
- A002 `assert` L13: `hasattr(Registry, 'resolver')`
- A003 `assert` L14: `isinstance(Resource, type)`
- A004 `assert` L15: `hasattr(Resource, 'from_contents')`
- A005 `assert` L16: `exceptions is not None`
- A006 `assert` L17: `issubclass(getattr(exceptions, 'NoSuchAnchor'), BaseException)`
- A007 `assert` L18: `issubclass(getattr(exceptions, 'Unresolvable'), BaseException)`
- A008 `assert` L19: `jsonschema is not None`
- A009 `assert` L20: `getattr(jsonschema, 'DRAFT202012') is not None`
- A010 `assert` L21: `issubclass(getattr(jsonschema, 'UnknownDialect'), BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `attrs, rpds`
- forbidden imports: `referencing`
- source entrypoints: `referencing.Registry, referencing.Registry.resolver, referencing.jsonschema.DRAFT202012, referencing.jsonschema.lookup_recursive_ref`
- oracle source files: `none`
- runtime dependencies: `none`
- oracle notes: Oracle is referencing runtime modules; repo includes referencing/tests for copy-all penalty.

## Machine Issues

- public_tests/test_public_api.py uses undeclared API reference featurelifted.Registry.with_resources
- hidden_tests/test_hidden_behavior.py uses undeclared API reference featurelifted.Registry.with_resource
