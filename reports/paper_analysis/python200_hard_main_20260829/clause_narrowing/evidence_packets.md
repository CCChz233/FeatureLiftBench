# Hidden 首败逐题证据包

> 每题给出：失败断言、该测试声明映射到的契约条款原文、以及提交中对应符号的实现。用于判定义务是否已被契约确定。

## `aiohttp__url_params_core__hard3_001`

### 失败用例 `test_invalid_header_name_raises`

声明映射条款：B002, B003

- B002: `normalize_headers` returns a case-insensitive `CIMultiDict`.
- B003: Invalid header names raise `InvalidHeaderName`.

```python
def test_invalid_header_name_raises():
    headers = CIMultiDict()
    with pytest.raises(InvalidHeaderName):
        headers["bad header"] = "1"
```

失败证据：

```text
Failed: DID NOT RAISE <class 'featurelifted.headers.InvalidHeaderName'>
```

测试驱动但未在 `required_api` 声明的成员：`CIMultiDict.__getitem__; CIMultiDict.__setitem__; str.__contains__`

提交实现 `CIMultiDict`：

```python
class CIMultiDict(MutableMapping):
    """Case-insensitive multi-valued mapping.

    Keys compare equal regardless of letter casing, duplicate keys are kept in
    insertion order, and ``getall(key)`` returns every value stored for a key.
    """

    def __init__(self, *args, **kwargs) -> None:
        self._items: list[tuple[str, Any]] = []
        self._key_to_pos: dict[str, list[int]] = {}
        if args:
            if len(args) > 1:
                raise TypeError(
                    "CIMultiDict expected at most 1 positional argument, "
                    f"got {len(args)}"
                )
            self._extend(args[0])
        if kwargs:
            self._extend(kwargs)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _extend(self, arg: Any) -> None:
        if isinstance(arg, Mapping):
            iterable = arg.items()
        else:
            iterable = arg
        for key, value in iterable:
            self.add(key, value)

    def _rebuild_without(self, remove: set[int]) -> None:
        """Rebuild internal tables dropping the given positions."""
        new_items: list[tuple[str, Any]] = []
        new_key_to_pos: dict[str, list[int]] = {}
        for index, pair in enumerate(self._items):
            if index in remove:
                continue
            new_items.append(pair)
            new_key_to_pos.setdefault(_ci_key(pair[0]), []).append(
                len(new_items) - 1
            )
        self._items = new_items
        self._key_to_pos = new_key_to_pos

    # ------------------------------------------------------------------
    # Core multi-dict mutations
    # ------------------------------------------------------------------
    def add(self, key: str, value: Any) -> None:
        """Append *value* for *key*, keeping any existing values."""
        self._items.append((key, value))
        self._ke
```

提交实现 `__setitem__`：

```python
def __setitem__(self, key: str, value: Any) -> None:
        positions = self._key_to_pos.get(_ci_key(key))
        if positions is None:
            self.add(key, value)
            return
        remove = set(positions[1:])
        if not remove:
            # Replace the single stored pair in place, updating casing.
            self._items[positions[0]] = (key, value)
            return
        new_items: list[tuple[str, Any]] = []
        new_key_to_pos: dict[str, list[int]] = {}
        for index, (old_key, old_value) in enumerate(self._items):
            if index in remove:
                continue
            if index == positions[0]:
                old_key, old_value = key, value
            new_items.append((old_key, old_value))
            new_key_to_pos.setdefault(_ci_key(old_key), []).append(
                len(new_items) - 1
            )
        self._items = new_items
        self._key_to_pos = new_key_to_pos
```

提交实现 `__getitem__`：

```python
def __getitem__(self, key: str) -> Any:
        positions = self._key_to_pos.get(_ci_key(key))
        if positions is None:
            raise KeyError(key)
        return self._items[positions[0]][1]
```

提交实现 `getall`：

```python
def getall(self, key: str) -> list[str]:
        """Return all values stored for *key* as a list."""
        positions = self._key_to_pos.get(_ci_key(key))
        if positions is None:
            raise KeyError(key)
        return [self._items[pos][1] for pos in positions]
```

提交实现 `__contains__`：

```python
def __contains__(self, key: object) -> bool:
        if not isinstance(key, str):
            return False
        return _ci_key(key) in self._key_to_pos
```

## `dateutil__zone_resolver_core__hard3_001`

### 失败用例 `test_alias_resolution`

声明映射条款：B003

- B003: When a zone alias is resolved, ZoneResolver follows aliases to the canonical zone and raises UnknownZoneError for missing names or alias cycles.

```python
def test_alias_resolution():
    resolver = ZoneResolver()
    resolver.register_alias("US/Eastern", "America/New_York")
    zone = resolver.load_zone("US/Eastern", {"America/New_York": TZIF})
    assert zone.name == "America/New_York"
    assert resolver.get("US/Eastern") is zone
```

失败证据：

```text
featurelifted._resolver.UnknownZoneError: US/Eastern
```

提交实现 `ZoneResolver`：

```python
class ZoneResolver(object):
    """Resolves time zone names to parsed :class:`TZZone` objects.

    Zones are loaded from raw tzfile bytes via :meth:`load_zone`. Registered
    aliases are followed (with cycle detection) to the canonical zone name.
    """

    def __init__(self) -> None:
        self._zones = {}
        self._aliases = {}
        self._cache = {}

    def load_zone(self, name: str, tzdata: dict[str, bytes]) -> TZZone:
        """Load the zone named ``name`` from the ``tzdata`` mapping.

        ``tzdata`` maps zone names to raw tzfile bytes; the zone identified by
        ``name`` is parsed and made available to :meth:`get`.

        :param name: the zone name to load.
        :param tzdata: a mapping of zone names to tzfile bytes.
        :raises UnknownZoneError: if ``name`` is not present in ``tzdata``.
        """
        if name not in tzdata:
            raise UnknownZoneError(name)
        data = tzdata[name]
        zone = build_zone(name, data)
        self._zones[name] = data
        self._cache[name] = zone
        return zone

    def get(self, name: str) -> TZZone:
        """Return the parsed zone for ``name``.

        Aliases are followed to their canonical zone name with cycle
        detection.

        :param name: a zone name or alias.
        :raises UnknownZoneError: if the name is missing or an alias cycle is
            encountered.
        """
        canonical = self._resolve(name)
        zone = self._cache.get(canonical)
        if zone is None:
            data = self._zones.get(canonical)
            if data is None:
                raise UnknownZoneError(name)
            zone = build_zone(canonical, data)
            self._cache[canonical] = zone
        return zone

    def register_alias(self, alias: str, canonical: str) -> None:
        """Register ``alias`` as a name for ``canonical``."""
        self._aliases[alias] = canonical

    def _resolve(self, name):
        """Follow alias chains to a canonical zone nam
```

提交实现 `load_zone`：

```python
def load_zone(self, name: str, tzdata: dict[str, bytes]) -> TZZone:
        """Load the zone named ``name`` from the ``tzdata`` mapping.

        ``tzdata`` maps zone names to raw tzfile bytes; the zone identified by
        ``name`` is parsed and made available to :meth:`get`.

        :param name: the zone name to load.
        :param tzdata: a mapping of zone names to tzfile bytes.
        :raises UnknownZoneError: if ``name`` is not present in ``tzdata``.
        """
        if name not in tzdata:
            raise UnknownZoneError(name)
        data = tzdata[name]
        zone = build_zone(name, data)
        self._zones[name] = data
        self._cache[name] = zone
        return zone
```

提交实现 `get`：

```python
def get(self, name: str) -> TZZone:
        """Return the parsed zone for ``name``.

        Aliases are followed to their canonical zone name with cycle
        detection.

        :param name: a zone name or alias.
        :raises UnknownZoneError: if the name is missing or an alias cycle is
            encountered.
        """
        canonical = self._resolve(name)
        zone = self._cache.get(canonical)
        if zone is None:
            data = self._zones.get(canonical)
            if data is None:
                raise UnknownZoneError(name)
            zone = build_zone(canonical, data)
            self._cache[canonical] = zone
        return zone
```

提交实现 `register_alias`：

```python
def register_alias(self, alias: str, canonical: str) -> None:
        """Register ``alias`` as a name for ``canonical``."""
        self._aliases[alias] = canonical
```

## `installer__wheel_record_core__hard3_001`

### 失败用例 `test_multiple_dist_info_raises`

声明映射条款：B002

- B002: `find_dist_info` locates a unique `.dist-info` directory among archive names.

```python
def test_multiple_dist_info_raises():
    names = ["a-1.dist-info/METADATA", "b-2.dist-info/RECORD"]
    with pytest.raises(ValueError):
        find_dist_info(names)
```

失败证据：

```text
Failed: DID NOT RAISE <class 'ValueError'>
```

## `pygments__lexer_core__001`

### 失败用例 `test_stripall_option_removes_whitespace_tokens`

声明映射条款：B004

- B004: The extracted feature must support this observable behavior: honor lexer options such as stripall and ensurenl. Required observable cases include stripall option removes whitespace tokens.

```python
def test_stripall_option_removes_whitespace_tokens() -> None:
    lexer = PythonLexer(stripall=True)
    pairs = list(lex("  x  =  1  ", lexer))

    assert all(ttype is not token.Text for ttype, _ in pairs)
    assert [value for _, value in pairs if value.strip()] == ["x", "=", "1"]
```

失败证据：

```text
assert False
+  where False = all(<generator object test_stripall_option_removes_whitespace_tokens.<locals>.<genexpr> at 0x795860db0120>)
```

## `pytest__marker_registry_core__hard3_001`

### 失败用例 `test_check_unknown_strict_raises`

声明映射条款：B003

- B003: `check_unknown` warns or raises for unregistered markers.

```python
def test_check_unknown_strict_raises():
    registry = MarkerRegistry()
    try:
        registry.check_unknown("missing", strict=True)
    except KeyError:
        pass
    else:
        raise AssertionError("strict unknown marker should raise KeyError")
```

失败证据：

```text
featurelifted._mark.UnknownMarkerWarning: Unknown marker 'missing' not found in `markers` configuration option
```

提交实现 `MarkerRegistry`：

```python
class MarkerRegistry:
    """Registry of known markers and their descriptions.

    Markers can be registered directly via :meth:`register`, loaded from
    ini-style configuration via :meth:`from_ini`, or contributed by plugins
    via :meth:`merge_plugin_markers`.
    """

    def __init__(self) -> None:
        self._markers: dict[str, Marker] = {}

    @classmethod
    def from_ini(cls, value: str | list[str]) -> MarkerRegistry:
        """Build a registry from ``markers`` ini configuration lines.

        ``value`` may be a list of marker lines or a single (possibly
        multi-line) string.  Each line has the form ``name(condition):
        description``; the condition and description are optional.
        """
        registry = cls()
        if isinstance(value, str):
            lines = value.splitlines()
        else:
            lines = value
        for line in lines:
            parsed = _parse_marker_line(line)
            if parsed is None:
                continue
            name, description = parsed
            registry.register(name, description)
        return registry

    def register(
        self, name: str, description: str = "", *, _overwrite: bool = False
    ) -> None:
        """Register a marker under ``name`` with the given ``description``.

        By default an already-registered marker is left untouched; pass
        ``_overwrite=True`` to replace it.
        """
        if name not in self._markers or _overwrite:
            self._markers[name] = Marker(name, description)

    def merge_plugin_markers(self, plugin_markers: dict[str, str]) -> None:
        """Register markers provided by plugins.

        Each plugin marker is registered with its description unless a
        marker with the same name is already known; existing markers are
        never overwritten.
        """
        for name, description in plugin_markers.items():
            if name not in self._markers:
                self._markers[name] = Marker(name, descri
```

提交实现 `register`：

```python
def register(
        self, name: str, description: str = "", *, _overwrite: bool = False
    ) -> None:
        """Register a marker under ``name`` with the given ``description``.

        By default an already-registered marker is left untouched; pass
        ``_overwrite=True`` to replace it.
        """
        if name not in self._markers or _overwrite:
            self._markers[name] = Marker(name, description)
```

提交实现 `merge_plugin_markers`：

```python
def merge_plugin_markers(self, plugin_markers: dict[str, str]) -> None:
        """Register markers provided by plugins.

        Each plugin marker is registered with its description unless a
        marker with the same name is already known; existing markers are
        never overwritten.
        """
        for name, description in plugin_markers.items():
            if name not in self._markers:
                self._markers[name] = Marker(name, description)
```

提交实现 `get`：

```python
def get(self, name: str) -> Marker | None:
        """Return the marker registered under ``name``, or ``None``."""
        return self._markers.get(name)
```

提交实现 `check_unknown`：

```python
def check_unknown(self, name: str, *, strict: bool = False) -> None:
        """Check whether ``name`` is a registered marker.

        If the marker is not registered an :class:`UnknownMarkerWarning` is
        emitted; when ``strict`` is true the warning is raised instead.
        """
        if name in self._markers:
            return
        if strict:
            raise UnknownMarkerWarning(
                f"Unknown marker {name!r} not found in `markers` "
                "configuration option"
            )
        warnings.warn(
            f"Unknown marker {name!r} - is this a typo?  You can register "
            "custom marks to avoid this warning - for details, see "
            "https://docs.pytest.org/en/stable/how-to/mark.html",
            UnknownMarkerWarning,
            stacklevel=2,
        )
```

## `python_decouple__config_repository_core__001`

### 失败用例 `test_env_file_quotes_comments_and_empty`

声明映射条款：B001, B002, B003, B004

- B001: The extracted feature must support this observable behavior: environment variables override repository values. Required observable cases include precedence defaults and casts; csv cast; env file quotes comments and empty; choices and float.
- B002: The extracted feature must support this observable behavior: .env quoted-value and comment parsing. Required observable cases include precedence defaults and casts; csv cast; env file quotes comments and empty; choices and float.
- B003: The extracted feature must support this observable behavior: required and default value behavior. Required observable cases include precedence defaults and casts; csv cast; env file quotes comments and empty; choices and float.
- B004: The extracted feature must support this observable behavior: bool, int, float, Csv, and Choices casting. Required observable cases include precedence defaults and casts; csv cast; env file quotes comments and empty; choices and float.

```python
def test_env_file_quotes_comments_and_empty(tmp_path):
    path = tmp_path / ".env"
    path.write_text("NAME='Ada Lovelace' # note\nEMPTY=\nFLAG=YES\n", encoding="utf-8")
    config = Config(RepositoryEnv(path), environ={})
    assert config("NAME") == "Ada Lovelace"
    assert config("EMPTY") == ""
    assert config("FLAG", cast=bool) is True
```

失败证据：

```text
assert "'Ada Lovelace' # note" == 'Ada Lovelace'
- Ada Lovelace
+ 'Ada Lovelace' # note
```

## `responses__request_matcher_core__hard3_001`

### 失败用例 `test_query_and_header_matchers_and_once_behavior`

声明映射条款：B002, B003

- B002: Support `query_string_matcher` and `header_matcher` helper matchers.
- B003: `once=True` responses are removed after the first successful match.

```python
def test_query_and_header_matchers_and_once_behavior():
    registry = MockResponseRegistry()
    registry.add(
        MockResponse(
            url="http://example.com?a=1",
            method="GET",
            matchers=[query_string_matcher({"a": "1"}), header_matcher({"X-Test": "1"})],
            once=True,
        )
    )
    request = PreparedRequest()
    request.prepare(method="GET", url="http://example.com?a=1", headers={"X-Test": "1"})
    first, _ = registry.find(request)
    second, _ = registry.find(request)
    assert first is not None
    assert second is None
    assert len(registry.call_history) == 2
```

失败证据：

```text
assert 1 == 2
+  where 1 = len([Call(request=<PreparedRequest [GET]>, response=<featurelifted.MockResponse object at 0x75c3dd23a410>)])
+    where [Call(request=<PreparedRequest [GET]>, response=<featurelifted.MockResponse object at 0x75c3dd23a410>)] = <featurelifted.MockResponseRegistry object at 0x75c3dd23a4d0>.call_history
```

提交实现 `MockResponseRegistry`：

```python
class MockResponseRegistry:
    """Registry that stores ``MockResponse`` objects and finds matches."""

    def __init__(self) -> None:
        self._responses: List[MockResponse] = []
        self.call_history: CallList = CallList()

    @property
    def registered(self) -> List[MockResponse]:
        return self._responses

    def reset(self) -> None:
        self._responses = []
        self.call_history.reset()

    def add(self, response: MockResponse) -> MockResponse:
        if any(response is resp for resp in self.registered):
            # If the same instance is registered more than once, store a copy.
            response = copy.deepcopy(response)
        self.registered.append(response)
        return response

    def _record_call(self, response: MockResponse, request: PreparedRequest) -> None:
        response.call_count += 1
        call = Call(request, response)
        self.call_history.add_call(call)
        response._calls.add_call(call)
        if response.once:
            for i, resp in enumerate(self.registered):
                if resp is response:
                    self.registered.pop(i)
                    break

    def find(
        self, request: PreparedRequest
    ) -> Tuple[Optional[MockResponse], List[str]]:
        """Find the first registered response matching the request.

        Returns a tuple of the matched response (``None`` if nothing matched)
        and a list of reasons why the other registered responses did not match.
        """
        found = None
        found_match = None
        match_failed_reasons: List[str] = []
        for i, response in enumerate(self.registered):
            match_result, reason = response.matches(request)
            if match_result:
                if found is None:
                    found = i
                    found_match = response
                else:
                    if self.registered[found].call_count > 0:
                        # The previously matched response was alrea
```

提交实现 `add`：

```python
def add(self, request: Any, response: Any) -> None:
        self._calls.append(Call(request, response))
```

提交实现 `reset`：

```python
def reset(self) -> None:
        self._calls = []
```

提交实现 `find`：

```python
def find(
        self, request: PreparedRequest
    ) -> Tuple[Optional[MockResponse], List[str]]:
        """Find the first registered response matching the request.

        Returns a tuple of the matched response (``None`` if nothing matched)
        and a list of reasons why the other registered responses did not match.
        """
        found = None
        found_match = None
        match_failed_reasons: List[str] = []
        for i, response in enumerate(self.registered):
            match_result, reason = response.matches(request)
            if match_result:
                if found is None:
                    found = i
                    found_match = response
                else:
                    if self.registered[found].call_count > 0:
                        # The previously matched response was already used.
                        self.registered.pop(found)
                        found_match = response
                        break
                    # Multiple matches found. Remove & return the first response.
                    match = self.registered.pop(found)
                    self._record_call(match, request)
                    return match, match_failed_reasons
            else:
                match_failed_reasons.append(reason)

        if found_match is not None:
            self._record_call(found_match, request)
        return found_match, match_failed_reasons
```

## `zope_interface__adapter_registry_core__001`

### 失败用例 `test_named_registration_exactness_and_unregister_value_guard`

声明映射条款：B003

- B003: Registrations are separated by text name: named and unnamed adapters can coexist, `registered` reports only an exact registration, and `unregister` removes only the matching registration and value.

```python
def test_named_registration_exactness_and_unregister_value_guard() -> None:
    class ISource(fl.Interface):
        pass

    class ITarget(fl.Interface):
        pass

    unnamed = object()
    named = object()
    registry = fl.AdapterRegistry()
    registry.register((ISource,), ITarget, "", unnamed)
    registry.register((ISource,), ITarget, "blue", named)
    assert registry.registered((ISource,), ITarget) is unnamed
    assert registry.registered((ISource,), ITarget, "blue") is named
    assert not registry.unregister((ISource,), ITarget, "blue", unnamed)
    assert registry.registered((ISource,), ITarget, "blue") is named
    assert not registry.unregister((ISource,), ITarget, "blue", named)
    assert registry.registered((ISource,), ITarget, "blue") is None
    assert registry.registered((ISource,), ITarget) is unnamed
```

失败证据：

```text
AssertionError: assert not True
+  where True = <bound method BaseAdapterRegistry.unregister of <featurelifted.adapter.AdapterRegistry object at 0x7d71b747fb90>>((<InterfaceClass test_hidden_behavior.ISource>,), <InterfaceClass test_hidden_behavior.ITarget>, 'blue', <object object at 0x7d71b8136660>)
+    where <bound method BaseAdapterRegistry.unregister of <featurelifted.adapter.AdapterRegistry object at 0x7d71b747fb90>> = <featurelifted.adapter.AdapterRegistry object at 0x7d71b747fb90>.unregister
```

测试驱动但未在 `required_api` 声明的成员：`InterfaceSpecification.__contains__`

提交实现 `AdapterRegistry`：

```python
class AdapterRegistry(BaseAdapterRegistry):
    """
    A full implementation of ``IAdapterRegistry`` that adds support for
    sub-registries.
    """

    LookupClass = AdapterLookup

    def __init__(self, bases=()):
        # AdapterRegisties are invalidating registries, so
        # we need to keep track of our invalidating subregistries.
        self._v_subregistries = weakref.WeakKeyDictionary()

        super().__init__(bases)

    def _addSubregistry(self, r):
        self._v_subregistries[r] = 1

    def _removeSubregistry(self, r):
        if r in self._v_subregistries:
            del self._v_subregistries[r]

    def _setBases(self, bases):
        old = self.__dict__.get('__bases__', ())
        for r in old:
            if r not in bases:
                r._removeSubregistry(self)
        for r in bases:
            if r not in old:
                r._addSubregistry(self)

        super()._setBases(bases)

    def changed(self, originally_changed):
        super().changed(originally_changed)

        for sub in self._v_subregistries.keys():
            sub.changed(originally_changed)
```

提交实现 `register`：

```python
def register(self, required, provided, name, value):
        if not isinstance(name, str):
            raise ValueError('name is not a string')
        if value is None:
            self.unregister(required, provided, name, value)
            return

        required = tuple([_convert_None_to_Interface(r) for r in required])
        name = _normalize_name(name)
        order = len(required)
        byorder = self._adapters
        while len(byorder) <= order:
            byorder.append(self._mappingType())
        components = byorder[order]
        key = required + (provided,)

        for k in key:
            d = components.get(k)
            if d is None:
                d = self._mappingType()
                components[k] = d
            components = d

        if components.get(name) is value:
            return

        components[name] = value

        n = self._provided.get(provided, 0) + 1
        self._provided[provided] = n
        if n == 1:
            self._v_lookup.add_extendor(provided)

        self.changed(self)
```

提交实现 `registered`：

```python
def registered(self, required, provided, name=''):
        return self._find_leaf(
            self._adapters,
            required,
            provided,
            _normalize_name(name)
        )
```

提交实现 `unregister`：

```python
def unregister(self, required, provided, name, value=None):
        required = tuple([_convert_None_to_Interface(r) for r in required])
        order = len(required)
        byorder = self._adapters
        if order >= len(byorder):
            return False
        components = byorder[order]
        key = required + (provided,)

        # Keep track of how we got to `components`:
        lookups = []
        for k in key:
            d = components.get(k)
            if d is None:
                return False
            lookups.append((components, k))
            components = d

        old = components.get(name)
        if old is None:
            return False
        if (value is not None) and (old is not value):
            return False

        del components[name]
        if not components:
            # Clean out empty containers, since we don't want our keys
            # to reference global objects (interfaces) unnecessarily.
            # This is often a problem when an interface is slated for
            # removal; a hold-over entry in the registry can make it
            # difficult to remove such interfaces.
            for comp, k in reversed(lookups):
                d = comp[k]
                if d:
                    break
                else:
                    del comp[k]
            while byorder and not byorder[-1]:
                del byorder[-1]
        n = self._provided[provided] - 1
        if n == 0:
            del self._provided[provided]
            self._v_lookup.remove_extendor(provided)
        else:
            self._provided[provided] = n

        self.changed(self)
        return True
```

提交实现 `queryAdapter`：

```python
def queryAdapter(self, object, provided, name='', default=None):
        return self.adapter_hook(provided, object, name, default)
```

提交实现 `lookupAll`：

```python
def lookupAll(self, required, provided):
        cache = self._mcache.get(provided)
        if cache is None:
            cache = {}
            self._mcache[provided] = cache

        required = tuple(required)
        result = cache.get(required, _not_in_mapping)
        if result is _not_in_mapping:
            result = self._uncached_lookupAll(required, provided)
            cache[required] = result

        return result
```

提交实现 `queryMultiAdapter`：

```python
def queryMultiAdapter(self, objects, provided, name='', default=None):
        factory = self.lookup([providedBy(o) for o in objects], provided, name)
        if factory is None:
            return default

        result = factory(*[
            o.__self__ if isinstance(o, super) else o for o in objects
        ])
        if result is None:
            return default

        return result
```

提交实现 `__contains__`：

```python
def __contains__(self, interface):
        """Test whether an interface is in the specification
        """

        return self.extends(interface) and interface in self.interfaces()
```

