# FeatureLift Task: Mako template lexer and expression parse core

Extract Mako template lexing into a parse tree plus Python expression/control fragment analysis without original mako import or template runtime rendering.

## Target API

- Import: `import featurelifted; from featurelifted import Lexer, parsetree, PythonCode, PythonFragment, SyntaxException, CompileException`
- Callable: `featurelifted.Lexer.parse`
- Signature: `Lexer(text: str, filename: str | None = None).parse() -> parsetree.TemplateNode`

## Excluded Behavior

- template compilation, codegen, and runtime rendering
- TemplateLookup, caching, and filesystem loading
- CLI, extensions, babel/beaker plugins
- original mako import at runtime

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `mako`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — lex template source into parsetree nodes (text, expression, control, tags)
- **B002** — parse ${...} expressions and % control lines
- **B003** — analyze Python fragments for declared and undeclared identifiers
- **B004** — report SyntaxException and CompileException with line positions
- **B005** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B006** — the submitted package does not import forbidden upstream packages: mako
<!-- featureliftbench:behavior-clauses:end -->
