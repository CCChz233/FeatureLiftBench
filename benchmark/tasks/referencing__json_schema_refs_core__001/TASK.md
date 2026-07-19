# FeatureLift Task: JSON Schema $ref resolution

Extract referencing Registry/Resolver $ref, anchor, and fragment resolution for JSON Schema dialects without jsonschema validator implementations.

## Target API

- Import: `from featurelifted import Registry, Resource; from featurelifted.jsonschema import DRAFT202012, DRAFT7, UnknownDialect; from featurelifted.exceptions import Unresolvable, NoSuchAnchor`
- Callable: `featurelifted.Registry.resolver`
- Signature: `Registry.resolver(base_uri: str) -> Resolver`

## Excluded Behavior

- jsonschema validation keyword implementations
- network retrieval of remote schemas
- referencing test suite and original package import

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `referencing`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — Registry resource registration and base URI resolution
- **B002** — $ref pointer and external URI chaining
- **B003** — $anchor and JSON Schema dialect specifications
- **B004** — typed unresolvable and unknown dialect errors
- **B005** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B006** — the submitted package does not import forbidden upstream packages: referencing
<!-- featureliftbench:behavior-clauses:end -->
