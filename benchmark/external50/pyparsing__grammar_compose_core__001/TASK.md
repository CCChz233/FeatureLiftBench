# FeatureLift Task: pyparsing grammar compose

Extract a task-scoped subset of `pyparsing` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    alphas,
    Group,
    Keyword,
    Literal,
    nums,
    OneOrMore,
    Optional,
    ParseException,
    ParseResults,
    Regex,
    Suppress,
    Word,
    ZeroOrMore,
)
```

## Required API Details

- `Word` class must be importable
  - `Word.parse_string` callable must exist
- `Literal` class must be importable
  - `Literal.parse_string` callable must exist
- `Keyword` class must be importable
- `Regex` class must be importable
- `Optional` class must be importable
- `ZeroOrMore` class must be importable
- `OneOrMore` class must be importable
  - `OneOrMore.parse_string` callable must exist
- `Group` class must be importable
  - `Group.parse_string` callable must exist
- `Suppress` class must be importable
- `ParseException` must be importable and raisable
- `ParseResults` class must be importable
  - `ParseResults.as_list` callable must exist
  - `ParseResults.as_dict` callable must exist
- `alphas` constant must exist
- `nums` constant must exist

## Required Behavior

- The extracted feature must support this observable behavior: compose Word/Literal/Optional/Group helpers and parse_string with named results. Required observable cases include word literal compose; optional group.
- The extracted feature must support this observable behavior: Keyword/Regex/ZeroOrMore/OneOrMore/Suppress composition. Required observable cases include keyword and regex; zero one or more; group structure.
- The extracted feature must support this observable behavior: ParseException on mismatch including parse_all leftovers. Required observable cases include parse exception; parse all flag.
- ParseResults supports as_list/as_dict accessors used in tests.
- The package exposes the required task API paths for Word/Literal/Keyword/Regex/Optional/ZeroOrMore/OneOrMore/Group/Suppress/ParseException/ParseResults/alphas/nums with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: pyparsing.

## Constraints

- Forbidden imports: `pyparsing`.
- Do not implement railroad diagrams.
- Do not implement infixNotation suite.
- Do not implement parse actions.
- Do not implement original pyparsing import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — The extracted feature must support this observable behavior: compose Word/Literal/Optional/Group helpers and parse_string with named results. Required observable cases include word literal compose; optional group.
- **B002** — The extracted feature must support this observable behavior: Keyword/Regex/ZeroOrMore/OneOrMore/Suppress composition. Required observable cases include keyword and regex; zero one or more; group structure.
- **B003** — The extracted feature must support this observable behavior: ParseException on mismatch including parse_all leftovers. Required observable cases include parse exception; parse all flag.
- **B004** — ParseResults supports as_list/as_dict accessors used in tests.
- **B005** — The package exposes the required task API paths for Word/Literal/Keyword/Regex/Optional/ZeroOrMore/OneOrMore/Group/Suppress/ParseException/ParseResults/alphas/nums with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: pyparsing.
<!-- featureliftbench:behavior-clauses:end -->
