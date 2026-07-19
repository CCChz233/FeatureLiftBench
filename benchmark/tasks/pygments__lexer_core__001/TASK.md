# FeatureLift Task: Regex lexer core

Extract Pygments lexer infrastructure and Python lexer tokenization as a standalone package.

## Target API

- Import: `from featurelifted import lex, get_lexer_by_name, PythonLexer; from featurelifted import token`
- Callable: `featurelifted.lex`
- Signature: `lex(code: str, lexer: Lexer) -> Iterable[tuple[token._TokenType, str]]`

## Excluded Behavior

- HTML, LaTeX, terminal, and other formatters
- command-line pygmentize tool
- hundreds of non-Python language lexers
- original project tests and documentation

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `pygments`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — tokenize Python source with PythonLexer and lex()
- **B002** — resolve lexers by alias with get_lexer_by_name
- **B003** — emit Token types for keywords, strings, comments, numbers, operators, and names
- **B004** — honor lexer options such as stripall and ensurenl
- **B005** — support modeline and encoding helpers used by lexer lookup
- **B006** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B007** — the submitted package does not import forbidden upstream packages: pygments
<!-- featureliftbench:behavior-clauses:end -->
