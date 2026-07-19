# FeatureLift Task: Table formatting core

Extract tabulate() table formatting with format registry, Unicode display width, column alignment, and data normalization without importing tabulate or CLI entrypoints.

## Target API

- Import: `import featurelifted; from featurelifted import tabulate, tabulate_formats, simple_separated_format`
- Callable: `featurelifted.tabulate`
- Signature: `tabulate(tabular_data, headers=(), tablefmt='simple', floatfmt='g', intfmt='', numalign='default', stralign='default', missingval='', showindex='default', disable_numparse=False, colglobalalign=None, colalign=None, preserve_whitespace=False, maxcolwidths=None, headersglobalalign=None, headersalign=None, rowalign=None, maxheadercolwidths=None, break_long_words=True, break_on_hyphens=True)`

## Excluded Behavior

- CLI entrypoint tabulate/cli.py and __main__
- upstream benchmark and example scripts
- original tabulate import at runtime

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `tabulate`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — tabulate() renders simple, grid, pipe, and plain table formats
- **B002** — automatic numeric decimal alignment and string column padding
- **B003** — colalign and colglobalalign per-column alignment overrides
- **B004** — Unicode wide-character display width via wcwidth when available
- **B005** — ANSI escape sequences excluded from visible column width
- **B006** — simple_separated_format builds custom separator TableFormat
- **B007** — tabulate_formats lists supported output format names
- **B008** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B009** — the submitted package does not import forbidden upstream packages: tabulate
<!-- featureliftbench:behavior-clauses:end -->
