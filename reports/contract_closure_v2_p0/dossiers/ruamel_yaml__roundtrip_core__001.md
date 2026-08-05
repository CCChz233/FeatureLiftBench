# Contract V2 P0: ruamel_yaml__roundtrip_core__001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `9/24`

## Required API

- `featurelifted.YAML` (class) `(*, typ: 'Optional[Union[List[Text], Text]]' = None, pure: 'Any' = False, output: 'Any' = None, plug_ins: 'Any' = None) -> 'None'`
- `featurelifted.YAML.dump` (method)
- `featurelifted.YAML.load` (method)
- `featurelifted.round_trip_load` (function) `(stream: 'StreamTextType', version: 'Optional[VersionType]' = None, preserve_quotes: 'Optional[bool]' = None) -> 'Any'`
- `featurelifted.round_trip_dump` (function) `(data: 'Any', stream: 'Optional[StreamType]' = None, Dumper: 'Any' = <class 'RoundTripDumper'>, default_style: 'Any' = None, default_flow_style: 'Any' = None, canonical: 'Optional[bool]' = None, indent: 'Optional[int]' = None, width: 'Optional[int]' = None, allow_unicode: 'Optional[bool]' = None, line_break: 'Any' = None, encoding: 'Any' = None, explicit_start: 'Optional[bool]' = None, explicit_end: 'Optional[bool]' = None, version: 'Optional[VersionType]' = None, tags: 'Any' = None, block_seq_indent: 'Any' = None, top_level_colon_align: 'Any' = None, prefix_colon: 'Any' = None) -> 'Any'`
- `featurelifted.CommentedMap` (class) `(*args: 'Any', **kw: 'Any') -> 'None'`
- `featurelifted.CommentedMap.fa` (attribute)
- `featurelifted.CommentedMap.__getitem__` (method) `(self, key) -> value`
- `featurelifted.CommentedMap.keys` (method) `(self) -> KeysView`
- `featurelifted.comments` (module)
- `featurelifted.comments.Format` (class)
- `featurelifted.comments.Format.set_flow_style` (method) `(self) -> None`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: round-trip load/dump preserves end-of-line comments. Required observable cases include roundtrip basic mapping; eol comment preserved; flow style dump; anchor alias roundtrip.
- **B002**: The extracted feature must support this observable behavior: CommentedMap key order preserved. Required observable cases include key order preserved; no ruamel import surface.
- **B003**: The extracted feature must support this observable behavior: flow style and literal block scalars. Required observable cases include flow style dump; literal block scalar.
- **B004**: The package exposes the required task API paths `featurelifted.YAML`, `featurelifted.YAML.dump`, `featurelifted.YAML.load`, `featurelifted.round_trip_load`, `featurelifted.round_trip_dump`, `featurelifted.CommentedMap`, `featurelifted.CommentedMap.fa`, `featurelifted.CommentedMap.__getitem__`, `featurelifted.CommentedMap.keys`, `featurelifted.comments`, `featurelifted.comments.Format`, `featurelifted.comments.Format.set_flow_style` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_roundtrip_basic_mapping`

- mapping: `B001`
- API: `featurelifted.YAML`
- risk: `none`
- A001 `assert` L10: `data['a'] == 1`
- A002 `assert` L11: `data['b'] == 'two'`
- A003 `assert` L15: `stream.getvalue().strip() == text.strip()`

### `public_tests/test_public_api.py::test_key_order_preserved`

- mapping: `B002`
- API: `featurelifted.YAML, featurelifted.YAML.load`
- risk: `ordering_semantics`
- A001 `assert` L21: `list(data.keys()) == ['z', 'a']`

### `hidden_tests/test_hidden_behavior.py::test_eol_comment_preserved`

- mapping: `B001`
- API: `featurelifted.YAML`
- risk: `none`
- A001 `assert` L16: `'# note' in stream.getvalue()`
- A002 `assert` L17: `data['key'] == 'value'`

### `hidden_tests/test_hidden_behavior.py::test_flow_style_dump`

- mapping: `B001, B003`
- API: `featurelifted.CommentedMap, featurelifted.YAML, featurelifted.YAML.dump`
- risk: `none`
- A001 `assert` L26: `out.strip().startswith('{') or '[' in out`

### `hidden_tests/test_hidden_behavior.py::test_literal_block_scalar`

- mapping: `B003`
- API: `featurelifted.YAML, featurelifted.YAML.dump, featurelifted.YAML.load`
- risk: `none`
- A001 `assert` L32: `data['body'] == 'line1\nline2\n'`
- A002 `assert` L35: `'|' in stream.getvalue()`

### `hidden_tests/test_hidden_behavior.py::test_anchor_alias_roundtrip`

- mapping: `B001`
- API: `featurelifted.YAML, featurelifted.YAML.load`
- risk: `none`
- A001 `assert` L41: `data['child']['x'] == 1`

### `hidden_tests/test_hidden_behavior.py::test_key_order_hidden`

- mapping: `B002`
- API: `featurelifted.YAML, featurelifted.YAML.load`
- risk: `ordering_semantics`
- A001 `assert` L46: `list(data.keys()) == ['third', 'first', 'second']`

### `hidden_tests/test_hidden_behavior.py::test_no_ruamel_import_surface`

- mapping: `B005`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L59: `not import_pattern.search(text)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B004`
- API: `featurelifted.CommentedMap, featurelifted.YAML, featurelifted.comments, featurelifted.round_trip_dump, featurelifted.round_trip_load`
- risk: `none`
- A001 `assert` L13: `isinstance(YAML, type)`
- A002 `assert` L14: `hasattr(YAML, 'dump')`
- A003 `assert` L15: `hasattr(YAML, 'load')`
- A004 `assert` L16: `callable(round_trip_load)`
- A005 `assert` L17: `callable(round_trip_dump)`
- A006 `assert` L18: `isinstance(CommentedMap, type)`
- A007 `assert` L19: `CommentedMap is not None`
- A008 `assert` L20: `hasattr(CommentedMap, '__getitem__')`
- A009 `assert` L21: `hasattr(CommentedMap, 'keys')`
- A010 `assert` L22: `comments is not None`
- A011 `assert` L23: `isinstance(getattr(comments, 'Format'), type)`
- A012 `assert` L24: `hasattr(getattr(comments, 'Format'), 'set_flow_style')`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `ruamel`
- source entrypoints: `ruamel.yaml.round_trip_load, ruamel.yaml.round_trip_dump, ruamel.yaml.YAML`
- oracle source files: `ruamel/yaml/__init__.py, ruamel/yaml/anchor.py, ruamel/yaml/comments.py, ruamel/yaml/compat.py, ruamel/yaml/composer.py, ruamel/yaml/configobjwalker.py, ruamel/yaml/constructor.py, ruamel/yaml/docinfo.py, ruamel/yaml/dumper.py, ruamel/yaml/emitter.py, ruamel/yaml/error.py, ruamel/yaml/events.py, ruamel/yaml/loader.py, ruamel/yaml/main.py, ruamel/yaml/nodes.py, ruamel/yaml/parser.py, ruamel/yaml/reader.py, ruamel/yaml/representer.py, ruamel/yaml/resolver.py, ruamel/yaml/scalarbool.py, ruamel/yaml/scalarfloat.py, ruamel/yaml/scalarint.py, ruamel/yaml/scalarstring.py, ruamel/yaml/scanner.py, ruamel/yaml/serializer.py, ruamel/yaml/tag.py, ruamel/yaml/timestamp.py, ruamel/yaml/tokens.py, ruamel/yaml/util.py`
- runtime dependencies: `none`
- oracle notes: Full ruamel.yaml Python modules except cyaml C extension.
