# typeguard__check_type_pipeline_core__001

- release: `external50`
- lift: `Composite`
- coupling: `data_model_coupling`
- strict validation: `PASS`
- tests/assertions: `9/13`

## Required API

- `featurelifted.check_type` (function) `(value, expected_type, *, collection_check_strategy=...)`
- `featurelifted.TypeCheckError` (class)
- `featurelifted.CollectionCheckStrategy` (class)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: check_type for nested list/dict. Required observable cases include nested collections.
- **B002**: The extracted feature must support this observable behavior: Optional/Union handling. Required observable cases include optional union.
- **B003**: The extracted feature must support this observable behavior: TypeCheckError on mismatch and CollectionCheckStrategy differences. Required observable cases include type check error; first item strategy can miss.
- **B004**: dict[str, list[int]] nesting is checked.
- **B005**: The package exposes check_type/TypeCheckError/CollectionCheckStrategy with the kinds listed in this contract.
- **B006**: the submitted package does not import forbidden upstream packages: typeguard.

## Tests

### `public_tests/test_public_api.py::test_nested_collections`

- mapping: `B001`
- API: `featurelifted.check_type`
- risk: `none`
- A001 `assert` L9: `check_type([1, 2], list[int]) == [1, 2]`
- A002 `assert` L10: `check_type({'a': 1}, dict[str, int]) == {'a': 1}`

### `public_tests/test_public_api.py::test_optional_union`

- mapping: `B002`
- API: `featurelifted.check_type`
- risk: `none`
- A001 `assert` L14: `check_type(None, Optional[int]) is None`
- A002 `assert` L15: `check_type(1, Union[int, str]) == 1`

### `public_tests/test_public_api.py::test_type_check_error`

- mapping: `B003`
- API: `featurelifted.CollectionCheckStrategy, featurelifted.TypeCheckError, featurelifted.check_type`
- risk: `none`
- A001 `assert` L22: `False`

### `public_tests/test_public_api.py::test_collection_strategy`

- mapping: `B004`
- API: `featurelifted.CollectionCheckStrategy, featurelifted.check_type`
- risk: `none`
- A001 `assert` L29: `check_type((1, 2, 3), tuple[int, ...], collection_check_strategy=all_items) == (1, 2, 3)`

### `hidden_tests/test_hidden_behavior.py::test_dict_nested_list`

- mapping: `B001, B004`
- API: `featurelifted.check_type`
- risk: `none`
- A001 `assert` L12: `check_type(value, dict[str, list[int]]) == value`

### `hidden_tests/test_hidden_behavior.py::test_first_item_strategy_can_miss`

- mapping: `B002`
- API: `featurelifted.CollectionCheckStrategy, featurelifted.TypeCheckError, featurelifted.check_type`
- risk: `none`
- A001 `assert` L22: `False`

### `hidden_tests/test_hidden_behavior.py::test_optional_reject`

- mapping: `B003`
- API: `featurelifted.TypeCheckError, featurelifted.check_type`
- risk: `none`
- A001 `assert` L30: `False`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L41: `not pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.CollectionCheckStrategy, featurelifted.TypeCheckError, featurelifted.check_type`
- risk: `none`
- A001 `assert` L5: `callable(check_type)`
- A002 `assert` L6: `TypeCheckError is not None`
- A003 `assert` L7: `CollectionCheckStrategy['ALL_ITEMS'] is not None`

## Dependency / Oracle Evidence

- allowed dependencies: `typing-extensions`
- forbidden imports: `typeguard`
- source entrypoints: `none`
- oracle source files: `src/typeguard/_checkers.py, src/typeguard/__init__.py`
- runtime dependencies: `typing-extensions`
- oracle notes: Composite check_type nested collection/Union/Optional + CollectionCheckStrategy.
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
