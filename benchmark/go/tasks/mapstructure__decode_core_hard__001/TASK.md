# Task: mapstructure__decode_core_hard__001

Extract map-to-struct decoding from the `mapstructure` snapshot in `repo/` into package `featurelifted`.

## Output

```go
import "featurelifted"

err := featurelifted.Decode(map[string]any{"name": "alice"}, &dest)
decoder, err := featurelifted.NewDecoder(&featurelifted.DecoderConfig{Result: &dest})
```

The extracted package should support standalone decoding for configuration-style `map[string]any` inputs without importing the original module.

## Constraints

- Do not import `github.com/go-viper/mapstructure` or `github.com/go-viper/mapstructure/v2`.
- Submission must be a standalone Go module with package `featurelifted`.
- Preserve the public API names used by the tests: `Decode`, `DecodeMetadata`, `NewDecoder`, `DecoderConfig`, `Metadata`, `DecodeHookFunc`, `DecodeHookFuncType`, `DecodeHookFuncValue`, `ComposeDecodeHookFunc`, and `StringToSliceHookFunc`.
- Keep the reusable decoding slice; do not copy unrelated cache, schema, or registry helpers.

## Run tests (eval only)

```bash
go test ./public_tests/...
```
