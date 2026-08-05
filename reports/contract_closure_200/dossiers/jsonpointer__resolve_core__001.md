# jsonpointer__resolve_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `15/35`

## Required API

- `featurelifted.EndOfList` (class) `(list_) -> None`
- `featurelifted.JsonPointer` (class) `(pointer)`
- `featurelifted.JsonPointer.from_parts` (method) `(parts)`
- `featurelifted.JsonPointer.get_parts` (method) `(self)`
- `featurelifted.JsonPointer.path` (attribute)
- `featurelifted.JsonPointerException` (exception)
- `featurelifted.resolve_pointer` (function) `(doc, pointer, default=<object object>)`
- `featurelifted.set_pointer` (function) `(doc, pointer, value, inplace=True)`
- `featurelifted.escape` (function) `(s: str) -> str`
- `featurelifted.unescape` (function) `(s: str) -> str`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: resolve pointers against nested dict/list documents. Required observable cases include resolve root empty pointer; resolve nested dict path; resolve array index; set pointer inplace; json pointer path round trip; end of list marker; pointer join operator.
- **B002**: The extracted feature must support this observable behavior: set values including array append via '-' token. Required observable cases include resolve array index; set pointer inplace; array index rejects leading zero; set append via dash; set out of place deepcopy.
- **B003**: The extracted feature must support this observable behavior: escape and unescape ~ and / in token names. Required observable cases include escape round trip paths.
- **B004**: The extracted feature must support this observable behavior: default values for missing paths and invalid escapes. Required observable cases include json pointer path round trip; escape round trip paths; invalid escape raises; resolve missing with default.
- **B005**: The package exposes the required task API paths `featurelifted.EndOfList`, `featurelifted.JsonPointer`, `featurelifted.JsonPointer.from_parts`, `featurelifted.JsonPointer.get_parts`, `featurelifted.JsonPointer.path`, `featurelifted.JsonPointerException`, `featurelifted.resolve_pointer`, `featurelifted.set_pointer`, `featurelifted.escape`, `featurelifted.unescape` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_resolve_root_empty_pointer`

- mapping: `B001`
- API: `featurelifted.resolve_pointer`
- risk: `none`
- A001 `assert` L15: `resolve_pointer(DOC, '') is DOC`

### `public_tests/test_public_api.py::test_resolve_nested_dict_path`

- mapping: `B001`
- API: `featurelifted.resolve_pointer`
- risk: `filesystem_resource`
- A001 `assert` L19: `resolve_pointer(DOC, '/foo/another prop/baz') == 'A string'`

### `public_tests/test_public_api.py::test_resolve_array_index`

- mapping: `B001, B002`
- API: `featurelifted.resolve_pointer`
- risk: `none`
- A001 `assert` L23: `resolve_pointer(DOC, '/foo/anArray/0/prop') == 44`

### `public_tests/test_public_api.py::test_set_pointer_inplace`

- mapping: `B001, B002`
- API: `featurelifted.resolve_pointer, featurelifted.set_pointer`
- risk: `none`
- A001 `assert` L29: `resolve_pointer(doc, '/foo/items/1') == 99`

### `public_tests/test_public_api.py::test_json_pointer_path_round_trip`

- mapping: `B001, B004`
- API: `featurelifted.JsonPointer`
- risk: `none`
- A001 `assert` L34: `ptr.path == '/foo/0'`
- A002 `assert` L35: `ptr.get_parts() == ['foo', '0']`

### `hidden_tests/test_hidden_behavior.py::test_escape_round_trip_paths`

- mapping: `B003, B004`
- API: `featurelifted.JsonPointer, featurelifted.JsonPointer.from_parts, featurelifted.escape, featurelifted.unescape`
- risk: `none`
- A001 `assert` L41: `escape('a/b~c') == 'a~1b~0c'`
- A002 `assert` L42: `unescape('a~1b~0c') == 'a/b~c'`
- A003 `assert` L38: `ptr.path == path`
- A004 `assert` L40: `rebuilt == ptr`

### `hidden_tests/test_hidden_behavior.py::test_invalid_escape_raises`

- mapping: `B004`
- API: `featurelifted.JsonPointer, featurelifted.JsonPointerException`
- risk: `exception_semantics`
- A001 `raises` L46: `pytest.raises(JsonPointerException)`
- A002 `raises` L48: `pytest.raises(JsonPointerException)`

### `hidden_tests/test_hidden_behavior.py::test_end_of_list_marker`

- mapping: `B001`
- API: `featurelifted.EndOfList, featurelifted.JsonPointerException, featurelifted.resolve_pointer`
- risk: `exception_semantics`
- A001 `assert` L55: `isinstance(result, EndOfList)`
- A002 `raises` L56: `pytest.raises(JsonPointerException)`

### `hidden_tests/test_hidden_behavior.py::test_array_index_rejects_leading_zero`

- mapping: `B002`
- API: `featurelifted.JsonPointerException, featurelifted.resolve_pointer`
- risk: `exception_semantics`
- A001 `raises` L62: `pytest.raises(JsonPointerException)`

### `hidden_tests/test_hidden_behavior.py::test_set_append_via_dash`

- mapping: `B002`
- API: `featurelifted.resolve_pointer, featurelifted.set_pointer`
- risk: `none`
- A001 `assert` L69: `resolve_pointer(doc, '/foo/2') == 'cod'`

### `hidden_tests/test_hidden_behavior.py::test_set_out_of_place_deepcopy`

- mapping: `B002`
- API: `featurelifted.resolve_pointer, featurelifted.set_pointer`
- risk: `none`
- A001 `assert` L76: `resolve_pointer(newdoc, '/foo/1') == 'cod'`
- A002 `assert` L77: `resolve_pointer(doc, '/foo/1') == 'baz'`
- A003 `assert` L78: `doc == original`

### `hidden_tests/test_hidden_behavior.py::test_resolve_missing_with_default`

- mapping: `B004`
- API: `featurelifted.resolve_pointer`
- risk: `none`
- A001 `assert` L82: `resolve_pointer(SPEC_DOC, '/missing', None) is None`
- A002 `assert` L83: `resolve_pointer(SPEC_DOC, '/a%20b', None) is None`

### `hidden_tests/test_hidden_behavior.py::test_pointer_join_operator`

- mapping: `B001`
- API: `featurelifted.JsonPointer`
- risk: `none`
- A001 `assert` L90: `joined.path == '/a/b/c/a/b'`
- A002 `assert` L91: `ptr2 in ptr1`
- A003 `assert` L92: `JsonPointer('/b/c') not in ptr1`

### `hidden_tests/test_hidden_behavior.py::test_no_jsonpointer_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L102: `not import_pattern.search(text)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.EndOfList, featurelifted.JsonPointer, featurelifted.JsonPointerException, featurelifted.escape, featurelifted.resolve_pointer, featurelifted.set_pointer, featurelifted.unescape`
- risk: `none`
- A001 `assert` L15: `isinstance(EndOfList, type)`
- A002 `assert` L16: `isinstance(JsonPointer, type)`
- A003 `assert` L17: `hasattr(JsonPointer, 'from_parts')`
- A004 `assert` L18: `hasattr(JsonPointer, 'get_parts')`
- A005 `assert` L19: `JsonPointer is not None`
- A006 `assert` L20: `issubclass(JsonPointerException, BaseException)`
- A007 `assert` L21: `callable(resolve_pointer)`
- A008 `assert` L22: `callable(set_pointer)`
- A009 `assert` L23: `callable(escape)`
- A010 `assert` L24: `callable(unescape)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `jsonpointer`
- source entrypoints: `jsonpointer.JsonPointer, jsonpointer.resolve_pointer, jsonpointer.set_pointer, jsonpointer.escape, jsonpointer.unescape`
- oracle source files: `jsonpointer.py`
- runtime dependencies: `none`
- oracle notes: Oracle splits jsonpointer.py into _escape, _errors, and _pointer modules.
