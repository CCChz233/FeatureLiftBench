# coverage__source_selection_core__001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `7/16`

## Required API

- `featurelifted.SourceSelector` (class) `(*, source: 'list[str] | None' = None, source_pkgs: 'list[str] | None' = None, run_include: 'list[str] | None' = None, run_omit: 'list[str] | None' = None, cover_pylib: 'bool' = False) -> 'None'`
- `featurelifted.SourceSelector.skip_reason` (method) `(self, filename: 'str', modulename: 'str | None' = None) -> 'str | None'`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: honor --source directory and package specifications. Required observable cases include source selector honors source tree; source selector honors omit; source selector rejects non utf8 filename.
- **B002**: The extracted feature must support this observable behavior: apply run include and omit glob patterns after source scoping. Required observable cases include source selector honors omit; source selector package name; source selector include without source; source selector omit wins over include.
- **B003**: The extracted feature must support this observable behavior: exclude stdlib, third-party, and coverage.py paths when no source is set. Required observable cases include source selector package name; source selector rejects non utf8 filename.
- **B004**: The extracted feature must support this observable behavior: return human-readable skip reasons for rejected files. Required observable cases include source selector rejects non utf8 filename.
- **B005**: The package exposes the required task API paths `featurelifted.SourceSelector`, `featurelifted.SourceSelector.skip_reason` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_source_selector_honors_source_tree`

- mapping: `B001`
- API: `featurelifted.SourceSelector`
- risk: `filesystem_resource`
- A001 `assert` L19: `selector.skip_reason(str(inside)) is None`
- A002 `assert` L20: `selector.skip_reason(str(outside)) is not None`
- A003 `assert` L21: `'falls outside' in selector.skip_reason(str(outside))`

### `public_tests/test_public_api.py::test_source_selector_honors_omit`

- mapping: `B001, B002`
- API: `featurelifted.SourceSelector`
- risk: `filesystem_resource`
- A001 `assert` L34: `reason is not None`
- A002 `assert` L35: `'omit' in reason`

### `hidden_tests/test_hidden_behavior.py::test_source_selector_package_name`

- mapping: `B002, B003`
- API: `featurelifted.SourceSelector`
- risk: `filesystem_resource`
- A001 `assert` L17: `selector.skip_reason(str(module), modulename='mypkg.mod') is None`
- A002 `assert` L18: `selector.skip_reason(str(module), modulename='other.mod') is not None`

### `hidden_tests/test_hidden_behavior.py::test_source_selector_include_without_source`

- mapping: `B002`
- API: `featurelifted.SourceSelector`
- risk: `filesystem_resource`
- A001 `assert` L31: `selector.skip_reason(str(included)) is None`
- A002 `assert` L33: `reason is not None`
- A003 `assert` L34: `'include' in reason`

### `hidden_tests/test_hidden_behavior.py::test_source_selector_rejects_non_utf8_filename`

- mapping: `B001, B003, B004`
- API: `featurelifted.SourceSelector`
- risk: `filesystem_resource`
- A001 `assert` L41: `reason is not None`
- A002 `assert` L42: `'non-encodable' in reason`

### `hidden_tests/test_hidden_behavior.py::test_source_selector_omit_wins_over_include`

- mapping: `B002`
- API: `featurelifted.SourceSelector`
- risk: `filesystem_resource`
- A001 `assert` L58: `selector.skip_reason(str(kept)) is None`
- A002 `assert` L59: `selector.skip_reason(str(omitted)) is not None`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.SourceSelector`
- risk: `none`
- A001 `assert` L9: `isinstance(SourceSelector, type)`
- A002 `assert` L10: `hasattr(SourceSelector, 'skip_reason')`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `coverage`
- source entrypoints: `coverage.inorout.InOrOut.check_include_omit_etc, coverage.inorout.InOrOut.__init__`
- oracle source files: `none`
- runtime dependencies: `none`
- oracle notes: InOrOut source/include/omit selection closure with matchers, config defaults, and disposition helpers.
