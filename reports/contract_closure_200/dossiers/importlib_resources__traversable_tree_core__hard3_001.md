# importlib_resources__traversable_tree_core__hard3_001

- release: `frozen_python150`
- lift: `Composite`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `8/24`

## Required API

- `featurelifted.TraversalError` (exception)
- `featurelifted.files` (function) `(anchor: 'types.ModuleType | str | MemoryTraversable') -> 'FileTraversable | MemoryTraversable'`
- `featurelifted.read_binary` (function) `(anchor: 'types.ModuleType | str | MemoryTraversable', resource: 'str') -> 'bytes'`
- `featurelifted.read_text` (function) `(anchor: 'types.ModuleType | str | MemoryTraversable', resource: 'str', encoding: 'str' = 'utf-8', errors: 'str' = 'strict') -> 'str'`
- `featurelifted.MemoryTraversable` (class) `(name: 'str', children: "dict[str, 'MemoryTraversable'] | None" = None, data: 'bytes | None' = None) -> 'None'`
- `featurelifted.MemoryTraversable.directory` (method) `(name: 'str', entries: 'dict[str, Any]') -> "'MemoryTraversable'"`
- `featurelifted.MemoryTraversable.joinpath` (method) `(self, *descendants: 'Any') -> "'MemoryTraversable'"`

## Public Behaviors

- **B001**: When files receives a module object or importable module-name string, it resolves the same package anchor.
- **B002**: For filesystem packages, files returns a Traversable rooted at the package directory with stable child names.
- **B003**: For in-memory package trees, MemoryTraversable exposes the same directory, file, open, and read operations as filesystem-backed traversables.
- **B004**: Traversable nodes report name, is_file, and is_dir and implement iterdir, open, read_bytes, and read_text consistently.
- **B005**: joinpath and the slash operator traverse child resources while preventing escape above the package root.
- **B006**: read_text honors the requested encoding and read_binary returns the resource bytes unchanged.
- **B007**: Parent traversal and missing-resource reads raise TraversalError instead of accessing paths outside the declared resource tree.
- **B008**: The package exposes the required task API paths `featurelifted.TraversalError`, `featurelifted.files`, `featurelifted.read_binary`, `featurelifted.read_text`, `featurelifted.MemoryTraversable`, `featurelifted.MemoryTraversable.directory`, `featurelifted.MemoryTraversable.joinpath` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_files_returns_traversable_for_package`

- mapping: `B004`
- API: `featurelifted.files`
- risk: `filesystem_resource`
- A001 `assert` L27: `root.is_dir()`
- A002 `assert` L28: `{'__init__.py', 'data', 'plain.txt'}.issubset({child.name for child in root.iterdir()})`
- A003 `assert` L31: `root.joinpath('plain.txt').is_file()`
- A004 `assert` L32: `root.joinpath('plain.txt').read_text() == 'hello'`

### `public_tests/test_public_contract.py::test_read_text_and_binary_from_string_anchor`

- mapping: `B001, B006`
- API: `featurelifted.read_binary, featurelifted.read_text`
- risk: `filesystem_resource`
- A001 `assert` L39: `read_text('samplepkg', 'data/config.json') == '{"enabled": true}'`
- A002 `assert` L40: `read_binary('samplepkg', 'data/blob.bin') == b'\x00\x01payload'`

### `hidden_tests/test_hidden_contract.py::test_nested_joinpath_accepts_multiple_segments`

- mapping: `B004, B005`
- API: `featurelifted.files`
- risk: `filesystem_resource`
- A001 `assert` L28: `resource.name == 'data.bin'`
- A002 `assert` L29: `resource.is_file()`
- A003 `assert` L30: `resource.read_bytes() == bytes(range(5))`

### `hidden_tests/test_hidden_contract.py::test_text_encoding_and_binary_open_are_preserved`

- mapping: `B001, B003, B004, B006`
- API: `featurelifted.files`
- risk: `filesystem_resource`
- A001 `assert` L37: `root.joinpath('nested/inner/utf16.txt').read_text(encoding='utf-16') == 'snowman'`
- A002 `assert` L39: `stream.read() == bytes(range(5))`

### `hidden_tests/test_hidden_contract.py::test_parent_traversal_is_rejected`

- mapping: `B005, B007`
- API: `featurelifted.TraversalError, featurelifted.files, featurelifted.read_text`
- risk: `exception_semantics, filesystem_resource`
- A001 `raises` L45: `pytest.raises(TraversalError)`
- A002 `raises` L47: `pytest.raises(TraversalError)`

### `hidden_tests/test_hidden_contract.py::test_memory_traversable_matches_filesystem_contract`

- mapping: `B002`
- API: `featurelifted.MemoryTraversable, featurelifted.MemoryTraversable.directory, featurelifted.files, featurelifted.read_binary, featurelifted.read_text`
- risk: `filesystem_resource`
- A001 `assert` L62: `files(tree).joinpath('docs').is_dir()`
- A002 `assert` L63: `read_text(tree, 'docs/intro.txt') == 'hello'`
- A003 `assert` L64: `read_binary(tree, 'docs/payload.bin') == b'\x10 '`

### `hidden_tests/test_hidden_contract.py::test_missing_resource_raises_traversal_error`

- mapping: `B007`
- API: `featurelifted.TraversalError, featurelifted.files`
- risk: `exception_semantics, filesystem_resource`
- A001 `raises` L70: `pytest.raises(TraversalError)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B008`
- API: `featurelifted.MemoryTraversable, featurelifted.TraversalError, featurelifted.files, featurelifted.read_binary, featurelifted.read_text`
- risk: `none`
- A001 `assert` L13: `issubclass(TraversalError, BaseException)`
- A002 `assert` L14: `callable(files)`
- A003 `assert` L15: `callable(read_binary)`
- A004 `assert` L16: `callable(read_text)`
- A005 `assert` L17: `isinstance(MemoryTraversable, type)`
- A006 `assert` L18: `hasattr(MemoryTraversable, 'directory')`
- A007 `assert` L19: `hasattr(MemoryTraversable, 'joinpath')`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `importlib_resources`
- source entrypoints: `importlib_resources.files, importlib_resources.read_text, importlib_resources.read_binary, importlib_resources.abc.Traversable`
- oracle source files: `repo/importlib_resources/__init__.py, repo/importlib_resources/_common.py, repo/importlib_resources/_functional.py, repo/importlib_resources/abc.py, repo/importlib_resources/readers.py, repo/importlib_resources/simple.py, repo/pyproject.toml`
- runtime dependencies: `none`
- oracle notes: Task-scoped Traversable resource tree. Zip adapters, as_file, deprecated contents/path helpers, and temporary extraction are intentionally excluded. Upstream declares Apache-2.0 in pyproject.toml; no standalone LICENSE file exists at the pinned commit.
