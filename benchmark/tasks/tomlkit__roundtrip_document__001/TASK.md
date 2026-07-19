# FeatureLift Task: TOML document parse and round-trip editing

Extract tomlkit's core TOML parsing, document editing, and formatting-preserving dump API as a standalone package.

## Target API

- Import: `from featurelifted import parse, loads, dumps, document, table, inline_table, array, aot, string, item; from featurelifted.exceptions import ParseError, UnexpectedCharError, InvalidUnicodeValueError`
- Callable: `featurelifted.parse`
- Signature: `parse(string: str | bytes) -> TOMLDocument`

## Excluded Behavior

- original project tests
- original documentation
- release tooling and CI configuration
- packaging metadata from the original project
- external toml compliance test fixtures

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `tomlkit`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — parse TOML strings and bytes into mutable TOMLDocument objects
- **B002** — preserve comments, blank lines, table order, inline tables, literal strings, multiline strings, and array formatting when dumping parsed documents
- **B003** — dump plain mappings, nested mappings, arrays, inline tables, and arrays of tables
- **B004** — support document/table/inline_table/array/aot/string/item constructors
- **B005** — support sorted-key dumping for mappings and parsed documents
- **B006** — support datetime, date, time, integers, floats, booleans, arrays, tables, dotted keys, and unicode strings
- **B007** — raise stable ParseError subclasses with line and column information for malformed TOML
- **B008** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B009** — the submitted package does not import forbidden upstream packages: tomlkit
<!-- featureliftbench:behavior-clauses:end -->
