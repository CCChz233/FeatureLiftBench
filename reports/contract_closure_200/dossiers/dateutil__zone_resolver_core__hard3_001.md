# dateutil__zone_resolver_core__hard3_001

- release: `frozen_python150`
- lift: `Composite`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `5/13`

## Required API

- `featurelifted.ZoneResolver` (class) `() -> 'None'`
- `featurelifted.ZoneResolver.load_zone` (method) `(self, name: 'str', tzdata: 'dict[str, bytes]') -> 'TZZone'`
- `featurelifted.ZoneResolver.get` (method) `(self, name: 'str') -> 'TZZone'`
- `featurelifted.ZoneResolver.register_alias` (method) `(self, alias: 'str', canonical: 'str') -> 'None'`
- `featurelifted.parse_tzfile` (function) `(data: 'bytes') -> 'dict[str, int]'`
- `featurelifted.UnknownZoneError` (exception)
- `featurelifted.InvalidTZFileError` (exception)

## Public Behaviors

- **B001**: `parse_tzfile` validates tzfile headers and extracts metadata.
- **B002**: Aliases resolve to canonical zone names with cycle detection.
- **B003**: When a zone alias is resolved, ZoneResolver follows aliases to the canonical zone and raises UnknownZoneError for missing names or alias cycles.
- **B004**: The package exposes the required task API paths `featurelifted.ZoneResolver`, `featurelifted.ZoneResolver.load_zone`, `featurelifted.ZoneResolver.get`, `featurelifted.ZoneResolver.register_alias`, `featurelifted.parse_tzfile`, `featurelifted.UnknownZoneError`, `featurelifted.InvalidTZFileError` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_load_zone_caches`

- mapping: `B002`
- API: `featurelifted.ZoneResolver`
- risk: `state_mutation`
- A001 `assert` L10: `zone.name == 'UTC'`
- A002 `assert` L11: `resolver.get('UTC') is zone`

### `hidden_tests/test_hidden_contract.py::test_alias_resolution`

- mapping: `B003`
- API: `featurelifted.ZoneResolver`
- risk: `none`
- A001 `assert` L13: `zone.name == 'America/New_York'`
- A002 `assert` L14: `resolver.get('US/Eastern') is zone`

### `hidden_tests/test_hidden_contract.py::test_circular_alias_raises`

- mapping: `B003`
- API: `featurelifted.UnknownZoneError, featurelifted.ZoneResolver`
- risk: `exception_semantics`
- A001 `raises` L21: `pytest.raises(UnknownZoneError)`

### `hidden_tests/test_hidden_contract.py::test_invalid_tzfile_header`

- mapping: `B001, B002`
- API: `featurelifted.InvalidTZFileError`
- risk: `exception_semantics`
- A001 `raises` L26: `pytest.raises(InvalidTZFileError)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B004`
- API: `featurelifted.InvalidTZFileError, featurelifted.UnknownZoneError, featurelifted.ZoneResolver, featurelifted.parse_tzfile`
- risk: `none`
- A001 `assert` L12: `isinstance(ZoneResolver, type)`
- A002 `assert` L13: `hasattr(ZoneResolver, 'load_zone')`
- A003 `assert` L14: `hasattr(ZoneResolver, 'get')`
- A004 `assert` L15: `hasattr(ZoneResolver, 'register_alias')`
- A005 `assert` L16: `callable(parse_tzfile)`
- A006 `assert` L17: `issubclass(UnknownZoneError, BaseException)`
- A007 `assert` L18: `issubclass(InvalidTZFileError, BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `dateutil`
- source entrypoints: `dateutil.zoneinfo.ZoneResolver`
- oracle source files: `repo/src/dateutil/zoneinfo/__init__.py, repo/src/dateutil/tz/tz.py`
- runtime dependencies: `none`
- oracle notes: Zone resolver subset without full tz conversion.
