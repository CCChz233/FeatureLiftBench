# Design card: uritools__uri_join_normalize_core__001

**status:** `validated_staging`  
**wave:** W4  
**package:** `uritools`  
**repository_url:** https://github.com/tkem/uritools  
**planned_lift_type:** Adapted  
**final_lift_type:** Adapted  
**reclassification_reason:** None  
**feature_family:** protocol_state_transition  
**entanglement:** parser_state_coupling  
**feature_one_liner:** urisplit/urijoin/urinorm helpers  
**lift_review_flag:** none  
**skim_status:** `pass` (2026-07-31)

> Filled for design_card phase. `feasibility.commit` still unresolved until pin.  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/archive/plans/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.urisplit(uri: str) -> SplitResult"
  - "featurelifted.uriunsplit(parts: SplitResult | tuple) -> str"
  - "featurelifted.urijoin(base: str, ref: str, strict: bool = False) -> str"
  - "featurelifted.urinorm(uri: str) -> str  # Adapted: recompose via getscheme/getauthority/getpath (dot-segment normalize)"
  - "featurelifted.uridecode(s: str, encoding: str = 'utf-8') -> str"
  - "featurelifted.uriencode(s: str, safe: str = '', encoding: str = 'utf-8') -> str"
returns:
  - "SplitResult is a 5-tuple namedtuple with fields: scheme, authority, path, query, fragment"
  - "uriunsplit/urijoin/urinorm return str"
  - "uridecode returns decoded str; uriencode returns percent-encoded str"
exceptions:
  - "ValueError on malformed URI when strict validation applies"
defaults:
  - "urijoin strict=False"
  - "uriencode safe=''; encoding='utf-8'"
  - "uridecode encoding='utf-8'"
state_effects:
  - "none"
```

## upstream_mapping

```yaml
primary_symbols:
  - "uritools.urisplit"
  - "uritools.urijoin"
  - "uritools.SplitResult.getpath / getscheme / getauthority (adapted urinorm)"
supporting_components:
  - "uritools.uriencode"
  - "uritools.uridecode"
  - "uritools.SplitResult"
semantic_delta:
  - "Export flat featurelifted helpers; SplitResult fields declared explicitly"
  - "uriencode/uridecode kept because join/normalize roundtrips commonly need percent-coding of path/query segments"
```

## oracle_basis

```yaml
basis: upstream
notes: |
  Adapted packaging of uritools helpers as one Required API surface.
```

## scope

```yaml
included:
  - "urisplit/uriunsplit for absolute and relative refs"
  - "urijoin with strict=False default and strict=True validation cases"
  - "urinorm as Adapted recompose: scheme/authority normalized + getpath() dot-segment collapse (upstream urinorm removed)"
  - "uriencode/uridecode for UTF-8 percent coding used by join/norm roundtrips"
excluded:
  - "network fetch"
  - "IRI-only edge tables beyond what uritools implements"
  - "uridefrag / uricompose helpers outside the Required API"
```

## feasibility

```yaml
commit: "1908bfa847b319ee01fb83b100381b1cafad94c5"  # tag v6.1.3
license: "MIT"
python_versions:
  - "3.10"
  - "3.11"
  - "3.12"
native_or_heavy_dependencies: "none"
offline_resources: "string-only URI ops"
```

## acceptance

```yaml
closure_review: pass
reference_pass: pass
isolation_pass: pass
no_original_import: pass
overlap_check: pass
```

## agent_notes

- Staging path: `benchmark/staging/uritools__uri_join_normalize_core__001/`
- Skim passed; pin commit before materialize.
- Do not promote to `benchmark/tasks/` in pilot wave.
