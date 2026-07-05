# Task Design: mapstructure__decode_symbol_core__002 (Go)

Status: draft-spike

## Why This Task

The previous mapstructure hardening attempt still had a clean file boundary:
OpenHands + `deepseek/deepseek-v4-flash` copied the same oracle file set and
passed hidden tests. This redesign keeps the useful map-to-struct decoder
feature but makes the extraction boundary symbol-level. The agent must separate
decode behavior from adjacent encode, schema, cache, and registry code that
lives in the same source files.

## Practical reuse

1. **Reuse module** - a standalone `featurelifted` config decoder that maps
   `map[string]any` values into typed structs with tags, hooks, weak
   conversion, metadata, and text unmarshalling.
2. **Who imports it** - CLI/config libraries, service bootstrap code, and API
   adapters that need map-to-struct decoding without vendoring a full
   configuration framework.
3. **Why not copy-all** - upstream-adjacent files also contain encode/flatten,
   schema validation, cache planning, and hook registry helpers. Those are
   plausible neighboring utilities but unnecessary for runtime decoding.

## Source

| Field | Value |
| --- | --- |
| Source repo | https://github.com/go-viper/mapstructure |
| Commit | v2.2.1-derived-symbol-slice |
| License | MIT |
| Language | Go |
| Difficulty | hard |
| Tags | reflection, symbol-boundary, hardening |

## Entanglement

```json
{
  "level": "high",
  "types": [
    "reflection_coupling",
    "data_model_coupling",
    "global_state_registry_coupling",
    "implicit_dependency_coupling"
  ],
  "description": "The target decoder depends on reflection dispatch, tag parsing, hook order, metadata state, weak conversion, and text unmarshalling. Non-target encode/cache/schema helpers intentionally share the same files and helper types.",
  "signals": [
    "reflect.Value",
    "mapstructure tag parsing",
    "DecodeHook composition",
    "Metadata.Unused",
    "encoding.TextUnmarshaler"
  ]
}
```

## Target Feature

### Source entrypoints

- `Decode(input, output interface{}) error`
- `DecodeMetadata(input, output interface{}, metadata *Metadata) error`
- `NewDecoder(config *DecoderConfig) (*Decoder, error)`
- `ComposeDecodeHookFunc(...) DecodeHookFunc`
- `StringToSliceHookFunc(sep string) DecodeHookFuncType`

### Output API

```go
import "featurelifted"

featurelifted.Decode(input, &out)
featurelifted.NewDecoder(&featurelifted.DecoderConfig{Result: &out})
featurelifted.ComposeDecodeHookFunc(...)
featurelifted.StringToSliceHookFunc(",")
```

## Included Behaviors

- Tagged map-to-struct decode.
- Nested pointer allocation and recursive struct decode.
- Slice/map element decode with weak string/float conversions.
- `encoding.TextUnmarshaler` support.
- Decode hook composition in caller-provided order.
- Squashed embedded struct conflict detection.
- `Metadata.Keys`, `Metadata.Unused`, and `ErrorUnused`.

## Excluded Behaviors

- Encode/flatten struct-to-map behavior.
- Field cache planning API.
- Schema validation registry.
- Hook registry mutation API.
- CLI, docs, original tests, original module import.

## Boundary Plan

The oracle boundary is a symbol set, not a file set. At least four source files
must mix target and non-target code. A correct oracle needs to copy target
symbols, delete neighboring non-target symbols, and repair dependencies.

### Target symbols

- `DecoderConfig`, `Metadata`, `Decoder`
- `NewDecoder`, `Decode`, `DecodeMetadata`, `(*Decoder).Decode`
- `decodeValue`, `decodeStruct`, `decodeSlice`, `decodeMapValue`
- `fieldInfo`, `decodeFieldInfo`, tag/squash helpers
- `DecodeHookFunc`, `DecodeHookFuncType`, `ComposeDecodeHookFunc`
- `StringToSliceHookFunc`
- `tryTextUnmarshal`
- `Error`, `appendError`, `errorString`

### Non-target symbols sharing source files

| Source file | Target symbols | Non-target symbols in same file | Why full-file copy is too broad |
| --- | --- | --- | --- |
| `repo/decode.go` | `Decoder`, `NewDecoder`, `Decode`, `decodeValue` | `Encoder`, `Encode`, `flattenValue`, encode options | Copying the file brings reverse encode behavior unrelated to map-to-struct decode. |
| `repo/fields.go` | tag parsing, squash metadata, field lookup | field cache planner, schema field registry | Cache/schema helpers are plausible but not required at runtime. |
| `repo/hooks.go` | hook type adapters, composition, string-to-slice hook | hook registry mutation and validation helpers | Registry APIs add public surface and LOC without supporting target tests. |
| `repo/values.go` | weak conversion, slice/map decode, TextUnmarshaler | normalization and path rendering helpers for encode/schema paths | Full file copy preserves non-target formatting helpers. |
| `repo/errors.go` | decode error aggregation | schema validation error formatting | Error types must be separated by behavior. |

### Oracle transformation

- Extract target symbols from mixed files into a compact package.
- Remove encode/flatten/cache/schema/registry APIs even when they share helper
  structs or constants with target code.
- Keep only helper fields and error constructors required by target public and
  hidden behavior.
- Rewrite package/module names to `featurelifted`.
- Avoid preserving the upstream file structure when that structure contains
  non-target symbols.

### File-boundary rejection check

- [x] Oracle must not equal a list of complete `.go` files.
- [x] Public tests and TASK may name APIs, not source files.
- [x] Source files must not use `excluded`, `noise`, or `non-target` naming.
- [x] Copy-all must pass with substantially higher extraction than oracle.

## Test Plan

### Public

- Basic tagged struct decode.
- `DecodeMetadata` records used keys.
- Simple weak string-to-int conversion.

### Hidden

- Nested pointer decode with slices and maps.
- `encoding.TextUnmarshaler` success and failure.
- Hook composition order where the first hook changes the type consumed by the
  second hook.
- Squash conflict across embedded structs.
- `ErrorUnused` plus `Metadata.Unused` for extra keys.
- One case where encode/cache/schema symbols are present in source but not
  needed by target API.

## Module Probes

| Probe | Remove symbol/file group | Hidden test(s) that must fail |
| --- | --- | --- |
| Value dispatch | weak conversion + slice/map decode symbols | nested pointer/slice/map hidden test |
| Text unmarshalling | `tryTextUnmarshal` path | text unmarshal hidden test |
| Hook order | `ComposeDecodeHookFunc` chain | hook composition hidden test |
| Struct metadata | squash + unused metadata helpers | squash/unused hidden test |

## Baseline Expectations

| Variant | Public | Hidden | Extraction |
| --- | --- | --- | --- |
| oracle | pass | pass | 0.20-0.60; symbol-level compact closure |
| naive | pass | fail | <=0.11 |
| copy_all | pass | pass | >=0.85 or documented trim exception; clearly above oracle |
| OpenHands Flash | ideally public pass / hidden fail | | hard only if not oracle/copy_all footprint |

## Go / No-Go

- [ ] Practical reuse three-question answer remains credible.
- [ ] Boundary Plan proves the task is not file-boundary extraction.
- [ ] Oracle requires symbol-level pruning from mixed files.
- [ ] Public tests do not leak source file names or hidden edges.
- [ ] Docker oracle/naive/copy_all/probes pass.
- [ ] OpenHands + Flash result is not oracle-footprint or copy-all-footprint hidden pass.

Decision: draft-spike

## References

- [GO_PILOT_PLAYBOOK.md](../GO_PILOT_PLAYBOOK.md)
- [GO_QUALITY_RUBRIC.md](../GO_QUALITY_RUBRIC.md)
- [GO_TASK_FORMAT.md](../GO_TASK_FORMAT.md)
