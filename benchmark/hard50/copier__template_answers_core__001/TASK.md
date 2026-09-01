# FeatureLift Task: Answers and question schema

Build a standalone `featurelifted` package that evaluates Copier question defaults, loads answers YAML, and validates choices without copying a template over the network.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    AnswersMap,
    InvalidTypeError,
    load_answersfile_data,
    Question,
    SandboxedEnvironment,
)
```

## Required API Details

- `AnswersMap(user=<factory>, init=<factory>, metadata=<factory>, last=<factory>, user_defaults=<factory>, external=<factory>)` class constructor
  - `AnswersMap.__init__(self, *args, **kwargs)`
- `Question(var_name: str, answers: AnswersMap, context: Mapping, jinja_env: SandboxedEnvironment, type: str = '', default=MISSING, choices=<factory>, **fields)` class constructor
  - `Question.__init__(self, *args, **kwargs)`
  - `Question.get_default(self) -> Any`
  - `Question.parse_answer(self, answer: Any) -> Any`
- `SandboxedEnvironment(*args, **kwargs)` class constructor
  - `SandboxedEnvironment.__init__(self, *args, **kwargs)`
- `load_answersfile_data(dst_path, answers_file='.copier-answers.yml', *, warn_on_missing=False) -> dict`
- `InvalidTypeError` must be importable and raisable

## Required Behavior

- A `Question` with `type='str'` and `default='alice'` returns `'alice'` from `get_default()` when the answers map has no override; an `AnswersMap(init={...})` override is returned instead of the declared default.
- When `{dst}/.copier-answers.yml` contains YAML mappings, `load_answersfile_data(dst)` returns those keys; a missing file returns `{}`; a custom `answers_file` name is read when provided.
- Calling `parse_answer` with a value not in `choices` raises `ValueError` whose message contains `Invalid choice`; a typed `int` question rejects a non-integer string.
- The package exposes `AnswersMap`, `Question`, `SandboxedEnvironment`, `load_answersfile_data`, and `InvalidTypeError` with the callable signatures listed in this contract.
- The package exposes all required answers/question API paths with the callable signatures listed in this contract.
- The submitted package source does not import the forbidden upstream package `copier`.

## Constraints

- Forbidden imports: `copier`.
- Do not implement run_copy over network.
- Do not implement git clone of template.
- Do not implement interactive prompt UI.
- Do not implement runtime import of copier.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — A `Question` with `type='str'` and `default='alice'` returns `'alice'` from `get_default()` when the answers map has no override; an `AnswersMap(init={...})` override is returned instead of the declared default.
- **B002** — When `{dst}/.copier-answers.yml` contains YAML mappings, `load_answersfile_data(dst)` returns those keys; a missing file returns `{}`; a custom `answers_file` name is read when provided.
- **B003** — Calling `parse_answer` with a value not in `choices` raises `ValueError` whose message contains `Invalid choice`; a typed `int` question rejects a non-integer string.
- **B004** — The package exposes `AnswersMap`, `Question`, `SandboxedEnvironment`, `load_answersfile_data`, and `InvalidTypeError` with the callable signatures listed in this contract.
- **B005** — The package exposes all required answers/question API paths with the callable signatures listed in this contract.
- **B006** — The submitted package source does not import the forbidden upstream package `copier`.
<!-- featureliftbench:behavior-clauses:end -->
