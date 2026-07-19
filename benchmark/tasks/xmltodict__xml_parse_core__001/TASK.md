# FeatureLift Task: XML parse and unparse core

Extract xmltodict SAX-to-ordered-dict parsing and dict-to-XML unparsing with namespace, attribute prefix, and mixed-content handling without importing xmltodict.

## Target API

- Import: `import featurelifted; from featurelifted import parse, unparse, ParsingInterrupted`
- Callable: `featurelifted.parse`
- Signature: `parse(xml_input, encoding=None, process_namespaces=False, **kwargs)`

## Excluded Behavior

- streaming item_depth callbacks and ParsingInterrupted control flow
- postprocessor hooks and force_list / force_cdata selectors
- process_comments and comment_key emission
- CLI marshal streaming entrypoint
- original xmltodict import at runtime

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `xmltodict`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — parse XML strings into ordered dicts with @ attribute prefix
- **B002** — unparse dicts back to XML with matching attr_prefix and cdata_key
- **B003** — duplicate sibling elements become lists
- **B004** — process_namespaces with optional namespace URI collapse map
- **B005** — mixed content via #text alongside child elements
- **B006** — custom attr_prefix and cdata_key options
- **B007** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B008** — the submitted package does not import forbidden upstream packages: xmltodict
<!-- featureliftbench:behavior-clauses:end -->
