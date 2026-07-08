# FeatureLift Task: Case-insensitive multidict mutation and proxy behavior

Extract a pure-Python subset of aio-libs/multidict into a standalone `featurelifted` package.

The implementation must not import `multidict`, must not read from `repo/`, must not use the network, and must use only the standard library.

## Target API

```python
from featurelifted import MultiDict, CIMultiDict, MultiDictProxy, CIMultiDictProxy
```

## Required Behavior

- `MultiDict` stores duplicate keys in insertion order; `__getitem__` returns the most recent value.
- `add` appends another value for a key; `getall` returns all values for a key.
- `popone` removes and returns the most recent value; `popall` removes and returns every value.
- `CIMultiDict` compares keys case-insensitively and stores case-insensitive string keys.
- `MultiDictProxy` and `CIMultiDictProxy` mutate their underlying base mapping.
- Equality compares stored key/value pairs (case-insensitively for `CIMultiDict`).

## Constraints

- Forbidden imports: `multidict`.
- Forbidden path access: `repo/`, `multidict/`.
- Do not depend on the C extension implementation.

## Public vs Hidden Tests

Public tests cover basic mutation, duplicate keys, and proxy writes.
Hidden tests cover `popone`/`popall`, case-insensitive lookup/equality, and proxy reflection semantics.
