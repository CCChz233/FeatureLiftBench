# Python Task Examples

## Purpose

This document records representative Python task patterns. It should not reveal hidden tests or oracle files beyond what is already visible in task metadata and public design docs.

## Example Pattern: Parser or Tokenizer

Representative tasks:

- `sqlparse__parse_split_core__001`
- `python_frontmatter__roundtrip_core__001`
- `json5__parse_core__001`
- `croniter__cron_parse_core__001`

Why this is a good FeatureLift pattern:

- The public API is easy to describe.
- Correct behavior depends on parser state, token normalization, edge cases, and error handling.
- Hidden tests can distinguish narrow stubs from behavior-preserving extraction.

Design risk:

- If the parser is already isolated in one module, the task may become file copying rather than dependency closure recovery.

## Example Pattern: Validator

Representative tasks:

- `email_validator__validate_core__001`
- `cerberus__schema_validate_core__001`
- `voluptuous__schema_validate_core__001`
- `jsonschema__validator_core__001`

Why this is a good FeatureLift pattern:

- Validators have concrete observable behavior.
- Hidden tests can cover invalid inputs, nested schemas, custom errors, and compatibility details.
- Agents must preserve both success values and failure modes.

Design risk:

- Hidden tests must not introduce validators or schema features outside the declared target feature.

## Example Pattern: Serializer / Deserializer

Representative tasks:

- `dataclasses_json__serde_core__001`
- `msgpack__pack_unpack_core__001`
- `tomlkit__roundtrip_document__001`
- `ruamel_yaml__roundtrip_core__001`

Why this is a good FeatureLift pattern:

- Behavior includes round-trip fidelity, formatting, type conversion, and edge-case compatibility.
- Runtime dependencies may involve helper classes, constants, and data models.

Design risk:

- Round-trip tasks can push agents toward copying large format libraries. Compactness needs to be measured carefully.

## Example Pattern: Framework or Registry Core

Representative tasks:

- `jinja2__compile_render_core__001`
- `pytest__fixture_resolve_core__001`
- `pluggy__hook_call_order__001`
- `vibe_app__plugin_registry_core__001`

Why this is a good FeatureLift pattern:

- These tasks stress runtime behavior, global registries, extension points, and callback ordering.
- They are less reducible to a single local function.

Design risk:

- Scope can become too broad. Public and hidden tests must define a bounded reusable slice.

## Example Pattern: Config or Environment Loader

Representative tasks:

- `python_dotenv__env_parse_core__001`
- `environs__typed_env_core__001`
- `configobj__roundtrip_config_core__001`
- `coverage__config_merge_core__001`

Why this is a good FeatureLift pattern:

- Behavior depends on parsing, precedence, defaults, environment values, and error cases.
- It mirrors real migration and internal-library extraction use cases.

Design risk:

- Tests must isolate environment variables and file paths to avoid nondeterminism.

## Example Pattern: Curated Legacy or Vibe App Feature

Representative tasks:

- `vibe_app__rules_engine_core__001`
- `vibe_app__pricing_rules_core__001`
- `vibe_app__yaml_config_bootstrap__001`

Why this is useful:

- Curated apps can model messy internal repositories that are not represented by polished OSS packages.
- They can stress compact extraction from legacy clutter.

Design risk:

- Curated tasks need strong documentation to show they are not toy problems.

## TODO

- Add one audited mini case study per pattern after official experiments.
- Add examples of public-hidden gap without exposing hidden assertions.
- Link each example to its task design note after the canonical docs structure is finalized.
