# Task: semver__version_parse_core__001

Extract semantic version parsing and comparison from the `Masterminds/semver` snapshot in `repo/` into package `featurelifted`.

## Output

```go
import "featurelifted"

v, err := featurelifted.Parse("1.2.3")
cmp, err := featurelifted.Compare("1.0.0-alpha", "1.0.0")
```

`Parse` should return a version value exposing `Major`, `Minor`, and `Patch` fields.

## Constraints

- Do not import `github.com/Masterminds/semver`.
- Submission must be a standalone Go module with package `featurelifted`.
- Public tests cover basic major/minor/patch parsing and numeric comparison.
- Hidden tests cover prerelease ordering, invalid version errors, and build metadata comparison.

## Run tests (eval only)

```bash
go test ./public_tests/...
```
