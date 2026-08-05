# msgpack__pack_unpack_core__001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `14/34`

## Required API

- `featurelifted.packb` (function) `(o, **kwargs)`
- `featurelifted.unpackb` (function) `(packed, **kwargs)`
- `featurelifted.pack` (function) `(o, stream, **kwargs)`
- `featurelifted.unpack` (function) `(stream, **kwargs)`
- `featurelifted.dumps` (function) `(o, **kwargs)`
- `featurelifted.loads` (function) `(packed, **kwargs)`
- `featurelifted.Packer` (class) `(*, default=None, use_single_float=False, autoreset=True, use_bin_type=True, strict_types=False, datetime=False, unicode_errors=None, buf_size=None)`
- `featurelifted.Unpacker` (class) `(file_like=None, *, read_size=0, use_list=True, raw=False, timestamp=0, strict_map_key=True, object_hook=None, object_pairs_hook=None, list_hook=None, unicode_errors=None, max_buffer_size=104857600, ext_hook=<class 'ExtType'>, max_str_len=-1, max_bin_len=-1, max_array_len=-1, max_map_len=-1, max_ext_len=-1)`
- `featurelifted.ExtType` (class) `(code, data)`
- `featurelifted.Timestamp` (class) `(seconds, nanoseconds=0)`
- `featurelifted.ExtraData` (exception)
- `featurelifted.FormatError` (exception)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: packb/unpackb roundtrip for nil, bool, int, float, str, bytes, list, tuple, dict. Required observable cases include pack unpack none bool int; pack unpack string and bytes; pack unpack list and dict; timestamp roundtrip; ext type roundtrip; strict map key allows int keys; extra data raises; ext hook transforms extension; format error on invalid bytes.
- **B002**: The extracted feature must support this observable behavior: Packer options: use_bin_type, use_single_float, default hook, datetime timestamps. Required observable cases include unpack stream reads filelike.
- **B003**: The extracted feature must support this observable behavior: Unpacker streaming feed/unpack, strict_map_key, raw/bin decoding, ext_hook. Required observable cases include packer unpacker streaming; strict map key allows int keys; ext hook transforms extension; unpack stream reads filelike.
- **B004**: The extracted feature must support this observable behavior: Timestamp extension type pack/unpack (32/64/96-bit encodings). Required observable cases include pack unpack none bool int; pack unpack string and bytes; pack unpack list and dict; timestamp roundtrip.
- **B005**: The extracted feature must support this observable behavior: ExtType custom extension payloads. Required observable cases include unpack stream reads filelike.
- **B006**: The extracted feature must support this observable behavior: ExtraData, FormatError, StackError, OutOfData exception semantics. Required observable cases include unpack stream reads filelike.
- **B007**: The package exposes the required task API paths `featurelifted.packb`, `featurelifted.unpackb`, `featurelifted.pack`, `featurelifted.unpack`, `featurelifted.dumps`, `featurelifted.loads`, `featurelifted.Packer`, `featurelifted.Unpacker`, `featurelifted.ExtType`, `featurelifted.Timestamp`, `featurelifted.ExtraData`, `featurelifted.FormatError` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_pack_unpack_none_bool_int`

- mapping: `B001, B004`
- API: `none detected`
- risk: `none`
- A001 `assert` L13: `_roundtrip(None) is None`
- A002 `assert` L14: `_roundtrip(True) is True`
- A003 `assert` L15: `_roundtrip(False) is False`
- A004 `assert` L16: `_roundtrip(42) == 42`
- A005 `assert` L17: `_roundtrip(-7) == -7`

### `public_tests/test_public_api.py::test_pack_unpack_string_and_bytes`

- mapping: `B001, B004`
- API: `featurelifted.packb, featurelifted.unpackb`
- risk: `none`
- A001 `assert` L21: `_roundtrip('hello') == 'hello'`
- A002 `assert` L23: `unpackb(packed) == b'abc'`

### `public_tests/test_public_api.py::test_pack_unpack_list_and_dict`

- mapping: `B001, B004`
- API: `none detected`
- risk: `none`
- A001 `assert` L27: `_roundtrip([1, 'two', None]) == [1, 'two', None]`
- A002 `assert` L28: `_roundtrip({'a': 1, 'b': [2, 3]}) == {'a': 1, 'b': [2, 3]}`

### `public_tests/test_public_api.py::test_packer_unpacker_streaming`

- mapping: `B003`
- API: `featurelifted.Unpacker, featurelifted.packb`
- risk: `none`
- A001 `assert` L35: `unpacker.unpack() == {'x': [1, 2, 3]}`

### `public_tests/test_public_api.py::test_dumps_loads_aliases`

- mapping: `B007`
- API: `featurelifted.dumps, featurelifted.loads`
- risk: `none`
- A001 `assert` L42: `loads(payload) == [1, 2, 3]`

### `hidden_tests/test_hidden_behavior.py::test_timestamp_roundtrip`

- mapping: `B001, B004`
- API: `featurelifted.Timestamp, featurelifted.packb, featurelifted.unpackb`
- risk: `none`
- A001 `assert` L23: `unpackb(packb(ts)) == ts`
- A002 `assert` L25: `unpackb(packb(ts64)) == ts64`

### `hidden_tests/test_hidden_behavior.py::test_ext_type_roundtrip`

- mapping: `B001`
- API: `featurelifted.ExtType, featurelifted.packb, featurelifted.unpackb`
- risk: `none`
- A001 `assert` L30: `unpackb(packb(ext)) == ext`

### `hidden_tests/test_hidden_behavior.py::test_strict_map_key_allows_int_keys`

- mapping: `B001, B003`
- API: `featurelifted.packb, featurelifted.unpackb`
- risk: `none`
- A001 `assert` L36: `unpackb(packed, strict_map_key=False) == value`

### `hidden_tests/test_hidden_behavior.py::test_extra_data_raises`

- mapping: `B001`
- API: `featurelifted.ExtraData, featurelifted.packb, featurelifted.unpackb`
- risk: `exception_semantics`
- A001 `raises` L41: `pytest.raises(ExtraData)`
- A002 `assert` L43: `exc.value.unpacked == 1`
- A003 `assert` L44: `exc.value.extra == b'\x00'`

### `hidden_tests/test_hidden_behavior.py::test_ext_hook_transforms_extension`

- mapping: `B001, B003`
- API: `featurelifted.ExtType, featurelifted.packb, featurelifted.unpackb`
- risk: `none`
- A001 `assert` L54: `unpackb(packed, ext_hook=hook) == {'a': 123}`

### `hidden_tests/test_hidden_behavior.py::test_format_error_on_invalid_bytes`

- mapping: `B001`
- API: `featurelifted.FormatError, featurelifted.unpackb`
- risk: `exception_semantics`
- A001 `raises` L58: `pytest.raises(FormatError)`

### `hidden_tests/test_hidden_behavior.py::test_unpack_stream_reads_filelike`

- mapping: `B002, B003, B005, B006`
- API: `featurelifted.packb, featurelifted.unpack`
- risk: `none`
- A001 `assert` L66: `unpack(BytesIO(payload)) == {'k': 'v'}`

### `hidden_tests/test_hidden_behavior.py::test_no_msgpack_import_surface`

- mapping: `B008`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L76: `not import_pattern.search(text)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B007`
- API: `featurelifted.ExtType, featurelifted.ExtraData, featurelifted.FormatError, featurelifted.Packer, featurelifted.Timestamp, featurelifted.Unpacker, featurelifted.dumps, featurelifted.loads, featurelifted.pack, featurelifted.packb, featurelifted.unpack, featurelifted.unpackb`
- risk: `none`
- A001 `assert` L20: `callable(packb)`
- A002 `assert` L21: `callable(unpackb)`
- A003 `assert` L22: `callable(pack)`
- A004 `assert` L23: `callable(unpack)`
- A005 `assert` L24: `callable(dumps)`
- A006 `assert` L25: `callable(loads)`
- A007 `assert` L26: `isinstance(Packer, type)`
- A008 `assert` L27: `isinstance(Unpacker, type)`
- A009 `assert` L28: `isinstance(ExtType, type)`
- A010 `assert` L29: `isinstance(Timestamp, type)`
- A011 `assert` L30: `issubclass(ExtraData, BaseException)`
- A012 `assert` L31: `issubclass(FormatError, BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `msgpack`
- source entrypoints: `msgpack.packb, msgpack.unpackb, msgpack.Packer, msgpack.Unpacker, msgpack.ext.ExtType, msgpack.ext.Timestamp, msgpack.fallback, msgpack.exceptions`
- oracle source files: `msgpack/__init__.py, msgpack/exceptions.py, msgpack/ext.py, msgpack/fallback.py`
- runtime dependencies: `none`
- oracle notes: Oracle uses pure-Python fallback only (no Cython). fallback.py is split into codec.py, unpacker.py, and packer.py for module probes; Cython .pyx and headers are excluded.
