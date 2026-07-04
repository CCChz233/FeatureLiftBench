# Task: mapstructure__decode_core__001

Extract map-to-struct decoding from the `mapstructure` snapshot in `repo/` into package `featurelifted`.

## Output

```go
import "featurelifted"

featurelifted.Decode(map[string]any{"name": "alice", "age": 30}, &dest)
```

## Constraints

- Do not import `github.com/go-viper/mapstructure`.
- Submission: standalone Go module (`go.mod` + package `featurelifted`).
- Public tests cover basic struct decode; hidden tests cover weak typing, squash, hooks, unused keys.

## Run tests (eval only)

```bash
go test ./public_tests/...
```
