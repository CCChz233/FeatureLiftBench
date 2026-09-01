# FeatureLift Task: Controller command and hooks

Build a standalone `featurelifted` package providing Cement-style App controller registration, argv dispatch, and post_setup hooks.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    App,
    Controller,
    ex,
)
```

## Required API Details

- `App(label: str | None = None, **kw)` class constructor
  - `App.__init__(self, label: str | None = None, **kw) -> None`
  - `App.setup(self) -> None`
  - `App.run(self)`
- `Controller(*args, **kw)` class constructor
- `ex(hide: bool = False, arguments=None, label: str | None = None, **parser_options)`

## Required Behavior

- An `App` subclass whose `Meta.handlers` lists a `Controller` with an `@ex` command named in `Meta.argv` returns that command's result from `run()` after setup.
- A `post_setup` hook listed in `Meta.hooks` runs during setup and receives the application object.
- After setup, the application has an installed controller, and a second `@ex` command on the same controller is selected by changing `Meta.argv`.
- The package exposes `App`, `Controller`, and `ex` with construction, `setup`, and `run` as listed in this contract.
- The submitted package source does not import the forbidden upstream package `cement`.

## Constraints

- Forbidden imports: `cement`.
- Do not implement redis extensions.
- Do not implement scanning /etc config dirs.
- Do not implement runtime import of cement.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — An `App` subclass whose `Meta.handlers` lists a `Controller` with an `@ex` command named in `Meta.argv` returns that command's result from `run()` after setup.
- **B002** — A `post_setup` hook listed in `Meta.hooks` runs during setup and receives the application object.
- **B003** — After setup, the application has an installed controller, and a second `@ex` command on the same controller is selected by changing `Meta.argv`.
- **B004** — The package exposes `App`, `Controller`, and `ex` with construction, `setup`, and `run` as listed in this contract.
- **B005** — The submitted package source does not import the forbidden upstream package `cement`.
<!-- featureliftbench:behavior-clauses:end -->
