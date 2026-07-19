# FeatureLift Task: Structure/unstructure core

Extract cattrs Converter with structure/unstructure for attrs classes, dataclasses, and nested dict/list payloads with generated dict hooks and field overrides, without original cattrs import.

## Target API

- Import: `import featurelifted; from featurelifted import Converter, structure, unstructure; from featurelifted.gen import make_dict_structure_fn, make_dict_unstructure_fn, override; from featurelifted.errors import ClassValidationError, ForbiddenExtraKeysError`
- Callable: `featurelifted.Converter.structure`
- Signature: `Converter.structure(obj: Any, cl: type) -> Any`

## Excluded Behavior

- preconf JSON/YAML/msgpack adapters and third-party codec integrations
- strategies package for union/subclass hook registry explosion
- GenConverter code generation and transform_error validation helpers
- upstream tests, docs, benchmarks, and packaging metadata
- original cattrs import at runtime

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `cattrs`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — round-trip attrs and dataclass instances through dict payloads
- **B002** — structure and unstructure nested mappings and sequences
- **B003** — register custom dict structure/unstructure hooks via gen helpers
- **B004** — apply per-field rename and omit_if_default overrides
- **B005** — reject extra dict keys when forbid_extra_keys is enabled
- **B006** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B007** — the submitted package does not import forbidden upstream packages: cattrs
<!-- featureliftbench:behavior-clauses:end -->
