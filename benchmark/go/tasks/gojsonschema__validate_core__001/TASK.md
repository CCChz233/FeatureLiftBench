# Task: hello_featurelifted__001

Extract `Add(a, b int) int` from the sample repo into package `featurelifted`.

## Output

```go
import "featurelifted"

featurelifted.Add(1, 2) // => 3
```

## Constraints

- Do not import `originalpkg`.
- Submission must be a standalone Go module with package `featurelifted`.
- Public tests cover basic positive addition; hidden tests cover negatives and zero.

## Run tests (eval only)

```bash
go test ./public_tests/...
```
