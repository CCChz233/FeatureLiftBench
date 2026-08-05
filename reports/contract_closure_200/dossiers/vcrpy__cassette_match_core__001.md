# vcrpy__cassette_match_core__001

- release: `external50`
- lift: `Composite`
- coupling: `framework_coupling`
- strict validation: `PASS`
- tests/assertions: `6/10`

## Required API

- `featurelifted.use_cassette` (function)
- `featurelifted.VCR` (class)
- `featurelifted.VCR.use_cassette` (method)
- `featurelifted.VCR.record_mode` (attribute)
- `featurelifted.VCR.use_cassette` (method)
- `featurelifted.Cassette` (class)
- `featurelifted.Cassette.play_count` (attribute)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: replay cassette via use_cassette with urllib. Required observable cases include use cassette replay.
- **B002**: The extracted feature must support this observable behavior: VCR factory with record_mode and match_on. Required observable cases include vcr factory.
- **B003**: The extracted feature must support this observable behavior: match_on method/uri and play_count. Required observable cases include match on method uri; cassette path record mode none.
- **B004**: record_mode='none' never records new interactions in tests.
- **B005**: The package exposes use_cassette and VCR with the kinds listed in this contract.
- **B006**: the submitted package does not import forbidden upstream packages: vcr.

## Tests

### `public_tests/test_public_api.py::test_use_cassette_replay`

- mapping: `B001`
- API: `featurelifted.use_cassette`
- risk: `filesystem_resource`
- A001 `assert` L32: `resp.read().decode() == 'hello-vcr'`

### `public_tests/test_public_api.py::test_vcr_factory`

- mapping: `B002`
- API: `featurelifted.VCR`
- risk: `none`
- A001 `assert` L39: `v.record_mode == 'none'`

### `hidden_tests/test_hidden_behavior.py::test_match_on_method_uri`

- mapping: `B001, B003, B004`
- API: `featurelifted.VCR, featurelifted.VCR.use_cassette`
- risk: `filesystem_resource`
- A001 `assert` L32: `body == b'hello-vcr'`

### `hidden_tests/test_hidden_behavior.py::test_cassette_path_record_mode_none`

- mapping: `B002`
- API: `featurelifted.use_cassette`
- risk: `filesystem_resource`
- A001 `assert` L40: `cass.play_count >= 1`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L54: `not pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.VCR, featurelifted.VCR.use_cassette`
- risk: `none`
- A001 `assert` L5: `hasattr(featurelifted, 'Cassette')`
- A002 `assert` L6: `hasattr(featurelifted, 'VCR')`
- A003 `assert` L7: `hasattr(featurelifted, 'use_cassette')`
- A004 `assert` L8: `callable(featurelifted.VCR.use_cassette)`
- A005 `assert` L9: `callable(featurelifted.VCR.use_cassette)`

## Dependency / Oracle Evidence

- allowed dependencies: `pyyaml, urllib3, wrapt`
- forbidden imports: `vcr`
- source entrypoints: `none`
- oracle source files: `vcr/config.py, vcr/cassette.py, vcr/matchers.py`
- runtime dependencies: `pyyaml, urllib3, wrapt`
- oracle notes: Composite use_cassette replay with pre-recorded yaml; record_mode=none.
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
