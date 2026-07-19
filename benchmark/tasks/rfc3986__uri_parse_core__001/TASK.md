# FeatureLift Task: RFC3986 URI parse, build, and validate subset

Extract rfc3986 URIReference parsing, normalization, and URIBuilder without importing rfc3986.

## Target API

- Import: `import featurelifted; from featurelifted import URIBuilder, URIReference, is_valid_uri, normalize_uri, uri_reference`
- Callable: `featurelifted.uri_reference`
- Signature: `uri_reference(uri, encoding='utf-8') -> URIReference`

## Excluded Behavior

- IRI full unicode normalization
- validators beyond basic is_valid_uri
- original rfc3986 import at runtime

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `rfc3986`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — parse URI components and authority subcomponents
- **B002** — normalize scheme/host/path
- **B003** — URIBuilder compose and finalize
- **B004** — is_valid_uri convenience check
- **B005** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B006** — the submitted package does not import forbidden upstream packages: rfc3986
<!-- featureliftbench:behavior-clauses:end -->
