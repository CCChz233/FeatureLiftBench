# deepdiff__deep_compare_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `8/14`

## Required API

- `featurelifted.DeepDiff` (class) `(t1: Any, t2: Any, _original_type: Optional[Any] = None, cache_purge_level: int = 1, cache_size: int = 0, cache_tuning_sample_size: int = 0, custom_operators: Optional[List[Any]] = None, cutoff_distance_for_pairs: float = 0.3, cutoff_intersection_for_pairs: float = 0.7, default_timezone: Union[datetime.timezone, ForwardRef('BaseTzInfo')] = datetime.timezone.utc, encodings: Optional[List[str]] = None, exclude_obj_callback: Optional[Callable] = None, exclude_obj_callback_strict: Optional[Callable] = None, exclude_paths: Union[str, List[str], Set[str], FrozenSet[str], NoneType] = None, exclude_regex_paths: Union[str, List[str], Pattern[str], List[Pattern[str]], NoneType] = None, exclude_types: Optional[List[type]] = None, get_deep_distance: bool = False, group_by: Union[str, Tuple[str, str], Callable, NoneType] = None, group_by_sort_key: Union[str, Callable, NoneType] = None, hasher: Optional[Callable] = None, hashes: Optional[Dict[Any, Any]] = None, ignore_encoding_errors: bool = False, ignore_nan_inequality: bool = False, ignore_numeric_type_changes: bool = False, ignore_order: bool = False, ignore_order_func: Optional[Callable] = None, ignore_private_variables: bool = True, ignore_string_case: bool = False, ignore_string_type_changes: bool = False, ignore_type_in_groups: Optional[List[Tuple[Any, ...]]] = None, ignore_type_subclasses: bool = False, ignore_uuid_types: bool = False, include_obj_callback: Optional[Callable] = None, include_obj_callback_strict: Optional[Callable] = None, include_paths: Union[str, List[str], NoneType] = None, iterable_compare_func: Optional[Callable] = None, log_frequency_in_sec: int = 0, log_scale_similarity_threshold: float = 0.1, log_stacktrace: bool = False, math_epsilon: Optional[float] = None, max_diffs: Optional[int] = None, max_passes: int = 10000000, multiprocessing: bool = False, multiprocessing_workers: Optional[int] = None, multiprocessing_threshold: Optional[int] = None, number_format_notation: Literal['f', 'e'] = 'f', number_to_string_func: Optional[Callable] = None, progress_logger: Callable[[str], NoneType] = <bound method Logger.info of <Logger diff (WARNING)>>, report_repetition: bool = False, significant_digits: Optional[int] = None, threshold_to_diff_deeper: float = 0.33, truncate_datetime: Optional[str] = None, use_enum_value: bool = False, use_log_scale: bool = False, verbose_level: int = 1, view: str = 'text', zip_ordered_iterables: bool = False, _parameters: Optional[Dict[str, Any]] = None, _shared_parameters: Optional[Dict[str, Any]] = None, **kwargs)`
- `featurelifted.DeepDiff.get` (method) `(self, key, default=None, /)`
- `featurelifted.parse_path` (function) `(path, root_element=('root', 'GETATTR'), include_actions=False)`
- `featurelifted.extract` (function) `(obj, path)`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: DeepDiff dict/list value changes. Required observable cases include shallow dict diff; identical nested; nested dict change; list item added.
- **B002**: The extracted feature must support this observable behavior: exclude_paths and include_paths filtering. Required observable cases include exclude paths wildcard.
- **B003**: The extracted feature must support this observable behavior: parse_path and extract by path expression. Required observable cases include parse path and extract.
- **B004**: The package exposes the required task API paths `featurelifted.DeepDiff`, `featurelifted.DeepDiff.get`, `featurelifted.parse_path`, `featurelifted.extract` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_shallow_dict_diff`

- mapping: `B001`
- API: `featurelifted.DeepDiff`
- risk: `none`
- A001 `assert` L10: `'values_changed' in diff`
- A002 `assert` L11: `diff['values_changed']["root['b']"]['new_value'] == 3`

### `public_tests/test_public_api.py::test_identical_nested`

- mapping: `B001`
- API: `featurelifted.DeepDiff`
- risk: `none`
- A001 `assert` L17: `DeepDiff(d1, d2) == {}`

### `hidden_tests/test_hidden_behavior.py::test_nested_dict_change`

- mapping: `B001`
- API: `featurelifted.DeepDiff`
- risk: `none`
- A001 `assert` L13: `"root['outer']['inner']" in diff.get('values_changed', {})`

### `hidden_tests/test_hidden_behavior.py::test_exclude_paths_wildcard`

- mapping: `B002`
- API: `featurelifted.DeepDiff`
- risk: `none`
- A001 `assert` L20: `"root['b']" in diff.get('values_changed', {})`
- A002 `assert` L21: `"root['a']['secret']" not in diff.get('values_changed', {})`

### `hidden_tests/test_hidden_behavior.py::test_list_item_added`

- mapping: `B001`
- API: `featurelifted.DeepDiff`
- risk: `none`
- A001 `assert` L28: `'iterable_item_added' in diff`

### `hidden_tests/test_hidden_behavior.py::test_parse_path_and_extract`

- mapping: `B003`
- API: `featurelifted.extract, featurelifted.parse_path`
- risk: `filesystem_resource`
- A001 `assert` L34: `elements`
- A002 `assert` L35: `extract(obj, "root['users'][0]['name']") == 'ada'`

### `hidden_tests/test_hidden_behavior.py::test_no_deepdiff_import_surface`

- mapping: `B005`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L45: `not import_pattern.search(text)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B004`
- API: `featurelifted.DeepDiff, featurelifted.extract, featurelifted.parse_path`
- risk: `none`
- A001 `assert` L11: `isinstance(DeepDiff, type)`
- A002 `assert` L12: `hasattr(DeepDiff, 'get')`
- A003 `assert` L13: `callable(parse_path)`
- A004 `assert` L14: `callable(extract)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `deepdiff`
- source entrypoints: `deepdiff.DeepDiff, deepdiff.path.parse_path, deepdiff.path.extract`
- oracle source files: `deepdiff/diff.py, deepdiff/helper.py, deepdiff/model.py, deepdiff/base.py, deepdiff/path.py, deepdiff/lfucache.py, deepdiff/serialization.py, deepdiff/distance.py`
- runtime dependencies: `none`
- oracle notes: DeepDiff core with path/exclude_paths; copy-all adds search/delta/commands.
