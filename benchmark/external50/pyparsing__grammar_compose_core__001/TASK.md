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
  - `Word.parse_string(instring: str, parse_all: bool = False) -> ParseResults`
- `Literal` class must be importable
  - `Literal.parse_string(instring: str, parse_all: bool = False) -> ParseResults`
- `Keyword` class must be importable
- `Regex` class must be importable
- `Optional` class must be importable
- `ZeroOrMore` class must be importable
- `OneOrMore` class must be importable
  - `OneOrMore.parse_string(instring: str, parse_all: bool = False) -> ParseResults`
- `Group` class must be importable
  - `Group.parse_string(instring: str, parse_all: bool = False) -> ParseResults`
- `Suppress` class must be importable
- `ParseException` must be importable and raisable
- `ParseResults` class must be importable
  - `ParseResults.as_list() -> list`
  - `ParseResults.as_dict() -> dict`
- `alphas` constant must exist
- `nums` constant must exist

## Required Behavior

- When Word and Literal expressions are combined with `+`, calling `parse_string` on matching text returns a ParseResults whose `as_list()` preserves token order and whose results names are available through `as_dict()`; wrapping expressions in Group nests their tokens as one list, and an absent Optional expression contributes no token.
- When Keyword or Regex expressions match, named Regex text appears in ParseResults; ZeroOrMore accepts zero or more repetitions, OneOrMore parses repeated words, and Suppress accepts either an expression or a string such as `","` and omits each matched separator from the returned tokens.
- Calling `parse_string` with input that does not match the expression raises ParseException with a nonnegative `loc`; when `parse_all=True`, otherwise-valid input with unmatched trailing text also raises ParseException.
- For a successful parse, ParseResults.as_list() returns the positional token structure and ParseResults.as_dict() returns the values assigned results names, including nested Group structure where applicable.
- The package exposes the required task API paths for Word/Literal/Keyword/Regex/Optional/ZeroOrMore/OneOrMore/Group/Suppress/ParseException/ParseResults/alphas/nums with the kinds listed in this contract.
- Scanning every Python file in the submitted package finds no `import pyparsing` or `from pyparsing ...` statement.

## Constraints

- Forbidden imports: `pyparsing`.
- Do not implement railroad diagrams.
- Do not implement infixNotation suite.
- Do not implement parse actions.
- Do not implement original pyparsing import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — When Word and Literal expressions are combined with `+`, calling `parse_string` on matching text returns a ParseResults whose `as_list()` preserves token order and whose results names are available through `as_dict()`; wrapping expressions in Group nests their tokens as one list, and an absent Optional expression contributes no token.
- **B002** — When Keyword or Regex expressions match, named Regex text appears in ParseResults; ZeroOrMore accepts zero or more repetitions, OneOrMore parses repeated words, and Suppress accepts either an expression or a string such as `","` and omits each matched separator from the returned tokens.
- **B003** — Calling `parse_string` with input that does not match the expression raises ParseException with a nonnegative `loc`; when `parse_all=True`, otherwise-valid input with unmatched trailing text also raises ParseException.
- **B004** — For a successful parse, ParseResults.as_list() returns the positional token structure and ParseResults.as_dict() returns the values assigned results names, including nested Group structure where applicable.
- **B005** — The package exposes the required task API paths for Word/Literal/Keyword/Regex/Optional/ZeroOrMore/OneOrMore/Group/Suppress/ParseException/ParseResults/alphas/nums with the kinds listed in this contract.
- **B006** — Scanning every Python file in the submitted package finds no `import pyparsing` or `from pyparsing ...` statement.
<!-- featureliftbench:behavior-clauses:end -->
