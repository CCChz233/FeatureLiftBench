# FeatureLift Task: Markdown plugins and HTML renderer

Build a standalone `featurelifted` package providing mistune-style `create_markdown` with HTML rendering and plugins.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    create_markdown,
    HTMLRenderer,
)
```

## Required API Details

- `create_markdown(escape=None, hard_wrap=False, renderer='html', plugins=None) -> Markdown`
- `HTMLRenderer` class must be importable

## Required Behavior

- `create_markdown()` returns a callable that renders emphasis (`**bold**`) as `<strong>` HTML.
- The default HTML renderer turns inline code spans such as `` `code` `` into `<code>` HTML.
- `create_markdown(plugins=['strikethrough'])` renders `~~text~~` using `<del>` HTML, which the plugin-less default renderer does not.
- `HTMLRenderer` is a constructible renderer class usable as the default HTML backend of `create_markdown`.
- The package exposes `create_markdown` and `HTMLRenderer` with the callable paths listed in this contract.
- The submitted package source does not import the forbidden upstream package `mistune`.

## Constraints

- Forbidden imports: `mistune`.
- Do not implement full CLI.
- Do not implement every plugin in tree.
- Do not implement runtime import of mistune.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — `create_markdown()` returns a callable that renders emphasis (`**bold**`) as `<strong>` HTML.
- **B002** — The default HTML renderer turns inline code spans such as `` `code` `` into `<code>` HTML.
- **B003** — `create_markdown(plugins=['strikethrough'])` renders `~~text~~` using `<del>` HTML, which the plugin-less default renderer does not.
- **B004** — `HTMLRenderer` is a constructible renderer class usable as the default HTML backend of `create_markdown`.
- **B005** — The package exposes `create_markdown` and `HTMLRenderer` with the callable paths listed in this contract.
- **B006** — The submitted package source does not import the forbidden upstream package `mistune`.
<!-- featureliftbench:behavior-clauses:end -->
