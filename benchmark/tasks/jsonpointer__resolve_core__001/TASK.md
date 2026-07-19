# FeatureLift Task: JSON Pointer resolve and set

Extract RFC 6901 JSON Pointer parsing, resolve, set, and escape/unescape without importing jsonpointer.

## Target API

- Import: `import featurelifted; from featurelifted import EndOfList, JsonPointer, JsonPointerException, resolve_pointer, set_pointer, escape, unescape`
- Callable: `featurelifted.resolve_pointer`
- Signature: `resolve_pointer(doc, pointer, default=...)`

## Excluded Behavior

- jsonpatch operations beyond pointer resolve/set
- upstream tests and docs
- original jsonpointer import at runtime

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `jsonpointer`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — resolve pointers against nested dict/list documents
- **B002** — set values including array append via '-' token
- **B003** — escape and unescape ~ and / in token names
- **B004** — default values for missing paths and invalid escapes
- **B005** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B006** — the submitted package does not import forbidden upstream packages: jsonpointer
<!-- featureliftbench:behavior-clauses:end -->
