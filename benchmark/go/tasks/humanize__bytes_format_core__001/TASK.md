# Task: humanize__bytes_format_core__001

Extract byte-size formatting and parsing from the `go-humanize` snapshot in `repo/` into package `featurelifted`.

## Output

```go
import "featurelifted"

featurelifted.Bytes(1024 * 1024)   // => "1.0 MB"
featurelifted.IBytes(1024 * 1024)  // => "1.0 MiB"
featurelifted.ParseBytes("42 MB")  // => 42000000, nil
```

## Constraints

- Do not import `github.com/dustin/go-humanize`.
- Submission must be a standalone Go module with package `featurelifted`.
- Public tests cover SI formatting, IEC formatting, and basic parsing.
- Hidden tests cover suffix variants, comma parsing, rounding, and overflow errors.

## Run tests (eval only)

```bash
go test ./public_tests/...
```
